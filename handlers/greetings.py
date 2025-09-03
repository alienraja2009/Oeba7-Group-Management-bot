from telegram import Update
from telegram.ext import CommandHandler, ChatMemberHandler
from config import OWNER_ID
import database
import datetime

async def set_welcome(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat

    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command is for groups only.")
        return

    # Check permissions
    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if user.id != OWNER_ID and chat_member.status not in ['administrator', 'creator']:
        await update.message.reply_text("You don't have permission to set welcome messages.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /setwelcome <message>\nUse {user} for username, {chat} for chat name.")
        return

    welcome_message = ' '.join(context.args)
    database.update_group_settings(chat.id, welcome_message=welcome_message)

    await update.message.reply_text("✅ Welcome message updated successfully!")

async def toggle_welcome(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat

    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command is for groups only.")
        return

    # Check permissions
    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if user.id != OWNER_ID and chat_member.status not in ['administrator', 'creator']:
        await update.message.reply_text("You don't have permission to toggle welcome messages.")
        return

    settings = database.get_group_settings(chat.id)
    if settings:
        new_status = 0 if settings[2] else 1  # welcome_enabled is at index 2
        database.update_group_settings(chat.id, welcome_enabled=new_status)
        status_text = "enabled" if new_status else "disabled"
        await update.message.reply_text(f"✅ Welcome messages {status_text}!")
    else:
        database.update_group_settings(chat.id, welcome_enabled=1)
        await update.message.reply_text("✅ Welcome messages enabled!")

async def set_goodbye(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat

    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command is for groups only.")
        return

    # Check permissions
    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if user.id != OWNER_ID and chat_member.status not in ['administrator', 'creator']:
        await update.message.reply_text("You don't have permission to set goodbye messages.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /setgoodbye <message>\nUse {user} for username, {chat} for chat name.")
        return

    goodbye_message = ' '.join(context.args)
    database.update_group_settings(chat.id, goodbye_message=goodbye_message)

    await update.message.reply_text("✅ Goodbye message updated successfully!")

async def toggle_goodbye(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat

    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command is for groups only.")
        return

    # Check permissions
    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if user.id != OWNER_ID and chat_member.status not in ['administrator', 'creator']:
        await update.message.reply_text("You don't have permission to toggle goodbye messages.")
        return

    settings = database.get_group_settings(chat.id)
    if settings:
        new_status = 0 if settings[3] else 1  # goodbye_enabled is at index 3
        database.update_group_settings(chat.id, goodbye_enabled=new_status)
        status_text = "enabled" if new_status else "disabled"
        await update.message.reply_text(f"✅ Goodbye messages {status_text}!")
    else:
        database.update_group_settings(chat.id, goodbye_enabled=1)
        await update.message.reply_text("✅ Goodbye messages enabled!")

async def handle_chat_member_update(update: Update, context):
    chat_member_update = update.chat_member

    if not chat_member_update:
        return

    chat = update.effective_chat
    user = chat_member_update.new_chat_member.user
    old_status = chat_member_update.old_chat_member.status
    new_status = chat_member_update.new_chat_member.status

    settings = database.get_group_settings(chat.id)
    if not settings:
        return

    # Handle new member joins
    if old_status in ['left', 'kicked', 'banned'] and new_status in ['member', 'administrator', 'creator']:
        if settings[2]:  # welcome_enabled
            welcome_msg = settings[4].replace('{user}', user.mention_html()).replace('{chat}', chat.title)
            await context.bot.send_message(chat.id, welcome_msg, parse_mode='HTML')

    # Handle member leaves
    elif old_status in ['member', 'administrator', 'creator'] and new_status in ['left', 'kicked', 'banned']:
        if settings[3]:  # goodbye_enabled
            goodbye_msg = settings[5].replace('{user}', user.mention_html()).replace('{chat}', chat.title)
            await context.bot.send_message(chat.id, goodbye_msg, parse_mode='HTML')

# Handlers
set_welcome_handler = CommandHandler("setwelcome", set_welcome)
toggle_welcome_handler = CommandHandler("welcome", toggle_welcome)
set_goodbye_handler = CommandHandler("setgoodbye", set_goodbye)
toggle_goodbye_handler = CommandHandler("goodbye", toggle_goodbye)
chat_member_update_handler = ChatMemberHandler(handle_chat_member_update, ChatMemberHandler.CHAT_MEMBER)
