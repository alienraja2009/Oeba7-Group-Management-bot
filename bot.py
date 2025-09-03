import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, InlineQueryHandler
from config import TOKEN, LOG_LEVEL
import database

# Import handlers
from handlers.promotions import promote_handler, depromote_handler
from handlers.protections import protection_handler
from handlers.reporting import report_handler
from handlers.bans import ban_handler
from handlers.mod_tools import mod_panel_handler, mod_action_handler
from handlers.stats import stats_handler
from handlers.auto_defense import chat_member_handler
from handlers.owner_tools import contact_handler, owner_reply_handler, generate_code_handler, set_custom_title_handler, delete_code_handler, list_codes_handler, ban_user_handler, unban_user_handler, broadcast_handler, broadcast_confirm_handler, broadcast_history_handler
from handlers.utilities import rules_handler, announce_handler, poll_handler, ranks_handler, inline_handler, redeem_handler
from handlers.message_handler import message_handler
from handlers.moderation import mute_handler, unmute_handler, warn_handler, unwarn_handler, purge_handler
from handlers.greetings import set_welcome_handler, toggle_welcome_handler, set_goodbye_handler, toggle_goodbye_handler, chat_member_update_handler

# Set up logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)

# Initialize database
database.create_tables()

async def start(update: Update, context):
    await update.message.reply_text("""
🌐 Greetings! I am the Group Management Bot⚡

🛡️ **Advanced Moderation Features:**
• Mute/Unmute users with custom durations
• Warning system with tracking
• Message purging capabilities
• Comprehensive ban management

📢 **Greetings & Welcome System:**
• Customizable welcome messages
• Automatic goodbye messages
• Toggle on/off functionality

📝 **Information & Rules:**
• User info lookup (/info)
• Custom group rules (/setrules)
• Private/public rules settings

🧹 **Cleaning & Organization:**
• Command message cleaning
• Message filtering system

📊 **Enhanced Statistics:**
• Message tracking
• User activity monitoring
• Group analytics

Use /help to explore all commands! 🔑 Redeem special codes with /redeem for exclusive ranks!

✍️ Crafted with precision by @Oeba7
    """)

async def help_command(update: Update, context):
    help_text = """
    🎨 Available Commands 🎨

🔹 /start - Activate the bot and receive a welcome message
🔹 /help - Display this command list for quick guidance

👑 OWNER COMMANDS 👑
🔹 /promote rank - Promote a member to a higher rank (reply to user's message)
🔹 /demote - Demote a member to a lower rank (reply to user's message)
🔹 /set_title custom title text - Set a custom title for a user (reply to user's message)
🔹 /generate_code [code] [rank] [duration] - Generate a new redeem code with specific rank
🔹 /list_codes - List all redeem codes with their status and details
🔹 /delete_code CODE - Delete a redeem code and cancel its features
🔹 /ban_user USER_ID [reason] - Ban a user from using the bot across all groups
🔹 /unban_user USER_ID - Unban a user and allow them to use the bot again
🔹 /broadcast groups/users/group <message> - Send broadcast messages to groups or users
🔹 /broadcast preview <type> <message> - Preview broadcast before sending
🔹 /broadcast_history - View broadcast history and statistics

🛡️ MODERATION COMMANDS 🛡️
🔹 /mute [duration] - Mute a user (reply to user's message, default 1h)
🔹 /unmute - Unmute a user (reply to user's message)
🔹 /warn [reason] - Warn a user (reply to user's message)
🔹 /unwarn - Remove all warnings from a user (reply to user's message)
🔹 /purge - Delete messages from replied message to current message
🔹 /ban @user reason duration - Temporarily or permanently ban a user

📢 GREETINGS COMMANDS 📢
🔹 /setwelcome <message> - Set welcome message for new members
🔹 /welcome on/off - Enable/disable welcome messages
🔹 /setgoodbye <message> - Set goodbye message for leaving members
🔹 /goodbye on/off - Enable/disable goodbye messages

📝 INFO COMMANDS 📝
🔹 /id - Get user ID and chat information
🔹 /info @username - Get detailed information about a user (reply or mention)

📜 RULES COMMANDS 📜
🔹 /rules - Display community rules
🔹 /setrules <text> - Set community rules (admins only)
🔹 /resetrules - Reset rules to default
🔹 /privaterules on/off - Make rules private/public

🧹 CLEANING COMMANDS 🧹
🔹 /cleancommand all - Clean all command messages
🔹 /keepcommand all - Keep all command messages
🔹 /cleancommand <type> - Clean specific command type
🔹 /keepcommand <type> - Keep specific command type

⚙️ DISABLE/ENABLE COMMANDS ⚙️
🔹 /disable <command> - Disable a command in the group
🔹 /enable <command> - Enable a disabled command
🔹 /disabled - List all disabled commands
🔹 /disableable - List all disableable commands
🔹 /disableadmin on/off - Toggle admin command restrictions

🔍 FILTERS COMMANDS 🔍
🔹 /filter <word> <reply> - Add a word filter with reply
🔹 /stop <word> - Remove a word filter
🔹 /filters - List all active filters

📊 OTHER COMMANDS 📊
🔹 /report @user reason - Report a user to moderators
🔹 /modpanel - Open the moderation control panel
🔹 /stats - View live group statistics
🔹 /ranks - View the ranking system and powers
🔹 /redeem code - Redeem a special code for exclusive ranks
🔹 /contact_owner message - Contact the group owner

⚡ Crafted with care to keep your community safe, structured, and thriving.
👤 Created by @Oeba7
    """
    await update.message.reply_text(help_text)

def main():
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Add feature handlers
    application.add_handler(promote_handler)
    application.add_handler(depromote_handler)
    application.add_handler(protection_handler)
    application.add_handler(report_handler)
    application.add_handler(ban_handler)
    application.add_handler(mod_panel_handler)
    application.add_handler(mod_action_handler)
    application.add_handler(stats_handler)
    application.add_handler(chat_member_handler)
    application.add_handler(contact_handler)
    application.add_handler(owner_reply_handler)
    application.add_handler(generate_code_handler)
    application.add_handler(set_custom_title_handler)
    application.add_handler(delete_code_handler)
    application.add_handler(list_codes_handler)
    application.add_handler(ban_user_handler)
    application.add_handler(unban_user_handler)
    application.add_handler(broadcast_handler)
    application.add_handler(broadcast_confirm_handler)
    application.add_handler(broadcast_history_handler)
    application.add_handler(rules_handler)
    application.add_handler(announce_handler)
    application.add_handler(poll_handler)
    application.add_handler(ranks_handler)
    application.add_handler(inline_handler)
    application.add_handler(redeem_handler)
    application.add_handler(message_handler)

    # Add new moderation handlers
    application.add_handler(mute_handler)
    application.add_handler(unmute_handler)
    application.add_handler(warn_handler)
    application.add_handler(unwarn_handler)
    application.add_handler(purge_handler)

    # Add greetings handlers
    application.add_handler(set_welcome_handler)
    application.add_handler(toggle_welcome_handler)
    application.add_handler(set_goodbye_handler)
    application.add_handler(toggle_goodbye_handler)
    application.add_handler(chat_member_update_handler)

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
