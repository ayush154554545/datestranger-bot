"""
Session Message Dispatcher.
Ensures single-flight, deduplicated, sequential, and cancellable message handling
per active synthetic conversation session. Completely eliminates duplicate greetings
and out-of-order race conditions.
"""

from collections import deque
import threading
import time
from typing import Any, Callable, Dict, Optional, Set
from datestranger.synthetic.models import DialogueResponse, ConversationState


class SessionDispatcher:
    """
    Manages per-session message queues, task cancellation on stop,
    deduplication of Telegram update/message IDs, and greeting synchronization.
    """

    def __init__(
        self,
        synthetic_engine: Any,
        send_message_callback: Callable[[int, int, str], None],
        typing_callback: Optional[Callable[[int], None]] = None,
    ):
        self.engine = synthetic_engine
        self.send_message = send_message_callback
        self.send_typing = typing_callback or (lambda uid: None)
        self._session_locks: Dict[str, threading.Lock] = {}
        self._session_queues: Dict[str, deque] = {}
        self._pending_greetings: Dict[str, threading.Timer] = {}
        self._processed_event_ids: Set[str] = set()
        self._lock = threading.RLock()

    def register_session(self, conv_id: str, real_uid: int, synthetic_pid: int):
        with self._lock:
            self._session_locks[conv_id] = threading.Lock()
            self._session_queues[conv_id] = deque()

    def _interruptible_sleep(self, mem: Any, duration: float, step: float = 0.05) -> bool:
        if duration <= 0:
            return True
        end_time = time.time() + duration
        while time.time() < end_time:
            if not mem.is_active or mem.has_ended or getattr(mem, "cancellation_requested", False):
                return False
            time.sleep(min(step, max(0.001, end_time - time.time())))
        return not (not mem.is_active or mem.has_ended or getattr(mem, "cancellation_requested", False))

    def schedule_opening_greeting(
        self,
        conv_id: str,
        real_uid: int,
        synthetic_pid: int,
        delay_seconds: float = 2.0,
    ):
        """
        Schedules the initial greeting. If the user sends a message before this timer fires,
        the timer is cancelled immediately, preventing duplicate greetings.
        """
        with self._lock:
            if conv_id in self._pending_greetings:
                self._pending_greetings[conv_id].cancel()

            def _fire_greeting():
                with self._lock:
                    self._pending_greetings.pop(conv_id, None)

                # Acquire per-session lock to serialize greeting with any incoming user message
                with self._lock:
                    if conv_id not in self._session_locks:
                        self._session_locks[conv_id] = threading.Lock()
                    session_lock = self._session_locks[conv_id]

                print(f"[DISPATCHER] Acquiring lock for greeting {conv_id}")
                with session_lock:
                    print(f"[DISPATCHER] Lock acquired for greeting {conv_id}")
                    mem = self.engine.memory_mgr.get(conv_id)
                    if (
                        not mem
                        or not mem.is_active
                        or mem.has_ended
                        or getattr(mem, "cancellation_requested", False)
                        or mem.greeting_sent
                        or mem.messages_exchanged > 0
                    ):
                        print(f"[DISPATCHER] Greeting cancelled/inactive for {conv_id}")
                        return

                    try:
                        mem.greeting_sent = True
                        resp = self.engine.generate_opening(conv_id)

                        delay = resp.delay_seconds
                        if delay > 1.5:
                            if not self._interruptible_sleep(mem, delay * 0.4):
                                return
                            self.send_typing(real_uid)
                            if not self._interruptible_sleep(mem, delay * 0.6):
                                return
                        else:
                            self.send_typing(real_uid)
                            if not self._interruptible_sleep(mem, delay):
                                return

                        if not mem.is_active or mem.has_ended or getattr(mem, "cancellation_requested", False):
                            return

                        self.send_message(real_uid, synthetic_pid, resp.text)
                    except Exception as e:
                        print(f"[SESSION DISPATCHER GREETING ERROR] {e}")
                    finally:
                        print(f"[DISPATCHER] Releasing lock for greeting {conv_id}")
                print(f"[DISPATCHER] Lock released for greeting {conv_id}")

            t = threading.Timer(delay_seconds, _fire_greeting)
            self._pending_greetings[conv_id] = t
            t.daemon = True
            t.start()

    def cancel_pending_greeting(self, conv_id: str):
        """Cancels opening greeting if user spoke first."""
        with self._lock:
            timer = self._pending_greetings.pop(conv_id, None)
            if timer:
                timer.cancel()
            mem = self.engine.memory_mgr.get(conv_id)
            if mem:
                mem.greeting_sent = True

    def is_session_active(self, conv_id: str) -> bool:
        mem = self.engine.memory_mgr.get(conv_id)
        return bool(mem and mem.is_active and not mem.has_ended)

    def dispatch_user_message(
        self,
        conv_id: str,
        real_uid: int,
        synthetic_pid: int,
        user_text: str,
        event_id: Optional[Any] = None,
        on_conversation_end: Optional[Callable[[int, int], None]] = None,
    ):
        """
        Processes incoming user message sequentially:
        1. Deduplicates by event_id (e.g. Telegram message_id).
        2. Cancels any pending unprompted greeting.
        3. Enqueues and processes in order without concurrent collisions.
        """
        # Deduplication check
        if event_id is not None:
            dedup_key = f"{conv_id}:{event_id}"
            with self._lock:
                if dedup_key in self._processed_event_ids:
                    print(f"[DEDUP] Skipping duplicate event {dedup_key}")
                    return
                self._processed_event_ids.add(dedup_key)
                if len(self._processed_event_ids) > 10000:
                    self._processed_event_ids.clear()

        # Cancel pending greeting because user has already spoken!
        self.cancel_pending_greeting(conv_id)

        # Get or create per-session lock
        with self._lock:
            if conv_id not in self._session_locks:
                self._session_locks[conv_id] = threading.Lock()
            session_lock = self._session_locks[conv_id]

        def _worker():
            print(f"[DISPATCHER] Acquiring lock for {conv_id}")
            with session_lock:
                print(f"[DISPATCHER] Lock acquired, generating response")
                mem = self.engine.memory_mgr.get(conv_id)
                if not mem or not mem.is_active or mem.has_ended or getattr(mem, "cancellation_requested", False):
                    print(f"[DISPATCHER] Session inactive or ended, aborting worker for {conv_id}")
                    return

                try:
                    resp = self.engine.handle_user_message(conv_id, user_text, message_id=event_id)

                    # If stop command was detected, abort immediately without sending filler
                    if resp.should_end_conversation and not resp.text:
                        self.stop_session(conv_id)
                        if on_conversation_end:
                            on_conversation_end(real_uid, synthetic_pid)
                        return

                    delay = resp.delay_seconds
                    if delay > 2.0:
                        if not self._interruptible_sleep(mem, delay * 0.4):
                            return
                        self.send_typing(real_uid)
                        if not self._interruptible_sleep(mem, delay * 0.6):
                            return
                    else:
                        self.send_typing(real_uid)
                        if not self._interruptible_sleep(mem, delay):
                            return

                    if not mem.is_active or mem.has_ended or getattr(mem, "cancellation_requested", False):
                        return

                    if resp.text:
                        self.send_message(real_uid, synthetic_pid, resp.text)

                    # Handle double message if any
                    if resp.is_double_message and resp.second_message_text:
                        gap = resp.second_message_delay or 2.0
                        if not self._interruptible_sleep(mem, gap * 0.5):
                            return
                        self.send_typing(real_uid)
                        if not self._interruptible_sleep(mem, gap * 0.5):
                            return
                        if mem.is_active and not mem.has_ended and not getattr(mem, "cancellation_requested", False):
                            self.send_message(real_uid, synthetic_pid, resp.second_message_text)

                    if resp.should_end_conversation:
                        self.stop_session(conv_id)
                        if on_conversation_end:
                            on_conversation_end(real_uid, synthetic_pid)

                except Exception as e:
                    print(f"[SESSION DISPATCHER WORKER ERROR] {e}")
                finally:
                    print(f"[DISPATCHER] Response generated, releasing lock")
            print(f"[DISPATCHER] Lock released for {conv_id}")

        # Run worker in sequential session thread
        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def stop_session(self, conv_id: str):
        """Immediately halts any in-flight or scheduled tasks for this conversation."""
        with self._lock:
            # 1. Cancel pending greeting
            timer = self._pending_greetings.pop(conv_id, None)
            if timer:
                timer.cancel()

            # 2. Mark memory inactive
            mem = self.engine.memory_mgr.get(conv_id)
            if mem:
                mem.is_active = False
                mem.has_ended = True
                mem.cancellation_requested = True

            # 3. Clean up engine
            self.engine.end_conversation(conv_id, reason="stop_command")

            # 4. Clean up queues and session locks
            self._session_queues.pop(conv_id, None)
            self._session_locks.pop(conv_id, None)

    def force_cleanup(self, conv_id: str, timeout: float = 0.5):
        """Force stops session and waits briefly for in-flight threads."""
        self.stop_session(conv_id)
        time.sleep(timeout)
