from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler
from config import OWNER_ID
import database

async def mod_panel(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat
    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command is for groups only.")
        return

    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if user.id != OWNER_ID and chat_member.status not in ['administrator', 'creator']:
        await update.message.reply_text("You don't have permission to use mod panel.")
        return

    keyboard = [
        [InlineKeyboardButton("Mute 1h", callback_data="mute_1h")],
        [InlineKeyboardButton("Ban 24h", callback_data="ban_24h")],
        [InlineKeyboardButton("Warn", callback_data="warn")],
        [InlineKeyboardButton("Kick", callback_data="kick")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Mod Panel:", reply_markup=reply_markup)

async def handle_mod_action(update: Update, context):
    query = update.callback_query
    await query.answer()

    action = query.data
    user = query.from_user
    chat = query.message.chat

    # Assume target is replied to message
    if not query.message.reply_to_message:
        await query.edit_message_text("Reply to a message to perform action.")
        return

    target_user = query.message.reply_to_message.from_user

    if action == "mute_1h":
        await context.bot.restrict_chat_member(chat.id, target_user.id, until_date=query.message.date.timestamp() + 3600)
        await query.edit_message_text(f"Muted {target_user.mention_html()} for 1 hour.", parse_mode='HTML')
    elif action == "ban_24h":
        await context.bot.ban_chat_member(chat.id, target_user.id, until_date=query.message.date.timestamp() + 86400)
        await query.edit_message_text(f"Banned {target_user.mention_html()} for 24 hours.", parse_mode='HTML')
    elif action == "warn":
        await query.edit_message_text(f"Warned {target_user.mention_html()}.", parse_mode='HTML')
    elif action == "kick":
        await context.bot.ban_chat_member(chat.id, target_user.id)
        await context.bot.unban_chat_member(chat.id, target_user.id)
        await query.edit_message_text(f"Kicked {target_user.mention_html()}.", parse_mode='HTML')

    # Log action
    database.log_action(user.id, action, target_user.id, "", chat.id, query.message.date.isoformat())

# Handlers
mod_panel_handler = CommandHandler("modpanel", mod_panel)
mod_action_handler = CallbackQueryHandler(handle_mod_action, pattern="^(mute_1h|ban_24h|warn|kick)$")
