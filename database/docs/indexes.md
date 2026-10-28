# PostgreSQL Indexing Strategy & Query Optimization

## 1. Indexing Overview
To support 50,000+ users and 1,000+ concurrent active sessions with low latency, PostgreSQL indexes are defined for high-traffic query patterns.

---

## 2. Index Matrix & Query Justifications

### 2.1 Identity & Profile Indexes
| Index Name | Table | Columns | Type | Target Query / Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `idx_users_telegram_id` | `users` | `telegram_user_id` | B-tree Unique | Fast user lookup on Telegram message ingestion |
| `idx_users_last_seen` | `users` | `last_seen_at DESC` | B-tree | Active user analytics & session cleanup |
| `idx_profiles_demographics` | `profiles` | `gender, age, country` | Compound B-tree | Stranger matching filter criteria evaluation |

### 2.2 Matching Engine Indexes
| Index Name | Table | Columns | Type | Target Query / Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `idx_one_active_match_per_user` | `match_participants` | `user_id` | Partial Unique (`WHERE status = 'active'`) | **Race-condition proof enforcement preventing double active matching** |
| `idx_matches_status_created` | `matches` | `status, created_at` | Compound B-tree | Active match monitoring & timeout sweep workers |

### 2.3 Messaging Indexes
| Index Name | Table | Columns | Type | Target Query / Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `idx_chat_messages_session_time` | `chat_messages` | `chat_session_id, created_at DESC` | Compound B-tree | Chat history pagination & session logging |
| `idx_chat_messages_sender` | `chat_messages` | `sender_user_id` | B-tree | User message count and moderation lookup |

### 2.4 Moderation & Safety Indexes
| Index Name | Table | Columns | Type | Target Query / Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `idx_blocks_pair` | `blocks` | `(blocker_user_id, blocked_user_id)` | Primary Key | Instant block check prior to match confirmation |
| `idx_bans_user_expiry` | `bans` | `user_id, expires_at` | Compound B-tree | Active ban check on bot interaction |
| `idx_reports_status` | `reports` | `status, created_at` | Compound B-tree | Admin moderation queue ordering |

### 2.5 Monetization & Referrals
| Index Name | Table | Columns | Type | Target Query / Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `idx_payments_provider_tx` | `payment_transactions` | `provider_transaction_id` | B-tree Unique | Idempotent Telegram Stars checkout validation |
| `idx_premium_user_status` | `premium_subscriptions` | `user_id, status, expires_at` | Compound B-tree | Active entitlement verification |
| `idx_referrals_referred` | `referrals` | `referred_user_id` | B-tree Unique | Anti double-referral enforcement |
