# -*- coding: utf-8 -*-
# ============================================================
#        DATE STRANGER | CHAT BOT
#        @datestranger_chatbot
# ============================================================

import telebot
import os
import requests
import threading
from datetime import datetime
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
BOT_USER   = "@datestranger_chatbot"

# ── Discord Webhooks ─────────────────────────────────────────
STATUS_WEBHOOK      = os.getenv("STATUS_WEBHOOK")
GIRL_WEBHOOK        = os.getenv("GIRL_WEBHOOK")
BOY_WEBHOOK         = os.getenv("BOY_WEBHOOK")
OTHER_WEBHOOK       = os.getenv("OTHER_WEBHOOK")
GIRL_MEDIA_WEBHOOK  = os.getenv("GIRL_MEDIA_WEBHOOK")
BOY_MEDIA_WEBHOOK   = os.getenv("BOY_MEDIA_WEBHOOK")
OTHER_MEDIA_WEBHOOK = os.getenv("OTHER_MEDIA_WEBHOOK")

bot    = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
client = MongoClient(MONGO_URL)
db     = client["datestranger"]

users_col   = db["users"]
waiting_col = db["waiting"]
chats_col   = db["active_chats"]
reports_col = db["reports"]


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


# ============================================================
# DISCORD WEBHOOK HELPERS
# ============================================================

def _send_discord(webhook_url, payload):
    """Send payload to Discord webhook in a background thread."""
    if not webhook_url:
        return
    def _send():
        try:
            requests.post(webhook_url, json=payload, timeout=10)
        except Exception as e:
            print(f"[DISCORD ERROR] {e}")
    threading.Thread(target=_send, daemon=True).start()


def _gender_webhook(gender: str):
    """Return the correct signup-notification webhook for a gender."""
    g = (gender or "").lower()
    if g == "female":
        return GIRL_WEBHOOK
    elif g == "male":
        return BOY_WEBHOOK
    else:
        return OTHER_WEBHOOK


def _gender_media_webhook(gender: str):
    """Return the correct media-notification webhook for a gender."""
    g = (gender or "").lower()
    if g == "female":
        return GIRL_MEDIA_WEBHOOK
    elif g == "male":
        return BOY_MEDIA_WEBHOOK
    else:
        return OTHER_MEDIA_WEBHOOK


def _tg_profile_url(user_id):
    return f"https://t.me/user?id={user_id}"


def build_user_embed(user, title: str, color: int):
    """Build a Discord embed dict from a user document."""
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
    tg_link     = f"[Open Profile]({_tg_profile_url(uid)})"

    embed = {
        "title"       : title,
        "color"       : color,
        "timestamp"   : datetime.utcnow().isoformat(),
        "footer"      : {"text": f"{BOT_NAME} • {BOT_USER}"},
        "fields"      : [
            {"name": "🆔 User ID",       "value": f"`{uid}`",     "inline": True},
            {"name": "📛 Nickname",      "value": name,            "inline": True},
            {"name": "📱 TG Username",   "value": f"@{username}",  "inline": True},
            {"name": "👤 TG Name",       "value": tg_name,         "inline": True},
            {"name": f"{gender_icon} Gender", "value": gender,     "inline": True},
            {"name": "🎂 Age",           "value": str(age),        "inline": True},
            {"name": "🌍 Country",       "value": country,         "inline": True},
            {"name": "🗣 Language",      "value": language,        "inline": True},
            {"name": "💡 Interest",      "value": interest,        "inline": True},
            {"name": "💬 Total Chats",   "value": str(chats),      "inline": True},
            {"name": "📅 Joined",        "value": joined,          "inline": True},
            {"name": "🕐 Last Active",   "value": last_active,     "inline": True},
            {"name": "🔰 Status",        "value": is_banned_u,     "inline": True},
            {"name": "🔗 Telegram",      "value": tg_link,         "inline": False},
        ]
    }
    return embed


def notify_new_user(user, event: str = "join"):
    """
    Only notify if gender is female.
    Sends to GIRL_WEBHOOK and STATUS_WEBHOOK.
    """
    gender = (user.get("gender") or "").lower()

    # Only care about girls
    if gender != "female":
        return

    embed = build_user_embed(user, "🆕 New 👩 GIRL Joined!", 0xFF69B4)
    embed["fields"].insert(0, {
        "name": "📋 Event",
        "value": "✅ Signup Complete" if event == "signup" else "👋 Joined Bot",
        "inline": True
    })

    _send_discord(GIRL_WEBHOOK, {"embeds": [embed]})
    _send_discord(STATUS_WEBHOOK, {"embeds": [embed]})

def notify_media_shared(sender_user, media_type: str, file_url: str = None):
    """
    Only notify for PHOTO sends.
    Sends to the correct gender media webhook.
    """
    # Only care about photos
    if media_type != "photo":
        return

    gender = (sender_user.get("gender") or "other").lower()
    color_map = {"female": 0xFF69B4, "male": 0x4169E1, "other": 0x9B59B6}
    icon_map  = {"female": "👩 Girl", "male": "👨 Boy", "other": "🌈 Other"}

    color = color_map.get(gender, 0x95A5A6)
    title = f"📸 {icon_map.get(gender, 'User')} Sent a Photo"

    uid      = sender_user.get("user_id", "N/A")
    name     = sender_user.get("name") or "N/A"
    username = sender_user.get("tg_username") or ""
    tg_name  = sender_user.get("tg_first_name") or ""
    # Build best possible username display
    if username:
        username_display = f"@{username}"
    elif tg_name:
        username_display = f"{tg_name} (no @username)"
    else:
        username_display = f"ID: {sender_user.get('user_id', 'N/A')}"
    age      = sender_user.get("age", "N/A")
    country  = sender_user.get("country") or "N/A"
    language = sender_user.get("language") or "N/A"

    embed = {
        "title"    : title,
        "color"    : color,
        "timestamp": datetime.utcnow().isoformat(),
        "footer"   : {"text": f"{BOT_NAME} • {BOT_USER}"},
        "fields"   : [
            {"name": "🆔 User ID",     "value": f"`{uid}`",        "inline": True},
            {"name": "📛 Nickname",    "value": name,               "inline": True},
            {"name": "📱 TG Username", "value": username_display,   "inline": True},
            {"name": "🎂 Age",         "value": str(age),           "inline": True},
            {"name": "🌍 Country",     "value": country,            "inline": True},
            {"name": "🗣 Language",    "value": language,           "inline": True},
            {"name": "🔗 Telegram",    "value": f"[Open]({_tg_profile_url(uid)})", "inline": False},
        ]
    }

    if file_url:
        embed["image"] = {"url": file_url}

    _send_discord(_gender_media_webhook(gender), {"embeds": [embed]})


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


def add_waiting(user_id):
    if not in_waiting(user_id):
        waiting_col.insert_one({
            "user_id"  : user_id,
            "timestamp": datetime.now()
        })


def remove_waiting(user_id):
    waiting_col.delete_one({"user_id": user_id})


def create_chat(uid1, uid2):
    chats_col.insert_one({
        "user1"  : uid1,
        "user2"  : uid2,
        "started": datetime.now()
    })
    users_col.update_one({"user_id": uid1}, {"$inc": {"total_chats": 1}})
    users_col.update_one({"user_id": uid2}, {"$inc": {"total_chats": 1}})


def end_chat(user_id):
    chats_col.delete_many({
        "$or": [{"user1": user_id}, {"user2": user_id}]
    })


# ── Matching ────────────────────────────────────────────────

def find_match(user_id):
    me = get_user(user_id)
    if not me:
        return None

    my_gender   = (me.get("gender") or "").lower()
    my_language = (me.get("language") or "any").lower()
    my_f_gender = (me.get("filter_gender") or "any").lower()
    my_f_lang   = (me.get("filter_language") or "any").lower()

    candidates = list(waiting_col.find({"user_id": {"$ne": user_id}}))
    if not candidates:
        return None

    best_score     = -1
    best_candidate = None

    for c in candidates:
        c_user = get_user(c["user_id"])
        if not c_user or not c_user.get("signup_complete"):
            continue

        c_gender   = (c_user.get("gender") or "").lower()
        c_language = (c_user.get("language") or "any").lower()
        c_f_gender = (c_user.get("filter_gender") or "any").lower()
        c_f_lang   = (c_user.get("filter_language") or "any").lower()

        i_want_them  = my_f_gender == "any" or my_f_gender == c_gender
        they_want_me = c_f_gender == "any" or c_f_gender == my_gender
        gender_ok    = i_want_them and they_want_me

        lang_ok = (
            my_f_lang == "any" or c_f_lang == "any" or
            my_f_lang == c_language or c_f_lang == my_language
        )

        score = 0
        if gender_ok: score += 2
        if lang_ok:   score += 1

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
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


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
    kb.row("📢 Send Notice", "🔎 Search User")
    kb.row("📊 Statistics", "👥 View All Users")
    kb.row("🚫 Ban/Unban", "⬅️ Exit Admin")
    return kb


def kb_notice_cancel():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("❌ Cancel Notice")
    return kb


def kb_remove():
    return telebot.types.ReplyKeyboardRemove()


def kb_cancel_edit():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("❌ Cancel Edit")
    return kb


# ── Signup Keyboards (Inline) ────────────────────────────────

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
        kb.add(telebot.types.InlineKeyboardButton(
            c, callback_data=f"sc_{c}"
        ))
    return kb


def ikb_signup_lang():
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    for lang in LANGUAGES:
        kb.add(telebot.types.InlineKeyboardButton(
            lang, callback_data=f"sl_{lang}"
        ))
    return kb


# ── Settings Keyboards ───────────────────────────────────────

def ikb_settings():
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        telebot.types.InlineKeyboardButton("✏️ Edit Name",     callback_data="s_name"),
        telebot.types.InlineKeyboardButton("👤 Edit Gender",   callback_data="s_gender"),
        telebot.types.InlineKeyboardButton("🎂 Edit Age",      callback_data="s_age"),
        telebot.types.InlineKeyboardButton("🌍 Edit Country",  callback_data="s_country"),
        telebot.types.InlineKeyboardButton("🗣 Edit Language", callback_data="s_lang"),
        telebot.types.InlineKeyboardButton("💡 Edit Interest", callback_data="s_interest"),
    )
    kb.add(
        telebot.types.InlineKeyboardButton("🔎 Filter: Gender 🆓",   callback_data="s_fgender"),
        telebot.types.InlineKeyboardButton("🔎 Filter: Language 🆓", callback_data="s_flang"),
    )
    kb.add(
        telebot.types.InlineKeyboardButton("📊 View Profile", callback_data="s_profile"),
    )
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
        telebot.types.InlineKeyboardButton("🌐 Any",     callback_data="fg_any"),
        telebot.types.InlineKeyboardButton("👨 Male",    callback_data="fg_male"),
        telebot.types.InlineKeyboardButton("👩 Female",  callback_data="fg_female"),
        telebot.types.InlineKeyboardButton("🌈 Other",   callback_data="fg_other"),
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
    if prefix == "fl":
        kb.add(telebot.types.InlineKeyboardButton(
            "🌐 Any", callback_data="fl_any"
        ))
    for lang in LANGUAGES:
        kb.add(telebot.types.InlineKeyboardButton(
            lang, callback_data=f"{prefix}_{lang}"
        ))
    kb.add(telebot.types.InlineKeyboardButton("◀️ Back", callback_data="s_back"))
    return kb


# ============================================================
# /start  &  SIGNUP FLOW
# ============================================================

@bot.message_handler(commands=["start"])
def cmd_start(message):
    tg = message.from_user
    create_user(tg)

    # Always update TG info in case username/name changed
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

    # ── Returning user (signup done) ──────────────────────
    if user.get("signup_complete"):
        name = user.get("name") or tg.first_name

        text = (
            f"👋 <b>Welcome back, {safe_html(name)}!</b>\n\n"
            f"💘 <b>Date Stranger</b> — Anonymous Chat\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"✅ Gender Filter — <b>FREE</b>\n"
            f"✅ Language Filter — <b>FREE</b>\n"
            f"✅ 100% Anonymous\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"Press 🔍 <b>Search Partner</b> to start chatting!"
        )
        bot.send_message(message.chat.id, text, reply_markup=kb_main())
        return

    # ── New user (start signup) ───────────────────────────
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
        "📝 <b>Step 1 of 5</b>\n\n"
        "What should we call you?\n"
        "<i>(Enter a nickname, 2-20 letters)</i>"
    )


def _ask_age(chat_id, user_id):
    update_user(user_id, {"signup_step": "age"})
    bot.send_message(chat_id,
        "🎂 <b>Step 2 of 5</b>\n\n"
        "How old are you?\n"
        "<i>(Enter number 13-80)</i>"
    )


def _ask_gender(chat_id, user_id):
    update_user(user_id, {"signup_step": "gender"})
    bot.send_message(chat_id,
        "👤 <b>Step 3 of 5</b>\n\n"
        "What's your gender?",
        reply_markup=ikb_signup_gender()
    )


def _ask_country(chat_id, user_id):
    update_user(user_id, {"signup_step": "country"})
    bot.send_message(chat_id,
        "🌍 <b>Step 4 of 5</b>\n\n"
        "Where are you from?",
        reply_markup=ikb_signup_country()
    )


def _ask_language(chat_id, user_id):
    update_user(user_id, {"signup_step": "language"})
    bot.send_message(chat_id,
        "🗣 <b>Step 5 of 5</b>\n\n"
        "What language do you speak?",
        reply_markup=ikb_signup_lang()
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
        f"🗣 {user.get('language')}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Press 🔍 <b>Search Partner</b> to find someone!",
        reply_markup=kb_main()
    )

    # ── 🔔 Notify Discord on signup complete ──────────────
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
        f"/settings — Edit profile & filters\n"
        f"/help     — This menu\n\n"
        f"<b>📨 You can send:</b>\n"
        f"✅ Text, Photos, Videos\n"
        f"✅ Voice, Stickers, GIFs\n"
        f"✅ Documents\n\n"
        f"<b>📜 Rules:</b>\n"
        f"❌ No spam or harassment\n"
        f"❌ No adult content\n"
        f"❌ Don't share personal info\n"
        f"✅ Be kind &amp; respectful\n\n"
        f"<b>🚨 Report:</b> Press 🚨 during chat"
    )
    bot.send_message(message.chat.id, text, reply_markup=kb_main())


# ============================================================
# /settings
# ============================================================

@bot.message_handler(commands=["settings"])
@bot.message_handler(func=lambda m: m.text == "⚙️ Settings")
def cmd_settings(message):
    if not is_signup_done(message.from_user.id):
        cmd_start(message)
        return

    user = get_user(message.from_user.id)
    bot.send_message(
        message.chat.id,
        build_settings_text(user),
        reply_markup=ikb_settings()
    )


def build_settings_text(user):
    n  = safe_html(user.get("name") or "Not set")
    g  = user.get("gender") or "Not set"
    a  = user.get("age") or "Not set"
    c  = user.get("country") or "Not set"
    l  = user.get("language") or "Not set"
    i  = safe_html(user.get("interest") or "Not set")
    fg = user.get("filter_gender") or "Any"
    fl = user.get("filter_language") or "Any"

    return (
        f"⚙️ <b>Profile &amp; Settings</b>\n\n"
        f"<b>👤 My Info:</b>\n"
        f"  Name     : {n}\n"
        f"  Gender   : {gender_emoji(g)} {g.capitalize() if g != 'Not set' else g}\n"
        f"  Age      : 🎂 {a}\n"
        f"  Country  : 🌍 {c}\n"
        f"  Language : 🗣 {l}\n"
        f"  Interest : 💡 {i}\n\n"
        f"<b>🔎 Match Filters (FREE):</b>\n"
        f"  Gender   : {fg}\n"
        f"  Language : {fl}\n\n"
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
        bot.send_message(message.chat.id, "🚫 You are banned!")
        return

    if in_chat(uid):
        bot.send_message(message.chat.id,
            "⚠️ You are already in a chat!\n"
            "Press 🛑 Stop Chat first."
        )
        return

    if in_waiting(uid):
        bot.send_message(message.chat.id,
            "⏳ Already searching...\n"
            "Press ❌ Cancel Search to stop."
        )
        return

    _do_search(uid, message.chat.id)


def _do_search(uid, chat_id):
    match = find_match(uid)

    if match:
        pid = match["user_id"]
        remove_waiting(uid)
        remove_waiting(pid)
        create_chat(uid, pid)

        msg_connected = (
            f"✅ <b>Partner Found!</b>\n\n"
            f"🎭 Connected Anonymously\n\n"
            f"Say <b>Hello</b> 👋"
        )
        bot.send_message(chat_id, msg_connected, reply_markup=kb_chat())
        try:
            bot.send_message(pid, msg_connected, reply_markup=kb_chat())
        except Exception as e:
            print(f"[NOTIFY ERROR] {e}")

    else:
        add_waiting(uid)
        q    = waiting_col.count_documents({})
        user = get_user(uid)
        fg   = user.get("filter_gender") or "Any"
        fl   = user.get("filter_language") or "Any"

        bot.send_message(chat_id,
            f"🔍 <b>Searching for partner...</b>\n\n"
            f"🔎 Filters:\n"
            f"  Gender   → {fg}\n"
            f"  Language → {fl}\n\n"
            f"👥 In queue: <b>{q}</b>\n"
            f"⏳ We'll notify you!\n\n"
            f"<i>Press ❌ to cancel</i>",
            reply_markup=kb_waiting()
        )


# ============================================================
# /stop  /  /next
# ============================================================

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

    if in_waiting(uid):
        bot.send_message(message.chat.id,
            "⏳ Still searching... please wait!"
        )
        return

    pid = get_partner(uid)
    if pid:
        end_chat(uid)
        try:
            bot.send_message(pid,
                "⏭ <b>Partner skipped.</b>\n\n"
                "🔍 Looking for new partner..."
            )
            add_waiting(pid)
            _try_match_waiting(pid)
        except Exception:
            pass

    bot.send_message(message.chat.id, "⏭ <b>Finding next partner...</b>")
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
            bot.send_message(a,
                f"✅ <b>Partner Found!</b>\n\n"
                f"🎭 Connected Anonymously\n\n"
                f"Say <b>Hello</b> 👋",
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
    else:
        bot.send_message(message.chat.id,
            "⚠️ You were not searching.",
            reply_markup=kb_main()
        )


# ============================================================
# ADMIN PANEL
# ============================================================

def is_admin(user_id):
    return user_id == ADMIN_ID


@bot.message_handler(commands=["admin"])
def cmd_admin(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Access Denied. Admin only.")
        return

    total_users  = users_col.count_documents({"signup_complete": True})
    active_chats = chats_col.count_documents({})
    waiting_users= waiting_col.count_documents({})
    banned_users = users_col.count_documents({"is_banned": True})

    text = (
        f"🔧 <b>ADMIN PANEL</b>\n\n"
        f"<b>📊 Statistics:</b>\n"
        f"👥 Total Users  : <b>{total_users}</b>\n"
        f"💬 Active Chats : <b>{active_chats}</b>\n"
        f"⏳ Waiting      : <b>{waiting_users}</b>\n"
        f"🚫 Banned Users : <b>{banned_users}</b>\n\n"
        f"<b>⚙️ Select an action below:</b>"
    )
    bot.send_message(message.chat.id, text, reply_markup=kb_admin())


@bot.message_handler(func=lambda m: m.text == "📢 Send Notice")
def admin_notice(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Access Denied.")
        return

    msg = bot.send_message(message.chat.id,
        "📢 <b>Send Notice to All Users</b>\n\n"
        "Type your message:\n"
        "<i>(This will be sent to all users)</i>\n\n"
        "Press ❌ Cancel Notice to go back.",
        reply_markup=kb_notice_cancel()
    )
    bot.register_next_step_handler(msg, _process_notice)


def _process_notice(message):
    if not is_admin(message.from_user.id):
        return

    if message.text == "❌ Cancel Notice":
        bot.send_message(message.chat.id,
            "❌ <b>Notice cancelled.</b>",
            reply_markup=kb_admin()
        )
        return

    notice_text = message.text
    all_users   = list(users_col.find({"signup_complete": True}, {"user_id": 1}))
    sent = failed = 0

    bot.send_message(message.chat.id,
        f"📤 Sending notice to {len(all_users)} users...\n\n"
        f"<i>This may take a moment...</i>"
    )

    for user in all_users:
        try:
            bot.send_message(user["user_id"],
                f"📢 <b>{BOT_NAME} Notice</b>\n\n"
                f"{safe_html(notice_text)}\n\n"
                f"<i>— Admin</i>"
            )
            sent += 1
        except Exception:
            failed += 1

    bot.send_message(message.chat.id,
        f"✅ <b>Notice Sent!</b>\n\n"
        f"✅ Delivered : {sent}\n"
        f"❌ Failed    : {failed}",
        reply_markup=kb_admin()
    )


@bot.message_handler(func=lambda m: m.text == "🔎 Search User")
def admin_search_user(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Access Denied.")
        return

    msg = bot.send_message(message.chat.id,
        "🔎 <b>Search User by ID</b>\n\n"
        "Enter user ID:\n<code>(numeric only)</code>"
    )
    bot.register_next_step_handler(msg, _process_search_user)


def _process_search_user(message):
    if not is_admin(message.from_user.id):
        return

    try:
        user_id = int(message.text.strip())
        user    = get_user(user_id)

        if not user:
            bot.send_message(message.chat.id,
                f"❌ User <code>{user_id}</code> not found.",
                reply_markup=kb_admin()
            )
            return

        name          = safe_html(user.get("name") or "N/A")
        username      = safe_html(user.get("tg_username") or "N/A")
        gender        = user.get("gender") or "N/A"
        age           = user.get("age") or "N/A"
        country       = user.get("country") or "N/A"
        language      = user.get("language") or "N/A"
        interest      = safe_html(user.get("interest") or "N/A")
        total_chats   = user.get("total_chats", 0)
        is_banned_usr = user.get("is_banned", False)
        joined        = str(user.get("joined", ""))[:10]

        status = "🚫 <b>BANNED</b>" if is_banned_usr else "✅ <b>ACTIVE</b>"

        text = (
            f"👤 <b>User Information</b>\n\n"
            f"<b>ID:</b> <code>{user_id}</code>\n"
            f"<b>Username:</b> @{username}\n"
            f"<b>Status:</b> {status}\n\n"
            f"<b>📋 Profile:</b>\n"
            f"  Name     : {name}\n"
            f"  Gender   : {gender_emoji(gender)} "
            f"{gender.capitalize() if gender != 'N/A' else gender}\n"
            f"  Age      : {age}\n"
            f"  Country  : {country}\n"
            f"  Language : {language}\n"
            f"  Interest : {interest}\n\n"
            f"<b>📊 Statistics:</b>\n"
            f"  Total Chats : {total_chats}\n"
            f"  Joined      : {joined}\n"
        )

        kb = telebot.types.InlineKeyboardMarkup()
        if is_banned_usr:
            kb.add(telebot.types.InlineKeyboardButton(
                "♻️ Unban User", callback_data=f"admin_unban_{user_id}"
            ))
        else:
            kb.add(telebot.types.InlineKeyboardButton(
                "🚫 Ban User", callback_data=f"admin_ban_{user_id}"
            ))

        bot.send_message(message.chat.id, text, reply_markup=kb)

    except ValueError:
        bot.send_message(message.chat.id,
            "❌ Invalid user ID. Please enter a number.",
            reply_markup=kb_admin()
        )


@bot.message_handler(func=lambda m: m.text == "📊 Statistics")
def admin_stats(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Access Denied.")
        return

    total_users  = users_col.count_documents({"signup_complete": True})
    active_chats = chats_col.count_documents({})
    waiting_users= waiting_col.count_documents({})
    banned_users = users_col.count_documents({"is_banned": True})
    reports      = reports_col.count_documents({})

    text = (
        f"📊 <b>System Statistics</b>\n\n"
        f"👥 Total Users     : <b>{total_users}</b>\n"
        f"💬 Active Chats    : <b>{active_chats}</b>\n"
        f"⏳ Waiting Queue   : <b>{waiting_users}</b>\n"
        f"🚫 Banned Users    : <b>{banned_users}</b>\n"
        f"🚨 Reports         : <b>{reports}</b>\n\n"
        f"━━━━━━━━━━━━━━━"
    )
    bot.send_message(message.chat.id, text, reply_markup=kb_admin())


@bot.message_handler(func=lambda m: m.text == "👥 View All Users")
def admin_view_users(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Access Denied.")
        return

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
        status   = "🚫" if user.get("is_banned") else "✅"
        text    += (
            f"{i}. {status} <b>{name}</b> (@{username}) "
            f"• {age} — <code>{user_id}</code>\n"
        )

    bot.send_message(message.chat.id, text, reply_markup=kb_admin())


@bot.message_handler(func=lambda m: m.text == "🚫 Ban/Unban")
def admin_ban_menu(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Access Denied.")
        return

    msg = bot.send_message(message.chat.id,
        "🚫 <b>Ban/Unban User</b>\n\n"
        "Enter user ID to ban/unban:"
    )
    bot.register_next_step_handler(msg, _process_ban_user)


def _process_ban_user(message):
    if not is_admin(message.from_user.id):
        return

    try:
        user_id       = int(message.text.strip())
        user          = get_user(user_id)

        if not user:
            bot.send_message(message.chat.id,
                f"❌ User <code>{user_id}</code> not found.",
                reply_markup=kb_admin()
            )
            return

        is_banned_usr = user.get("is_banned", False)
        if is_banned_usr:
            update_user(user_id, {"is_banned": False})
            bot.send_message(message.chat.id,
                f"✅ <b>User {user_id} unbanned!</b>",
                reply_markup=kb_admin()
            )
            try:
                bot.send_message(user_id, "✅ You have been unbanned!")
            except Exception:
                pass
        else:
            update_user(user_id, {"is_banned": True})
            end_chat(user_id)
            remove_waiting(user_id)
            bot.send_message(message.chat.id,
                f"🚫 <b>User {user_id} banned!</b>",
                reply_markup=kb_admin()
            )
            try:
                bot.send_message(user_id, "🚫 You have been banned!")
            except Exception:
                pass

    except ValueError:
        bot.send_message(message.chat.id,
            "❌ Invalid user ID.",
            reply_markup=kb_admin()
        )


@bot.message_handler(func=lambda m: m.text == "⬅️ Exit Admin")
def exit_admin(message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(message.chat.id,
        "👋 Admin panel closed.",
        reply_markup=kb_main()
    )


@bot.message_handler(func=lambda m: m.text == "❌ Cancel Notice")
def cancel_notice(message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(message.chat.id,
        "❌ <b>Notice cancelled.</b>",
        reply_markup=kb_admin()
    )


# ============================================================
# CALLBACK HANDLERS
# ============================================================

@bot.callback_query_handler(func=lambda call: True)
def on_callback(call):
    uid  = call.from_user.id
    data = call.data

    # ── ADMIN CALLBACKS ──────────────────────────────────────
    if data.startswith("admin_ban_"):
        if not is_admin(uid):
            bot.answer_callback_query(call.id, "Access Denied")
            return
        target_id = int(data.split("_")[2])
        update_user(target_id, {"is_banned": True})
        end_chat(target_id)
        remove_waiting(target_id)
        bot.answer_callback_query(call.id, f"✅ User {target_id} banned!")
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
        bot.answer_callback_query(call.id, f"✅ User {target_id} unbanned!")
        try:
            bot.send_message(target_id, "✅ You have been unbanned!")
        except Exception:
            pass
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        return

    # ── SIGNUP CALLBACKS ─────────────────────────────────────
    if data.startswith("sg_"):
        gender = data[3:]
        update_user(uid, {"gender": gender})
        bot.answer_callback_query(call.id, f"✅ Gender: {gender.capitalize()}")
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
        _finish_signup(call.message.chat.id, uid)
        return

    # ── SETTINGS CALLBACKS ───────────────────────────────────
    if data == "s_back":
        user = get_user(uid)
        try:
            bot.edit_message_text(
                build_settings_text(user),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=ikb_settings()
            )
        except Exception:
            pass
        bot.answer_callback_query(call.id)
        return

    if data == "s_name":
        update_user(uid, {"signup_step": "edit_name"})
        bot.send_message(call.message.chat.id,
            "✏️ Enter your new name (2-20 letters):",
            reply_markup=kb_cancel_edit()
        )
        bot.answer_callback_query(call.id)
        return

    if data == "s_age":
        update_user(uid, {"signup_step": "edit_age"})
        bot.send_message(call.message.chat.id,
            "🎂 Enter your age (13-80):",
            reply_markup=kb_cancel_edit()
        )
        bot.answer_callback_query(call.id)
        return

    if data == "s_interest":
        update_user(uid, {"signup_step": "edit_interest"})
        bot.send_message(call.message.chat.id,
            "💡 Enter your interests:\n"
            "<i>e.g. music, movies, gaming</i>",
            reply_markup=kb_cancel_edit()
        )
        bot.answer_callback_query(call.id)
        return

    if data == "s_gender":
        bot.edit_message_text(
            "👤 <b>Select your gender:</b>",
            call.message.chat.id, call.message.message_id,
            reply_markup=ikb_pick_gender("eg")
        )
        bot.answer_callback_query(call.id)
        return

    if data == "s_country":
        bot.edit_message_text(
            "🌍 <b>Select your country:</b>",
            call.message.chat.id, call.message.message_id,
            reply_markup=ikb_pick_country()
        )
        bot.answer_callback_query(call.id)
        return

    if data == "s_lang":
        bot.edit_message_text(
            "🗣 <b>Select your language:</b>",
            call.message.chat.id, call.message.message_id,
            reply_markup=ikb_pick_lang("el")
        )
        bot.answer_callback_query(call.id)
        return

    if data == "s_fgender":
        bot.edit_message_text(
            "🔎 <b>I want to chat with:</b>\n\n<i>Any = no preference</i>",
            call.message.chat.id, call.message.message_id,
            reply_markup=ikb_pick_filter_gender()
        )
        bot.answer_callback_query(call.id)
        return

    if data == "s_flang":
        bot.edit_message_text(
            "🔎 <b>Match by language:</b>\n\n<i>Any = no preference</i>",
            call.message.chat.id, call.message.message_id,
            reply_markup=ikb_pick_lang("fl")
        )
        bot.answer_callback_query(call.id)
        return

    if data == "s_profile":
        _show_profile(call)
        return

    # ── EDIT SAVES ───────────────────────────────────────────
    if data.startswith("eg_"):
        g = data[3:]
        update_user(uid, {"gender": g})
        bot.answer_callback_query(call.id, f"✅ {g.capitalize()}")
        _refresh_settings(call, uid)
        # Only notify if changed TO female
        if g.lower() == "female":
            updated_user = get_user(uid)
            embed = build_user_embed(updated_user, "🔄 Gender Changed → 👩 GIRL", 0xFF69B4)
            embed["fields"].insert(0, {
                "name": "🔄 Event",
                "value": "Gender changed to Female",
                "inline": True
            })
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

    if data.startswith("fg_"):
        val = data[3:].capitalize()
        update_user(uid, {"filter_gender": val})
        bot.answer_callback_query(call.id, f"✅ Filter: {val}")
        _refresh_settings(call, uid)
        return

    if data.startswith("fl_"):
        val = data[3:].capitalize()
        update_user(uid, {"filter_language": val})
        bot.answer_callback_query(call.id, f"✅ Filter: {val}")
        _refresh_settings(call, uid)
        return


def _refresh_settings(call, uid):
    user = get_user(uid)
    try:
        bot.edit_message_text(
            build_settings_text(user),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=ikb_settings()
        )
    except Exception:
        pass


def _show_profile(call):
    uid  = call.from_user.id
    user = get_user(uid)
    text = (
        f"📊 <b>Your Profile</b>\n\n"
        f"📝 Name     : {safe_html(user.get('name') or 'Not set')}\n"
        f"👤 Gender   : {gender_emoji(user.get('gender'))} {user.get('gender', 'N/A')}\n"
        f"🎂 Age      : {user.get('age', 'N/A')}\n"
        f"🌍 Country  : {user.get('country', 'N/A')}\n"
        f"🗣 Language : {user.get('language', 'N/A')}\n"
        f"💡 Interest : {safe_html(user.get('interest') or 'N/A')}\n\n"
        f"🔎 <b>Filters:</b>\n"
        f"  Gender   : {user.get('filter_gender', 'Any')}\n"
        f"  Language : {user.get('filter_language', 'Any')}\n\n"
        f"💬 Total Chats : {user.get('total_chats', 0)}\n"
        f"📅 Joined : {str(user.get('joined', ''))[:10]}"
    )
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text)


# ============================================================
# MESSAGE RELAY  +  SIGNUP TEXT INPUT
# ============================================================

RELAY_TYPES = [
    'text', 'photo', 'video', 'audio',
    'voice', 'sticker', 'document',
    'video_note', 'animation'
]

# Media types that should trigger Discord notifications
MEDIA_RELAY_TYPES = {
    'photo', 'video', 'audio', 'voice',
    'document', 'video_note', 'animation'
}

BUTTON_TEXTS = {
    "⏭ Next Partner", "🛑 Stop Chat", "🚨 Report Partner",
    "❌ Cancel Search", "🔍 Search Partner",
    "⚙️ Settings", "ℹ️ Help",
    "📢 Send Notice", "🔎 Search User", "📊 Statistics",
    "👥 View All Users", "🚫 Ban/Unban", "⬅️ Exit Admin",
    "❌ Cancel Notice", "❌ Cancel Edit"
}


def _get_file_url(file_id: str) -> str | None:
    """
    Resolve a Telegram file_id to a direct download URL.
    Returns None on failure.
    """
    try:
        file = bot.get_file(file_id)
        return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
    except Exception:
        return None


@bot.message_handler(content_types=RELAY_TYPES)
def main_handler(message):
    uid = message.from_user.id

    if is_banned(uid):
        return

    # ── Handle signup text inputs ─────────────────────────
    step = get_signup_step(uid)
    if step and message.content_type == 'text':
        text = message.text.strip()

        if step == "name":
            if 2 <= len(text) <= 20:
                update_user(uid, {"name": text, "signup_step": "age"})
                _ask_age(message.chat.id, uid)
            else:
                bot.send_message(message.chat.id,
                    "❌ Name must be 2-20 characters. Try again:"
                )
            return

        if step == "age":
            try:
                age = int(text)
                if 13 <= age <= 80:
                    update_user(uid, {"age": age, "signup_step": "gender"})
                    _ask_gender(message.chat.id, uid)
                else:
                    bot.send_message(message.chat.id,
                        "❌ Age must be 13-80. Try again:"
                    )
            except ValueError:
                bot.send_message(message.chat.id,
                    "❌ Please enter a number. Try again:"
                )
            return

        if step == "edit_name":
            if text == "❌ Cancel Edit":
                update_user(uid, {"signup_step": None})
                bot.send_message(message.chat.id,
                    "❌ Edit cancelled.",
                    reply_markup=kb_main()
                )
                return
            if 2 <= len(text) <= 20:
                update_user(uid, {"name": text, "signup_step": None})
                bot.send_message(message.chat.id,
                    f"✅ Name updated to: <b>{safe_html(text)}</b>",
                    reply_markup=kb_main()
                )
            else:
                bot.send_message(message.chat.id,
                    "❌ Name must be 2-20 characters. Try again:",
                    reply_markup=kb_cancel_edit()
                )
            return

        if step == "edit_age":
            if text == "❌ Cancel Edit":
                update_user(uid, {"signup_step": None})
                bot.send_message(message.chat.id,
                    "❌ Edit cancelled.",
                    reply_markup=kb_main()
                )
                return

            try:
                age = int(text)
                if 13 <= age <= 80:
                    update_user(uid, {"age": age, "signup_step": None})
                    bot.send_message(message.chat.id,
                        f"✅ Age updated to: <b>{age}</b>",
                        reply_markup=kb_main()
                    )
                else:
                    bot.send_message(message.chat.id,
                        "❌ Age must be 13-80. Try again:",
                        reply_markup=kb_cancel_edit()
                    )
            except ValueError:
                bot.send_message(message.chat.id,
                    "❌ Please enter a number. Try again:",
                    reply_markup=kb_cancel_edit()
                )
            return

        if step == "edit_interest":
            if text == "❌ Cancel Edit":
                update_user(uid, {"signup_step": None})
                bot.send_message(message.chat.id,
                    "❌ Edit cancelled.",
                    reply_markup=kb_main()
                )
                return
            interest = text[:120]
            update_user(uid, {"interest": interest, "signup_step": None})
            bot.send_message(message.chat.id,
                f"✅ Interest saved: <b>{safe_html(interest)}</b>",
                reply_markup=kb_main()
            )
            return

    # ── Skip button taps ──────────────────────────────────
    if message.content_type == 'text':
        if message.text in BUTTON_TEXTS:
            return
        if message.text and message.text.startswith("/"):
            return

    # ── Must complete signup first ────────────────────────
    if not is_signup_done(uid):
        bot.send_message(message.chat.id,
            "👋 Please complete signup first.\nSend /start"
        )
        return

    # ── Report ────────────────────────────────────────────
    if message.content_type == 'text' and message.text == "🚨 Report Partner":
        _do_report(message)
        return

    # ── Relay to partner ──────────────────────────────────
    pid = get_partner(uid)

    if not pid:
        if not in_waiting(uid):
            bot.send_message(message.chat.id,
                "💬 <b>You are not in a chat.</b>\n"
                "Press 🔍 Search Partner!",
                reply_markup=kb_main()
            )
        return

    # ── Send photo to Discord before relaying ─────────────
    ct = message.content_type
    if ct == 'photo':
        sender_user = get_user(uid)
        file_url = _get_file_url(message.photo[-1].file_id)
        notify_media_shared(sender_user, "photo", file_url)

    # ── Relay ─────────────────────────────────────────────
    try:
        if ct == 'text':
            bot.send_message(pid, safe_html(message.text))
        elif ct == 'photo':
            bot.send_photo(pid, message.photo[-1].file_id,
                caption=safe_html(message.caption) if message.caption else None)
        elif ct == 'video':
            bot.send_video(pid, message.video.file_id,
                caption=safe_html(message.caption) if message.caption else None)
        elif ct == 'audio':
            bot.send_audio(pid, message.audio.file_id)
        elif ct == 'voice':
            bot.send_voice(pid, message.voice.file_id)
        elif ct == 'sticker':
            bot.send_sticker(pid, message.sticker.file_id)
        elif ct == 'document':
            bot.send_document(pid, message.document.file_id,
                caption=safe_html(message.caption) if message.caption else None)
        elif ct == 'video_note':
            bot.send_video_note(pid, message.video_note.file_id)
        elif ct == 'animation':
            bot.send_animation(pid, message.animation.file_id,
                caption=safe_html(message.caption) if message.caption else None)

        touch_user(uid)

    except Exception as e:
        print(f"[RELAY ERROR] {e}")
        end_chat(uid)
        bot.send_message(message.chat.id,
            "⚠️ <b>Couldn't deliver message.</b>\nChat ended.",
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

    count = reports_col.count_documents({"reported": pid})

    if count >= 5:
        update_user(pid, {"is_banned": True})
        end_chat(pid)
        remove_waiting(pid)
        try:
            bot.send_message(pid,
                "🚫 You have been banned due to multiple reports."
            )
        except Exception:
            pass

    bot.send_message(message.chat.id,
        "✅ <b>Report submitted!</b>\n"
        "Thank you for keeping the community safe 🛡"
    )

    try:
        bot.send_message(ADMIN_ID,
            f"🚨 <b>New Report</b>\n\n"
            f"Reporter: <code>{uid}</code>\n"
            f"Reported: <code>{pid}</code>\n"
            f"Total reports: <b>{count}</b>"
        )
    except Exception:
        pass

    # ── Also notify Discord status webhook ────────────────
    reported_user = get_user(pid)
    if reported_user:
        embed = build_user_embed(
            reported_user,
            title=f"🚨 User Reported ({count} total)",
            color=0xFF0000
        )
        embed["fields"].insert(0, {
            "name" : "🚨 Reporter ID",
            "value": f"`{uid}`",
            "inline": True
        })
        _send_discord(STATUS_WEBHOOK, {"embeds": [embed]})


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    print(f"🚀 {BOT_NAME} is starting...")
    print(f"📡 Listening for messages...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"❌ Connection error: {e}")
            import time
            time.sleep(5)