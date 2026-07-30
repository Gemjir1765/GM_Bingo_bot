
import json
import os
import random
import logging

from telegram import (
Update,
InlineKeyboardButton,
InlineKeyboardMarkup,
ReplyKeyboardMarkup,
KeyboardButton
)

from telegram.ext import (
ApplicationBuilder,
CommandHandler,
CallbackQueryHandler,
MessageHandler,
ConversationHandler,
ContextTypes,
filters
)

# ==========================
# BOT SETTINGS
#==========================

import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6602052739


#==========================
# PAYMENT SETTINGS
#==========================

ADMIN_COMMISSION_PERCENT = 30


logging.basicConfig(
format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
level=logging.INFO,
)

logger = logging.getLogger(__name__)

#==========================
# FILES
#==========================

USERS_FILE = "users.json"
GAME_FILE = "game.json"

#==========================
#CONVERSATION STATES
#==========================

LANGUAGE = 0
FULL_NAME = 1
PHONE = 2
LOCATION = 3
#==========================
#JSON FUNCTIONS
#==========================

def load_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


#==========================
#LOAD DATA
#==========================

users = load_json(USERS_FILE)
game = load_json(GAME_FILE)


#==========================
#DEFAULT GAME DATA
#==========================

if not game:
   game = {
     "started": False,
     "numbers": [],
     "called_numbers": [],
     "winner": None
}

save_json(GAME_FILE, game)
#==========================
#START COMMAND
#==========================

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
        "🌍 Please choose your language.\n\n"
        "Mee afaan filadhu.\n\n"
        "እባክዎ ቋንቋ ይምረጡ።",
        reply_markup=reply_markup
    )

    return LANGUAGE


#==========================
#LANGUAGE CALLBACK
#==========================

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    language = query.data

    context.user_data["language"] = language

    if language == "or":
        text = (
            "✅ Afaan Oromoo filatte.\n\n"
            "📝 Mee maqaa guutuu kee barreessi:"
        )

    elif language == "en":
        text = (
            "✅ English selected.\n\n"
            "📝 Please enter your full name:"
        )

    else:
        text = (
            "✅ አማርኛ ተመርጧል።\n\n"
            "📝 እባክዎ ሙሉ ስምዎን ያስገቡ።"
        )

    await query.message.reply_text(text)

    return FULL_NAME

#==========================
# FULL NAME
#==========================

async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    full_name = update.message.text.strip()

    context.user_data["full_name"] = full_name

    user_id = str(update.effective_user.id)

    if user_id not in users:
        users[user_id] = {}

    users[user_id]["telegram_id"] = update.effective_user.id
    users[user_id]["username"] = update.effective_user.username
    users[user_id]["full_name"] = full_name
    users[user_id]["language"] = context.user_data["language"]

    save_json(USERS_FILE, users)

    language = context.user_data["language"]

    keyboard = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(
                    "📱 Share Phone Number",
                    request_contact=True
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    if language == "or":
        text = "📱 Mee lakkoofsa bilbilaa kee Share Phone Number jedhu tuquun ergi."

    elif language == "en":
        text = "📱 Please tap Share Phone Number to send your phone number."

    else:
        text = "📱 እባክዎ Share Phone Number በመጫን ስልክ ቁጥርዎን ይላኩ።"

    await update.message.reply_text(
        text,
        reply_markup=keyboard
    )

    return PHONE

#==========================
#PHONE NUMBER
#==========================

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):

    contact = update.message.contact

    if contact is None:
        await update.message.reply_text(
            "❌ Please use the Share Phone Number button."
        )
        return PHONE

    user_id = str(update.effective_user.id)

    users[user_id]["phone"] = contact.phone_number

    save_json(USERS_FILE, users)

    language = context.user_data["language"]

    keyboard = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(
                    "📍 Share Location",
                    request_location=True
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    if language == "or":
        text = "📍 Mee Share Location jedhu tuquun iddoo kee ergi."

    elif language == "en":
        text = "📍 Please tap Share Location to send your location."

    else:
        text = "📍 እባክዎ Share Location በመጫን አካባቢዎን ይላኩ።"

    await update.message.reply_text(
        text,
        reply_markup=keyboard
    )

    return LOCATION

#==========================
#LOCATION
#==========================

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.text.strip()
    if location is None:
        await update.message.reply_text(
            "❌ Please use the Share Location button."
        )
        return LOCATION

    user_id = str(update.effective_user.id)
    users[user_id]["location"] = location
    
    users[user_id]["registered"] = True

    save_json(USERS_FILE, users)

    language = context.user_data["language"]

    if language == "or":
        text = (
            "✅ Galmeen kee milkaa'eera.\n\n"
            "🎉 Gara tapha GM Bingo baga nagaan dhuftan!"
        )

    elif language == "en":
        text = (
            "✅ Registration completed successfully.\n\n"
            "🎉 Welcome to GM Bingo!"
        )

    else:
        text = (
            "✅ ምዝገባዎ በተሳካ ሁኔታ ተጠናቋል።\n\n"
            "🎉 ወደ GM Bingo እንኳን በደህና መጡ!"
        )

    await update.message.reply_text(text)

    # Kaardii Bingo uumuuf
    # await generate_bingo_card(update, context)

    return ConversationHandler.END

#==========================
#BINGO CARD
#==========================

def generate_card():
    card = {
        "B": random.sample(range(1, 16), 5),
        "I": random.sample(range(16, 31), 5),
        "N": random.sample(range(31, 46), 5),
        "G": random.sample(range(46, 61), 5),
        "O": random.sample(range(61, 76), 5)
    }

    card["N"][2] = "FREE"

    return card


def format_card(card):
    text = "🎲 GM BINGO CARD\n\n"
    text += " B I N G O\n\n"

    for i in range(5):
        row = []

        for col in ["B", "I", "N", "G", "O"]:
            value = card[col][i]

            if value == "FREE":
                row.append("FREE")
            else:
                row.append(f"{value:02}")

        text += " | ".join(row) + "\n"

    return text

async def generate_bingo_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    card = generate_card()

    users[user_id]["card"] = card

    save_json(USERS_FILE, users)

    await update.message.reply_text(
        format_card(card)
    )


#==========================
# GAME FUNCTIONS
#==========================

def new_game():
    numbers = list(range(1, 76))
    random.shuffle(numbers)

    game["started"] = True
    game["numbers"] = numbers
    game["called_numbers"] = []
    game["winner"] = None

    save_json(GAME_FILE, game)

async def call_next_number(context: ContextTypes.DEFAULT_TYPE):
    if not game["started"]:
        return

    if len(game["numbers"]) == 0:
        game["started"] = False
        save_json(GAME_FILE, game)
        return

    number = game["numbers"].pop(0)

    game["called_numbers"].append(number)

    save_json(GAME_FILE, game)

    users_data = load_json(USERS_FILE)

    for user_id in users_data:
        try:
            await context.bot.send_message(
                chat_id=int(user_id),
                text=f"🎲 New Number: {number}"
            )

        except Exception:
            pass

#==========================
#ADMIN COMMANDS
#==========================

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    new_game()

    await update.message.reply_text(
        "✅ GM Bingo game started."
    )


async def next_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await call_next_number(context)

    await update.message.reply_text(
        "✅ Next number sent."
    )

#==========================
#CHECK BINGO LINES
#==========================

def count_winning_lines(card, called_numbers):
    lines = []

    # Horizontal
    for row in range(5):
        line = []

        for col in ["B", "I", "N", "G", "O"]:
            line.append(card[col][row])

        lines.append(line)

    # Vertical
    for col in ["B", "I", "N", "G", "O"]:
        lines.append(card[col])

    # Diagonal 1
    diagonal1 = []
    for i, col in enumerate(["B", "I", "N", "G", "O"]):
        diagonal1.append(card[col][i])

    lines.append(diagonal1)

    # Diagonal 2
    diagonal2 = []
    for i, col in enumerate(["O", "G", "N", "I", "B"]):
        diagonal2.append(card[col][i])

    lines.append(diagonal2)

    completed = 0

    for line in lines:
        ok = True

        for number in line:
            if number != "FREE" and number not in called_numbers:
                ok = False
                break

        if ok:
            completed += 1

    return completed

#==========================
#BINGO CLAIM
#==========================
async def claim_bingo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in users:
        await update.message.reply_text(
            "❌ You are not registered."
        )
        return

    if game["winner"] is not None:
        await update.message.reply_text(
            "🏆 This round is already finished."
        )
        return

    card = users[user_id].get("card")

    if not card:
        await update.message.reply_text(
            "❌ You don't have a Bingo card."
        )
        return

    called_numbers = game["called_numbers"]

    winning_lines = count_winning_lines(
        card,
        called_numbers
    )

    if winning_lines >= 2:

        if "winners" not in game:
            game["winners"] = []

        game["winners"].append({
            "user_id": user_id,
            "name": users[user_id]["full_name"],
            "lines": winning_lines
        })

        game["winner"] = user_id

        save_json(GAME_FILE, game)

        await update.message.reply_text(
            "🎉 CONGRATULATIONS!\n\n"
            "✅ You created two winning lines.\n"
            "🏆 You are a winner!"
        )

    else:

        await update.message.reply_text(
            f"❌ Not yet.\n"
            f"You have {winning_lines} winning line(s).\n"
            "You need 2 lines to win."
        )


#==========================
#PRIZE CALCULATION
#==========================

def calculate_prize(total_amount):
    admin_fee = (
        total_amount *
        ADMIN_COMMISSION_PERCENT /
        100
    )

    prize_pool = total_amount - admin_fee

    return admin_fee, prize_pool


def divide_prize(prize_pool, winners):
    if len(winners) == 0:
        return []

    each_prize = prize_pool / len(winners)

    results = []

    for winner in winners:
        results.append({
            "user_id": winner["user_id"],
            "name": winner["name"],
            "amount": each_prize
        })

    return results

#==========================
#FINISH ROUND
#==========================
async def finish_round(context, total_amount):
    winners = game.get("winners", [])

    if not winners:
        return

    admin_fee, prize_pool = calculate_prize(
        total_amount
    )

    prizes = divide_prize(
        prize_pool,
        winners
    )

    message = "🏆 GM Bingo Winners\n\n"

    for item in prizes:
        message += (
            f"🥇 {item['name']}\n"
            f"💰 Prize: {item['amount']}\n\n"
        )

    message += (
        f"👑 Admin Commission: {admin_fee}\n"
        f"🎁 Total Prize Pool: {prize_pool}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=message
    )

#==========================
#WINNERS MANAGEMENT
#==========================

def add_winner(user_id):
    if "winners" not in game:
        game["winners"] = []

    # Namni tokko yeroo lama akka hin galmoofne
    for winner in game["winners"]:
        if winner["user_id"] == user_id:
            return False

    game["winners"].append({
        "user_id": user_id,
        "name": users[user_id]["full_name"]
    })

    save_json(GAME_FILE, game)

    return True


#==========================
#NEW ROUND
#==========================

def reset_round():
    game["started"] = False
    game["numbers"] = []
    game["called_numbers"] = []
    game["winners"] = []

    save_json(GAME_FILE, game)


#==========================
# ANNOUNCE WINNERS
#==========================

async def announce_winners(context):
    winners = game.get("winners", [])

    if not winners:
        return

    text = "🏆 GM Bingo Winners\n\n"

    for index, winner in enumerate(winners, start=1):
        text += (
            f"{index}. {winner['name']}\n"
        )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text
    )


#==========================
# MAIN BOT SETUP
#==========================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Operation cancelled."
    )

    return ConversationHandler.END

def main():
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )



# Registration Conversation

    conv_handler = ConversationHandler(

        entry_points=[
            CommandHandler(
                "start",
                start
            )
        ],

        states={

            LANGUAGE: [
                CallbackQueryHandler(
                    language_callback
                )
            ],

            FULL_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_full_name
                )
            ],

            PHONE: [
                MessageHandler(
                    filters.CONTACT,
                    get_phone
                )
            ],

            LOCATION: [
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        get_location
    )
]
                )
            ]
        },

        fallbacks=[
            CommandHandler(
                "cancel",
                cancel
            )
        ]
    )


    # User handlers

    app.add_handler(conv_handler)

    app.add_handler(
        CommandHandler(
            "bingo",
            claim_bingo
        )
    )


    # Admin handlers

    app.add_handler(
        CommandHandler(
            "start_game",
            start_game
        )
    )

    app.add_handler(
        CommandHandler(
            "next",
            next_number
        )
    )


    print("GM Bingo Bot started...")


    app.run_polling()


if __name__ == "__main__":
    main()
