# Data Retention & Cleanup Policy

## 1. Data Classification & Retention Periods
| Category | Storage Entity | Retention Period | Deletion Action |
| :--- | :--- | :--- | :--- |
| **User Identity & Profile** | `users`, `profiles` | Active lifetime | Soft delete upon account deletion request (`account_status = 'deleted'`) |
| **Live Chat Messages** | `chat_messages` | 30 days after match end | Automated cron purge job |
| **Moderation Evidence** | `reports`, `bans` | 365 days | Archived for security audit |
| **Payment Receipts** | `payment_transactions` | 7 years | Financial tax compliance |
| **Discord Logs** | Discord Channel | External Webhook | Managed by Discord server retention |

## 2. Automated Purge Jobs
PostgreSQL database functions and cron workers execute cleanup sweeps for expired chat messages and stale waiting queue entries.
