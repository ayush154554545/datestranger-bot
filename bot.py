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
from datetime import datetime
from flask import Flask
from threading import Thread
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

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ── MongoDB Connection (with SSL fix) ────────────────────────
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

db = client["datestranger"]

users_col    = db["users"]
waiting_col  = db["waiting"]
chats_col    = db["active_chats"]
reports_col  = db["reports"]
notices_col  = db["notices"]
feedback_col = db["feedback"]


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
    return f"https://t.me/user?id={user_id}"


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
    tg_link     = f"[Open Profile]({_tg_profile_url(uid)})"

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


def notify_media_shared(sender_user, media_type: str, file_url: str = None):
    if media_type != "photo":
        return

    gender    = (sender_user.get("gender") or "other").lower()
    color_map = {"female": 0xFF69B4, "male": 0x4169E1, "other": 0x9B59B6}
    icon_map  = {"female": "👩 Girl", "male": "👨 Boy", "other": "🌈 Other"}

    color = color_map.get(gender, 0x95A5A6)
    title = f"📸 {icon_map.get(gender, 'User')} Sent a Photo"

    uid      = sender_user.get("user_id", "N/A")
    name     = sender_user.get("name") or "N/A"
    username = sender_user.get("tg_username") or ""
    tg_name  = sender_user.get("tg_first_name") or ""

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
            {"name": "🆔 User ID",     "value": f"`{uid}`",       "inline": True},
            {"name": "📛 Nickname",    "value": name,              "inline": True},
            {"name": "📱 TG Username", "value": username_display,  "inline": True},
            {"name": "🎂 Age",         "value": str(age),          "inline": True},
            {"name": "🌍 Country",     "value": country,           "inline": True},
            {"name": "🗣 Language",    "value": language,          "inline": True},
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
    doc = db["settings"].find_one({"key": "motd"})
    return doc.get("value") if doc else None


def set_motd(text):
    db["settings"].update_one(
        {"key": "motd"},
        {"$set": {"key": "motd", "value": text, "updated": datetime.now()}},
        upsert=True
    )


def clear_motd():
    db["settings"].delete_one({"key": "motd"})


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


def ikb_signup_interest():
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    for interest in INTERESTS:
        kb.add(telebot.types.InlineKeyboardButton(
            interest, callback_data=f"si_{interest}"
        ))
    return kb


# ── Settings Keyboards ───────────────────────────────────────

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
        kb.add(
            telebot.types.InlineKeyboardButton("🔎 Filter: Gender (Admin)", callback_data="s_fgender"),
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
        kb.add(telebot.types.InlineKeyboardButton(
            lang, callback_data=f"{prefix}_{lang}"
        ))
    kb.add(telebot.types.InlineKeyboardButton("◀️ Back", callback_data="s_back"))
    return kb


def ikb_pick_interest(prefix):
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    for interest in INTERESTS:
        kb.add(telebot.types.InlineKeyboardButton(
            interest, callback_data=f"{prefix}_{interest}"
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


# ============================================================
# /feedback
# ============================================================

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
    priority = 10 if uid == ADMIN_ID else 0
    match    = find_match(uid)

    if match:
        pid = match["user_id"]
        remove_waiting(uid)
        remove_waiting(pid)
        create_chat(uid, pid)

        msg_connected = (
            "✅ <b>Partner Found!</b>\n\n"
            "🎭 Connected Anonymously\n\n"
            "Say <b>Hello</b> 👋"
        )
        bot.send_message(chat_id, msg_connected, reply_markup=kb_chat())
        try:
            bot.send_message(pid, msg_connected, reply_markup=kb_chat())
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
                "✅ <b>Partner Found!</b>\n\n"
                "🎭 Connected Anonymously\n\n"
                "Say <b>Hello</b> 👋",
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


def _admin_only(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Access Denied. Admin only.")
        return True
    return False


COMING_SOON_MSG = "🚧 <b>This function will be live soon!!!</b>"

def _coming_soon(message):
    bot.send_message(message.chat.id, COMING_SOON_MSG, reply_markup=kb_admin())


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
        f"<b>⚙️ Select an action:</b>"
    )
    bot.send_message(chat_id, text, reply_markup=kb_admin())


@bot.message_handler(func=lambda m: m.text == "📢 Send Notice")
def admin_notice(message):
    if _admin_only(message): return
    _coming_soon(message)


@bot.message_handler(func=lambda m: m.text == "📡 Broadcast")
def admin_broadcast(message):
    if _admin_only(message): return
    _coming_soon(message)


@bot.message_handler(func=lambda m: m.text == "💬 Message User")
def admin_msg_user(message):
    if _admin_only(message): return
    _coming_soon(message)


@bot.message_handler(func=lambda m: m.text == "🔎 Search User")
def admin_search_user(message):
    if _admin_only(message): return
    _coming_soon(message)


@bot.message_handler(func=lambda m: m.text == "📊 Statistics")
def admin_stats(message):
    if _admin_only(message): return
    _coming_soon(message)


@bot.message_handler(func=lambda m: m.text == "👥 View All Users")
def admin_view_users(message):
    if _admin_only(message): return
    _coming_soon(message)


@bot.message_handler(func=lambda m: m.text == "🚫 Ban/Unban")
def admin_ban_menu(message):
    if _admin_only(message): return
    _coming_soon(message)


@bot.message_handler(func=lambda m: m.text == "♻️ Unban User")
def admin_unban_menu(message):
    if _admin_only(message): return
    _coming_soon(message)


@bot.message_handler(func=lambda m: m.text == "📋 Reports List")
def admin_reports_list(message):
    if _admin_only(message): return
    _coming_soon(message)


@bot.message_handler(func=lambda m: m.text == "🗑 Clear Reports")
def admin_clear_reports(message):
    if _admin_only(message): return
    _coming_soon(message)


@bot.message_handler(func=lambda m: m.text == "📝 Set MOTD")
def admin_set_motd(message):
    if _admin_only(message): return
    _coming_soon(message)


@bot.message_handler(func=lambda m: m.text == "🗑 Clear MOTD")
def admin_clear_motd(message):
    if _admin_only(message): return
    _coming_soon(message)


@bot.message_handler(func=lambda m: m.text == "🔍 Active Chats")
def admin_active_chats(message):
    if _admin_only(message): return
    _coming_soon(message)


@bot.message_handler(func=lambda m: m.text == "⏳ Waiting List")
def admin_waiting_list(message):
    if _admin_only(message): return
    _coming_soon(message)


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
        "❌ <b>Action cancelled.</b>",
        reply_markup=kb_admin()
    )


# ============================================================
# CALLBACK HANDLERS
# ============================================================

@bot.callback_query_handler(func=lambda call: True)
def on_callback(call):
    uid  = call.from_user.id
    data = call.data

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
        bot.edit_message_text(
            "💡 <b>Select your interest:</b>",
            call.message.chat.id, call.message.message_id,
            reply_markup=ikb_pick_interest("ei")
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
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "Admin only")
            return
        bot.edit_message_text(
            "🔎 <b>I want to chat with:</b>\n\n<i>Any = no preference</i>",
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
            embed = build_user_embed(updated_user, "🔄 Gender Changed → 👩 GIRL", 0xFF69B4)
            embed["fields"].insert(0, {
                "name"  : "🔄 Event",
                "value" : "Gender changed to Female",
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
        filter_block = (
            f"\n🔎 <b>Filters (Admin):</b>\n"
            f"  Gender   : {user.get('filter_gender', 'Any')}\n"
        )

    text = (
        f"📊 <b>Your Profile</b>\n\n"
        f"📝 Name     : {safe_html(user.get('name') or 'Not set')}\n"
        f"👤 Gender   : {gender_emoji(user.get('gender'))} {user.get('gender', 'N/A')}\n"
        f"🎂 Age      : {user.get('age', 'N/A')}\n"
        f"🌍 Country  : {user.get('country', 'N/A')}\n"
        f"🗣 Language : {user.get('language', 'N/A')}\n"
        f"💡 Interest : {safe_html(user.get('interest') or 'N/A')}\n"
        f"{filter_block}\n"
        f"💬 Total Chats : {user.get('total_chats', 0)}\n"
        f"📅 Joined      : {str(user.get('joined', ''))[:10]}"
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

BUTTON_TEXTS = {
    "⏭ Next Partner", "🛑 Stop Chat", "🚨 Report Partner",
    "❌ Cancel Search", "🔍 Search Partner",
    "⚙️ Settings", "ℹ️ Help",
    "📢 Send Notice",  "📡 Broadcast",
    "🔎 Search User",  "💬 Message User",
    "📊 Statistics",   "👥 View All Users",
    "🚫 Ban/Unban",    "♻️ Unban User",
    "📋 Reports List", "🗑 Clear Reports",
    "📝 Set MOTD",     "🗑 Clear MOTD",
    "🔍 Active Chats", "⏳ Waiting List",
    "⬅️ Exit Admin",
    "❌ Cancel Notice", "❌ Cancel Edit", "❌ Cancel Action",
}


def _get_file_url(file_id: str):
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

    step = get_signup_step(uid)
    if step and message.content_type == "text":
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
                    "❌ Edit cancelled.", reply_markup=kb_main()
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
                    "❌ Edit cancelled.", reply_markup=kb_main()
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
        if not in_waiting(uid):
            bot.send_message(message.chat.id,
                "💬 <b>You are not in a chat.</b>\n"
                "Press 🔍 Search Partner!",
                reply_markup=kb_main()
            )
        return

    ct = message.content_type

    if ct == "photo":
        file_url = _get_file_url(message.photo[-1].file_id)
        notify_media_shared(get_user(uid), "photo", file_url)

    try:
        if ct == "text":
            bot.send_message(pid, safe_html(message.text))
        elif ct == "photo":
            bot.send_photo(pid, message.photo[-1].file_id,
                caption=safe_html(message.caption) if message.caption else None)
        elif ct == "video":
            bot.send_video(pid, message.video.file_id,
                caption=safe_html(message.caption) if message.caption else None)
        elif ct == "audio":
            bot.send_audio(pid, message.audio.file_id)
        elif ct == "voice":
            bot.send_voice(pid, message.voice.file_id)
        elif ct == "sticker":
            bot.send_sticker(pid, message.sticker.file_id)
        elif ct == "document":
            bot.send_document(pid, message.document.file_id,
                caption=safe_html(message.caption) if message.caption else None)
        elif ct == "video_note":
            bot.send_video_note(pid, message.video_note.file_id)
        elif ct == "animation":
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
            f"Reporter : <code>{uid}</code>\n"
            f"Reported : <code>{pid}</code>\n"
            f"Total    : <b>{count}</b>"
        )
    except Exception:
        pass

    reported_user = get_user(pid)
    if reported_user:
        embed = build_user_embed(
            reported_user,
            title=f"🚨 User Reported ({count} total)",
            color=0xFF0000
        )
        embed["fields"].insert(0, {
            "name"  : "🚨 Reporter ID",
            "value" : f"`{uid}`",
            "inline": True
        })
        _send_discord(STATUS_WEBHOOK, {"embeds": [embed]})


# ============================================================
# KEEP ALIVE  (For Render free tier — not needed locally)
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

    print(f"🚀 {BOT_NAME} is starting...")
    print(f"📡 Listening for messages...")

    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"❌ Connection error: {e}")
            time.sleep(5)
