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


# =========================
# GLOBAL VARIABLES
# =========================

# Admin Telegram ID
ADMIN_ID = 6602052739


# Users / Players data
players = {}


# Bingo called numbers
called_numbers = []


# Winners list
winners = []


# Game status
game_running = False


# User registration steps
user_steps = {}


# Database name
DATABASE = "bingo.db"

# =========================
# DATABASE
# =========================

def init_db():

    conn = sqlite3.connect(DATABASE)

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

    user_steps[user_id] = "name"

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
        f"{format_card(card)}"
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
def format_card(card):

    text = "🎫 BINGO CARD\n\n"

    text += " B    I    N    G    O\n"
    text += "---------------------\n"


    for i in range(5):

        row = ""

        for col in ["B", "I", "N", "G", "O"]:

            row += f"{str(card[col][i]):^5}"


        text += row + "\n"


    return text
    keyboard = [
    ["🎮 Start Game"],
    ["🔢 Next Number"],
    ["📊 Statistics"],
    ["📢 Broadcast"]
]
    async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text


    if text == "🎮 Start Game":

        await start_game(update, context)


    elif text == "🔢 Next Number":

        await next_number(update, context)


    elif text == "📊 Statistics":

        await statistics(update, context)


    elif text == "📢 Broadcast":

        await broadcast(update, context)
        async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id


    if user_id != ADMIN_ID:

        await update.message.reply_text(
            "❌ Ati admin miti."
        )

        return


    total_players = len(players)

    total_cards = 0

    for user in players:

        total_cards += len(players[user]["cards"])


    total_winners = len(winners)

    called = len(called_numbers)


    await update.message.reply_text(
        "📊 Statistics\n\n"
        f"👥 Players: {total_players}\n"
        f"🎫 Cards: {total_cards}\n"
        f"🔢 Called Numbers: {called}\n"
        f"🏆 Winners: {total_winners}"
        
    )
    async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id


    if user_id != ADMIN_ID:

        await update.message.reply_text(
            "❌ Ati admin miti."
        )

        return


    context.user_data["broadcast"] = True


    await update.message.reply_text(
        "📢 Ergaa erguuf barreessi."
    )
    async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if context.user_data.get("broadcast") != True:

        return


    message = update.message.text


    sent = 0


    for user_id in players:

        try:

            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 Beeksisa Admin:\n\n{message}"
            )

            sent += 1


        except:

            pass


    await update.message.reply_text(
        f"✅ Ergaan ergameera.\n"
        f"👥 Users: {sent}"
    )


    context.user_data.clear()
    if __name__ == "__main__":

    init_db()


    app = Application.builder().token(
        "TOKEN_KEE"
    ).build()


    # Start
    app.add_handler(
        CommandHandler("start", start)
    )


    # Buy Card
    app.add_handler(
        CommandHandler("buy", buy_card)
    )


    # Admin Dashboard
    app.add_handler(
        CommandHandler("admin", admin_dashboard)
    )


    # Admin Commands
    app.add_handler(
        CommandHandler("start_game", start_game)
    )

    app.add_handler(
        CommandHandler("next", next_number)
    )

    app.add_handler(
        CommandHandler("stats", statistics)
    )


    # Player Bingo Check
    app.add_handler(
        CommandHandler("bingo", check_bingo)
    )


    # Text Handlers
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            register_user
        )
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            admin_buttons
        )
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            send_broadcast
        )
    )


    print("🤖 Bingo Bot Started...")


    app.run_polling()
