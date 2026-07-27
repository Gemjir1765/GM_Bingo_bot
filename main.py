from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "7680436212:AAGekyAeVrMyMcJI0BSWV5NUzuF9NthlJLk"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 Baga nagaan dhuftan gara GM Bingo!"
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

print("GM Bingo Bot started...")
app.run_polling()
