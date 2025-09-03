from telegram import Update
from telegram.ext import CommandHandler
from config import OWNER_ID, RANKS
import database

# Rank permissions mapping
rank_permissions = {
    'e_rank': {
        'can_delete_messages': True,
        'can_invite_users': True
    },
    'd_rank': {
        'can_delete_messages': True,
        'can_invite_users': True,
        'can_pin_messages': True,
        'can_manage_video_chats': True
    },
    'a_rank': {
        'can_delete_messages': True,
        'can_invite_users': True,
        'can_pin_messages': True,
        'can_manage_video_chats': True,
        'can_restrict_members': True
    },
    's_rank': {
        'can_delete_messages': True,
        'can_invite_users': True,
        'can_pin_messages': True,
        'can_manage_video_chats': True,
        'can_promote_members': True,
        'can_manage_chat': True,
        'can_restrict_members': True
    },
    'monarch_rank': {
        'can_delete_messages': True,
        'can_invite_users': True,
        'can_pin_messages': True,
        'can_manage_video_chats': True,
        'can_promote_members': True,
        'can_manage_chat': True,
        'can_restrict_members': True,
        'can_change_info': True
    },
    'private_owner': {
        'can_delete_messages': True,
        'can_invite_users': True,
        'can_pin_messages': True,
        'can_manage_video_chats': True,
        'can_promote_members': True,
        'can_manage_chat': True,
        'can_restrict_members': True,
        'can_change_info': True
    }
}

# Rank name mapping for convenience
rank_map = {
    'e': 'e_rank',
    'd': 'd_rank',
    'a': 'a_rank',
    's': 's_rank',
    'monarch': 'monarch_rank',
    'private': 'private_owner'
}

async def promote(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat
    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command is for groups only.")
        return

    # Check if user is owner or admin
    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if user.id != OWNER_ID and chat_member.status not in ['administrator', 'creator']:
        await update.message.reply_text("You don't have permission to promote users.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /promote rank (reply to the user's message)")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to the user's message to promote them.")
        return

    target_user = update.message.reply_to_message.from_user
    rank = context.args[0].lower()
    if rank in rank_map:
        rank = rank_map[rank]
    if rank not in RANKS:
        await update.message.reply_text(f"Invalid rank. Available ranks: {', '.join(RANKS.keys())} or shortcuts: {', '.join(rank_map.keys())}")
        return

    # Update rank in database
    database.update_user_rank(target_user.id, rank)

    # Promote in Telegram with appropriate permissions
    if rank in rank_permissions:
        try:
            await context.bot.promote_chat_member(
                chat.id,
                target_user.id,
                **rank_permissions[rank]
            )
        except Exception as e:
            await update.message.reply_text(f"Failed to promote in Telegram: {e}")

    # Notify group about the promotion with rank display
    rank_name = RANKS.get(rank, "member")
    await context.bot.send_message(chat.id, f"User @{target_user.username or target_user.first_name} has been promoted to {rank_name}.")

    await update.message.reply_text(f"Promoted @{target_user.username or 'user'} to {RANKS[rank]}.")

async def demote(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat
    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command is for groups only.")
        return

    # Check if user is owner or admin
    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if user.id != OWNER_ID and chat_member.status not in ['administrator', 'creator']:
        await update.message.reply_text("You don't have permission to demote users.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to the user's message to demote them.")
        return

    target_user = update.message.reply_to_message.from_user

    # Get current rank from database
    current_rank = database.get_user_rank(target_user.id)
    if not current_rank:
        await update.message.reply_text("User has no rank to demote.")
        return

    # Define rank hierarchy (highest to lowest)
    rank_hierarchy = ['monarch_rank', 's_rank', 'a_rank', 'd_rank', 'e_rank', 'private_owner']

    if current_rank not in rank_hierarchy:
        await update.message.reply_text("User has an unknown rank.")
        return

    current_index = rank_hierarchy.index(current_rank)

    # Cannot demote below private_owner
    if current_rank == 'private_owner':
        await update.message.reply_text("Cannot demote below private_owner rank.")
        return

    # Demote to next lower rank
    new_index = current_index + 1
    if new_index >= len(rank_hierarchy):
        await update.message.reply_text("User is already at the lowest rank.")
        return

    new_rank = rank_hierarchy[new_index]

    # Update rank in database
    database.update_user_rank(target_user.id, new_rank)

    # Update Telegram permissions
    if new_rank in rank_permissions:
        try:
            await context.bot.promote_chat_member(
                chat.id,
                target_user.id,
                **rank_permissions[new_rank]
            )
        except Exception as e:
            await update.message.reply_text(f"Failed to update Telegram permissions: {e}")

    # Notify group about the demotion
    rank_name = RANKS.get(new_rank, "member")
    await context.bot.send_message(chat.id, f"User @{target_user.username or target_user.first_name} has been demoted to {rank_name}.")

    await update.message.reply_text(f"Demoted @{target_user.username or 'user'} to {RANKS[new_rank]}.")

# Handlers
promote_handler = CommandHandler("promote", promote)
depromote_handler = CommandHandler("demote", demote)
