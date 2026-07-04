import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

app = Flask(__name__)

telegram_app = Application.builder().token(BOT_TOKEN).build()

# Default emoji list
EMOJIS = [
    "👍",
    "❤️",
    "🔥",
    "😂",
    "😍",
    "👏",
    "🤩",
    "😎",
    "🎉",
    "⚡",
]

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Auto Reaction Bot is working!"
    )

# ================= SHOW EMOJIS =================

async def show_emojis(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "Current emojis:\n\n"
        + " ".join(EMOJIS)
    )

# ================= ADMIN CHECK =================

async def is_admin(update, context):

    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id,
    )

    return member.status in [
        "creator",
        "administrator",
    ]

# ================= ADD EMOJI =================

async def add_emoji(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    global EMOJIS

    if not await is_admin(update, context):
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/addemoji 😀"
        )
        return

    emoji = context.args[0]

    if emoji not in EMOJIS:
        EMOJIS.append(emoji)

    await update.message.reply_text(
        f"✅ Added: {emoji}"
    )

# ================= REMOVE EMOJI =================

async def remove_emoji(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    global EMOJIS

    if not await is_admin(update, context):
        return

    if not context.args:
        return

    emoji = context.args[0]

    if emoji in EMOJIS:
        EMOJIS.remove(emoji)

    await update.message.reply_text(
        f"❌ Removed: {emoji}"
    )

# ================= HANDLERS =================

telegram_app.add_handler(
    CommandHandler(
        "start",
        start,
    )
)

telegram_app.add_handler(
    CommandHandler(
        "emojis",
        show_emojis,
    )
)

telegram_app.add_handler(
    CommandHandler(
        "addemoji",
        add_emoji,
    )
)

telegram_app.add_handler(
    CommandHandler(
        "removeemoji",
        remove_emoji,
    )
)

# ================= FLASK =================

@app.route("/")
def home():
    return "Bot Running"

@app.route(
    f"/{BOT_TOKEN}",
    methods=["POST"],
)
def webhook():

    try:

        update = Update.de_json(
            request.get_json(force=True),
            telegram_app.bot,
        )

        asyncio.run(
            telegram_app.process_update(
                update
            )
        )

        return "OK", 200

    except Exception as e:

        print(
            "WEBHOOK ERROR:",
            e,
        )

        return "ERROR", 500

# ================= STARTUP =================

async def startup():

    await telegram_app.initialize()

    await telegram_app.start()

    webhook_url = (
        f"{RENDER_URL}/{BOT_TOKEN}"
    )

    await telegram_app.bot.set_webhook(
        webhook_url
    )

    print(
        "Webhook:",
        webhook_url,
    )

# ================= MAIN =================

if __name__ == "__main__":

    asyncio.run(
        startup()
    )

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                10000,
            )
        ),
    )
