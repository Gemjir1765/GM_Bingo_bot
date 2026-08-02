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
        
def generate_card():

    card = {
        "B": random.sample(range(1, 16), 5),
        "I": random.sample(range(16, 31), 5),
        "N": random.sample(range(31, 46), 5),
        "G": random.sample(range(46, 61), 5),
        "O": random.sample(range(61, 76), 5)
    }

    # FREE center
    card["N"][2] = "FREE"

    return card
    async def buy_card(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id


    card = generate_card()


    if user_id not in players:

        players[user_id] = {
            "cards": []
        }


    players[user_id]["cards"].append(card)


    await update.message.reply_text(
        "🎫 Kaardiin kee qophaa'eera!\n\n"
        f"{card}"
    )
    def format_card(card):

    text = "🎫 BINGO CARD\n\n"
    text += " B     I     N     G     O\n"
    text += "-----------------------\n"

    for i in range(5):

        row = ""

        for col in ["B", "I", "N", "G", "O"]:

            row += f"{str(card[col][i]):^7}"

        text += row + "\n"

    return text
    async def buy_card(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    card = generate_card()


    if user_id not in players:

        players[user_id] = {
            "cards": []
        }


    players[user_id]["cards"].append(card)


    await update.message.reply_text(
        format_card(card)
    )
    async def admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id


    if user_id != ADMIN_ID:

        await update.message.reply_text(
            "❌ Ati admin miti."
        )

        return


    keyboard = [
        ["🎮 Start Game"],
        ["🔢 Next Number"],
        ["📊 Statistics"],
        ["📢 Broadcast"]
    ]


    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


    await update.message.reply_text(
        "👑 Admin Dashboard",
        reply_markup=reply_markup
    )
    async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id != ADMIN_ID:

        await update.message.reply_text(
            "❌ Ati admin miti."
        )

        return


    global game_running, called_numbers, winners

    game_running = True

    called_numbers.clear()

    winners.clear()


    await update.message.reply_text(
        "🎮 Taphaan Bingo jalqabameera!\n\n"
        "🔢 Lakkoofsa waamuuf qophiidha."
        
    )
    async def next_number(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id != ADMIN_ID:

        await update.message.reply_text(
            "❌ Ati admin miti."
        )

        return


    global called_numbers, game_running


    if not game_running:

        await update.message.reply_text(
            "❌ Taphaan hin jalqabamne."
        )

        return


    if len(called_numbers) >= 75:

        await update.message.reply_text(
            "✅ Lakkoofsi hundi waamameera."
        )

        return


    while True:

        number = random.randint(1, 75)

        if number not in called_numbers:

            called_numbers.append(number)

            break


    await update.message.reply_text(
        f"🔔 Lakkoofsi haaraan:\n\n"
        f"🎱 {number}\n\n"
        f"📋 Waamaman:\n{called_numbers}"
        async def check_bingo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id


    if user_id not in players:

        await update.message.reply_text(
            "❌ Jalqaba kaardii bitadhu."
        )

        return


    if len(players[user_id]["cards"]) == 0:

        await update.message.reply_text(
            "❌ Kaardii hin qabdu."
        )

        return


    card = players[user_id]["cards"][0]


    win = True


    for col in ["B", "I", "N", "G", "O"]:

        for number in card[col]:

            if number != "FREE" and number not in called_numbers:

                win = False



    if win:

        if user_id not in winners:

            winners.append(user_id)


        await update.message.reply_text(
            "🎉 BINGO!\n\n"
            "Ati injifatteerta!"
        )


    else:

        await update.message.reply_text(
            "❌ Ammaaf Bingo hin taane."
        )
    )
    async def buy_card(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id


    card = generate_card()


    if user_id not in players:

        players[user_id] = {
            "cards": []
        }


    players[user_id]["cards"].append(card)


    await update.message.reply_text(
        "🎫 Kaardii kee argatteetta!\n\n"
        f"{format_card(card)}"
    )
