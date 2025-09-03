import re
from telegram import Update
from telegram.ext import MessageHandler, filters
from config import BLACKLIST_WORDS, SPAM_THRESHOLD, FLOOD_THRESHOLD
import database

# Track user messages for flood detection
user_messages = {}

async def check_message(update: Update, context):
    user = update.effective_user
    message = update.message
    chat = update.effective_chat

    if not message or not chat or chat.type not in ['group', 'supergroup']:
        return

    text = message.text or ""

    # Link protection
    if re.search(r'http[s]?://', text):
        await message.delete()
        await context.bot.send_message(chat.id, f"{user.mention_html()} sent a link, which is not allowed.", parse_mode='HTML')
        return

    # Spam protection: check for blacklisted words
    for word in BLACKLIST_WORDS:
        if word.lower() in text.lower():
            await message.delete()
            await context.bot.send_message(chat.id, f"{user.mention_html()} used a blacklisted word.", parse_mode='HTML')
            return

    # Flood protection
    user_id = user.id
    current_time = message.date.timestamp()

    if user_id not in user_messages:
        user_messages[user_id] = []

    user_messages[user_id].append(current_time)

    # Remove old messages (older than 60 seconds)
    user_messages[user_id] = [t for t in user_messages[user_id] if current_time - t < 60]

    if len(user_messages[user_id]) > FLOOD_THRESHOLD:
        await context.bot.restrict_chat_member(chat.id, user_id, until_date=current_time + 300)  # mute for 5 min
        await context.bot.send_message(chat.id, f"{user.mention_html()} is flooding, muted for 5 minutes.", parse_mode='HTML')
        user_messages[user_id] = []

# Handler
protection_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, check_message)
