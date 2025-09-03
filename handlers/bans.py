from telegram import Update
from telegram.ext import CommandHandler
from config import OWNER_ID
import database
from datetime import datetime, timedelta

async def ban(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat
    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command is for groups only.")
        return

    # Check permissions
    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if user.id != OWNER_ID and chat_member.status not in ['administrator', 'creator']:
        await update.message.reply_text("You don't have permission to ban users.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /ban @username reason [duration in hours]")
        return

    target_username = context.args[0]
    if not target_username.startswith('@'):
        await update.message.reply_text("Please mention the user with @username.")
        return

    reason = context.args[1]
    duration_hours = int(context.args[2]) if len(context.args) > 2 else 0  # 0 for permanent

    # Find target user
    target_user = None
    async for member in context.bot.get_chat_members(chat.id):
        if member.user.username == target_username[1:]:
            target_user = member.user
            break

    if not target_user:
        await update.message.reply_text("User not found in the group.")
        return

    # Ban in Telegram
    until_date = None if duration_hours == 0 else datetime.now() + timedelta(hours=duration_hours)
    try:
        await context.bot.ban_chat_member(chat.id, target_user.id, until_date=until_date)
    except Exception as e:
        await update.message.reply_text(f"Failed to ban: {e}")
        return

    # Save to database
    duration_seconds = duration_hours * 3600 if duration_hours > 0 else 0
    timestamp = datetime.now().isoformat()
    database.add_ban(target_user.id, reason, duration_seconds, user.id, chat.id, timestamp)
    database.log_action(user.id, 'ban', target_user.id, reason, chat.id, timestamp)

    duration_text = f"for {duration_hours} hours" if duration_hours > 0 else "permanently"
    await update.message.reply_text(f"Banned {target_username} {duration_text}. Reason: {reason}")

# Handler
ban_handler = CommandHandler("ban", ban)
