# Moderation & Safety Architecture

## 1. Overview
DateWithStranger employs a multi-tiered moderation system to enforce 18+ adult safety, user privacy, and abuse prevention.

---

## 2. Moderation Workflow
1. **Report Filing**: Users can file reports during chat via `/report` (`Nudity/NSFW`, `Spam/Scam`, `Abuse/Harassment`, `Underage`, `Other`).
2. **Admin Watch Mode**: Administrators can monitor live chat streams using `/watch <user_id>`.
3. **User Bans**: Administrators issue bans (`/ban <user_id> <reason>`). Banned user records (`is_banned = true`) block signup and matching attempts at the database layer.
4. **Audit Trail**: Every moderation action is recorded in PostgreSQL `admin_actions` table.
