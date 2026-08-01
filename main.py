
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

# Kaardii Bingo uumuuf
# await generate_bingo_card(update, context)

return ConversationHandler.END
keyboard = [
    ["🎫 Buy Card", "💰 Wallet"],
    ["🎮 My Cards", "🏆 Winners"],
    ["💸 Withdraw", "⚙️ Settings"],
    ["📞 Support"]
]

reply_markup = ReplyKeyboardMarkup(
    keyboard,
    resize_keyboard=True,
    one_time_keyboard=False
)

await update.message.reply_text(
    text,
    reply_markup=reply_markup
)

# Kaardii Bingo uumuuf
# await generate_bingo_card(update, context)

return ConversationHandler.END

# Kaardii Bingo uumuuf
# await generate_bingo_card(update, context)

return ConversationHandler.END


#==========================
# BUY CARD
#==========================
async def buy_card(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🎫 Buy Card\n\n"
        "Kaardii Bingo filachuuf qophaa'i"
    )

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

    await update.message.reply_text(
        text,
        reply_markup=reply_markup
    )

async def buy_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎫 Kaardii Bingo filachuuf qophaa'aa...\n\n"
        "Amma sirna kaardii 400 itti aanu irratti ijaarra."
    )
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
async def buy_card(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["1 Card"],
        ["2 Cards"],
        ["3 Cards"],
        ["5 Cards"],
        ["🔙 Back"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🎫 Buy Bingo Card\n\n"
        "Mee baay'ina kaardii barbaaddu filadhu.",
        reply_markup=reply_markup
    )
async def card_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):

    choice = update.message.text

    prices = {
        "1 Card": 10,
        "2 Cards": 20,
        "3 Cards": 30,
        "5 Cards": 50
    }

    if choice not in prices:
        return

    amount = prices[choice]

    context.user_data["card_quantity"] = choice
    context.user_data["card_price"] = amount

    await update.message.reply_text(
        f"🎫 Filannoo kee:\n\n"
        f"Kaardii: {choice}\n"
        f"Gatii: {amount} birr\n\n"
        "Kaffaltii erga gootee booda proof/payment ragaa ergi."
    )


ADMIN_ID = 6602052739


async def payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):

proof = update.message.text

quantity = context.user_data.get("card_quantity")
amount = context.user_data.get("card_price")

if not quantity or not amount:
await update.message.reply_text(
"❌ Dura kaardii filadhu."
)
return

user = update.effective_user

message = (
"💳 New Card Purchase Request\n\n"
f"👤 User: {user.full_name}\n"
f"🆔 ID: {user.id}\n"
f"🎫 Card: {quantity}\n"
f"💰 Amount: {amount} birr\n\n"
f"🧾 Payment Proof:\n{proof}"
)

await context.bot.send_message(
chat_id=ADMIN_ID,
text=message
)

await update.message.reply_text(
"✅ Kaffaltiin kee ergameera.\n"
"Admin mirkaneessu eegaa."
)
async def admin_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):

query = update.callback_query
await query.answer()

data = query.data

user_id = data.split("_")[2]

if data.startswith("approve"):
await context.bot.send_message(
chat_id=int(user_id),
text=(
"✅ Kaffaltiin kee mirkanaa'eera.\n\n"
"🎫 Kaardiin kee qophaa'aa jira."
)
)

await query.edit_message_text(
"✅ Payment Approved"
)

elif data.startswith("reject"):

await context.bot.send_message(
chat_id=int(user_id),
text=(
"❌ Kaffaltiin kee hin mirkanoofne.\n"
"Mee irra deebi'i."
)
)

await query.edit_message_text(
"❌ Payment Rejected"
)
keyboard = [
[
InlineKeyboardButton(
"✅ Approve",
callback_data=f"approve_{user.id}"
),
InlineKeyboardButton(
"❌ Reject",
callback_data=f"reject_{user.id}"
)
 ]
]

reply_markup = InlineKeyboardMarkup(keyboard)

await context.bot.send_message(
chat_id=ADMIN_ID,
text=message,
reply_markup=reply_markup
)
import random


def generate_card():

card = {
"B": random.sample(range(1, 16), 5),
"I": random.sample(range(16, 31), 5),
"N": random.sample(range(31, 46), 5),
"G": random.sample(range(46, 61), 5),
"O": random.sample(range(61, 76), 5)
}

return card


def format_card(card):

text = "🎫 Your Bingo Card\n\n"

text += " B I N G O\n"

for i in range(5):
row = (
f"{card['B'][i]} "
f"{card['I'][i]} "
f"{card['N'][i]} "
f"{card['G'][i]} "
f"{card['O'][i]}"
)

text += row + "\n"

return text
async def my_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):

user_id = update.effective_user.id

cards = user_cards.get(user_id, [])

if not cards:
await update.message.reply_text(
"❌ Ati amma kaardii hin qabdu."
)
return

text = "🎫 Kaardiiwwan kee:\n\n"

for index, card in enumerate(cards, start=1):

text += f"===== Card {index} =====\n"
text += format_card(card)
text += "\n"

await update.message.reply_text(text)
def create_wallet(user_id):

if user_id not in user_wallet:
user_wallet[user_id] = 0

if user_id not in payment_history:
payment_history[user_id] = []
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

user_id = update.effective_user.id

create_wallet(user_id)

amount = user_wallet[user_id]

await update.message.reply_text(
f"💰 Balance kee:\n\n"
f"{amount} birr"
)
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):

user_id = update.effective_user.id

create_wallet(user_id)

balance_amount = user_wallet[user_id]

if balance_amount <= 0:
await update.message.reply_text(
"❌ Balance kee gahaa miti."
)
return

await update.message.reply_text(
f"💸 Withdraw Request\n\n"
f"Balance kee: {balance_amount} birr\n\n"
"Mee qarshii meeqa baasuu akka barbaaddu barreessi."
)

context.user_data["withdraw_step"] = True
async def withdraw_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):

if not context.user_data.get("withdraw_step"):
return

user_id = update.effective_user.id

amount = int(update.message.text)

if amount > user_wallet.get(user_id, 0):

await update.message.reply_text(
"❌ Balance kee caala."
)
return


withdraw_requests[user_id] = {
"amount": amount,
"status": "pending"
}


await context.bot.send_message(
chat_id=ADMIN_ID,
text=(
"💸 New Withdraw Request\n\n"
f"User ID: {user_id}\n"
f"Amount: {amount} birr\n\n"
"Approve ykn Reject godhi."
)
)


await update.message.reply_text(
"✅ Withdraw request ergameera.\n"
"Admin mirkaneessa."
)

context.user_data["withdraw_step"] = False

async def admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):

user_id = update.effective_user.id

if not is_admin(user_id):
await update.message.reply_text(
"❌ Ati admin miti."
)
return


keyboard = [
["📊 Statistics"],
["💸 Withdraw Requests"],
["🎮 Start Game"],
["🔢 Next Number"],
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
async def admin_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):

if not is_admin(update.effective_user.id):
return


users = len(user_wallet)

cards = sum(
len(value)
for value in user_cards.values()
)


await update.message.reply_text(
"📊 GM Bingo Statistics\n\n"
f"👥 Users: {users}\n"
f"🎫 Cards: {cards}"
)
async def view_withdraw_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):

if not is_admin(update.effective_user.id):
return

if not withdraw_requests:

await update.message.reply_text(
"✅ Withdraw request hin jiru."
)
return


text = "💸 Pending Withdraw Requests\n\n"

keyboard = []


for user_id, data in withdraw_requests.items():

if data["status"] == "pending":

text += (
f"👤 User: {user_id}\n"
f"💰 Amount: {data['amount']} birr\n\n"
)

keyboard.append(
[
InlineKeyboardButton(
"✅ Approve",
callback_data=f"withdraw_ok_{user_id}"
),
InlineKeyboardButton(
"❌ Reject",
callback_data=f"withdraw_no_{user_id}"
)
 ]
)


reply_markup = InlineKeyboardMarkup(keyboard)


await update.message.reply_text(
text,
reply_markup=reply_markup
)
async def withdraw_action(update: Update, context: ContextTypes.DEFAULT_TYPE):

query = update.callback_query

await query.answer()

data = query.data

user_id = int(data.split("_")[2])


if data.startswith("withdraw_ok"):

amount = withdraw_requests[user_id]["amount"]

user_wallet[user_id] -= amount

withdraw_requests[user_id]["status"] = "approved"


await context.bot.send_message(
chat_id=user_id,
text=(
"✅ Withdraw kee mirkanaa'eera.\n\n"
f"💰 Amount: {amount} birr"
)
)


await query.edit_message_text(
"✅ Withdraw Approved"
)


elif data.startswith("withdraw_no"):

withdraw_requests[user_id]["status"] = "rejected"


await context.bot.send_message(
chat_id=user_id,
text="❌ Withdraw request kee diddatameera."
)


await query.edit_message_text(
"❌ Withdraw Rejected"
)

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

if not is_admin(update.effective_user.id):
return

broadcast_mode[update.effective_user.id] = True

await update.message.reply_text(
"📢 Ergaa users hundaaf ergamu barreessi."
)
async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):

admin_id = update.effective_user.id

if not broadcast_mode.get(admin_id):
return


message = update.message.text


for user_id in user_wallet.keys():

try:
await context.bot.send_message(
chat_id=user_id,
text=(
"📢 GM Bingo Message\n\n"
f"{message}"
)
)

except:
pass


broadcast_mode[admin_id] = False


await update.message.reply_text(
"✅ Message users hundaaf ergameera."
)
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):

global game_active, called_numbers

if not is_admin(update.effective_user.id):
return


game_active = True
called_numbers = []


await update.message.reply_text(
"🎮 Bingo Game Started!"
)
async def next_number(update: Update, context: ContextTypes.DEFAULT_TYPE):

global called_numbers


if not is_admin(update.effective_user.id):
return


if not game_active:

await update.message.reply_text(
"❌ Game hin jalqabne."
)
return


available = [
n for n in range(1,76)
if n not in called_numbers
 ]


if not available:
await update.message.reply_text(
"Game xumurameera."
)
return


number = random.choice(available)

called_numbers.append(number)


for user_id in user_wallet.keys():

try:
await context.bot.send_message(
chat_id=user_id,
text=f"🔢 Number Called: {number}"
)

except:
pass
async def claim_bingo(update: Update, context: ContextTypes.DEFAULT_TYPE):

user_id = update.effective_user.id

if not game_active:

await update.message.reply_text(
"❌ Game amma hin jirre."
)
return


cards = user_cards.get(user_id, [])


if not cards:

await update.message.reply_text(
"❌ Ati kaardii hin qabdu."
)
return


for card in cards:

card_numbers = []

for column in card.values():
card_numbers.extend(column)


if all(
number in called_numbers
for number in card_numbers
):

if user_id not in winners:

winners.append(user_id)


create_wallet(user_id)

user_wallet[user_id] += WINNER_PRIZE


await update.message.reply_text(
"🎉 BINGO WINNER!\n\n"
f"🏆 Prize: {WINNER_PRIZE} birr\n"
"💰 Gara wallet keetti galeera."
)


await context.bot.send_message(
chat_id=ADMIN_ID,
text=(
"🏆 New Winner!\n\n"
f"User ID: {user_id}\n"
f"Prize: {WINNER_PRIZE} birr"
)
)

return


await update.message.reply_text(
"❌ Amma Bingo hin xumurre."
)
def create_database():

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
user_id INTEGER PRIMARY KEY,
name TEXT,
phone TEXT,
location TEXT,
balance INTEGER DEFAULT 0
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS cards(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
card TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
type TEXT,
amount INTEGER,
status TEXT
)
""")


conn.commit()
def save_user(user_id, name, phone, location):

cursor.execute(
"""
INSERT OR IGNORE INTO users
(user_id,name,phone,location)
VALUES (?,?,?,?)
""",
(
user_id,
name,
phone,
location
)
)

conn.commit()
def save_card(user_id, card):

card_data = json.dumps(card)

cursor.execute(
"""
INSERT INTO cards
(user_id, card)
VALUES (?,?)
""",
(
user_id,
card_data
)
)

conn.commit()
def get_user_cards(user_id):

cursor.execute(
"""
SELECT card FROM cards
WHERE user_id=?
""",
(user_id,)
)

rows = cursor.fetchall()

cards = []

for row in rows:
cards.append(
json.loads(row[0])
)

return cards
def get_balance(user_id):

cursor.execute(
"""
SELECT balance FROM users
WHERE user_id=?
""",
(user_id,)
)

result = cursor.fetchone()

if result:
return result[0]

return 0
def update_balance(user_id, amount):

cursor.execute(
"""
UPDATE users
SET balance = balance + ?
WHERE user_id=?
""",
(
amount,
user_id
)
)

conn.commit()
#==========================
ADMIN GAME CONTROL
#==========================

game_status = False
called_numbers = []


async def admin_start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):

global game_status
global called_numbers
global winners

if update.effective_user.id != ADMIN_ID:
return

game_status = True
called_numbers.clear()
winners.clear()

await update.message.reply_text(
"🎮 Taphaan Bingo jalqabe!\n\n"
"Lakkoofsi haaraan amma keessaa bahuu danda'a."
)


async def admin_stop_game(update: Update, context: ContextTypes.DEFAULT_TYPE):

global game_status

if update.effective_user.id != ADMIN_ID:
return

game_status = False

await update.message.reply_text(
"🛑 Taphaan Bingo dhaabbate."
)


async def admin_game_status(update: Update, context: ContextTypes.DEFAULT_TYPE):

if update.effective_user.id != ADMIN_ID:
return

status = "🟢 ON" if game_status else "🔴 OFF"

await update.message.reply_text(
f"🎮 Game Status: {status}\n"
f"🔢 Lakkoofsa bahe: {len(called_numbers)}\n"
f"🏆 Winners: {len(winners)}"
)
def add_transaction(user_id, amount, transaction_type):
transactions.append({
"user_id": user_id,
"amount": amount,
"type": transaction_type
})
async def admin_wallet(update, context):

text = "💰 Wallet Transactions\n\n"

for t in transactions:
text += (
f"👤 User: {t['user_id']}\n"
f"💵 Amount: {t['amount']}\n"
f"📌 Type: {t['type']}\n\n"
)

await update.message.reply_text(text)
def add_balance(user_id, amount):

if user_id in users:
users[user_id]["balance"] += amount

add_transaction(
user_id,
amount,
"ADMIN_ADD_BALANCE"
)

return True

return False
def remove_balance(user_id, amount):

if user_id in users:

if users[user_id]["balance"] >= amount:

users[user_id]["balance"] -= amount

add_transaction(
user_id,
amount,
"ADMIN_REMOVE_BALANCE"
)

return True

return False
async def check_user_balance(update, context):

user_id = int(context.args[0])

if user_id in users:

balance = users[user_id]["balance"]

await update.message.reply_text(
f"👤 User: {user_id}\n"
f"💰 Balance: {balance}"
)

else:

await update.message.reply_text(
"❌ User hin argamne"
)
def create_withdraw_request(user_id, amount):

if user_id in users:

if users[user_id]["balance"] >= amount:

withdraw_requests.append({
"user_id": user_id,
"amount": amount,
"status": "PENDING"
})

return True

return False
async def withdraw(update, context):

user_id = update.effective_user.id

amount = int(context.args[0])

result = create_withdraw_request(
user_id,
amount
)

if result:

await update.message.reply_text(
"✅ Withdraw request ergame\n"
"Admin mirkaneessa."
)

else:

await update.message.reply_text(
"❌ Balance gahaa miti"
)
async def admin_withdraw_list(update, context):

text = "💸 Withdraw Requests\n\n"

for w in withdraw_requests:

if w["status"] == "PENDING":

text += (
f"👤 User: {w['user_id']}\n"
f"💰 Amount: {w['amount']}\n"
f"⏳ Status: {w['status']}\n\n"
)

await update.message.reply_text(text)
def approve_withdraw(index):

request = withdraw_requests[index]

user_id = request["user_id"]
amount = request["amount"]

if users[user_id]["balance"] >= amount:

users[user_id]["balance"] -= amount

request["status"] = "APPROVED"

add_transaction(
user_id,
amount,
"WITHDRAW_APPROVED"
)

return True

return False
def reject_withdraw(index):

withdraw_requests[index]["status"] = "REJECTED"

return True
async def admin_withdraw_list(update, context):

text = "💸 Withdraw Requests\n\n"

keyboard = []

for index, w in enumerate(withdraw_requests):

if w["status"] == "PENDING":

text += (
f"👤 User: {w['user_id']}\n"
f"💰 Amount: {w['amount']}\n\n"
)

keyboard.append([
InlineKeyboardButton(
"✅ Approve",
callback_data=f"approve_{index}"
),
InlineKeyboardButton(
"❌ Reject",
callback_data=f"reject_{index}"
)
 ])


reply_markup = InlineKeyboardMarkup(keyboard)

await update.message.reply_text(
text,
reply_markup=reply_markup
)
async def withdraw_callback(update, context):

query = update.callback_query

await query.answer()

data = query.data


if data.startswith("approve_"):

index = int(
data.split("_")[1]
)

result = approve_withdraw(index)


if result:

await query.edit_message_text(
"✅ Withdraw Approved"
)

else:

await query.edit_message_text(
"❌ Error"
)


elif data.startswith("reject_"):

index = int(
data.split("_")[1]
)

reject_withdraw(index)


await query.edit_message_text(
"❌ Withdraw Rejected"
)
def is_admin(user_id):

return user_id in ADMIN_IDS
async def admin_panel(update, context):

user_id = update.effective_user.id

if not is_admin(user_id):

await update.message.reply_text(
"❌ Admin qofaaf"
)

return


await update.message.reply_text(
"⚙️ Admin Dashboard\n\n"
"👥 Users\n"
"💰 Wallet\n"
"💸 Withdraw\n"
"🎫 Cards"
)
def ban_user(user_id):

if user_id in users:

users[user_id]["status"] = "BANNED"

return True

return False
def unban_user(user_id):

if user_id in users:

users[user_id]["status"] = "ACTIVE"

return True

return False
async def admin_users(update, context):

user_id = update.effective_user.id

if not is_admin(user_id):

await update.message.reply_text(
"❌ Admin qofaaf"
)
return


text = "👥 User List\n\n"

for uid, user in users.items():

text += (
f"🆔 ID: {uid}\n"
f"👤 Name: {user['name']}\n"
f"💰 Balance: {user['balance']}\n"
f"📌 Status: {user['status']}\n\n"
)


await update.message.reply_text(text)
async def user_profile(update, context):

if not is_admin(update.effective_user.id):

return


uid = int(context.args[0])


if uid in users:

user = users[uid]


await update.message.reply_text(
f"👤 User Profile\n\n"
f"🆔 ID: {uid}\n"
f"📛 Name: {user['name']}\n"
f"💰 Balance: {user['balance']}\n"
f"📌 Status: {user['status']}"
)

else:

await update.message.reply_text(
"❌ User hin argamne"
)

def search_user(name):

result = []

for uid, user in users.items():

if name.lower() in user["name"].lower():

result.append(uid)


return result
def save_card(user_id, card, price):

bingo_cards.append({

"user_id": user_id,
"card": card,
"price": price,
"status": "ACTIVE"

})
async def admin_cards(update, context):

if not is_admin(update.effective_user.id):

await update.message.reply_text(
"❌ Admin qofaaf"
)
return


text = "🎫 Bingo Cards\n\n"


for c in bingo_cards:

text += (
f"👤 User: {c['user_id']}\n"
f"🎫 Card: {c['card']}\n"
f"💰 Price: {c['price']}\n"
f"📌 Status: {c['status']}\n\n"
)


await update.message.reply_text(text)
def close_card(index):

if index < len(bingo_cards):

bingo_cards[index]["status"] = "CLOSED"

return True

return False
def start_game():

game["status"] = "RUNNING"

return True
import random


def draw_number():

number = random.randint(1,75)

if number not in game["drawn_numbers"]:

game["drawn_numbers"].append(number)

return number

return draw_number()
async def start_bingo(update, context):

if not is_admin(update.effective_user.id):

await update.message.reply_text(
"❌ Admin qofaaf"
)
return


game["status"] = "RUNNING"

await update.message.reply_text(
"🎲 Bingo Game Started!"
)
async def draw_bingo(update, context):

if not is_admin(update.effective_user.id):

return


number = draw_number()


await update.message.reply_text(
f"🎱 Number: {number}"
)
def check_card(card_numbers):

for number in card_numbers:

if number not in game["drawn_numbers"]:

return False


return True
def find_winner():

for card in bingo_cards:

if check_card(card["card"]):

game["winner"] = card["user_id"]

return card["user_id"]


return None
def set_winner(user_id):

game["winner"] = user_id
game["status"] = "FINISHED"

return True
def give_prize(user_id):

prize = game["prize"]


if user_id in users:

users[user_id]["balance"] += prize


add_transaction(
user_id,
prize,
"BINGO_WIN_PRIZE"
)


return True


return False
async def announce_winner(update, context):

if not is_admin(update.effective_user.id):

return


winner = game["winner"]


if winner:

await update.message.reply_text(
f"🏆 Winner:\n"
f"User ID: {winner}\n"
f"💰 Prize: {game['prize']}"
)

else:

await update.message.reply_text(
"❌ Winner hin jiru"
)
def finish_game(winner_id):

set_winner(winner_id)

give_prize(winner_id)
def buy_card(user_id, card):

if user_id not in users:

return False


if users[user_id]["balance"] < CARD_PRICE:

return False


users[user_id]["balance"] -= CARD_PRICE


save_card(
user_id,
card,
CARD_PRICE
)


add_transaction(
user_id,
CARD_PRICE,
"BUY_CARD"
)


return True
async def buy(update, context):

user_id = update.effective_user.id


card = generate_card()


result = buy_card(
user_id,
card
)


if result:

await update.message.reply_text(
"🎫 Kaardii bitameera!\n"
"Tapha keessatti hirmaatta."
)

else:

await update.message.reply_text(
"❌ Balance gahaa miti."
)
def generate_card():

return {
"B": random.sample(range(1,16),5),
"I": random.sample(range(16,31),5),
"N": random.sample(range(31,46),5),
"G": random.sample(range(46,61),5),
"O": random.sample(range(61,76),5)
}

def get_user_cards(user_id):

result = []

for card in bingo_cards:

if card["user_id"] == user_id:

result.append(card)


return result
def set_card_price(price):

global CARD_PRICE

CARD_PRICE = price

return True

def buy_multiple_cards(user_id, quantity):

total_price = CARD_PRICE * quantity


if user_id not in users:

return False


if users[user_id]["balance"] < total_price:

return False


users[user_id]["balance"] -= total_price


for i in range(quantity):

card = generate_card()

save_card(
user_id,
card,
CARD_PRICE
)


add_transaction(
user_id,
total_price,
"MULTIPLE_CARD_BUY"
)


return True
async def card_buy_handler(update, context):

user_id = update.effective_user.id

text = update.message.text


if text == "🎫 Buy 1 Card":

quantity = 1


elif text == "🎫 Buy 5 Cards":

quantity = 5


elif text == "🎫 Buy 10 Cards":

quantity = 10


else:

return


result = buy_multiple_cards(
user_id,
quantity
)


if result:

await update.message.reply_text(
f"✅ {quantity} Card bitameera!"
)

else:

await update.message.reply_text(
"❌ Balance gahaa miti"
)
async def show_card_price(update, context):

await update.message.reply_text(
f"🎫 Current Card Price: {CARD_PRICE}"
)
conn = sqlite3.connect(
"bingo.db",
check_same_thread=False
)

cursor = conn.cursor()
cursor.execute("""

CREATE TABLE IF NOT EXISTS users (

id INTEGER PRIMARY KEY,
name TEXT,
phone TEXT,
balance INTEGER DEFAULT 0,
status TEXT DEFAULT 'ACTIVE'

)

""")

conn.commit()
def create_user(
user_id,
name,
phone
):

cursor.execute(
"""
INSERT INTO users
(id,name,phone)
VALUES (?,?,?)
""",
(
user_id,
name,
phone
)
)

conn.commit()
def get_balance(user_id):

cursor.execute(
"""
SELECT balance
FROM users
WHERE id=?
""",
(user_id,)
)


result = cursor.fetchone()


if result:

return result[0]


return 0
def update_balance(
user_id,
amount
):

cursor.execute(
"""
UPDATE users
SET balance = balance + ?
WHERE id=?
""",
(
amount,
user_id
)
)


conn.commit()
cursor.execute("""

CREATE TABLE IF NOT EXISTS bingo_cards (

id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
card TEXT,
price INTEGER,
status TEXT DEFAULT 'ACTIVE'

)

""")

conn.commit()
def save_card_db(
user_id,
card,
price
):

cursor.execute(
"""
INSERT INTO bingo_cards
(user_id,card,price)
VALUES (?,?,?)
""",
(
user_id,
str(card),
price
)
)

conn.commit()
def get_cards(user_id):

cursor.execute(
"""
SELECT card,price,status
FROM bingo_cards
WHERE user_id=?
""",
(user_id,)
)


return cursor.fetchall()
cursor.execute("""

CREATE TABLE IF NOT EXISTS transactions (

id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
amount INTEGER,
type TEXT,
date TEXT

)

""")

conn.commit()
import datetime


def save_transaction(
user_id,
amount,
trans_type
):

cursor.execute(
"""
INSERT INTO transactions
(user_id,amount,type,date)
VALUES (?,?,?,?)
""",
(
user_id,
amount,
trans_type,
str(datetime.datetime.now())
)
)


conn.commit()
cursor.execute("""

CREATE TABLE IF NOT EXISTS winners (

id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
prize INTEGER,
date TEXT

)

""")

conn.commit()
def save_winner(
user_id,
prize
):

cursor.execute(
"""
INSERT INTO winners
(user_id,prize,date)
VALUES (?,?,?)
""",
(
user_id,
prize,
str(datetime.datetime.now())
)
)

conn.commit()
async def admin_users(update, context):

if not is_admin(update.effective_user.id):
return


cursor.execute(
"""
SELECT id,name,phone,balance,status
FROM users
"""
)


data = cursor.fetchall()


text = "👥 Users\n\n"


for user in data:

text += (
f"🆔 ID: {user[0]}\n"
f"👤 Name: {user[1]}\n"
f"📱 Phone: {user[2]}\n"
f"💰 Balance: {user[3]}\n"
f"📌 Status: {user[4]}\n\n"
)


await update.message.reply_text(text)

async def admin_cards(update, context):

if not is_admin(update.effective_user.id):
return


cursor.execute(
"""
SELECT user_id,card,price,status
FROM bingo_cards
"""
)


cards = cursor.fetchall()


text = "🎫 Cards\n\n"


for c in cards:

text += (
f"👤 User: {c[0]}\n"
f"🎫 Card: {c[1]}\n"
f"💰 Price: {c[2]}\n"
f"📌 Status: {c[3]}\n\n"
)


await update.message.reply_text(text)
async def admin_transactions(update, context):

if not is_admin(update.effective_user.id):
return


cursor.execute(
"""
SELECT user_id,amount,type,date
FROM transactions
ORDER BY id DESC
"""
)


transactions = cursor.fetchall()


text = "💰 Transactions\n\n"


for t in transactions:

text += (
f"👤 User: {t[0]}\n"
f"💵 Amount: {t[1]}\n"
f"📌 Type: {t[2]}\n"
f"📅 Date: {t[3]}\n\n"
)


await update.message.reply_text(text)
def get_user_count():

cursor.execute(
"""
SELECT COUNT(*)
FROM users
"""
)

result = cursor.fetchone()

return result[0]

def get_card_count():

cursor.execute(
"""
SELECT COUNT(*)
FROM bingo_cards
"""
)

result = cursor.fetchone()

return result[0]
def get_total_income():

cursor.execute(
"""
SELECT SUM(amount)
FROM transactions
WHERE type='BUY_CARD'
"""
)

result = cursor.fetchone()


if result[0]:

return result[0]


return 0
async def admin_stats(update, context):

if not is_admin(update.effective_user.id):

return


users_count = get_user_count()

cards_count = get_card_count()

income = get_total_income()


text = (
"📊 Dashboard Statistics\n\n"
f"👥 Users: {users_count}\n"
f"🎫 Cards Sold: {cards_count}\n"
f"💰 Income: {income}\n"
)


await update.message.reply_text(text)
def get_daily_income():

cursor.execute(
"""
SELECT SUM(amount)
FROM transactions
WHERE type='BUY_CARD'
AND date >= datetime('now','-1 day')
"""
)

result = cursor.fetchone()

return result[0] or 0
def get_weekly_income():

cursor.execute(
"""
SELECT SUM(amount)
FROM transactions
WHERE type='BUY_CARD'
AND date >= datetime('now','-7 day')
"""
)

result = cursor.fetchone()

return result[0] or 0
def get_monthly_income():

cursor.execute(
"""
SELECT SUM(amount)
FROM transactions
WHERE type='BUY_CARD'
AND date >= datetime('now','-30 day')
"""
)

result = cursor.fetchone()

return result[0] or 0
async def admin_report(update, context):

if not is_admin(update.effective_user.id):

return


daily = get_daily_income()

weekly = get_weekly_income()

monthly = get_monthly_income()

profit = get_profit()


text = (
"📊 Admin Report\n\n"
f"📅 Daily: {daily}\n"
f"📅 Weekly: {weekly}\n"
f"📅 Monthly: {monthly}\n\n"
f"💰 Profit: {profit}"
)


await update.message.reply_text(text)

id="c9m4qw"
def create_transaction_report():

filename = "transactions_report.csv"


cursor.execute(
"""
SELECT
user_id,
amount,
type,
date
FROM transactions
"""
)


data = cursor.fetchall()


with open(
filename,
"w",
newline=""
) as file:

writer = csv.writer(file)


writer.writerow([
"User ID",
"Amount",
"Type",
"Date"
 ])


for row in data:

writer.writerow(row)


return filename
id="h7p2vx"
async def export_transactions(update, context):

if not is_admin(update.effective_user.id):

return


file = create_transaction_report()


await update.message.reply_document(
document=open(file,"rb"),
caption="📊 Transaction Report"
)
id="n5k8mq"
def create_cards_report():

filename = "cards_report.csv"


cursor.execute(
"""
SELECT
user_id,
card,
price,
status
FROM bingo_cards
"""
)


data = cursor.fetchall()


with open(
filename,
"w",
newline=""
) as file:

writer = csv.writer(file)


writer.writerow([
"User",
"Card",
"Price",
"Status"
 ])


writer.writerows(data)


return filename
cursor.execute("""

CREATE TABLE IF NOT EXISTS admins (

user_id INTEGER PRIMARY KEY,
role TEXT

)

""")

conn.commit()
def add_admin(user_id, role="OWNER"):

cursor.execute(
"""
INSERT INTO admins
(user_id,role)
VALUES (?,?)
""",
(
user_id,
role
)
)

conn.commit()
def check_admin(user_id):

cursor.execute(
"""
SELECT role
FROM admins
WHERE user_id=?
""",
(user_id,)
)


result = cursor.fetchone()


if result:

return True


return False
async def error_handler(
update,
context
):

print(
"Error:",
context.error
)
def backup_database():

date = datetime.datetime.now().strftime(
"%Y-%m-%d"
)


shutil.copy(
"bingo.db",
f"backup_{date}.db"
)

# Registration Conversation
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start)
        ],
        states={
            LANGUAGE: [
                CallbackQueryHandler(language_callback)
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
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ]
    )

    # User handlers
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("bingo", claim_bingo))
    app.add_handler(
        MessageHandler(
            filters.Regex("^🎫 Buy Card$"),
            buy_card
        )
    )

    # Admin handlers
    app.add_handler(CommandHandler("start_game", start_game))
    app.add_handler(CommandHandler("next", next_number))

    print("GM Bingo Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
        
