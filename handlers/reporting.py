from telegram import Update
from telegram.ext import CommandHandler
from config import OWNER_ID
import database
from datetime import datetime

async def report(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat
    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command is for groups only.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /report @username reason")
        return

    target_username = context.args[0]
    if not target_username.startswith('@'):
        await update.message.reply_text("Please mention the user with @username.")
        return

    reason = ' '.join(context.args[1:])

    # Find target user ID
    target_user = None
    async for member in context.bot.get_chat_members(chat.id):
        if member.user.username == target_username[1:]:
            target_user = member.user
            break

    if not target_user:
        await update.message.reply_text("User not found in the group.")
        return

    # Save report to database
    timestamp = datetime.now().isoformat()
    database.add_report(user.id, target_user.id, reason, chat.id, timestamp)

    # Notify owner
    try:
        await context.bot.send_message(OWNER_ID, f"New report in {chat.title}:\nReporter: {user.mention_html()}\nReported: {target_user.mention_html()}\nReason: {reason}", parse_mode='HTML')
    except:
        pass  # Owner might not have started the bot

    await update.message.reply_text("Report submitted to the owner.")

# Handler
report_handler = CommandHandler("report", report)
