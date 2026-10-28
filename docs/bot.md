# Telegram Bot Specification — Date Stranger Bot

## 1. Interface & Handler Design
The bot interface is implemented using `pyTelegramBotAPI`. Handlers translate Telegram updates into DTOs, invoke application services, and format HTML/keyboard responses.

---

## 2. Command Structure

| Command | Permission | Description |
| :--- | :--- | :--- |
| `/start` | Public | Initiates signup wizard or main navigation menu. |
| `/search` | Registered (18+) | Enters matching queue for anonymous chat partner. |
| `/stop` | In Chat | Terminate current active anonymous chat session. |
| `/next` | In Chat | Leaves current chat and immediately searches for a new partner. |
| `/report` | In Chat | Opens report reason selection inline keyboard. |
| `/settings` | Registered | View and update profile, gender filters, and age filters. |
| `/premium` | Registered | Displays Telegram Stars premium plans and purchase invoice options. |
| `/invites` | Registered | Shows referral link and progress towards premium rewards. |
| `/admin` | Admin Only | Opens administrator control dashboard. |
| `/stats` | Admin Only | Renders real-time daily metrics dashboard. |
| `/broadcast` | Admin Only | Initiates message broadcast to registered users. |
| `/ban` | Admin Only | Ban specified user ID with reason. |
| `/unban` | Admin Only | Lift ban on specified user ID. |
| `/watch` | Admin Only | Intercepts live chat stream of specified target user. |

---

## 3. Keyboard & Navigation Layouts

### 3.1 Main Menu Reply Keyboard
* `🔍 Find Match`
* `⚙️ Settings` | `⭐ Premium`
* `🎁 Free Premium (Invites)` | `❓ Help`

### 3.2 Active Chat Reply Keyboard
* `🚪 Leave Chat` | `➡️ Next Stranger` | `🚨 Report Partner`
