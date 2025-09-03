from telegram import Update
from telegram.ext import ChatMemberHandler
from config import OWNER_ID
import database
from datetime import datetime, timedelta

# Track recent joins
recent_joins = []

async def handle_chat_member(update: Update, context):
    global recent_joins
    chat_member = update.chat_member
    chat = update.effective_chat
    user = chat_member.new_chat_member.user

    if chat_member.new_chat_member.status in ['member', 'administrator', 'creator']:
        # New join
        current_time = datetime.now()
        recent_joins.append((user.id, current_time))

        # Remove old joins (older than 60 seconds)
        recent_joins = [j for j in recent_joins if current_time - j[1] < timedelta(seconds=60)]

        if len(recent_joins) > 5:  # Threshold for raid
            # Lock group temporarily
            await context.bot.set_chat_permissions(chat.id, can_send_messages=False, until_date=current_time + timedelta(minutes=10))
            await context.bot.send_message(chat.id, "Raid detected! Group locked for 10 minutes.")
            # Notify owner
            try:
                await context.bot.send_message(OWNER_ID, f"Raid detected in {chat.title}!")
            except:
                pass
            recent_joins = []  # Reset

        # Add user to DB
        database.add_user(user.id, user.username, user.first_name, current_time.isoformat())

# Handler
chat_member_handler = ChatMemberHandler(handle_chat_member, ChatMemberHandler.CHAT_MEMBER)
