from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.ext.dispatcher import run_async
from tinydb import TinyDB, Query
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
db = TinyDB('users_data.json')
User = Query()

# Your bot token
BOT_TOKEN = "7250762077:AAGK73HxVLfK3FeCvWq52-aoUy9_XLGS0vM"
CHANNEL_USERNAME = '@genex_jod'  # Replace with your actual channel username
CHANNEL_LINK = 'https://t.me/genex_jod'  # Replace with your actual channel link

# Start command
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    if not db.contains(User.id == user.id):
        db.insert({'id': user.id, 'balance': 0, 'referred_by': None})

    keyboard = [
        [InlineKeyboardButton("Join Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("Verifying", callback_data='verify')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "Welcome! Please join the channel below and click 'Verifying' to start the bot.",
        reply_markup=reply_markup
    )

# Verify if user has joined the required channel
@run_async
def verify(update: Update, context: CallbackContext):
    query = update.callback_query
    user = query.from_user
    user_id = user.id

    try:
        member_status = context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id).status
        if member_status in ['member', 'administrator', 'creator']:
            query.edit_message_text(
                f"Thank you for joining! Refer your friends using your link: "
                f"https://t.me/{context.bot.username}?start={user.id}"
            )
        else:
            query.edit_message_text("⚠️ Join the channel to get the refer link.")
    except Exception as e:
        query.edit_message_text(f"⚠️ Join the channel to get the refer link. Error: {str(e)}")

# Refer command
@run_async
def refer(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    referrer_id = context.args[0] if context.args else None

    if referrer_id and referrer_id != str(user_id):
        referrer_id = int(referrer_id)
        if db.contains(User.id == referrer_id):
            referrer = db.get(User.id == referrer_id)
            db.update({'balance': referrer['balance'] + 0.5}, User.id == referrer_id)
            db.update({'referred_by': referrer_id}, User.id == user_id)
            update.message.reply_text(f"Thank you for joining through a referral!")
        else:
            update.message.reply_text("Invalid referral link.")
    else:
        update.message.reply_text("You cannot refer yourself.")

# Balance command
@run_async
def balance(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_data = db.get(User.id == user_id)
    balance = user_data["balance"]
    update.message.reply_text(f"Your current balance is ₹{balance}")

# Redeem command
@run_async
def redeem(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_data = db.get(User.id == user_id)
    balance = user_data["balance"]

    if balance >= 30:
        db.update({'balance': balance - 30}, User.id == user_id)
        update.message.reply_text("Congratulations! Your redeem code is ABC123")
    else:
        update.message.reply_text(f"You need ₹{30 - balance} more to redeem a code.")

# Commands list
@run_async
def cmds(update: Update, context: CallbackContext):
    commands = [
        "/start - Start the bot and get your referral link",
        "/refer <referral_id> - Refer a friend using their referral ID",
        "/balance - Check your current balance",
        "/redeem - Redeem your balance for a code"
    ]
    update.message.reply_text("\n".join(commands))

# Callback query handler for inline buttons
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'verify':
        verify(update, context)

# Main function to setup the bot
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("refer", refer))
    dispatcher.add_handler(CommandHandler("balance", balance))
    dispatcher.add_handler(CommandHandler("redeem", redeem))
    dispatcher.add_handler(CommandHandler("cmds", cmds))
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    
