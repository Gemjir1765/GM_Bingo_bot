from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import random
import sqlite3
# Game Variables

players = {}

called_numbers = []

winners = []

game_running = False
def init_db():

    conn = sqlite3.connect("bingo.db")

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        phone TEXT,
        location TEXT
    )
    """)

    conn.commit()

    conn.close()
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    await update.message.reply_text(
        "👋 Baga nagaan dhuftan!\n\n"
        "Maqaa keessan barreessaa."
    )

    context.user_data["step"] = "name"
    async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    text = update.message.text


    if context.user_data.get("step") == "name":

        context.user_data["name"] = text

        context.user_data["step"] = "phone"

        await update.message.reply_text(
            "📱 Lakkoofsa bilbilaa keessan galchaa."
        )

        return


    if context.user_data.get("step") == "phone":

        context.user_data["phone"] = text

        context.user_data["step"] = "location"

        await update.message.reply_text(
            "📍 Bakka jiraattan galchaa."
        )

        return


    if context.user_data.get("step") == "location":

        context.user_data["location"] = text


        conn = sqlite3.connect("bingo.db")

        cursor = conn.cursor()


        cursor.execute(
            """
            INSERT OR REPLACE INTO users
            (user_id, name, phone, location)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                context.user_data["name"],
                context.user_data["phone"],
                context.user_data["location"]
            )
        )


        conn.commit()
        conn.close()


        await update.message.reply_text(
            "✅ Galmeen keessan xumurameera!\n\n"
            "🎮 Taphachuu jalqabuuf qophiidha."
        )


        context.user_data.clear()
