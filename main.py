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
