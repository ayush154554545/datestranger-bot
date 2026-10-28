# Internal API & Service Contracts — Date Stranger Bot

## 1. Overview
This document specifies internal Python API contracts between the Telegram handler presentation layer, application services, and infrastructure repositories.

---

## 2. Core Service Interfaces

```python
class IMatchingService(ABC):
    @abstractmethod
    def enqueue_user(self, user_id: str, priority: int) -> bool:
        """Enrolls user in waiting queue."""
        pass

    @abstractmethod
    def find_and_create_match(self, user_id: str) -> Optional[MatchDTO]:
        """Atomically locks candidate partner and initializes active match."""
        pass

    @abstractmethod
    def leave_chat(self, user_id: str) -> bool:
        """Terminates active match and returns disconnected status."""
        pass


class IPaymentService(ABC):
    @abstractmethod
    def process_stars_payment(self, user_id: str, charge_id: str, plan_key: str, amount: int) -> PaymentResultDTO:
        """Idempotently records payment and updates subscription."""
        pass
```
