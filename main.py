import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import os
import random
import sqlite3
import json


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
# BINGO CARD SETTINGS
# =========================

TOTAL_CARDS = 200
CARD_PRICE = 20

ADMIN_PERCENT = 30
WINNER_PERCENT = 70


def calculate_prize(total_cards):

    total_pot = total_cards * CARD_PRICE

    admin_amount = total_pot * ADMIN_PERCENT / 100
    winner_amount = total_pot * WINNER_PERCENT / 100

    return total_pot, admin_amount, winner_amount

# =========================
# DATABASE
# =========================

def init_db():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        phone TEXT,
        location TEXT
    )
    """)

    # Bingo cards table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_number INTEGER UNIQUE NOT NULL,
        card_data TEXT NOT NULL,
        status TEXT DEFAULT 'AVAILABLE',
        owner_id INTEGER
    )
    """)

    conn.commit()
    conn.close()

    create_card_pool()

def load_players_from_db():

    global players

    players.clear()

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT owner_id, card_number, card_data
        FROM cards
        WHERE status = 'SOLD'
        AND owner_id IS NOT NULL
        ORDER BY id
    """)

    rows = cursor.fetchall()

    conn.close()

    for owner_id, card_number, card_data in rows:

        card = {
            "card_number": card_number,
            "card_data": json.loads(card_data)
        }

        if owner_id not in players:
            players[owner_id] = {
                "cards": []
            }

        players[owner_id]["cards"].append(card)

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

        conn = sqlite3.connect(DATABASE)
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
            "🎫 Kaardii Bingo filachuuf qophiidha."
        )

        keyboard = [
            ["🎫 Filadhu"]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(
            "🎫 Kaardii Bingo filadhu:",
            reply_markup=reply_markup
        )

        context.user_data.clear()
        return
        
             
    
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
    
def create_card_pool():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Yoo cards duraan uumamanii jiran, irra deebinee hin uumin
    cursor.execute("SELECT COUNT(*) FROM cards")

    count = cursor.fetchone()[0]

    if count >= TOTAL_CARDS:
        conn.close()
        return

    used_numbers = set()

    cursor.execute("SELECT card_number FROM cards")

    existing_numbers = cursor.fetchall()

    for row in existing_numbers:
        used_numbers.add(row[0])

    while count < TOTAL_CARDS:
         card_number = count + 1
        if card_number in used_numbers:
            continue

        used_numbers.add(card_number)

        card = generate_card()

        card_data = json.dumps(card)

        cursor.execute(
            """
            INSERT INTO cards
            (card_number, card_data, status, owner_id)
            VALUES (?, ?, 'AVAILABLE', NULL)
            """,
            (
                card_number,
                card_data
            )
        )

        count += 1

    conn.commit()
    conn.close()
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
    )
async def check_bingo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not game_running:
        await update.message.reply_text(
            "❌ Amma taphaan hin jalqabamne."
        )
        return

    if user_id not in players:
        await update.message.reply_text(
            "❌ Jalqaba kaardii bitadhu."
        )
        return

    cards = players[user_id].get("cards", [])

    if not cards:
        await update.message.reply_text(
            "❌ Kaardii hin qabdu."
        )
        return

    winning_cards = []

    for card in cards:

        card_data = card["card_data"]

        win = True

        for col in ["B", "I", "N", "G", "O"]:

            for number in card_data[col]:

                if number != "FREE" and number not in called_numbers:
                    win = False
                    break

            if not win:
                break

        if win:
            winning_cards.append(card)

    if winning_cards:

        if user_id not in winners:
            winners.append(user_id)

        card_numbers = [
            str(card["card_number"])
            for card in winning_cards
        ]

        await update.message.reply_text(
            "🎉 BINGO!\n\n"
            f"🏆 Kaardiiwwan mo'atan: "
            f"{', '.join(card_numbers)}\n\n"
            "Ati injifatteerta! 🏆"
        )

    else:

        await update.message.reply_text(
            "❌ Ammaaf Bingo hin taane."
        )
async def buy_card(update: Update, context: ContextTypes.DEFAULT_TYPE):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT card_number, status
        FROM cards
        ORDER BY card_number ASC
    """)

    cards = cursor.fetchall()

    conn.close()

    if not cards:
        await update.message.reply_text(
            "❌ Kaardiiwwan hin argamne."
        )
        return

    keyboard = []
    row = []

    for card_number, status in cards:

        if status == "AVAILABLE":
            button = f"🎫 {card_number}"
        else:
            button = f"🔴 {card_number}"

        row.append(button)

        if len(row) == 5:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🎫 GM BINGO\n\n"
        "Kaardii barbaaddan filadhaa.\n"
        "🟢 Kaardii bana = bitamuu danda'a\n"
        "🔴 Kaardii gurgurame = hin filatamu\n\n"
        f"💵 Gatii: {CARD_PRICE} Birr",
        reply_markup=reply_markup
    )


async def show_selected_card(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if not text.startswith("🎫 "):
        return

    try:
        card_number = int(text.replace("🎫 ", "").strip())
    except ValueError:
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT card_data, status
        FROM cards
        WHERE card_number = ?
        """,
        (card_number,)
    )

    result = cursor.fetchone()

    conn.close()

    if result is None:
        await update.message.reply_text(
            "❌ Kaardii kana hin argamne."
        )
        return

    card_data, status = result

    if status != "AVAILABLE":
        await update.message.reply_text(
            "❌ Kaardii kun yeroo ammaa nama biraatiif qabameera "
            "ykn gurgurameera."
        )
        return

    card = json.loads(card_data)

    keyboard = [
        [f"💳 Card #{card_number} — {CARD_PRICE} Birr"],
        ["⬅️ Deebi'i"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    # Card number filatame temporary keessatti kuusi
    context.user_data["selected_card"] = card_number

    await update.message.reply_text(
        f"🎫 GM BINGO\n\n"
        f"🔢 Card Number: {card_number}\n\n"
        f"{format_card(card)}\n"
        f"💵 Gatii: {CARD_PRICE} Birr\n\n"
        "👇 Kaardii kana bitachuuf button armaan gadii tuqi.",
        reply_markup=reply_markup
    )
    
async def reserve_card(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    card_number = context.user_data.get("selected_card")

    if card_number is None:
        await update.message.reply_text(
            "❌ Jalqaba kaardii filadhu."
        )
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT card_data, status
        FROM cards
        WHERE card_number = ?
        """,
        (card_number,)
    )

    result = cursor.fetchone()

    if result is None:
        conn.close()
        await update.message.reply_text(
            "❌ Kaardii hin argamne."
        )
        return

    card_data, status = result

    if status != "AVAILABLE":
        conn.close()
        await update.message.reply_text(
            "❌ Kaardii kun duraan qabameera ykn gurgurameera."
        )
        return

    # DEMO MODE keessatti kallattiin SOLD goona
    cursor.execute(
        """
        UPDATE cards
        SET status = 'SOLD',
            owner_id = ?
        WHERE card_number = ?
        AND status = 'AVAILABLE'
        """,
        (user_id, card_number)
    )

    conn.commit()

    changed = cursor.rowcount

    conn.close()

    if changed == 0:
        await update.message.reply_text(
            "❌ Kaardii kana namni biraa dursee fudhateera."
        )
        return

    card = {
    "card_number": card_number,
    "card_data": json.loads(card_data)
}

if user_id not in players:
    players[user_id] = {
        "cards": []
    }

players[user_id]["cards"].append(card)

    await update.message.reply_text(
        f"✅ DEMO PAYMENT MILKAA'E!\n\n"
        f"🎫 Card #{card_number}\n"
        f"💵 Gatii: {CARD_PRICE} Birr\n\n"
        f"{format_card(card)}\n\n"
        "🎮 Kaardii kanaan taphaachuu dandeessa."
    )

    context.user_data.pop("selected_card", None)
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

total_pot, admin_amount, winner_amount = calculate_prize(total_cards)

total_winners = len(winners)
called = len(called_numbers)
await update.message.reply_text(
    "📊 Statistics\n\n"
    f"👥 Players: {total_players}\n"
    f"🎫 Cards: {total_cards}\n"
    f"💵 Card Price: {CARD_PRICE} Birr\n"
    f"💰 Total Pot: {total_pot} Birr\n"
    f"🏆 Winner Pool (70%): {winner_amount} Birr\n"
    f"👑 Admin Share (30%): {admin_amount} Birr\n"
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

    text = update.message.text

    sent = 0

    for user_id in players:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 Beeksisa Admin:\n\n{text}"
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

    load_players_from_db()

    TOKEN = os.environ["BOT_TOKEN"]

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("buy", buy_card)
    )

    app.add_handler(
        CommandHandler("admin", admin_dashboard)
    )

    app.add_handler(
        CommandHandler("start_game", start_game)
    )

    app.add_handler(
        CommandHandler("next", next_number)
    )

    app.add_handler(
        CommandHandler("stats", statistics)
    )

    app.add_handler(
        CommandHandler("bingo", check_bingo)
    )

    app.add_handler(
    MessageHandler(
        filters.Regex("^🎫 Filadhu$"),
        buy_card
    )
)

app.add_handler(
    MessageHandler(
        filters.Regex(r"^🎫 \d+$"),
        show_selected_card

        app.add_handler(
    MessageHandler(
        filters.Regex(r"^💳 Card #\d+ — \d+ Birr$"),
        reserve_card        
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        register_user
    )
)

    print("🤖 Bingo Bot Started...")

    app.run_polling()
