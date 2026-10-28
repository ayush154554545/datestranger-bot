# Matching Engine Architecture & Mechanics

## 1. Overview
The matching engine connects users searching for anonymous 1-on-1 chats based on compatibility, priority scoring, and mutual filter rules.

---

## 2. Priority Queue Scoring
When a user enters the queue, a numerical priority score is assigned:
* **Admin**: `20` (Instant top-of-queue priority)
* **Premium User**: `10` (Priority matching over free users)
* **Free User**: `0` (Standard FIFO order)

Candidates in `waiting_queue` are ordered by:
```sql
ORDER BY priority DESC, entered_at ASC
```

---

## 3. Mutual Compatibility Matching Rules
A candidate match $(U_1, U_2)$ is valid if and only if **all** of the following conditions hold:

1. **Self-Match Guard**: $U_1 \neq U_2$.
2. **Account Status Guard**: Both $U_1$ and $U_2$ have completed signup (`signup_complete = true`) and neither is banned (`is_banned = false`).
3. **Active Chat Guard**: Neither $U_1$ nor $U_2$ is currently present in `active_matches`.
4. **Mutual Gender Filter Guard**:
   * If $U_1$ has an active gender filter ($Filter(U_1) \neq \text{'any'}$), then $Gender(U_2) = Filter(U_1)$.
   * If $U_2$ has an active gender filter ($Filter(U_2) \neq \text{'any'}$), then $Gender(U_1) = Filter(U_2)$.
   *(Note: Gender filters apply only when the user possesses active Premium status).*
5. **Mutual Age Filter Guard**:
   * $MinAge(Filter(U_1)) \le Age(U_2) \le MaxAge(Filter(U_1))$.
   * $MinAge(Filter(U_2)) \le Age(U_1) \le MaxAge(Filter(U_2))$.
   *(Note: Age filters apply only when the user possesses active Premium status).*

---

## 4. Race Condition & Concurrency Control

### Legacy Risk (In-Memory `match_lock`)
The legacy implementation used Python's `threading.Lock()`. This works within a single Python process, but fails completely under multi-worker or multi-instance container deployments, leading to double-matching.

### PostgreSQL Atomic Transaction Solution
In Supabase/PostgreSQL, matching is executed inside an atomic transaction using `SKIP LOCKED`:

```sql
BEGIN;

-- Lock the candidate row atomically
SELECT q.user_id 
FROM waiting_queue q
JOIN profiles p ON p.user_id = q.user_id
WHERE q.user_id <> :my_user_id
  AND (
    :my_gender_filter = 'any' OR p.gender = :my_gender_filter
  )
  AND p.age BETWEEN :my_min_age AND :my_max_age
ORDER BY q.priority DESC, q.entered_at ASC
FOR UPDATE SKIP LOCKED
LIMIT 1;

-- If candidate found:
DELETE FROM waiting_queue WHERE user_id IN (:my_user_id, :candidate_user_id);
INSERT INTO active_matches (user1_id, user2_id) VALUES (:my_user_id, :candidate_user_id);

COMMIT;
```

This guarantees that two workers simultaneously matching will never claim the same waiting user.
