# -*- coding: utf-8 -*-
# ============================================================
#        DATE STRANGER | CHAT BOT (TEST VERSION)
#        @testdate27_bot
# ============================================================

import telebot
import os
import requests
import threading
import time
import certifi
from datetime import datetime, timedelta
from collections import defaultdict
from flask import Flask
from threading import Thread, Lock
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN  = os.getenv("BOT_TOKEN")
MONGO_URL  = os.getenv("MONGO_URL")
ADMIN_ID   = int(os.getenv("ADMIN_ID"))
BOT_NAME   = "Date Stranger"
BOT_USER   = "@testdate27_bot"

# ── Discord Webhooks ─────────────────────────────────────────
STATUS_WEBHOOK      = os.getenv("STATUS_WEBHOOK")
GIRL_WEBHOOK        = os.getenv("GIRL_WEBHOOK")
BOY_WEBHOOK         = os.getenv("BOY_WEBHOOK")
OTHER_WEBHOOK       = os.getenv("OTHER_WEBHOOK")
GIRL_MEDIA_WEBHOOK  = os.getenv("GIRL_MEDIA_WEBHOOK")
BOY_MEDIA_WEBHOOK   = os.getenv("BOY_MEDIA_WEBHOOK")
OTHER_MEDIA_WEBHOOK = os.getenv("OTHER_MEDIA_WEBHOOK")

# ── Logging Webhooks ─────────────────────────────────────────
ALERTS_WEBHOOK    = os.getenv("ALERTS_WEBHOOK")
CHAT_LOG_WEBHOOK  = os.getenv("CHAT_LOG_WEBHOOK")
MEDIA_LOG_WEBHOOK = os.getenv("MEDIA_LOG_WEBHOOK")
VOICE_LOG_WEBHOOK = os.getenv("VOICE_LOG_WEBHOOK")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ── MongoDB Connection ───────────────────────────────────────
print("🔌 Connecting to MongoDB...")
client = MongoClient(
    MONGO_URL,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=30000,
    connectTimeoutMS=30000,
    socketTimeoutMS=30000,
)

try:
    client.admin.command('ping')
    print("✅ MongoDB Connected!")
except Exception as e:
    print(f"❌ MongoDB Connection Failed: {e}")
    exit(1)

DB_NAME = os.getenv("DB_NAME", "datestranger")
db = client[DB_NAME]

users_col    = db["users"]
waiting_col  = db["waiting"]
chats_col    = db["active_chats"]
reports_col  = db["reports"]
notices_col  = db["notices"]
feedback_col = db["feedback"]
settings_col = db["settings"]
stats_col    = db["daily_stats"]


# ============================================================
# CONSTANTS
# ============================================================

LANGUAGES = [
    "English", "Hindi", "Spanish", "Arabic",
    "French", "Russian", "Turkish", "Urdu",
    "Bengali", "Portuguese", "Indonesian", "Other"
]

COUNTRIES = [
    "🇮🇳 India", "🇺🇸 USA", "🇬🇧 UK", "🇨🇦 Canada",
    "🇦🇺 Australia", "🇵🇰 Pakistan", "🇧🇩 Bangladesh",
    "🇮🇩 Indonesia", "🇧🇷 Brazil", "🇷🇺 Russia",
    "🇩🇪 Germany", "🇫🇷 France", "🇪🇸 Spain", "🇮🇹 Italy",
    "🇹🇷 Turkey", "🇸🇦 Saudi Arabia", "🇦🇪 UAE",
    "🇵🇭 Philippines", "🇲🇾 Malaysia", "🌍 Other"
]

INTERESTS = [
    "💬 Chatting", "😘 Flirting", "😴 Bored",
    "❤️ Love", "💑 Relationship", "🔥 Intimacy",
    "🌶 Sex", "🔄 Exchange"
]

admin_states = {}

# ── Logging State ────────────────────────────────────────────
log_buffer = defaultdict(list)
log_buffer_lock = Lock()
watching_state = {}
active_chats_tracker = {}
tracker_lock = Lock()

daily_stats = {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "signups": 0,
    "chats_started": 0,
    "total_messages": 0,
    "photos": 0,
    "videos": 0,
    "voices": 0,
    "reports": 0,
    "bans": 0,
}
stats_lock = Lock()


# ============================================================
# DISCORD WEBHOOK HELPERS
# ============================================================

def _send_discord(webhook_url, payload):
    if not webhook_url:
        return
    def _send():
        try:
            requests.post(webhook_url, json=payload, timeout=10)
        except Exception as e:
            print(f"[DISCORD ERROR] {e}")
    Thread(target=_send, daemon=True).start()


def _send_discord_file(webhook_url, file_bytes, filename, content=""):
    if not webhook_url:
        return
    def _send():
        try:
            files = {'file': (filename, file_bytes)}
            data = {'content': content}
            requests.post(webhook_url, data=data, files=files, timeout=30)
        except Exception as e:
            print(f"[DISCORD FILE ERROR] {e}")
    Thread(target=_send, daemon=True).start()


def _gender_webhook(gender: str):
    g = (gender or "").lower()
    if g == "female":
        return GIRL_WEBHOOK
    elif g == "male":
        return BOY_WEBHOOK
    else:
        return OTHER_WEBHOOK


def _gender_media_webhook(gender: str):
    g = (gender or "").lower()
    if g == "female":
        return GIRL_MEDIA_WEBHOOK
    elif g == "male":
        return BOY_MEDIA_WEBHOOK
    else:
        return OTHER_MEDIA_WEBHOOK


def _tg_profile_url(user_id):
    return f"tg://user?id={user_id}"


def build_user_embed(user, title: str, color: int):
    uid         = user.get("user_id", "N/A")
    name        = user.get("name") or "N/A"
    username    = user.get("tg_username") or "N/A"
    tg_name     = user.get("tg_first_name") or "N/A"
    gender      = (user.get("gender") or "N/A").capitalize()
    age         = user.get("age", "N/A")
    country     = user.get("country") or "N/A"
    language    = user.get("language") or "N/A"
    interest    = user.get("interest") or "N/A"
    chats       = user.get("total_chats", 0)
    joined      = str(user.get("joined", ""))[:10]
    last_active = str(user.get("last_active", ""))[:16]
    is_banned_u = "🚫 Banned" if user.get("is_banned") else "✅ Active"

    gender_icon = {"Male": "👨", "Female": "👩"}.get(gender, "🌈")
    tg_link     = f"[Open Profile](tg://user?id={uid})"

    embed = {
        "title"     : title,
        "color"     : color,
        "timestamp" : datetime.utcnow().isoformat(),
        "footer"    : {"text": f"{BOT_NAME} • {BOT_USER}"},
        "fields"    : [
            {"name": "🆔 User ID",       "value": f"`{uid}`",    "inline": True},
            {"name": "📛 Nickname",      "value": name,           "inline": True},
            {"name": "📱 TG Username",   "value": f"@{username}", "inline": True},
            {"name": "👤 TG Name",       "value": tg_name,        "inline": True},
            {"name": f"{gender_icon} Gender", "value": gender,    "inline": True},
            {"name": "🎂 Age",           "value": str(age),       "inline": True},
            {"name": "🌍 Country",       "value": country,        "inline": True},
            {"name": "🗣 Language",      "value": language,       "inline": True},
            {"name": "💡 Interest",      "value": interest,       "inline": True},
            {"name": "💬 Total Chats",   "value": str(chats),     "inline": True},
            {"name": "📅 Joined",        "value": joined,         "inline": True},
            {"name": "🕐 Last Active",   "value": last_active,    "inline": True},
            {"name": "🔰 Status",        "value": is_banned_u,    "inline": True},
            {"name": "🔗 Telegram",      "value": tg_link,        "inline": False},
        ]
    }
    return embed


def notify_new_user(user, event: str = "join"):
    gender = (user.get("gender") or "").lower()
    if gender != "female":
        return

    embed = build_user_embed(user, "🆕 New 👩 GIRL Joined!", 0xFF69B4)
    embed["fields"].insert(0, {
        "name"  : "📋 Event",
        "value" : "✅ Signup Complete" if event == "signup" else "👋 Joined Bot",
        "inline": True
    })

    _send_discord(GIRL_WEBHOOK, {"embeds": [embed]})
    _send_discord(STATUS_WEBHOOK, {"embeds": [embed]})


# ============================================================
# DAILY STATS HELPERS
# ============================================================

def increment_stat(key, value=1):
    with stats_lock:
        today = datetime.now().strftime("%Y-%m-%d")
        if daily_stats["date"] != today:
            _save_daily_stats()
            for k in ["signups", "chats_started", "total_messages",
                      "photos", "videos", "voices", "reports", "bans"]:
                daily_stats[k] = 0
            daily_stats["date"] = today
        daily_stats[key] = daily_stats.get(key, 0) + value


def _save_daily_stats():
    try:
        stats_col.update_one(
            {"date": daily_stats["date"]},
            {"$set": dict(daily_stats)},
            upsert=True
        )
    except Exception as e:
        print(f"[STATS SAVE ERROR] {e}")


# ============================================================
# LOG CHANNEL & DISCORD LOGGING
# ============================================================

def _log_chat_started(uid1, uid2):
    user1 = get_user(uid1)
    user2 = get_user(uid2)
    if not user1 or not user2:
        return

    def info(u):
        n  = u.get("name") or "?"
        un = u.get("tg_username") or ""
        g  = u.get("gender", "?")
        a  = u.get("age", "?")
        c  = u.get("country", "?")
        un_str = f"@{un}" if un else "no_username"
        return f"{gender_emoji(g)} <b>{n}</b> ({un_str}) • {a} • {c}"

    msg = (
        f"━━━━━━━━━━━━━━━\n"
        f"🆕 <b>NEW CHAT</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"{info(user1)}\n"
        f"<code>{uid1}</code>\n\n"
        f"     ↕\n\n"
        f"{info(user2)}\n"
        f"<code>{uid2}</code>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    )

    try:
        bot.send_message(ADMIN_ID, msg)
    except Exception:
        pass

    chat_key = _chat_key(uid1, uid2)
    with tracker_lock:
        active_chats_tracker[chat_key] = {
            "users"    : [uid1, uid2],
            "started"  : datetime.now(),
            "msg_count": 0,
        }


def _log_chat_ended(uid):
    pid = get_partner(uid)
    if not pid:
        return
    chat_key = _chat_key(uid, pid)
    with tracker_lock:
        if chat_key in active_chats_tracker:
            chat_data = active_chats_tracker[chat_key]
            duration = (datetime.now() - chat_data["started"]).total_seconds() // 60
            msg_count = chat_data["msg_count"]
            del active_chats_tracker[chat_key]

            _flush_chat_buffer(chat_key)

            user1 = get_user(uid)
            user2 = get_user(pid)
            n1 = user1.get("name", "?") if user1 else "?"
            n2 = user2.get("name", "?") if user2 else "?"
            _send_discord(CHAT_LOG_WEBHOOK, {
                "embeds": [{
                    "title": "🛑 Chat Ended",
                    "color": 0xE74C3C,
                    "description": (
                        f"**{n1}** ↔ **{n2}**\n"
                        f"⏱ Duration: {int(duration)} min\n"
                        f"💬 Messages: {msg_count}"
                    ),
                    "timestamp": datetime.utcnow().isoformat()
                }]
            })


def _chat_key(uid1, uid2):
    a, b = sorted([uid1, uid2])
    return f"{a}_{b}"


def _add_to_log_buffer(from_uid, to_uid, text):
    chat_key = _chat_key(from_uid, to_uid)
    with log_buffer_lock:
        log_buffer[chat_key].append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "from": from_uid,
            "to"  : to_uid,
            "text": text,
        })

    with tracker_lock:
        if chat_key in active_chats_tracker:
            active_chats_tracker[chat_key]["msg_count"] += 1

    _forward_to_watcher(from_uid, to_uid, text)


def _forward_to_watcher(from_uid, to_uid, text):
    chat_key = _chat_key(from_uid, to_uid)
    for admin_id, watched_key in list(watching_state.items()):
        if watched_key == chat_key:
            from_user = get_user(from_uid)
            from_name = from_user.get("name", "?") if from_user else "?"
            try:
                bot.send_message(admin_id,
                    f"👁 <b>{from_name}</b>: {safe_html(text)}"
                )
            except Exception:
                pass

def _flush_chat_buffer(chat_key, chat_ended=False, end_reason="manual"):
    """
    Send buffered messages to Discord.
    chat_ended: True = post full conversation with end header
    """
    with log_buffer_lock:
        messages = log_buffer.pop(chat_key, [])

    if not messages:
        return

    # Get user info from chat_key (format: "uid1_uid2")
    try:
        uid_a, uid_b = chat_key.split("_")
        uid_a, uid_b = int(uid_a), int(uid_b)
    except Exception:
        # Fallback - get from first message
        first = messages[0]
        uid_a, uid_b = first["from"], first["to"]

    user_a = get_user(uid_a)
    user_b = get_user(uid_b)

    def user_info(u, uid):
        if not u:
            return f"Unknown (ID: {uid})"
        n  = u.get("name") or "?"
        un = u.get("tg_username") or ""
        g  = u.get("gender", "?")
        a  = u.get("age", "?")
        c  = u.get("country", "?")
        un_str = f"@{un}" if un else "no username"
        emoji = gender_emoji(g)
        return f"{emoji} **{n}** ({un_str}) • {a} • {c} • ID:`{uid}`"

    info_a = user_info(user_a, uid_a)
    info_b = user_info(user_b, uid_b)

    na = user_a.get("name", "?") if user_a else "?"
    nb = user_b.get("name", "?") if user_b else "?"

    # Build message lines
    lines = []
    for m in messages:
        if m["from"] == uid_a:
            from_name = na
        else:
            from_name = nb
        text = m["text"].replace("`", "'")[:500]
        lines.append(f"`[{m['time']}]` **{from_name}**: {text}")

    chat_body = "\n".join(lines)

    # Build header
    if chat_ended:
        title_icon = "🛑"
        if end_reason == "inactivity":
            title = f"{title_icon} Chat Ended (Inactivity)"
            color = 0xE67E22
        else:
            title = f"{title_icon} Chat Ended"
            color = 0xE74C3C
    else:
        title = "💬 Live Chat (Auto-Flushed)"
        color = 0x5865F2

    header = (
        f"**👤 USER 1:**\n{info_a}\n\n"
        f"**👤 USER 2:**\n{info_b}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"**💬 CONVERSATION ({len(messages)} messages):**\n"
    )

    full_description = header + chat_body

    # Discord embed limit is 4096 chars
    if len(full_description) > 4000:
        # Split into multiple embeds
        chunks = []
        current = header
        for line in lines:
            if len(current) + len(line) + 2 > 4000:
                chunks.append(current)
                current = ""
            current += line + "\n"
        if current:
            chunks.append(current)

        for i, chunk in enumerate(chunks, 1):
            embed = {
                "title": f"{title} (Part {i}/{len(chunks)})" if len(chunks) > 1 else title,
                "description": chunk,
                "color": color,
                "footer": {"text": f"Chat: {chat_key}"},
                "timestamp": datetime.utcnow().isoformat()
            }
            _send_discord(CHAT_LOG_WEBHOOK, {"embeds": [embed]})
    else:
        embed = {
            "title": title,
            "description": full_description,
            "color": color,
            "footer": {"text": f"Chat: {chat_key}"},
            "timestamp": datetime.utcnow().isoformat()
        }
        _send_discord(CHAT_LOG_WEBHOOK, {"embeds": [embed]})


def _log_media_to_discord(from_uid, to_uid, media_type, file_id, caption=None):
    try:
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

        r = requests.get(file_url, timeout=30)
        if r.status_code != 200:
            return

        u1 = get_user(from_uid)
        u2 = get_user(to_uid)

        # Sender info
        n1  = u1.get("name", "?") if u1 else "?"
        un1 = u1.get("tg_username", "") if u1 else ""
        g1  = u1.get("gender", "?") if u1 else "?"
        a1  = u1.get("age", "?") if u1 else "?"
        c1  = u1.get("country", "?") if u1 else "?"
        un1_str = f"@{un1}" if un1 else "no_username"

        # Receiver info
        n2  = u2.get("name", "?") if u2 else "?"
        un2 = u2.get("tg_username", "") if u2 else ""
        g2  = u2.get("gender", "?") if u2 else "?"
        a2  = u2.get("age", "?") if u2 else "?"
        c2  = u2.get("country", "?") if u2 else "?"
        un2_str = f"@{un2}" if un2 else "no_username"

        ext_map = {
            "photo"      : "jpg",
            "video"      : "mp4",
            "voice"      : "ogg",
            "video_note" : "mp4",
            "animation"  : "mp4",
            "audio"      : "mp3",
            "document"   : "bin",
            "sticker"    : "webp",
        }
        ext = ext_map.get(media_type, "bin")
        filename = f"{from_uid}_{int(time.time())}.{ext}"

        type_emoji = {
            "photo": "📸", "video": "🎥", "voice": "🎤",
            "video_note": "🎬", "animation": "🎞",
            "audio": "🎵", "document": "📄", "sticker": "🎨"
        }
        emoji = type_emoji.get(media_type, "📎")
        ge1 = gender_emoji(g1)
        ge2 = gender_emoji(g2)

        # ── Full caption with IDs ──
        cap = (
            f"**{emoji} {media_type.upper()}**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"**👤 FROM:**\n"
            f"{ge1} **{n1}** ({un1_str})\n"
            f"🆔 `{from_uid}` • {a1} • {c1}\n\n"
            f"**👤 TO:**\n"
            f"{ge2} **{n2}** ({un2_str})\n"
            f"🆔 `{to_uid}` • {a2} • {c2}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        if caption:
            cap += f"\n📝 **Caption:** {caption[:300]}"

        # ── Pick main webhook ──
        if media_type == "voice":
            webhook = VOICE_LOG_WEBHOOK
        else:
            webhook = MEDIA_LOG_WEBHOOK

        _send_discord_file(webhook, r.content, filename, cap)

        # ── ALSO send photos to gender-specific webhook ──
        if media_type == "photo":
            gender_webhook = _gender_media_webhook(g1)
            if gender_webhook and gender_webhook != webhook:
                _send_discord_file(gender_webhook, r.content, filename, cap)

        # Update msg count
        chat_key = _chat_key(from_uid, to_uid)
        with tracker_lock:
            if chat_key in active_chats_tracker:
                active_chats_tracker[chat_key]["msg_count"] += 1

        # Live watch notification
        for admin_id, watched_key in list(watching_state.items()):
            if watched_key == chat_key:
                try:
                    bot.send_message(admin_id,
                        f"👁 <b>{safe_html(n1)}</b>: [{emoji} sent {media_type}]"
                    )
                except Exception:
                    pass

    except Exception as e:
        print(f"[MEDIA LOG ERROR] {e}")


def buffer_flusher():
    """
    Background thread that:
    - Flushes very large buffers (>50 messages) to prevent memory issues
    - Normal flush happens ONLY when chat ends
    """
    while True:
        try:
            time.sleep(60)  # check every 60 seconds
            with log_buffer_lock:
                keys = list(log_buffer.keys())
            for k in keys:
                # Only flush if buffer has 50+ messages (prevent memory overflow)
                with log_buffer_lock:
                    msg_count = len(log_buffer.get(k, []))
                if msg_count >= 50:
                    _flush_chat_buffer(k)
        except Exception as e:
            print(f"[FLUSHER ERROR] {e}")


# ============================================================
# DAILY SUMMARY (00:00)
# ============================================================

def send_daily_summary():
    try:
        with stats_lock:
            _save_daily_stats()
            stats_copy = dict(daily_stats)

        date_str = stats_copy.get("date", "?")

        top_user = users_col.find_one(
            {"signup_complete": True},
            sort=[("total_chats", -1)]
        )
        top_user_str = "N/A"
        if top_user:
            top_user_str = f"{top_user.get('name', '?')} ({top_user.get('total_chats', 0)} chats)"

        embed = {
            "title": f"📊 Daily Summary — {date_str}",
            "color": 0x3498DB,
            "fields": [
                {"name": "👥 New Signups",  "value": str(stats_copy.get("signups", 0)), "inline": True},
                {"name": "💬 Chats Started","value": str(stats_copy.get("chats_started", 0)), "inline": True},
                {"name": "📨 Messages",     "value": str(stats_copy.get("total_messages", 0)), "inline": True},
                {"name": "📸 Photos",       "value": str(stats_copy.get("photos", 0)), "inline": True},
                {"name": "🎥 Videos",       "value": str(stats_copy.get("videos", 0)), "inline": True},
                {"name": "🎤 Voices",       "value": str(stats_copy.get("voices", 0)), "inline": True},
                {"name": "🚨 Reports",      "value": str(stats_copy.get("reports", 0)), "inline": True},
                {"name": "🚫 Bans",         "value": str(stats_copy.get("bans", 0)), "inline": True},
                {"name": "🏆 Top User",     "value": top_user_str, "inline": False},
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": f"{BOT_NAME} • Daily Report"}
        }

        _send_discord(ALERTS_WEBHOOK, {"embeds": [embed]})

        with stats_lock:
            for k in ["signups", "chats_started", "total_messages",
                      "photos", "videos", "voices", "reports", "bans"]:
                daily_stats[k] = 0
            daily_stats["date"] = datetime.now().strftime("%Y-%m-%d")

    except Exception as e:
        print(f"[DAILY SUMMARY ERROR] {e}")


def daily_summary_scheduler():
    last_sent_date = None
    while True:
        try:
            now = datetime.now()
            if now.hour == 0 and now.minute < 5:
                today = now.strftime("%Y-%m-%d")
                if last_sent_date != today:
                    send_daily_summary()
                    last_sent_date = today
            time.sleep(60)
        except Exception as e:
            print(f"[SUMMARY SCHEDULER ERROR] {e}")
            time.sleep(60)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_user(user_id):
    return users_col.find_one({"user_id": user_id})


def create_user(tg_user):
    if not get_user(tg_user.id):
        users_col.insert_one({
            "user_id"         : tg_user.id,
            "tg_first_name"   : tg_user.first_name or "",
            "tg_username"     : tg_user.username or "",
            "name"            : None,
            "gender"          : None,
            "age"             : None,
            "country"         : None,
            "language"        : None,
            "interest"        : None,
            "filter_gender"   : "Any",
            "filter_language" : "Any",
            "signup_complete" : False,
            "signup_step"     : None,
            "total_chats"     : 0,
            "is_banned"       : False,
            "is_vip"          : False,
            "joined"          : datetime.now(),
            "last_active"     : datetime.now(),
        })


def update_user(user_id, data):
    users_col.update_one({"user_id": user_id}, {"$set": data})


def touch_user(user_id):
    update_user(user_id, {"last_active": datetime.now()})


def is_banned(user_id):
    u = get_user(user_id)
    return u.get("is_banned", False) if u else False


def is_signup_done(user_id):
    u = get_user(user_id)
    return u.get("signup_complete", False) if u else False


def get_signup_step(user_id):
    u = get_user(user_id)
    return u.get("signup_step") if u else None


def get_motd():
    doc = settings_col.find_one({"key": "motd"})
    return doc.get("value") if doc else None


def set_motd(text):
    settings_col.update_one(
        {"key": "motd"},
        {"$set": {"key": "motd", "value": text, "updated": datetime.now()}},
        upsert=True
    )


def clear_motd():
    settings_col.delete_one({"key": "motd"})


# ── Chat State ───────────────────────────────────────────────

def get_partner(user_id):
    chat = chats_col.find_one({
        "$or": [{"user1": user_id}, {"user2": user_id}]
    })
    if chat:
        return chat["user2"] if chat["user1"] == user_id else chat["user1"]
    return None


def in_chat(user_id):
    return get_partner(user_id) is not None


def in_waiting(user_id):
    return waiting_col.find_one({"user_id": user_id}) is not None


def add_waiting(user_id, priority=0):
    if not in_waiting(user_id):
        waiting_col.insert_one({
            "user_id"  : user_id,
            "priority" : priority,
            "timestamp": datetime.now()
        })


def remove_waiting(user_id):
    waiting_col.delete_one({"user_id": user_id})


def create_chat(uid1, uid2):
    chats_col.insert_one({
        "user1"         : uid1,
        "user2"         : uid2,
        "started"       : datetime.now(),
        "last_message_at": datetime.now()
    })
    users_col.update_one({"user_id": uid1}, {"$inc": {"total_chats": 1}})
    users_col.update_one({"user_id": uid2}, {"$inc": {"total_chats": 1}})
    increment_stat("chats_started")
    _log_chat_started(uid1, uid2)


def end_chat(user_id):
    _log_chat_ended(user_id)
    chats_col.delete_many({
        "$or": [{"user1": user_id}, {"user2": user_id}]
    })


def update_chat_activity(user_id):
    chats_col.update_many(
        {"$or": [{"user1": user_id}, {"user2": user_id}]},
        {"$set": {"last_message_at": datetime.now()}}
    )


# ── Matching ────────────────────────────────────────────────

def find_match(user_id):
    me = get_user(user_id)
    if not me:
        return None

    my_gender   = (me.get("gender") or "").lower()
    my_f_gender = (me.get("filter_gender") or "any").lower() if user_id == ADMIN_ID else "any"

    candidates = list(
        waiting_col.find({"user_id": {"$ne": user_id}})
                   .sort([("priority", -1), ("timestamp", 1)])
    )
    if not candidates:
        return None

    best_score     = -1
    best_candidate = None

    for c in candidates:
        c_user = get_user(c["user_id"])
        if not c_user or not c_user.get("signup_complete"):
            continue

        c_gender   = (c_user.get("gender") or "").lower()
        c_user_id  = c_user.get("user_id")
        c_f_gender = (c_user.get("filter_gender") or "any").lower() if c_user_id == ADMIN_ID else "any"

        i_want_them  = (my_f_gender == "any") or (my_f_gender == c_gender)
        they_want_me = (c_f_gender  == "any") or (c_f_gender  == my_gender)

        if not i_want_them or not they_want_me:
            continue

        score = 10
        c_priority = c.get("priority", 0)
        if c_priority >= 10:
            score += 1000
        if user_id == ADMIN_ID:
            score += 500

        if score > best_score:
            best_score     = score
            best_candidate = c

    return best_candidate


# ── Display Helpers ─────────────────────────────────────────

def gender_emoji(gender):
    mapping = {"male": "👨", "female": "👩", "other": "🌈"}
    return mapping.get((gender or "").lower(), "👤")


def safe_html(text):
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )


# ============================================================
# KEYBOARDS
# ============================================================

def kb_main():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🔍 Search Partner")
    kb.row("⚙️ Settings", "ℹ️ Help")
    return kb


def kb_chat():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("⏭ Next Partner", "🛑 Stop Chat")
    kb.row("🚨 Report Partner")
    return kb


def kb_waiting():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("❌ Cancel Search")
    return kb


def kb_admin():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📢 Send Notice",   "📡 Broadcast")
    kb.row("🔎 Search User",   "💬 Message User")
    kb.row("📊 Statistics",    "👥 View All Users")
    kb.row("🚫 Ban/Unban",     "♻️ Unban User")
    kb.row("📋 Reports List",  "🗑 Clear Reports")
    kb.row("📝 Set MOTD",      "🗑 Clear MOTD")
    kb.row("🔍 Active Chats",  "⏳ Waiting List")
    kb.row("🧹 Clear All Waiting")
    kb.row("⬅️ Exit Admin")
    return kb


def kb_remove():
    return telebot.types.ReplyKeyboardRemove()


def kb_cancel_edit():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("❌ Cancel Edit")
    return kb


def kb_cancel_admin_action():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("❌ Cancel Action")
    return kb


# ── Signup Keyboards ────────────────────────────────────────

def ikb_signup_gender():
    kb = telebot.types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        telebot.types.InlineKeyboardButton("👨 Male",   callback_data="sg_male"),
        telebot.types.InlineKeyboardButton("👩 Female", callback_data="sg_female"),
        telebot.types.InlineKeyboardButton("🌈 Other",  callback_data="sg_other"),
    )
    return kb


def ikb_signup_country():
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    for c in COUNTRIES:
        kb.add(telebot.types.InlineKeyboardButton(c, callback_data=f"sc_{c}"))
    return kb


def ikb_signup_lang():
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    for lang in LANGUAGES:
        kb.add(telebot.types.InlineKeyboardButton(lang, callback_data=f"sl_{lang}"))
    return kb


def ikb_signup_interest():
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    for interest in INTERESTS:
        kb.add(telebot.types.InlineKeyboardButton(interest, callback_data=f"si_{interest}"))
    return kb


def ikb_settings(user_id):
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        telebot.types.InlineKeyboardButton("✏️ Edit Name",     callback_data="s_name"),
        telebot.types.InlineKeyboardButton("👤 Edit Gender",   callback_data="s_gender"),
        telebot.types.InlineKeyboardButton("🎂 Edit Age",      callback_data="s_age"),
        telebot.types.InlineKeyboardButton("🌍 Edit Country",  callback_data="s_country"),
        telebot.types.InlineKeyboardButton("🗣 Edit Language", callback_data="s_lang"),
        telebot.types.InlineKeyboardButton("💡 Edit Interest", callback_data="s_interest"),
    )
    if user_id == ADMIN_ID:
        kb.add(telebot.types.InlineKeyboardButton("🔎 Filter: Gender (Admin)", callback_data="s_fgender"))
    kb.add(telebot.types.InlineKeyboardButton("📊 View Profile", callback_data="s_profile"))
    return kb


def ikb_pick_gender(prefix):
    kb = telebot.types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        telebot.types.InlineKeyboardButton("👨 Male",   callback_data=f"{prefix}_male"),
        telebot.types.InlineKeyboardButton("👩 Female", callback_data=f"{prefix}_female"),
        telebot.types.InlineKeyboardButton("🌈 Other",  callback_data=f"{prefix}_other"),
    )
    kb.add(telebot.types.InlineKeyboardButton("◀️ Back", callback_data="s_back"))
    return kb


def ikb_pick_filter_gender():
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        telebot.types.InlineKeyboardButton("🌐 Any",    callback_data="fg_any"),
        telebot.types.InlineKeyboardButton("👨 Male",   callback_data="fg_male"),
        telebot.types.InlineKeyboardButton("👩 Female", callback_data="fg_female"),
        telebot.types.InlineKeyboardButton("🌈 Other",  callback_data="fg_other"),
    )
    kb.add(telebot.types.InlineKeyboardButton("◀️ Back", callback_data="s_back"))
    return kb


def ikb_pick_country():
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    for c in COUNTRIES:
        kb.add(telebot.types.InlineKeyboardButton(c, callback_data=f"ec_{c}"))
    kb.add(telebot.types.InlineKeyboardButton("◀️ Back", callback_data="s_back"))
    return kb


def ikb_pick_lang(prefix):
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    for lang in LANGUAGES:
        kb.add(telebot.types.InlineKeyboardButton(lang, callback_data=f"{prefix}_{lang}"))
    kb.add(telebot.types.InlineKeyboardButton("◀️ Back", callback_data="s_back"))
    return kb


def ikb_pick_interest(prefix):
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    for interest in INTERESTS:
        kb.add(telebot.types.InlineKeyboardButton(interest, callback_data=f"{prefix}_{interest}"))
    kb.add(telebot.types.InlineKeyboardButton("◀️ Back", callback_data="s_back"))
    return kb


# ============================================================
# /start  &  SIGNUP FLOW
# ============================================================

@bot.message_handler(commands=["start"])
def cmd_start(message):
    tg = message.from_user
    create_user(tg)

    update_user(tg.id, {
        "tg_first_name": tg.first_name or "",
        "tg_username"  : tg.username or "",
    })

    if is_banned(tg.id):
        bot.send_message(message.chat.id,
            "🚫 You are banned from Date Stranger."
        )
        return

    user = get_user(tg.id)

    if user.get("signup_complete"):
        name     = user.get("name") or tg.first_name
        interest = user.get("interest") or "Not set"

        motd      = get_motd()
        motd_text = f"\n\n📢 <b>Notice:</b>\n{safe_html(motd)}" if motd else ""

        text = (
            f"👋 <b>Welcome back, {safe_html(name)}!</b>\n\n"
            f"💘 <b>Date Stranger</b> — Anonymous Chat\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💡 <b>Your Interest:</b> {safe_html(interest)}\n"
            f"✅ 100% Anonymous\n"
            f"━━━━━━━━━━━━━━━"
            f"{motd_text}\n\n"
            f"Press 🔍 <b>Search Partner</b> to start chatting!"
        )
        bot.send_message(message.chat.id, text, reply_markup=kb_main())
        return

    bot.send_message(message.chat.id,
        f"💘 <b>Welcome to Date Stranger!</b>\n\n"
        f"Let's set up your profile first.\n"
        f"It takes just 30 seconds! ⏱\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<i>Your info is anonymous in chats.\n"
        f"It's only used to match you better!</i>"
    )
    _ask_name(message.chat.id, tg.id)


def _ask_name(chat_id, user_id):
    update_user(user_id, {"signup_step": "name"})
    bot.send_message(chat_id,
        "📝 <b>Step 1 of 6</b>\n\n"
        "What should we call you?\n"
        "<i>(Enter a nickname, 2-20 letters)</i>"
    )


def _ask_age(chat_id, user_id):
    update_user(user_id, {"signup_step": "age"})
    bot.send_message(chat_id,
        "🎂 <b>Step 2 of 6</b>\n\n"
        "How old are you?\n"
        "<i>(Enter number 13-80)</i>"
    )


def _ask_gender(chat_id, user_id):
    update_user(user_id, {"signup_step": "gender"})
    bot.send_message(chat_id,
        "👤 <b>Step 3 of 6</b>\n\n"
        "What's your gender?",
        reply_markup=ikb_signup_gender()
    )


def _ask_country(chat_id, user_id):
    update_user(user_id, {"signup_step": "country"})
    bot.send_message(chat_id,
        "🌍 <b>Step 4 of 6</b>\n\n"
        "Where are you from?",
        reply_markup=ikb_signup_country()
    )


def _ask_language(chat_id, user_id):
    update_user(user_id, {"signup_step": "language"})
    bot.send_message(chat_id,
        "🗣 <b>Step 5 of 6</b>\n\n"
        "What language do you speak?",
        reply_markup=ikb_signup_lang()
    )


def _ask_interest(chat_id, user_id):
    update_user(user_id, {"signup_step": "interest"})
    bot.send_message(chat_id,
        "💡 <b>Step 6 of 6</b>\n\n"
        "What are you here for?",
        reply_markup=ikb_signup_interest()
    )


def _finish_signup(chat_id, user_id):
    update_user(user_id, {
        "signup_complete": True,
        "signup_step"    : None
    })
    user = get_user(user_id)

    bot.send_message(chat_id,
        f"🎉 <b>All Done, {safe_html(user.get('name'))}!</b>\n\n"
        f"Your profile is ready ✅\n\n"
        f"👤 {gender_emoji(user.get('gender'))} "
        f"{user.get('gender', '').capitalize()}, {user.get('age')}\n"
        f"🌍 {user.get('country')}\n"
        f"🗣 {user.get('language')}\n"
        f"💡 {safe_html(user.get('interest') or 'N/A')}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Press 🔍 <b>Search Partner</b> to find someone!",
        reply_markup=kb_main()
    )

    increment_stat("signups")
    notify_new_user(user, event="signup")


# ============================================================
# /help
# ============================================================

@bot.message_handler(commands=["help"])
@bot.message_handler(func=lambda m: m.text == "ℹ️ Help")
def cmd_help(message):
    if not is_signup_done(message.from_user.id):
        cmd_start(message)
        return

    text = (
        f"ℹ️ <b>{BOT_NAME} — Help</b>\n\n"
        f"<b>📖 How To Use:</b>\n"
        f"1. Press 🔍 Search Partner\n"
        f"2. Start chatting anonymously\n"
        f"3. ⏭ Next to skip | 🛑 Stop to end\n\n"
        f"<b>⌨️ Commands:</b>\n"
        f"/start    — Home screen\n"
        f"/search   — Find a partner\n"
        f"/next     — Skip to next person\n"
        f"/stop     — End current chat\n"
        f"/settings — Edit profile\n"
        f"/help     — This menu\n"
        f"/feedback — Send feedback to admin\n\n"
        f"<b>📨 You can send:</b>\n"
        f"✅ Text, Photos, Videos\n"
        f"✅ Voice, Stickers, GIFs\n"
        f"✅ Documents\n\n"
        f"<b>📜 Rules:</b>\n"
        f"❌ No spam or harassment\n"
        f"❌ No adult content\n"
        f"❌ Don't share personal info\n"
        f"✅ Be kind &amp; respectful\n\n"
        f"<b>🚨 Report:</b> Press 🚨 during chat\n\n"
        f"<b>💬 Feedback:</b> /feedback your message"
    )
    bot.send_message(message.chat.id, text, reply_markup=kb_main())


@bot.message_handler(commands=["feedback"])
def cmd_feedback(message):
    uid = message.from_user.id
    if not is_signup_done(uid):
        cmd_start(message)
        return

    text = message.text.replace("/feedback", "").strip()
    if not text:
        bot.send_message(message.chat.id,
            "💬 <b>Send Feedback</b>\n\n"
            "Usage: /feedback <i>your message here</i>"
        )
        return

    feedback_col.insert_one({
        "user_id"  : uid,
        "text"     : text,
        "timestamp": datetime.now()
    })

    bot.send_message(message.chat.id,
        "✅ <b>Feedback sent!</b>\nThank you 🙏"
    )

    try:
        user = get_user(uid)
        name = user.get("name") or "N/A"
        bot.send_message(ADMIN_ID,
            f"💬 <b>New Feedback</b>\n\n"
            f"From: <code>{uid}</code> ({safe_html(name)})\n\n"
            f"📝 {safe_html(text)}"
        )
    except Exception:
        pass


# ============================================================
# /settings
# ============================================================

@bot.message_handler(commands=["settings"])
@bot.message_handler(func=lambda m: m.text == "⚙️ Settings")
def cmd_settings(message):
    if not is_signup_done(message.from_user.id):
        cmd_start(message)
        return

    uid  = message.from_user.id
    user = get_user(uid)
    bot.send_message(
        message.chat.id,
        build_settings_text(user, uid),
        reply_markup=ikb_settings(uid)
    )


def build_settings_text(user, user_id):
    n  = safe_html(user.get("name") or "Not set")
    g  = user.get("gender") or "Not set"
    a  = user.get("age") or "Not set"
    c  = user.get("country") or "Not set"
    l  = user.get("language") or "Not set"
    i  = safe_html(user.get("interest") or "Not set")
    fg = user.get("filter_gender") or "Any"

    filter_block = ""
    if user_id == ADMIN_ID:
        filter_block = (
            f"\n<b>🔎 Match Filters (Admin Only):</b>\n"
            f"  Gender   : {fg}\n"
        )

    return (
        f"⚙️ <b>Profile &amp; Settings</b>\n\n"
        f"<b>👤 My Info:</b>\n"
        f"  Name     : {n}\n"
        f"  Gender   : {gender_emoji(g)} {g.capitalize() if g != 'Not set' else g}\n"
        f"  Age      : 🎂 {a}\n"
        f"  Country  : 🌍 {c}\n"
        f"  Language : 🗣 {l}\n"
        f"  Interest : 💡 {i}\n"
        f"{filter_block}\n"
        f"<i>Tap below to update</i> 👇"
    )


# ============================================================
# /search
# ============================================================

@bot.message_handler(commands=["search"])
@bot.message_handler(func=lambda m: m.text == "🔍 Search Partner")
def cmd_search(message):
    uid = message.from_user.id

    if not is_signup_done(uid):
        cmd_start(message)
        return

    if is_banned(uid):
        bot.send_message(message.chat.id, "🚫 You are banned!", reply_markup=kb_main())
        return

    if in_chat(uid):
        bot.send_message(message.chat.id,
            "⚠️ You are already in a chat!\n"
            "Press 🛑 Stop Chat first.",
            reply_markup=kb_chat()
        )
        return

    if in_waiting(uid):
        bot.send_message(message.chat.id,
            "⏳ Already searching...\n"
            "Press ❌ Cancel Search to stop.",
            reply_markup=kb_waiting()
        )
        return

    _do_search(uid, message.chat.id)


def _build_admin_partner_card(partner_id):
    partner = get_user(partner_id)
    if not partner:
        return f"❌ User {partner_id} not found in DB."

    name        = safe_html(partner.get('name') or 'N/A')
    tg_first    = safe_html(partner.get('tg_first_name') or 'N/A')
    tg_username = partner.get('tg_username') or ""
    gender      = partner.get('gender') or 'N/A'
    age         = partner.get('age', 'N/A')
    country     = partner.get('country') or 'N/A'
    language    = partner.get('language') or 'N/A'
    interest    = safe_html(partner.get('interest') or 'N/A')
    total_chats = partner.get('total_chats', 0)
    joined      = str(partner.get('joined', ''))[:10]
    last_active = str(partner.get('last_active', ''))[:16]

    if tg_username:
        username_line = f"📱 <b>Username:</b> @{safe_html(tg_username)}"
        tg_link_line  = f"🔗 <b>Open:</b> https://t.me/{safe_html(tg_username)}"
    else:
        username_line = f"📱 <b>Username:</b> <i>No username set</i>"
        tg_link_line  = f"🔗 <b>Open:</b> <a href=\"tg://user?id={partner_id}\">Tap to open profile</a>"

    return (
        f"✅ <b>Partner Found!</b>\n\n"
        f"🔰 <b>ADMIN VIEW</b> (Hidden from partner)\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🆔 <b>User ID:</b> <code>{partner_id}</code>\n"
        f"📛 <b>Nickname:</b> {name}\n"
        f"👤 <b>TG Name:</b> {tg_first}\n"
        f"{username_line}\n"
        f"{gender_emoji(gender)} <b>Gender:</b> {gender.capitalize() if gender != 'N/A' else gender}\n"
        f"🎂 <b>Age:</b> {age}\n"
        f"🌍 <b>Country:</b> {country}\n"
        f"🗣 <b>Language:</b> {language}\n"
        f"💡 <b>Interest:</b> {interest}\n"
        f"💬 <b>Total Chats:</b> {total_chats}\n"
        f"📅 <b>Joined:</b> {joined}\n"
        f"🕐 <b>Last Active:</b> {last_active}\n"
        f"{tg_link_line}\n"
             f"━━━━━━━━━━━━━━━\n"
        f"🎭 <b>Connected Anonymously</b>\n\n"
        f"Say <b>Hello</b> 👋\n\n"
        f"⏰ <i>Chat will auto-close after 30 min of inactivity</i>"
      
    )


def _do_search(uid, chat_id):
    priority = 10 if uid == ADMIN_ID else 0
    match    = find_match(uid)

    if match:
        pid = match["user_id"]
        remove_waiting(uid)
        remove_waiting(pid)
        create_chat(uid, pid)

        if uid == ADMIN_ID:
            partner_details = _build_admin_partner_card(pid)
            bot.send_message(chat_id, partner_details,
                             reply_markup=kb_chat(),
                             disable_web_page_preview=True)
        else:
            msg_connected = (
                "✅ <b>Partner Found!</b>\n\n"
                "🎭 Connected Anonymously\n\n"
                "Say <b>Hello</b> 👋\n\n"
                "⏰ <i>Chat will auto-close after 30 min of inactivity</i>"
            )
            bot.send_message(chat_id, msg_connected, reply_markup=kb_chat())

        if pid == ADMIN_ID:
            try:
                searcher_details = _build_admin_partner_card(uid)
                bot.send_message(pid, searcher_details,
                                 reply_markup=kb_chat(),
                                 disable_web_page_preview=True)
            except Exception as e:
                print(f"[NOTIFY ADMIN ERROR] {e}")
        else:
            try:
                bot.send_message(pid,
                    "✅ <b>Partner Found!</b>\n\n"
                    "🎭 Connected Anonymously\n\n"
                    "Say <b>Hello</b> 👋\n\n"
                    "⏰ <i>Chat will auto-close after 30 min of inactivity</i>",
                    reply_markup=kb_chat()
                )
            except Exception as e:
                print(f"[NOTIFY ERROR] {e}")

    else:
        add_waiting(uid, priority=priority)
        q    = waiting_col.count_documents({})
        user = get_user(uid)
        interest = user.get("interest") or "Not set"

        admin_tag = ""
        filter_tag = ""
        if uid == ADMIN_ID:
            admin_tag  = "\n🔰 <b>Admin Priority Active</b>"
            fg = user.get("filter_gender") or "Any"
            filter_tag = f"\n🔎 Gender Filter → {fg}"

        bot.send_message(chat_id,
            f"🔍 <b>Searching for partner...</b>\n\n"
            f"💡 Your Interest: {safe_html(interest)}\n"
            f"👥 In queue: <b>{q}</b>"
            f"{filter_tag}"
            f"{admin_tag}\n\n"
            f"⏳ We'll notify you!\n"
            f"<i>Press ❌ to cancel</i>",
            reply_markup=kb_waiting()
        )


@bot.message_handler(commands=["stop"])
@bot.message_handler(func=lambda m: m.text == "🛑 Stop Chat")
def cmd_stop(message):
    _do_stop(message.from_user.id, message.chat.id)


def _do_stop(uid, chat_id):
    if in_waiting(uid):
        remove_waiting(uid)
        bot.send_message(chat_id,
            "❌ <b>Search cancelled.</b>\n\n"
            "Press 🔍 Search Partner anytime!",
            reply_markup=kb_main()
        )
        return

    pid = get_partner(uid)
    if pid:
        end_chat(uid)
        bot.send_message(chat_id,
            "🛑 <b>Chat ended.</b>\n\n"
            "Hope you enjoyed it! 😊\n"
            "Press 🔍 Search to find someone new!",
            reply_markup=kb_main()
        )
        try:
            bot.send_message(pid,
                "🛑 <b>Your partner left.</b>\n\n"
                "Press 🔍 Search to find someone new!",
                reply_markup=kb_main()
            )
        except Exception:
            pass
    else:
        bot.send_message(chat_id,
            "⚠️ You're not in a chat.\n"
            "Press 🔍 Search Partner!",
            reply_markup=kb_main()
        )


@bot.message_handler(commands=["next"])
@bot.message_handler(func=lambda m: m.text == "⏭ Next Partner")
def cmd_next(message):
    uid = message.from_user.id

    if not is_signup_done(uid):
        cmd_start(message)
        return

    if in_waiting(uid):
        bot.send_message(message.chat.id,
            "⏳ Still searching... please wait!",
            reply_markup=kb_waiting()
        )
        return

    pid = get_partner(uid)
    if pid:
        end_chat(uid)
        try:
            bot.send_message(pid,
                "⏭ <b>Partner skipped.</b>\n\n"
                "🔍 Looking for new partner...",
                reply_markup=kb_waiting()
            )
            add_waiting(pid)
            _try_match_waiting(pid)
        except Exception:
            pass

    bot.send_message(message.chat.id,
        "⏭ <b>Finding next partner...</b>",
        reply_markup=kb_waiting()
    )
    _do_search(uid, message.chat.id)


def _try_match_waiting(uid):
    match = find_match(uid)
    if not match:
        return
    pid = match["user_id"]
    remove_waiting(uid)
    remove_waiting(pid)
    create_chat(uid, pid)

    for a in [uid, pid]:
        try:
            if a == ADMIN_ID:
                partner = pid if a == uid else uid
                bot.send_message(a, _build_admin_partner_card(partner),
                                 reply_markup=kb_chat(),
                                 disable_web_page_preview=True)
            else:
                bot.send_message(a,
                    "✅ <b>Partner Found!</b>\n\n"
                    "🎭 Connected Anonymously\n\n"
                    "Say <b>Hello</b> 👋\n\n"
                    "⏰ <i>Chat will auto-close after 30 min of inactivity</i>",
                    reply_markup=kb_chat()
                )
        except Exception:
            pass


@bot.message_handler(func=lambda m: m.text == "❌ Cancel Search")
def cancel_search(message):
    uid = message.from_user.id
    if in_waiting(uid):
        remove_waiting(uid)
        bot.send_message(message.chat.id,
            "❌ <b>Search cancelled.</b>",
            reply_markup=kb_main()
        )
    elif in_chat(uid):
        bot.send_message(message.chat.id,
            "⚠️ You are in a chat, not searching.",
            reply_markup=kb_chat()
        )
    else:
        bot.send_message(message.chat.id,
            "⚠️ You were not searching.",
            reply_markup=kb_main()
        )


# ============================================================
# NEW MONITORING COMMANDS
# ============================================================

def _admin_cmd_only(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "🚫 Admin only command.")
        return False
    return True


@bot.message_handler(commands=["active"])
def cmd_active(message):
    if not _admin_cmd_only(message):
        return

    with tracker_lock:
        chats = list(active_chats_tracker.items())

    if not chats:
        bot.send_message(message.chat.id, "❌ No active chats.")
        return

    text = "🔍 <b>Active Chats</b>\n\n"
    for i, (key, data) in enumerate(chats, 1):
        u1, u2 = data["users"]
        user1 = get_user(u1)
        user2 = get_user(u2)
        n1 = user1.get("name", "?") if user1 else "?"
        n2 = user2.get("name", "?") if user2 else "?"
        un1 = user1.get("tg_username", "") if user1 else ""
        un2 = user2.get("tg_username", "") if user2 else ""
        u1_str = f"<b>{safe_html(n1)}</b>" + (f" (@{safe_html(un1)})" if un1 else "")
        u2_str = f"<b>{safe_html(n2)}</b>" + (f" (@{safe_html(un2)})" if un2 else "")
        duration = (datetime.now() - data["started"]).total_seconds() // 60
        text += (
            f"<b>{i}.</b> {u1_str} ↔ {u2_str}\n"
            f"   💬 {data['msg_count']} msgs | ⏱ {int(duration)} min\n\n"
        )

    text += f"\n<i>Use</i> <code>/watch N</code> <i>to monitor live</i>"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["watch"])
def cmd_watch(message):
    """Watch a specific active chat live - shows history first then live."""
    if not _admin_cmd_only(message):
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id,
            "Usage: /watch <number>\nUse /active to see numbers."
        )
        return

    try:
        num = int(parts[1])
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid number.")
        return

    with tracker_lock:
        chats = list(active_chats_tracker.items())

    if num < 1 or num > len(chats):
        bot.send_message(message.chat.id, f"❌ Chat #{num} not found.")
        return

    key, data = chats[num - 1]
    u1, u2 = data["users"]
    user1 = get_user(u1)
    user2 = get_user(u2)
    n1 = user1.get("name", "?") if user1 else "?"
    n2 = user2.get("name", "?") if user2 else "?"
    un1 = user1.get("tg_username", "") if user1 else ""
    un2 = user2.get("tg_username", "") if user2 else ""
    un1_str = f"@{un1}" if un1 else "no_username"
    un2_str = f"@{un2}" if un2 else "no_username"

    admin_id = message.from_user.id
    watching_state[admin_id] = key

    # ── Send watch header ──
    bot.send_message(message.chat.id,
        f"👁 <b>Now Watching Chat</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 <b>{safe_html(n1)}</b> ({un1_str}) — <code>{u1}</code>\n"
        f"     ↕\n"
        f"👤 <b>{safe_html(n2)}</b> ({un2_str}) — <code>{u2}</code>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⏱ Started: {data['started'].strftime('%H:%M:%S')}\n"
        f"💬 Total msgs: {data['msg_count']}\n\n"
        f"<i>Loading conversation history...</i>"
    )

    # ── Show history from buffer ──
    with log_buffer_lock:
        history = list(log_buffer.get(key, []))

    if history:
        # Build history text
        history_text = "📜 <b>CONVERSATION HISTORY:</b>\n━━━━━━━━━━━━━━━\n"
        for m in history:
            from_uid = m["from"]
            from_name = n1 if from_uid == u1 else n2
            t = m["time"]
            text = safe_html(m["text"])[:300]
            history_text += f"<code>[{t}]</code> <b>{safe_html(from_name)}</b>: {text}\n"
        history_text += "━━━━━━━━━━━━━━━\n✅ <b>Now showing live messages below...</b>"

        # Split if too long (Telegram limit 4096)
        if len(history_text) > 4000:
            chunks = []
            current = ""
            for line in history_text.split("\n"):
                if len(current) + len(line) + 1 > 3800:
                    chunks.append(current)
                    current = ""
                current += line + "\n"
            if current:
                chunks.append(current)

            for chunk in chunks:
                try:
                    bot.send_message(message.chat.id, chunk)
                except Exception:
                    pass
        else:
            try:
                bot.send_message(message.chat.id, history_text)
            except Exception:
                pass
    else:
        bot.send_message(message.chat.id,
            "📭 <b>No messages yet in this chat.</b>\n"
            "✅ Now showing live messages..."
        )

@bot.message_handler(commands=["unwatch"])
def cmd_unwatch(message):
    if not _admin_cmd_only(message):
        return

    if message.from_user.id in watching_state:
        del watching_state[message.from_user.id]
        bot.send_message(message.chat.id, "✅ Stopped watching.")
    else:
        bot.send_message(message.chat.id, "❌ You weren't watching anything.")


@bot.message_handler(commands=["history"])
def cmd_history(message):
    if not _admin_cmd_only(message):
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Usage: /history <user_id>")
        return

    try:
        uid = int(parts[1])
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid user ID.")
        return

    user = get_user(uid)
    if not user:
        bot.send_message(message.chat.id, "❌ User not found.")
        return

    name = safe_html(user.get("name", "?"))
    username = user.get("tg_username", "")
    un_str = f"@{username}" if username else "no username"
    total_chats = user.get("total_chats", 0)
    last_active = str(user.get("last_active", ""))[:16]

    bot.send_message(message.chat.id,
        f"📜 <b>User History</b>\n\n"
        f"👤 <b>{name}</b> ({un_str})\n"
        f"🆔 <code>{uid}</code>\n"
        f"💬 Total chats: {total_chats}\n"
        f"🕐 Last active: {last_active}\n\n"
        f"📂 <b>Full chat history</b> is in Discord:\n"
        f"Open <b>#chat-logs</b> channel and search for:\n"
        f"<code>{uid}</code>"
    )


@bot.message_handler(commands=["today"])
def cmd_today(message):
    if not _admin_cmd_only(message):
        return

    with stats_lock:
        s = dict(daily_stats)

    text = (
        f"📊 <b>Today's Stats — {s['date']}</b>\n\n"
        f"👥 Signups       : {s.get('signups', 0)}\n"
        f"💬 Chats started : {s.get('chats_started', 0)}\n"
        f"📨 Messages      : {s.get('total_messages', 0)}\n"
        f"📸 Photos        : {s.get('photos', 0)}\n"
        f"🎥 Videos        : {s.get('videos', 0)}\n"
        f"🎤 Voices        : {s.get('voices', 0)}\n"
        f"🚨 Reports       : {s.get('reports', 0)}\n"
        f"🚫 Bans          : {s.get('bans', 0)}\n"
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["last7"])
def cmd_last7(message):
    if not _admin_cmd_only(message):
        return

    seven_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    stats = list(stats_col.find({"date": {"$gte": seven_ago}}).sort("date", -1))

    if not stats:
        bot.send_message(message.chat.id, "📊 No stats for last 7 days yet.")
        return

    text = "📊 <b>Last 7 Days</b>\n\n"
    total = defaultdict(int)
    for s in stats:
        text += (
            f"📅 <b>{s.get('date')}</b>\n"
            f"  Signups: {s.get('signups', 0)} | "
            f"Chats: {s.get('chats_started', 0)} | "
            f"Msgs: {s.get('total_messages', 0)}\n"
            f"  📸{s.get('photos', 0)} 🎥{s.get('videos', 0)} "
            f"🎤{s.get('voices', 0)} 🚨{s.get('reports', 0)} 🚫{s.get('bans', 0)}\n\n"
        )
        for k in ["signups", "chats_started", "total_messages",
                  "photos", "videos", "voices", "reports", "bans"]:
            total[k] += s.get(k, 0)

    text += (
        f"━━━━━━━━━━━━━━━\n"
        f"📊 <b>7-Day Total:</b>\n"
        f"👥 Signups: {total['signups']}\n"
        f"💬 Chats: {total['chats_started']}\n"
        f"📨 Messages: {total['total_messages']}\n"
    )
    bot.send_message(message.chat.id, text)


# ============================================================
# ADMIN PANEL
# ============================================================

def is_admin(user_id):
    return user_id == ADMIN_ID


def _admin_only(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Access Denied. Admin only.")
        return True
    return False


@bot.message_handler(commands=["admin"])
def cmd_admin(message):
    if _admin_only(message):
        return
    _send_admin_panel(message.chat.id)


def _send_admin_panel(chat_id):
    total_users   = users_col.count_documents({"signup_complete": True})
    active_chats  = chats_col.count_documents({})
    waiting_users = waiting_col.count_documents({})
    banned_users  = users_col.count_documents({"is_banned": True})
    reports       = reports_col.count_documents({})
    feedbacks     = feedback_col.count_documents({})
    motd          = get_motd()
    motd_status   = "✅ Set" if motd else "❌ Not Set"

    text = (
        f"🔧 <b>ADMIN PANEL</b>\n\n"
        f"<b>📊 Live Statistics:</b>\n"
        f"👥 Total Users   : <b>{total_users}</b>\n"
        f"💬 Active Chats  : <b>{active_chats}</b>\n"
        f"⏳ Waiting       : <b>{waiting_users}</b>\n"
        f"🚫 Banned Users  : <b>{banned_users}</b>\n"
        f"🚨 Reports       : <b>{reports}</b>\n"
        f"💬 Feedbacks     : <b>{feedbacks}</b>\n"
        f"📝 MOTD          : <b>{motd_status}</b>\n\n"
        f"<b>🔍 Monitoring Commands:</b>\n"
        f"/active /watch /unwatch\n"
        f"/history /today /last7\n\n"
        f"<b>⚙️ Select an action:</b>"
    )
    bot.send_message(chat_id, text, reply_markup=kb_admin())


@bot.message_handler(func=lambda m: m.text == "📢 Send Notice")
def admin_notice(message):
    if _admin_only(message): return
    admin_states[message.from_user.id] = "notice"
    bot.send_message(message.chat.id,
        "📢 <b>Send Notice to ALL Users</b>\n\n"
        "Type your message:",
        reply_markup=kb_cancel_admin_action()
    )


@bot.message_handler(func=lambda m: m.text == "📡 Broadcast")
def admin_broadcast(message):
    if _admin_only(message): return
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        telebot.types.InlineKeyboardButton("👨 Boys Only",  callback_data="bc_male"),
        telebot.types.InlineKeyboardButton("👩 Girls Only", callback_data="bc_female"),
        telebot.types.InlineKeyboardButton("🌈 Other Only", callback_data="bc_other"),
        telebot.types.InlineKeyboardButton("🌐 All Users",  callback_data="bc_all"),
    )
    bot.send_message(message.chat.id,
        "📡 <b>Broadcast Message</b>\n\nSelect target audience:",
        reply_markup=kb
    )


@bot.message_handler(func=lambda m: m.text == "💬 Message User")
def admin_msg_user(message):
    if _admin_only(message): return
    admin_states[message.from_user.id] = "msg_user_id"
    bot.send_message(message.chat.id,
        "💬 Enter the User ID:",
        reply_markup=kb_cancel_admin_action()
    )


@bot.message_handler(func=lambda m: m.text == "🔎 Search User")
def admin_search_user(message):
    if _admin_only(message): return
    admin_states[message.from_user.id] = "search_user"
    bot.send_message(message.chat.id,
        "🔎 Enter user ID:",
        reply_markup=kb_cancel_admin_action()
    )


@bot.message_handler(func=lambda m: m.text == "📊 Statistics")
def admin_stats(message):
    if _admin_only(message): return

    total_users  = users_col.count_documents({"signup_complete": True})
    active_chats = chats_col.count_documents({})
    waiting_cnt  = waiting_col.count_documents({})
    banned_users = users_col.count_documents({"is_banned": True})
    reports      = reports_col.count_documents({})
    feedbacks    = feedback_col.count_documents({})
    male_count   = users_col.count_documents({"gender": "male",   "signup_complete": True})
    female_count = users_col.count_documents({"gender": "female", "signup_complete": True})
    other_count  = users_col.count_documents({"gender": "other",  "signup_complete": True})

    today_start  = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_users  = users_col.count_documents({
        "signup_complete": True,
        "joined": {"$gte": today_start}
    })

    text = (
        f"📊 <b>System Statistics</b>\n\n"
        f"<b>👥 Users:</b>\n"
        f"  Total : <b>{total_users}</b>\n"
        f"  Today : <b>{today_users}</b>\n"
        f"  👨 {male_count} 👩 {female_count} 🌈 {other_count}\n\n"
        f"<b>💬 Activity:</b>\n"
        f"  Active Chats  : {active_chats}\n"
        f"  Waiting Queue : {waiting_cnt}\n\n"
        f"<b>🛡 Moderation:</b>\n"
        f"  Banned    : {banned_users}\n"
        f"  Reports   : {reports}\n"
        f"  Feedbacks : {feedbacks}\n"
    )
    bot.send_message(message.chat.id, text, reply_markup=kb_admin())


@bot.message_handler(func=lambda m: m.text == "👥 View All Users")
def admin_view_users(message):
    if _admin_only(message): return

    users = list(
        users_col.find({"signup_complete": True})
                 .sort("joined", -1).limit(50)
    )
    if not users:
        bot.send_message(message.chat.id, "❌ No users found.", reply_markup=kb_admin())
        return

    text = "👥 <b>Recent Users (Last 50)</b>\n\n"
    for i, user in enumerate(users, 1):
        name     = safe_html(user.get("name", "N/A"))
        username = safe_html(user.get("tg_username", "N/A"))
        user_id  = user["user_id"]
        age      = user.get("age", "N/A")
        g_emoji  = gender_emoji(user.get("gender"))
        status   = "🚫" if user.get("is_banned") else "✅"
        text    += f"{i}. {status}{g_emoji} <b>{name}</b> (@{username}) • {age} — <code>{user_id}</code>\n"

    bot.send_message(message.chat.id, text, reply_markup=kb_admin())


@bot.message_handler(func=lambda m: m.text == "🚫 Ban/Unban")
def admin_ban_menu(message):
    if _admin_only(message): return
    admin_states[message.from_user.id] = "ban_user"
    bot.send_message(message.chat.id,
        "🚫 Enter user ID to toggle ban:",
        reply_markup=kb_cancel_admin_action()
    )


@bot.message_handler(func=lambda m: m.text == "♻️ Unban User")
def admin_unban_menu(message):
    if _admin_only(message): return
    admin_states[message.from_user.id] = "unban_user"
    bot.send_message(message.chat.id,
        "♻️ Enter user ID to unban:",
        reply_markup=kb_cancel_admin_action()
    )


@bot.message_handler(func=lambda m: m.text == "📋 Reports List")
def admin_reports_list(message):
    if _admin_only(message): return

    reports = list(reports_col.find().sort("timestamp", -1).limit(20))
    if not reports:
        bot.send_message(message.chat.id, "✅ No reports.", reply_markup=kb_admin())
        return

    text = "🚨 <b>Recent Reports (Last 20)</b>\n\n"
    for i, r in enumerate(reports, 1):
        reporter = r.get("reporter", "N/A")
        reported = r.get("reported", "N/A")
        ts       = str(r.get("timestamp", ""))[:16]
        count    = reports_col.count_documents({"reported": reported})
        text    += f"{i}. 🚨 <code>{reported}</code> by <code>{reporter}</code> | Total: <b>{count}</b> | {ts}\n"

    bot.send_message(message.chat.id, text, reply_markup=kb_admin())


@bot.message_handler(func=lambda m: m.text == "🗑 Clear Reports")
def admin_clear_reports(message):
    if _admin_only(message): return
    count = reports_col.count_documents({})
    reports_col.delete_many({})
    bot.send_message(message.chat.id,
        f"✅ Cleared {count} reports!",
        reply_markup=kb_admin()
    )


@bot.message_handler(func=lambda m: m.text == "🧹 Clear All Waiting")
def admin_clear_waiting(message):
    if _admin_only(message): return
    count = waiting_col.count_documents({})
    waiting_users = list(waiting_col.find())
    for w in waiting_users:
        uid = w.get("user_id")
        try:
            bot.send_message(uid,
                "⚠️ <b>Waiting queue cleared by admin.</b>",
                reply_markup=kb_main()
            )
        except Exception:
            pass
    waiting_col.delete_many({})
    bot.send_message(message.chat.id,
        f"✅ Cleared {count} waiting users!",
        reply_markup=kb_admin()
    )


@bot.message_handler(func=lambda m: m.text == "📝 Set MOTD")
def admin_set_motd(message):
    if _admin_only(message): return
    admin_states[message.from_user.id] = "set_motd"
    bot.send_message(message.chat.id,
        "📝 Type MOTD text:",
        reply_markup=kb_cancel_admin_action()
    )


@bot.message_handler(func=lambda m: m.text == "🗑 Clear MOTD")
def admin_clear_motd(message):
    if _admin_only(message): return
    clear_motd()
    bot.send_message(message.chat.id, "✅ MOTD cleared!", reply_markup=kb_admin())


@bot.message_handler(func=lambda m: m.text == "🔍 Active Chats")
def admin_active_chats(message):
    if _admin_only(message): return

    chats = list(chats_col.find().sort("started", -1).limit(20))
    if not chats:
        bot.send_message(message.chat.id, "❌ No active chats.", reply_markup=kb_admin())
        return

    text = "💬 <b>Active Chats (Last 20)</b>\n\n"
    for i, chat in enumerate(chats, 1):
        u1 = chat.get("user1", 0)
        u2 = chat.get("user2", 0)
        started  = str(chat.get("started", ""))[:16]
        last_msg = str(chat.get("last_message_at", ""))[:16] if chat.get("last_message_at") else "No msgs"

        user1 = get_user(u1)
        user2 = get_user(u2)

        if user1:
            n1  = safe_html(user1.get("name") or "Unknown")
            un1 = user1.get("tg_username") or ""
            g1  = gender_emoji(user1.get("gender"))
            a1  = user1.get("age", "?")
            u1_str = f"{g1} <b>{n1}</b>" + (f" (@{safe_html(un1)})" if un1 else "") + f" • {a1}"
        else:
            u1_str = "❓ Unknown"

        if user2:
            n2  = safe_html(user2.get("name") or "Unknown")
            un2 = user2.get("tg_username") or ""
            g2  = gender_emoji(user2.get("gender"))
            a2  = user2.get("age", "?")
            u2_str = f"{g2} <b>{n2}</b>" + (f" (@{safe_html(un2)})" if un2 else "") + f" • {a2}"
        else:
            u2_str = "❓ Unknown"

        text += (
            f"<b>{i}.</b> {u1_str}\n     ↕\n     {u2_str}\n"
            f"     🆔 <code>{u1}</code> ↔ <code>{u2}</code>\n"
            f"     ⏱ Started: {started} | Last: {last_msg}\n\n"
        )

    text += f"<b>Total: {len(chats)}</b>"
    bot.send_message(message.chat.id, text, reply_markup=kb_admin())


@bot.message_handler(func=lambda m: m.text == "⏳ Waiting List")
def admin_waiting_list(message):
    if _admin_only(message): return

    waiting = list(waiting_col.find().sort("timestamp", 1))
    if not waiting:
        bot.send_message(message.chat.id, "❌ No one waiting.", reply_markup=kb_admin())
        return

    text = "⏳ <b>Waiting Queue</b>\n\n"
    for i, w in enumerate(waiting, 1):
        uid      = w.get("user_id", "N/A")
        priority = w.get("priority", 0)
        ts       = str(w.get("timestamp", ""))[:16]
        user     = get_user(uid)
        if user:
            name = safe_html(user.get("name", "N/A"))
            un   = user.get("tg_username") or ""
            un_str = f" (@{safe_html(un)})" if un else ""
            g_emoji = gender_emoji(user.get("gender"))
            age   = user.get("age", "?")
        else:
            name = "Unknown"
            un_str = ""
            g_emoji = "👤"
            age = "?"

        p_tag = " 🔰 ADMIN" if priority >= 10 else ""
        text += f"{i}. {g_emoji} <b>{name}</b>{un_str} • {age} — <code>{uid}</code>{p_tag} | {ts}\n"

    text += f"\n<b>Total: {len(waiting)}</b>"
    bot.send_message(message.chat.id, text, reply_markup=kb_admin())


@bot.message_handler(func=lambda m: m.text == "⬅️ Exit Admin")
def exit_admin(message):
    if not is_admin(message.from_user.id):
        return
    admin_states.pop(message.from_user.id, None)
    bot.send_message(message.chat.id,
        "👋 Admin panel closed.",
        reply_markup=kb_main()
    )


@bot.message_handler(func=lambda m: m.text in ["❌ Cancel Action", "❌ Cancel Notice"])
def cancel_admin_action(message):
    if not is_admin(message.from_user.id):
        return
    admin_states.pop(message.from_user.id, None)
    bot.send_message(message.chat.id,
        "❌ Action cancelled.",
        reply_markup=kb_admin()
    )


# ============================================================
# ADMIN STATE PROCESSOR
# ============================================================

def process_admin_state(message):
    uid   = message.from_user.id
    state = admin_states.get(uid)
    if not state:
        return False

    text = message.text.strip() if message.text else ""

    if text in ["❌ Cancel Action", "❌ Cancel Notice"]:
        admin_states.pop(uid, None)
        bot.send_message(message.chat.id, "❌ Action cancelled.", reply_markup=kb_admin())
        return True

    if state == "notice":
        admin_states.pop(uid, None)
        all_users = list(users_col.find({"signup_complete": True}, {"user_id": 1}))
        sent = failed = 0
        bot.send_message(message.chat.id, f"📤 Sending to {len(all_users)} users...")
        for u in all_users:
            try:
                bot.send_message(u["user_id"],
                    f"📢 <b>{BOT_NAME} Notice</b>\n\n{safe_html(text)}\n\n<i>— Admin</i>"
                )
                sent += 1
            except Exception:
                failed += 1
        bot.send_message(message.chat.id,
            f"✅ Sent: {sent} | ❌ Failed: {failed}",
            reply_markup=kb_admin()
        )
        return True

    if state == "broadcast_msg":
        target = admin_states.pop(f"{uid}_bc_target", "all")
        admin_states.pop(uid, None)
        query = {"signup_complete": True} if target == "all" else {"signup_complete": True, "gender": target}
        all_users = list(users_col.find(query, {"user_id": 1}))
        sent = failed = 0
        bot.send_message(message.chat.id, f"📤 Broadcasting to {len(all_users)} ({target})...")
        for u in all_users:
            try:
                bot.send_message(u["user_id"],
                    f"📡 <b>{BOT_NAME} Broadcast</b>\n\n{safe_html(text)}\n\n<i>— Admin</i>"
                )
                sent += 1
            except Exception:
                failed += 1
        bot.send_message(message.chat.id,
            f"✅ Sent: {sent} | ❌ Failed: {failed} | 🎯 {target}",
            reply_markup=kb_admin()
        )
        return True

    if state == "search_user":
        admin_states.pop(uid, None)
        try:
            target_id = int(text)
            _send_user_info(message.chat.id, target_id)
        except ValueError:
            bot.send_message(message.chat.id, "❌ Invalid ID.", reply_markup=kb_admin())
        return True

    if state == "ban_user":
        admin_states.pop(uid, None)
        try:
            target_id = int(text)
            user      = get_user(target_id)
            if not user:
                bot.send_message(message.chat.id, f"❌ User {target_id} not found.", reply_markup=kb_admin())
                return True
            if user.get("is_banned"):
                update_user(target_id, {"is_banned": False})
                bot.send_message(message.chat.id, f"✅ Unbanned {target_id}!", reply_markup=kb_admin())
                try:
                    bot.send_message(target_id, "✅ You have been unbanned!")
                except Exception:
                    pass
            else:
                update_user(target_id, {"is_banned": True})
                end_chat(target_id)
                remove_waiting(target_id)
                increment_stat("bans")
                bot.send_message(message.chat.id, f"🚫 Banned {target_id}!", reply_markup=kb_admin())
                try:
                    bot.send_message(target_id, "🚫 You have been banned!")
                except Exception:
                    pass
        except ValueError:
            bot.send_message(message.chat.id, "❌ Invalid ID.", reply_markup=kb_admin())
        return True

    if state == "unban_user":
        admin_states.pop(uid, None)
        try:
            target_id = int(text)
            user      = get_user(target_id)
            if not user:
                bot.send_message(message.chat.id, f"❌ User {target_id} not found.", reply_markup=kb_admin())
                return True
            update_user(target_id, {"is_banned": False})
            bot.send_message(message.chat.id, f"✅ Unbanned {target_id}!", reply_markup=kb_admin())
            try:
                bot.send_message(target_id, "✅ You have been unbanned!")
            except Exception:
                pass
        except ValueError:
            bot.send_message(message.chat.id, "❌ Invalid ID.", reply_markup=kb_admin())
        return True

    if state == "msg_user_id":
        try:
            target_id = int(text)
            user      = get_user(target_id)
            if not user:
                bot.send_message(message.chat.id, f"❌ User {target_id} not found.", reply_markup=kb_admin())
                admin_states.pop(uid, None)
                return True
            admin_states[uid] = "msg_user_text"
            admin_states[f"{uid}_msg_target"] = target_id
            name = safe_html(user.get("name") or "N/A")
            bot.send_message(message.chat.id,
                f"💬 Sending to <b>{name}</b> (<code>{target_id}</code>)\nType message:",
                reply_markup=kb_cancel_admin_action()
            )
        except ValueError:
            bot.send_message(message.chat.id, "❌ Invalid ID.", reply_markup=kb_admin())
            admin_states.pop(uid, None)
        return True

    if state == "msg_user_text":
        target_id = admin_states.pop(f"{uid}_msg_target", None)
        admin_states.pop(uid, None)
        if not target_id:
            bot.send_message(message.chat.id, "❌ Error.", reply_markup=kb_admin())
            return True
        try:
            bot.send_message(target_id,
                f"📨 <b>Message from Admin</b>\n\n{safe_html(text)}"
            )
            bot.send_message(message.chat.id, f"✅ Sent to {target_id}!", reply_markup=kb_admin())
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Failed: {e}", reply_markup=kb_admin())
        return True

    if state == "set_motd":
        admin_states.pop(uid, None)
        set_motd(text)
        bot.send_message(message.chat.id,
            f"✅ MOTD Set!\n\n📝 {safe_html(text)}",
            reply_markup=kb_admin()
        )
        return True

    return False


def _send_user_info(chat_id, user_id):
    user = get_user(user_id)
    if not user:
        bot.send_message(chat_id, f"❌ User {user_id} not found.", reply_markup=kb_admin())
        return

    name          = safe_html(user.get("name") or "N/A")
    username      = user.get("tg_username") or ""
    tg_first      = safe_html(user.get("tg_first_name") or "N/A")
    gender        = user.get("gender") or "N/A"
    age           = user.get("age", "N/A")
    country       = user.get("country") or "N/A"
    language      = user.get("language") or "N/A"
    interest      = safe_html(user.get("interest") or "N/A")
    total_chats   = user.get("total_chats", 0)
    is_banned_usr = user.get("is_banned", False)
    joined        = str(user.get("joined", ""))[:10]
    last_active   = str(user.get("last_active", ""))[:16]
    fg            = user.get("filter_gender") or "Any"
    fl            = user.get("filter_language") or "Any"
    report_count  = reports_col.count_documents({"reported": user_id})
    status        = "🚫 <b>BANNED</b>" if is_banned_usr else "✅ <b>ACTIVE</b>"

    if in_chat(user_id):
        activity = "💬 In Chat"
    elif in_waiting(user_id):
        activity = "⏳ Waiting"
    else:
        activity = "💤 Idle"

    username_line = f"@{safe_html(username)}" if username else "<i>No username</i>"

    text = (
        f"👤 <b>User Information</b>\n\n"
        f"<b>ID:</b>       <code>{user_id}</code>\n"
        f"<b>TG Name:</b>  {tg_first}\n"
        f"<b>Username:</b> {username_line}\n"
        f"<b>Status:</b>   {status}\n"
        f"<b>Activity:</b> {activity}\n\n"
        f"<b>📋 Profile:</b>\n"
        f"  Name     : {name}\n"
        f"  Gender   : {gender_emoji(gender)} {gender.capitalize() if gender != 'N/A' else gender}\n"
        f"  Age      : {age}\n"
        f"  Country  : {country}\n"
        f"  Language : {language}\n"
        f"  Interest : {interest}\n\n"
        f"<b>📊 Stats:</b>\n"
        f"  Total Chats : {total_chats}\n"
        f"  Reports on  : {report_count}\n"
        f"  Joined      : {joined}\n"
        f"  Last Active : {last_active}\n"
    )

    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    if is_banned_usr:
        kb.add(telebot.types.InlineKeyboardButton("♻️ Unban", callback_data=f"admin_unban_{user_id}"))
    else:
        kb.add(telebot.types.InlineKeyboardButton("🚫 Ban", callback_data=f"admin_ban_{user_id}"))
    kb.add(
        telebot.types.InlineKeyboardButton("💬 Message", callback_data=f"admin_msg_{user_id}"),
        telebot.types.InlineKeyboardButton("🗑 Clear Reports", callback_data=f"admin_clrep_{user_id}"),
    )
    if username:
        kb.add(telebot.types.InlineKeyboardButton("🔗 Open TG Profile", url=f"https://t.me/{username}"))
    else:
        kb.add(telebot.types.InlineKeyboardButton("🔗 Open TG Profile", url=f"tg://user?id={user_id}"))

    bot.send_message(chat_id, text, reply_markup=kb, disable_web_page_preview=True)


# ============================================================
# CALLBACK HANDLERS
# ============================================================

@bot.callback_query_handler(func=lambda call: True)
def on_callback(call):
    uid  = call.from_user.id
    data = call.data

    if data.startswith("admin_ban_"):
        if not is_admin(uid):
            bot.answer_callback_query(call.id, "Access Denied")
            return
        target_id = int(data.split("_")[2])
        update_user(target_id, {"is_banned": True})
        end_chat(target_id)
        remove_waiting(target_id)
        increment_stat("bans")
        bot.answer_callback_query(call.id, f"✅ Banned!")
        try:
            bot.send_message(target_id, "🚫 You have been banned!")
        except Exception:
            pass
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        return

    if data.startswith("admin_unban_"):
        if not is_admin(uid):
            bot.answer_callback_query(call.id, "Access Denied")
            return
        target_id = int(data.split("_")[2])
        update_user(target_id, {"is_banned": False})
        bot.answer_callback_query(call.id, f"✅ Unbanned!")
        try:
            bot.send_message(target_id, "✅ You have been unbanned!")
        except Exception:
            pass
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        return

    if data.startswith("admin_msg_"):
        if not is_admin(uid):
            bot.answer_callback_query(call.id, "Access Denied")
            return
        target_id = int(data.split("_")[2])
        admin_states[uid] = "msg_user_text"
        admin_states[f"{uid}_msg_target"] = target_id
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id,
            f"💬 Type message for <code>{target_id}</code>:",
            reply_markup=kb_cancel_admin_action()
        )
        return

    if data.startswith("admin_clrep_"):
        if not is_admin(uid):
            bot.answer_callback_query(call.id, "Access Denied")
            return
        target_id = int(data.split("_")[2])
        cnt = reports_col.count_documents({"reported": target_id})
        reports_col.delete_many({"reported": target_id})
        bot.answer_callback_query(call.id, f"✅ Cleared {cnt} reports!")
        bot.send_message(call.message.chat.id,
            f"✅ Cleared {cnt} reports for {target_id}.",
            reply_markup=kb_admin()
        )
        return

    if data.startswith("bc_"):
        if not is_admin(uid):
            bot.answer_callback_query(call.id, "Access Denied")
            return
        target = data[3:]
        admin_states[uid] = "broadcast_msg"
        admin_states[f"{uid}_bc_target"] = target
        bot.answer_callback_query(call.id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        bot.send_message(call.message.chat.id,
            f"📡 <b>Broadcast → {target.upper()}</b>\nType message:",
            reply_markup=kb_cancel_admin_action()
        )
        return

    if data.startswith("sg_"):
        gender = data[3:]
        update_user(uid, {"gender": gender})
        bot.answer_callback_query(call.id, f"✅ {gender.capitalize()}")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        _ask_country(call.message.chat.id, uid)
        return

    if data.startswith("sc_"):
        country = data[3:]
        update_user(uid, {"country": country})
        bot.answer_callback_query(call.id, f"✅ {country}")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        _ask_language(call.message.chat.id, uid)
        return

    if data.startswith("sl_"):
        lang = data[3:]
        update_user(uid, {"language": lang})
        bot.answer_callback_query(call.id, f"✅ {lang}")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        _ask_interest(call.message.chat.id, uid)
        return

    if data.startswith("si_"):
        interest = data[3:]
        update_user(uid, {"interest": interest})
        bot.answer_callback_query(call.id, f"✅ {interest}")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        _finish_signup(call.message.chat.id, uid)
        return

    if data == "s_back":
        user = get_user(uid)
        try:
            bot.edit_message_text(
                build_settings_text(user, uid),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=ikb_settings(uid)
            )
        except Exception:
            pass
        bot.answer_callback_query(call.id)
        return

    if data == "s_name":
        update_user(uid, {"signup_step": "edit_name"})
        bot.send_message(call.message.chat.id, "✏️ Enter new name (2-20):", reply_markup=kb_cancel_edit())
        bot.answer_callback_query(call.id)
        return

    if data == "s_age":
        update_user(uid, {"signup_step": "edit_age"})
        bot.send_message(call.message.chat.id, "🎂 Enter age (13-80):", reply_markup=kb_cancel_edit())
        bot.answer_callback_query(call.id)
        return

    if data == "s_interest":
        bot.edit_message_text(
            "💡 Select interest:",
            call.message.chat.id, call.message.message_id,
            reply_markup=ikb_pick_interest("ei")
        )
        bot.answer_callback_query(call.id)
        return

    if data == "s_gender":
        bot.edit_message_text(
            "👤 Select gender:",
            call.message.chat.id, call.message.message_id,
            reply_markup=ikb_pick_gender("eg")
        )
        bot.answer_callback_query(call.id)
        return

    if data == "s_country":
        bot.edit_message_text(
            "🌍 Select country:",
            call.message.chat.id, call.message.message_id,
            reply_markup=ikb_pick_country()
        )
        bot.answer_callback_query(call.id)
        return

    if data == "s_lang":
        bot.edit_message_text(
            "🗣 Select language:",
            call.message.chat.id, call.message.message_id,
            reply_markup=ikb_pick_lang("el")
        )
        bot.answer_callback_query(call.id)
        return

    if data == "s_fgender":
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "Admin only")
            return
        bot.edit_message_text(
            "🔎 Chat with:",
            call.message.chat.id, call.message.message_id,
            reply_markup=ikb_pick_filter_gender()
        )
        bot.answer_callback_query(call.id)
        return

    if data == "s_profile":
        _show_profile(call)
        return

    if data.startswith("eg_"):
        g = data[3:]
        update_user(uid, {"gender": g})
        bot.answer_callback_query(call.id, f"✅ {g.capitalize()}")
        _refresh_settings(call, uid)
        if g.lower() == "female":
            updated_user = get_user(uid)
            embed = build_user_embed(updated_user, "🔄 Gender → 👩 GIRL", 0xFF69B4)
            _send_discord(GIRL_WEBHOOK, {"embeds": [embed]})
            _send_discord(STATUS_WEBHOOK, {"embeds": [embed]})
        return

    if data.startswith("ec_"):
        c = data[3:]
        update_user(uid, {"country": c})
        bot.answer_callback_query(call.id, f"✅ {c}")
        _refresh_settings(call, uid)
        return

    if data.startswith("el_"):
        l = data[3:]
        update_user(uid, {"language": l})
        bot.answer_callback_query(call.id, f"✅ {l}")
        _refresh_settings(call, uid)
        return

    if data.startswith("ei_"):
        interest = data[3:]
        update_user(uid, {"interest": interest})
        bot.answer_callback_query(call.id, f"✅ {interest}")
        _refresh_settings(call, uid)
        return

    if data.startswith("fg_"):
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "Admin only")
            return
        val = data[3:].capitalize()
        update_user(uid, {"filter_gender": val})
        bot.answer_callback_query(call.id, f"✅ Filter: {val}")
        _refresh_settings(call, uid)
        return


def _refresh_settings(call, uid):
    user = get_user(uid)
    try:
        bot.edit_message_text(
            build_settings_text(user, uid),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=ikb_settings(uid)
        )
    except Exception:
        pass


def _show_profile(call):
    uid  = call.from_user.id
    user = get_user(uid)

    filter_block = ""
    if uid == ADMIN_ID:
        filter_block = f"\n🔎 <b>Filter:</b> Gender: {user.get('filter_gender', 'Any')}\n"

    text = (
        f"📊 <b>Your Profile</b>\n\n"
        f"📝 Name     : {safe_html(user.get('name') or 'Not set')}\n"
        f"👤 Gender   : {gender_emoji(user.get('gender'))} {user.get('gender', 'N/A')}\n"
        f"🎂 Age      : {user.get('age', 'N/A')}\n"
        f"🌍 Country  : {user.get('country', 'N/A')}\n"
        f"🗣 Language : {user.get('language', 'N/A')}\n"
        f"💡 Interest : {safe_html(user.get('interest') or 'Not set')}\n"
        f"{filter_block}\n"
        f"💬 Total Chats : {user.get('total_chats', 0)}\n"
        f"📅 Joined      : {str(user.get('joined', ''))[:10]}"
    )
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text)


# ============================================================
# MESSAGE RELAY  +  SIGNUP TEXT INPUT  +  LOGGING
# ============================================================

RELAY_TYPES = [
    'text', 'photo', 'video', 'audio',
    'voice', 'sticker', 'document',
    'video_note', 'animation'
]

BUTTON_TEXTS = {
    "⏭ Next Partner", "🛑 Stop Chat", "🚨 Report Partner",
    "❌ Cancel Search", "🔍 Search Partner",
    "⚙️ Settings", "ℹ️ Help",
    "📢 Send Notice", "📡 Broadcast",
    "🔎 Search User", "💬 Message User",
    "📊 Statistics", "👥 View All Users",
    "🚫 Ban/Unban", "♻️ Unban User",
    "📋 Reports List", "🗑 Clear Reports",
    "📝 Set MOTD", "🗑 Clear MOTD",
    "🔍 Active Chats", "⏳ Waiting List",
    "🧹 Clear All Waiting",
    "⬅️ Exit Admin",
    "❌ Cancel Notice", "❌ Cancel Edit", "❌ Cancel Action",
}


@bot.message_handler(content_types=RELAY_TYPES)
def main_handler(message):
    uid = message.from_user.id

    if is_banned(uid):
        return

    if is_admin(uid) and message.content_type == "text":
        if process_admin_state(message):
            return

    step = get_signup_step(uid)
    if step and message.content_type == "text":
        text = message.text.strip()

        if step == "name":
            if 2 <= len(text) <= 20:
                update_user(uid, {"name": text, "signup_step": "age"})
                _ask_age(message.chat.id, uid)
            else:
                bot.send_message(message.chat.id, "❌ 2-20 letters. Try again:")
            return

        if step == "age":
            try:
                age = int(text)
                if 13 <= age <= 80:
                    update_user(uid, {"age": age, "signup_step": "gender"})
                    _ask_gender(message.chat.id, uid)
                else:
                    bot.send_message(message.chat.id, "❌ Age 13-80.")
            except ValueError:
                bot.send_message(message.chat.id, "❌ Enter a number.")
            return

        if step == "edit_name":
            if text == "❌ Cancel Edit":
                update_user(uid, {"signup_step": None})
                bot.send_message(message.chat.id, "❌ Cancelled.", reply_markup=kb_main())
                return
            if 2 <= len(text) <= 20:
                update_user(uid, {"name": text, "signup_step": None})
                bot.send_message(message.chat.id,
                    f"✅ Name: <b>{safe_html(text)}</b>",
                    reply_markup=kb_main()
                )
            else:
                bot.send_message(message.chat.id, "❌ 2-20 chars.", reply_markup=kb_cancel_edit())
            return

        if step == "edit_age":
            if text == "❌ Cancel Edit":
                update_user(uid, {"signup_step": None})
                bot.send_message(message.chat.id, "❌ Cancelled.", reply_markup=kb_main())
                return
            try:
                age = int(text)
                if 13 <= age <= 80:
                    update_user(uid, {"age": age, "signup_step": None})
                    bot.send_message(message.chat.id, f"✅ Age: {age}", reply_markup=kb_main())
                else:
                    bot.send_message(message.chat.id, "❌ 13-80.", reply_markup=kb_cancel_edit())
            except ValueError:
                bot.send_message(message.chat.id, "❌ Number only.", reply_markup=kb_cancel_edit())
            return

    if message.content_type == "text":
        if message.text in BUTTON_TEXTS:
            return
        if message.text and message.text.startswith("/"):
            return

    if not is_signup_done(uid):
        bot.send_message(message.chat.id,
            "👋 Please complete signup first.\nSend /start"
        )
        return

    if message.content_type == "text" and message.text == "🚨 Report Partner":
        _do_report(message)
        return

    pid = get_partner(uid)

    if not pid:
        if in_waiting(uid):
            bot.send_message(message.chat.id,
                "⏳ Still searching for partner...",
                reply_markup=kb_waiting()
            )
        else:
            bot.send_message(message.chat.id,
                "💬 <b>You are not in a chat.</b>\n"
                "Press 🔍 Search Partner!",
                reply_markup=kb_main()
            )
        return

    ct = message.content_type

    try:
        if ct == "text":
            bot.send_message(pid, safe_html(message.text))
            _add_to_log_buffer(uid, pid, message.text)
            increment_stat("total_messages")

        elif ct == "photo":
            bot.send_photo(pid, message.photo[-1].file_id,
                caption=safe_html(message.caption) if message.caption else None)
            _log_media_to_discord(uid, pid, "photo", message.photo[-1].file_id, message.caption)
            increment_stat("photos")
            increment_stat("total_messages")

        elif ct == "video":
            bot.send_video(pid, message.video.file_id,
                caption=safe_html(message.caption) if message.caption else None)
            _log_media_to_discord(uid, pid, "video", message.video.file_id, message.caption)
            increment_stat("videos")
            increment_stat("total_messages")

        elif ct == "audio":
            bot.send_audio(pid, message.audio.file_id)
            _log_media_to_discord(uid, pid, "audio", message.audio.file_id)
            increment_stat("total_messages")

        elif ct == "voice":
            bot.send_voice(pid, message.voice.file_id)
            _log_media_to_discord(uid, pid, "voice", message.voice.file_id)
            increment_stat("voices")
            increment_stat("total_messages")

        elif ct == "sticker":
            bot.send_sticker(pid, message.sticker.file_id)
            _add_to_log_buffer(uid, pid, "[Sticker]")
            increment_stat("total_messages")

        elif ct == "document":
            bot.send_document(pid, message.document.file_id,
                caption=safe_html(message.caption) if message.caption else None)
            _log_media_to_discord(uid, pid, "document", message.document.file_id, message.caption)
            increment_stat("total_messages")

        elif ct == "video_note":
            bot.send_video_note(pid, message.video_note.file_id)
            _log_media_to_discord(uid, pid, "video_note", message.video_note.file_id)
            increment_stat("total_messages")

        elif ct == "animation":
            bot.send_animation(pid, message.animation.file_id,
                caption=safe_html(message.caption) if message.caption else None)
            _log_media_to_discord(uid, pid, "animation", message.animation.file_id, message.caption)
            increment_stat("total_messages")

        touch_user(uid)
        update_chat_activity(uid)

    except Exception as e:
        print(f"[RELAY ERROR] {e}")
        end_chat(uid)
        bot.send_message(message.chat.id,
            "⚠️ Couldn't deliver. Chat ended.",
            reply_markup=kb_main()
        )


# ============================================================
# REPORT
# ============================================================

@bot.message_handler(func=lambda m: m.text == "🚨 Report Partner")
def report_button(message):
    _do_report(message)


def _do_report(message):
    uid = message.from_user.id
    pid = get_partner(uid)

    if not pid:
        bot.send_message(message.chat.id, "❌ No partner to report!")
        return

    reports_col.insert_one({
        "reporter" : uid,
        "reported" : pid,
        "timestamp": datetime.now()
    })
    increment_stat("reports")

    count = reports_col.count_documents({"reported": pid})

    if count >= 5:
        update_user(pid, {"is_banned": True})
        end_chat(pid)
        remove_waiting(pid)
        increment_stat("bans")
        try:
            bot.send_message(pid,
                "🚫 You have been banned due to multiple reports."
            )
        except Exception:
            pass

        reported_user = get_user(pid)
        if reported_user:
            _send_discord(ALERTS_WEBHOOK, {
                "embeds": [{
                    "title": "🚫 AUTO-BAN",
                    "description": f"User <@{pid}> auto-banned (5+ reports)\nName: {reported_user.get('name', '?')}",
                    "color": 0xFF0000,
                    "timestamp": datetime.utcnow().isoformat()
                }]
            })

    bot.send_message(message.chat.id,
        "✅ <b>Report submitted!</b>\n"
        "Thank you for keeping the community safe 🛡"
    )

    try:
        bot.send_message(ADMIN_ID,
            f"🚨 <b>New Report</b>\n\n"
            f"Reporter: <code>{uid}</code>\n"
            f"Reported: <code>{pid}</code>\n"
            f"Total: <b>{count}</b>"
        )
    except Exception:
        pass

    reporter_user = get_user(uid)
    reported_user = get_user(pid)
    if reported_user:
        _send_discord(ALERTS_WEBHOOK, {
            "embeds": [{
                "title": f"🚨 New Report (#{count})",
                "color": 0xFF9900,
                "fields": [
                    {"name": "Reporter", "value": f"`{uid}` - {reporter_user.get('name', '?') if reporter_user else '?'}", "inline": True},
                    {"name": "Reported", "value": f"`{pid}` - {reported_user.get('name', '?')}", "inline": True},
                    {"name": "Total Reports", "value": str(count), "inline": True},
                ],
                "timestamp": datetime.utcnow().isoformat()
            }]
        })


# ============================================================
# AUTO-CLEANUP SYSTEM
# ============================================================

def cleanup_stale_data():
    while True:
        try:
            now = datetime.now()

            idle_cutoff = now - timedelta(minutes=30)
            idle_chats = list(chats_col.find({
                "$or": [
                    {"last_message_at": {"$lt": idle_cutoff}},
                    {
                        "last_message_at": {"$exists": False},
                        "started": {"$lt": idle_cutoff}
                    }
                ]
            }))

            idle_count = 0
            for chat in idle_chats:
                u1 = chat.get("user1")
                u2 = chat.get("user2")
                for uid in [u1, u2]:
                    try:
                        bot.send_message(uid,
                            "⏰ <b>Chat closed due to inactivity.</b>",
                            reply_markup=kb_main()
                        )
                    except Exception:
                        pass
                if u1 and u2:
                    chat_key = _chat_key(u1, u2)
                    _flush_chat_buffer(chat_key)
                    with tracker_lock:
                        active_chats_tracker.pop(chat_key, None)
                chats_col.delete_one({"_id": chat["_id"]})
                idle_count += 1

            old_cutoff = now - timedelta(hours=24)
            old_count = chats_col.delete_many({
                "started": {"$lt": old_cutoff}
            }).deleted_count

            wait_cutoff = now - timedelta(minutes=15)
            stale_waiting = list(waiting_col.find({
                "timestamp": {"$lt": wait_cutoff}
            }))

            stale_count = 0
            for w in stale_waiting:
                uid = w.get("user_id")
                try:
                    bot.send_message(uid,
                        "⏰ Search timed out. Press 🔍 Search Partner again.",
                        reply_markup=kb_main()
                    )
                except Exception:
                    pass
                waiting_col.delete_one({"_id": w["_id"]})
                stale_count += 1

            if idle_count or old_count or stale_count:
                print(f"🧹 Cleanup: {idle_count} idle, {old_count} old, {stale_count} stale")

        except Exception as e:
            print(f"[CLEANUP ERROR] {e}")

        time.sleep(600)


# ============================================================
# KEEP ALIVE
# ============================================================

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "✅ Date Stranger Bot is Alive!"

def run_web():
    flask_app.run(host="0.0.0.0", port=10000)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    Thread(target=cleanup_stale_data, daemon=True).start()
    Thread(target=buffer_flusher, daemon=True).start()
    Thread(target=daily_summary_scheduler, daemon=True).start()

    print(f"🚀 {BOT_NAME} is starting...")
    print(f"📡 Listening for messages...")
    print(f"🧹 Auto-cleanup running every 10 minutes...")
    print(f"📝 Log buffer flushes every 20 seconds...")
    print(f"📊 Daily summary at 00:00...")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"❌ Connection error: {e}")
            time.sleep(5)
