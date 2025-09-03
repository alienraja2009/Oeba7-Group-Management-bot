from telegram import Update
from telegram.ext import MessageHandler, filters
from config import RANKS
import database

async def display_rank_on_message(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat

    # Only for groups
    if not chat or chat.type not in ['group', 'supergroup']:
        return

    # Update message count for stats tracking
    message_time = update.message.date.isoformat()
    database.update_user_message_count(user.id, chat.id, message_time)

    # Get user rank and custom title from database
    user_data = database.get_user(user.id)
    if user_data and user_data[3] != 'member':  # rank is at index 3
        rank = user_data[3]
        rank_name = RANKS.get(rank, "member")
        custom_title = user_data[4] if len(user_data) > 4 else None  # custom_title is at index 4

        if rank_name != "member":
            # Format the rank display as requested: "RANK-_______ the rank"
            rank_display = f"RANK-{rank_name.upper()}"
            if custom_title:
                display_text = f"@{user.username or user.first_name} is a {custom_title} ({rank_display})"
            else:
                display_text = f"@{user.username or user.first_name} is a {rank_display}"

            # Send rank display message
            await context.bot.send_message(chat.id, display_text)

# Handler
message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, display_rank_on_message)
