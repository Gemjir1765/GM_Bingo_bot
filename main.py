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
