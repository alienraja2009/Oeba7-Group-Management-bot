from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters
from config import OWNER_ID
import database
import datetime
import re

async def mute_user(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat

    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command is for groups only.")
        return

    # Check permissions
    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if user.id != OWNER_ID and chat_member.status not in ['administrator', 'creator']:
        await update.message.reply_text("You don't have permission to mute users.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user's message to mute them.")
        return

    target_user = update.message.reply_to_message.from_user
    reason = ' '.join(context.args) if context.args else "No reason provided"

    # Parse duration
    duration = 3600  # Default 1 hour
    if context.args:
        duration_str = context.args[0].lower()
        if duration_str.endswith('m'):
            duration = int(duration_str[:-1]) * 60
        elif duration_str.endswith('h'):
            duration = int(duration_str[:-1]) * 3600
        elif duration_str.endswith('d'):
            duration = int(duration_str[:-1]) * 86400
        else:
            duration = int(duration_str) * 3600  # Assume hours if no unit

    unmute_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)

    try:
        await context.bot.restrict_chat_member(
            chat.id,
            target_user.id,
            until_date=unmute_time,
            can_send_messages=False
        )

        database.add_mute(target_user.id, chat.id, reason, user.id,
                         datetime.datetime.now().isoformat(), unmute_time.isoformat())

        await update.message.reply_text(
            f"🔇 Muted {target_user.mention_html()} for {duration//3600}h {duration%3600//60}m\n"
            f"Reason: {reason}",
            parse_mode='HTML'
        )
    except Exception as e:
        await update.message.reply_text(f"Failed to mute user: {str(e)}")

async def unmute_user(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat

    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command is for groups only.")
        return

    # Check permissions
    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if user.id != OWNER_ID and chat_member.status not in ['administrator', 'creator']:
        await update.message.reply_text("You don't have permission to unmute users.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user's message to unmute them.")
        return

    target_user = update.message.reply_to_message.from_user

    try:
        await context.bot.restrict_chat_member(
            chat.id,
            target_user.id,
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )

        database.remove_mute(target_user.id, chat.id)

        await update.message.reply_text(
            f"🔊 Unmuted {target_user.mention_html()}.",
            parse_mode='HTML'
        )
    except Exception as e:
        await update.message.reply_text(f"Failed to unmute user: {str(e)}")

async def warn_user(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat

    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command is for groups only.")
        return

    # Check permissions
    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if user.id != OWNER_ID and chat_member.status not in ['administrator', 'creator']:
        await update.message.reply_text("You don't have permission to warn users.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user's message to warn them.")
        return

    target_user = update.message.reply_to_message.from_user
    reason = ' '.join(context.args) if context.args else "No reason provided"

    database.add_warning(target_user.id, chat.id, reason, user.id, datetime.datetime.now().isoformat())

    warning_count = database.get_user_warnings(target_user.id, chat.id)

    await update.message.reply_text(
        f"⚠️ Warned {target_user.mention_html()}\n"
        f"Reason: {reason}\n"
        f"Total warnings: {warning_count}",
        parse_mode='HTML'
    )

async def unwarn_user(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat

    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command is for groups only.")
        return

    # Check permissions
    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if user.id != OWNER_ID and chat_member.status not in ['administrator', 'creator']:
        await update.message.reply_text("You don't have permission to remove warnings.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user's message to remove their warnings.")
        return

    target_user = update.message.reply_to_message.from_user

    database.remove_user_warnings(target_user.id, chat.id)

    await update.message.reply_text(
        f"✅ Removed all warnings for {target_user.mention_html()}.",
        parse_mode='HTML'
    )

async def purge_messages(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat

    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command is for groups only.")
        return

    # Check permissions
    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if user.id != OWNER_ID and chat_member.status not in ['administrator', 'creator']:
        await update.message.reply_text("You don't have permission to purge messages.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message to purge from that point.")
        return

    try:
        # Delete messages from the replied message to current message
        message_id = update.message.reply_to_message.message_id
        current_message_id = update.message.message_id

        for msg_id in range(message_id, current_message_id + 1):
            try:
                await context.bot.delete_message(chat.id, msg_id)
            except:
                pass  # Message might already be deleted

        await update.message.reply_text("🗑️ Messages purged successfully.")
    except Exception as e:
        await update.message.reply_text(f"Failed to purge messages: {str(e)}")

# Handlers
mute_handler = CommandHandler("mute", mute_user)
unmute_handler = CommandHandler("unmute", unmute_user)
warn_handler = CommandHandler("warn", warn_user)
unwarn_handler = CommandHandler("unwarn", unwarn_user)
purge_handler = CommandHandler("purge", purge_messages)
