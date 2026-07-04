import os
import random
import asyncio
from flask import Flask, request
from telegram import Update, ReactionTypeEmoji
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

app = Flask(__name__)

telegram_app = Application.builder().token(BOT_TOKEN).build()

# Random emoji reactions
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

async def show_emojis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Current reactions:\n\n" + " ".join(EMOJIS)
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

async def add_emoji(update, context):

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

async def remove_emoji(update, context):

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

# ================= REAL MESSAGE REACTION =================

async def auto_reaction(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.message:
        return

    try:

        # Commands ignore
        if (
            update.message.text
            and update.message.text.startswith("/")
        ):
            return

        emoji = random.choice(EMOJIS)

        await context.bot.set_message_reaction(
            chat_id=update.effective_chat.id,
            message_id=update.message.message_id,
            reaction=[
                ReactionTypeEmoji(
                    emoji=emoji
                )
            ],
        )

        print(
            "REACTION:",
            emoji,
        )

    except Exception as e:

        print(
            "REACTION ERROR:",
            e,
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

telegram_app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        auto_reaction,
    )
)

# ================= FLASK =================

@app.route("/")
def home():
    return "Auto Reaction Bot Running"

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

    await telegram_app.bot.set_webhook(
        f"{RENDER_URL}/{BOT_TOKEN}"
    )

    print("Webhook set!")

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
