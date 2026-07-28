ADMIN_ID = 6602052739

game_active = False
players = []
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "7680436212:AAGekyAeVrMyMcJI0BSWV5NUzuF9NthlJLk"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton("🇪🇹 Afaan Oromoo", callback_data="or"),
            InlineKeyboardButton("🇬🇧 English", callback_data="en")
        ],
        [
            InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="am")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎉 Baga nagaan dhuftan gara GM Bingo!\n\n"
        "Afaan filadhu:",
        reply_markup=reply_markup)


async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "or":
        text = "Ati Afaan Oromoo filatte. 🎲"
    elif query.data == "en":
        text = "You selected English. 🎲"
    else:
        text = "Ati Afaan Amaaraa filatte. 🎲"

    await query.edit_message_text(text)


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(language))

print("GM Bingo Bot started...")
app.run_polling()
def is_admin(user_id):
    return user_id == ADMIN_ID


async def startgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global game_active, players

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin qofa.")
        return

    if game_active:
        await update.message.reply_text("⚠️ Game banameera.")
        return

    game_active = True
    players = []

    await update.message.reply_text(
        "🎱 GM Bingo game jalqabameera!"
    )


async def stopgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global game_active

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin qofa.")
        return

    game_active = False

    await update.message.reply_text(
        "🛑 Game dhaabbateera."
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if game_active:
        await update.message.reply_text(
            f"🎮 Game banaadha\n👥 Players: {len(players)}"
        )
    else:
        await update.message.reply_text(
            "⚪ Game hin jalqabamne."
        )
        app.add_handler(CommandHandler("startgame", startgame))
app.add_handler(CommandHandler("stopgame", stopgame))
app.add_handler(CommandHandler("status", status))
