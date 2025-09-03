from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters
from config import OWNER_ID, REDEEM_CODES
import re
import random
import string
import database
import sqlite3
import datetime

async def contact_owner(update: Update, context):
    user = update.effective_user
    message = ' '.join(context.args)

    if not message:
        await update.message.reply_text("Usage: /contact_owner your message")
        return

    try:
        await context.bot.send_message(OWNER_ID, f"Message from {user.mention_html()} (ID: {user.id}, Username: @{user.username or 'None'}):\n{message}", parse_mode='HTML')
        await update.message.reply_text("Message sent to owner.")
    except:
        await update.message.reply_text(f"Failed to contact owner. Please have the owner start the bot by sending /start to @{context.bot.username}, or DM @Oeba7 directly.")

async def owner_reply(update: Update, context):
    if update.effective_chat.id != OWNER_ID:
        return

    if not update.message.reply_to_message:
        return

    original_text = update.message.reply_to_message.text
    if not original_text or "Message from" not in original_text:
        return

    # Extract user ID
    match = re.search(r'\(ID: (\d+)', original_text)
    if not match:
        return

    user_id = int(match.group(1))
    reply_text = update.message.text

    try:
        await context.bot.send_message(user_id, f"Reply from owner:\n{reply_text}")
        await update.message.reply_text("Reply sent.")
    except:
        await update.message.reply_text("Failed to send reply.")

async def generate_code(update: Update, context):
    user = update.effective_user
    if user.id != OWNER_ID:
        await update.message.reply_text("This command is for the owner only.")
        return

    if len(context.args) == 0:
        # Generate a random code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        duration = 0  # permanent
    elif len(context.args) == 1:
        # Use custom code provided by owner, permanent
        code = context.args[0].upper()
        duration = 0
        # Validate custom code format (alphanumeric, length 4-20)
        if not (4 <= len(code) <= 20 and code.isalnum()):
            await update.message.reply_text("Invalid custom code. Use 4-20 alphanumeric characters.")
            return
    else:
        # Custom code with duration
        code = context.args[0].upper()
        duration_str = context.args[1].lower()
        duration = 0  # Initialize duration

        # Validate custom code format (alphanumeric, length 4-20)
        if not (4 <= len(code) <= 20 and code.isalnum()):
            await update.message.reply_text("Invalid custom code. Use 4-20 alphanumeric characters.")
            return

        # Parse duration
        if duration_str == 'permanent':
            duration = 0
        else:
            # Parse time units (e.g., 7d, 24h, 30m)
            match = re.match(r'^(\d+)([dhm])$', duration_str)
            if not match:
                await update.message.reply_text("Invalid duration format. Use format like 7d (days), 24h (hours), 30m (minutes), or 'permanent'.")
                return

            value, unit = match.groups()
            value = int(value)

            if unit == 'd':
                duration = value * 24 * 60 * 60  # days to seconds
            elif unit == 'h':
                duration = value * 60 * 60  # hours to seconds
            elif unit == 'm':
                duration = value * 60  # minutes to seconds

    # Check if code already exists
    existing_code = database.get_redeem_code(code)
    if existing_code:
        await update.message.reply_text("This code already exists.")
        return

    # Calculate expiration time
    created_at = datetime.datetime.now().isoformat()
    if duration == 0:
        expires_at = None
        duration_text = "permanent"
    else:
        expires_at = (datetime.datetime.now() + datetime.timedelta(seconds=duration)).isoformat()
        duration_text = f"{duration // (24*60*60)}d" if duration >= 24*60*60 else f"{duration // (60*60)}h" if duration >= 60*60 else f"{duration // 60}m"

    # Store in database
    database.add_redeem_code(code, duration, created_at, expires_at)

    await update.message.reply_text(f"Generated redeem code: `{code}`\nDuration: {duration_text}\nSend this to users for them to redeem in private groups.")

async def delete_code(update: Update, context):
    user = update.effective_user
    if user.id != OWNER_ID:
        await update.message.reply_text("This command is for the owner only.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /delete_code CODE")
        return

    code = context.args[0].upper()
    existing_code = database.get_redeem_code(code)
    if not existing_code:
        await update.message.reply_text("Code not found.")
        return

    # Mark code as banned (immediate cancellation of features)
    conn = sqlite3.connect(database.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE redeem_codes SET banned = 1 WHERE code = ?', (code,))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"Redeem code `{code}` has been deleted and features canceled immediately.")

async def ban_user(update: Update, context):
    user = update.effective_user
    if user.id != OWNER_ID:
        await update.message.reply_text("This command is for the owner only.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /ban_user USER_ID [reason]")
        return

    try:
        target_user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid user ID.")
        return

    reason = ' '.join(context.args[1:]) if len(context.args) > 1 else "No reason provided"
    banned_at = datetime.datetime.now().isoformat()

    # Add to banned_users table
    conn = sqlite3.connect(database.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO banned_users (user_id, reason, banned_at, banned_by) VALUES (?, ?, ?, ?)',
                   (target_user_id, reason, banned_at, user.id))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"User {target_user_id} has been banned from using the bot. Reason: {reason}")

async def unban_user(update: Update, context):
    user = update.effective_user
    if user.id != OWNER_ID:
        await update.message.reply_text("This command is for the owner only.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /unban_user USER_ID")
        return

    try:
        target_user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid user ID.")
        return

    conn = sqlite3.connect(database.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM banned_users WHERE user_id = ?', (target_user_id,))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"User {target_user_id} has been unbanned and can use the bot again.")

async def set_custom_title(update: Update, context):
    user = update.effective_user
    if user.id != OWNER_ID:
        await update.message.reply_text("This command is for the owner only.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to the user's message to set their custom title.")
        return

    target_user = update.message.reply_to_message.from_user

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /set_title custom title text")
        return

    custom_title = ' '.join(context.args)

    # Validate title length
    if len(custom_title) > 50:
        await update.message.reply_text("Custom title is too long. Maximum 50 characters.")
        return

    database.update_user_custom_title(target_user.id, custom_title)
    await update.message.reply_text(f"Custom title set for @{target_user.username or target_user.first_name}: {custom_title}")

# Handlers
contact_handler = CommandHandler("contact_owner", contact_owner)
owner_reply_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, owner_reply)
generate_code_handler = CommandHandler("generate_code", generate_code)
delete_code_handler = CommandHandler("delete_code", delete_code)
ban_user_handler = CommandHandler("ban_user", ban_user)
unban_user_handler = CommandHandler("unban_user", unban_user)
set_custom_title_handler = CommandHandler("set_title", set_custom_title)
