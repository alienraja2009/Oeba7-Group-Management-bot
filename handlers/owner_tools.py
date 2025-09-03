
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters
from config import OWNER_ID, REDEEM_CODES
import re
import random
import string
import database

# Add these imports if missing
from database import get_redeem_code, add_redeem_code, update_user_custom_title
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

    import datetime
    import secrets
    import string

    # Available ranks
    available_ranks = ['private_owner', 'e_rank', 'd_rank', 'a_rank', 's_rank', 'monarch_rank']

    # Available durations
    duration_options = {
        '1h': 3600,
        '6h': 21600,
        '12h': 43200,
        '1d': 86400,
        '3d': 259200,
        '7d': 604800,
        '30d': 2592000,
        'permanent': 0
    }

    if len(context.args) == 0:
        # Generate a random code with default settings
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
        rank = 'private_owner'
        duration = 0  # permanent
        duration_text = "permanent"
    elif len(context.args) == 1:
        arg = context.args[0].lower()
        if arg in available_ranks:
            # Generate random code with specified rank
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
            rank = arg
            duration = 0
            duration_text = "permanent"
        elif arg in duration_options:
            # Generate random code with specified duration
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
            rank = 'private_owner'
            duration = duration_options[arg]
            duration_text = arg if arg != 'permanent' else 'permanent'
        else:
            # Use custom code provided by owner, default settings
            code = context.args[0].upper()
            rank = 'private_owner'
            duration = 0
            duration_text = "permanent"
            # Validate custom code format (alphanumeric, length 4-20)
            if not (4 <= len(code) <= 20 and code.isalnum()):
                await update.message.reply_text("❌ Invalid custom code format!\n\nRequirements:\n• 4-20 characters\n• Alphanumeric only (A-Z, 0-9)\n• No special characters")
                return
    elif len(context.args) == 2:
        code_arg = context.args[0].upper()
        arg2 = context.args[1].lower()

        # Validate custom code format
        if not (4 <= len(code_arg) <= 20 and code_arg.isalnum()):
            await update.message.reply_text("❌ Invalid custom code format!\n\nRequirements:\n• 4-20 characters\n• Alphanumeric only (A-Z, 0-9)\n• No special characters")
            return

        if arg2 in available_ranks:
            # Custom code with specific rank
            code = code_arg
            rank = arg2
            duration = 0
            duration_text = "permanent"
        elif arg2 in duration_options:
            # Custom code with specific duration
            code = code_arg
            rank = 'private_owner'
            duration = duration_options[arg2]
            duration_text = arg2 if arg2 != 'permanent' else 'permanent'
        else:
            await update.message.reply_text(f"❌ Invalid second parameter!\n\nAvailable ranks: {', '.join(available_ranks)}\nAvailable durations: {', '.join(duration_options.keys())}")
            return
    elif len(context.args) == 3:
        code_arg = context.args[0].upper()
        rank_arg = context.args[1].lower()
        duration_arg = context.args[2].lower()

        # Validate custom code format
        if not (4 <= len(code_arg) <= 20 and code_arg.isalnum()):
            await update.message.reply_text("❌ Invalid custom code format!\n\nRequirements:\n• 4-20 characters\n• Alphanumeric only (A-Z, 0-9)\n• No special characters")
            return

        # Validate rank
        if rank_arg not in available_ranks:
            await update.message.reply_text(f"❌ Invalid rank!\n\nAvailable ranks: {', '.join(available_ranks)}")
            return

        # Validate duration
        if duration_arg not in duration_options:
            await update.message.reply_text(f"❌ Invalid duration!\n\nAvailable durations: {', '.join(duration_options.keys())}")
            return

        code = code_arg
        rank = rank_arg
        duration = duration_options[duration_arg]
        duration_text = duration_arg if duration_arg != 'permanent' else 'permanent'
    else:
        await update.message.reply_text("❌ Too many arguments!\n\nUsage:\n• /generate_code (random code, default settings)\n• /generate_code [rank] (random code with rank)\n• /generate_code [duration] (random code with duration)\n• /generate_code [custom_code] (custom code, default settings)\n• /generate_code [custom_code] [rank] (custom code with rank)\n• /generate_code [custom_code] [duration] (custom code with duration)\n• /generate_code [custom_code] [rank] [duration] (full customization)")
        return

    # Check if code already exists
    existing_code = database.get_redeem_code(code)
    if existing_code:
        await update.message.reply_text(f"❌ Code `{code}` already exists!\n\nPlease choose a different code or use the existing one.")
        return

    # Calculate expiration time
    created_at = datetime.datetime.now().isoformat()
    if duration == 0:
        expires_at = None
    else:
        expires_at = (datetime.datetime.now() + datetime.timedelta(seconds=duration)).isoformat()

    # Store in database
    try:
        database.add_redeem_code(code, rank, duration, created_at, expires_at)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to save code to database: {e}")
        return

    # Format rank name for display
    rank_display = {
        'private_owner': 'Private Owner',
        'e_rank': 'E-Rank',
        'd_rank': 'D-Rank',
        'a_rank': 'A-Rank',
        's_rank': 'S-Rank',
        'monarch_rank': 'Monarch-Rank'
    }.get(rank, rank)

    # Success message
    success_message = f"""✅ **Redeem Code Generated Successfully!**

🔑 **Code:** `{code}`
👑 **Rank:** {rank_display}
⏰ **Duration:** {duration_text}

📝 **Usage Instructions:**
• Send this code to users
• Users redeem with `/redeem {code}` in private groups
• Code can only be used once
• Works only in groups without usernames

⚠️ **Important:** Keep this code secure and share responsibly!"""

    await update.message.reply_text(success_message, parse_mode='Markdown')

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

async def list_codes(update: Update, context):
    user = update.effective_user
    if user.id != OWNER_ID:
        await update.message.reply_text("This command is for the owner only.")
        return

    try:
        conn = sqlite3.connect(database.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT code, rank, duration, created_at, expires_at, used, banned FROM redeem_codes ORDER BY created_at DESC')
        codes = cursor.fetchall()
        conn.close()
    except Exception as e:
        await update.message.reply_text(f"Database error: {e}")
        return

    if not codes:
        await update.message.reply_text("No redeem codes found.")
        return

    # Format rank names for display
    rank_display = {
        'private_owner': 'Private Owner',
        'e_rank': 'E-Rank',
        'd_rank': 'D-Rank',
        'a_rank': 'A-Rank',
        's_rank': 'S-Rank',
        'monarch_rank': 'Monarch-Rank'
    }

    message = "📋 **Your Redeem Codes:**\n\n"
    active_count = 0
    used_count = 0
    expired_count = 0

    import datetime
    now = datetime.datetime.now()

    for code_data in codes:
        code, rank, duration, created_at, expires_at, used, banned = code_data

        # Skip banned codes
        if banned:
            continue

        rank_name = rank_display.get(rank, rank)

        # Check status
        status = "✅ Active"
        if used:
            status = "❌ Used"
            used_count += 1
        elif expires_at and datetime.datetime.fromisoformat(expires_at) < now:
            status = "⏰ Expired"
            expired_count += 1
        else:
            active_count += 1

        # Format duration
        if duration == 0:
            duration_text = "Permanent"
        else:
            duration_text = f"{duration // (24*60*60)}d" if duration >= 24*60*60 else f"{duration // (60*60)}h" if duration >= 60*60 else f"{duration // 60}m"

        message += f"🔑 `{code}`\n"
        message += f"👑 {rank_name} | ⏰ {duration_text}\n"
        message += f"📊 {status}\n\n"

    # Add summary
    summary = f"📈 **Summary:**\n"
    summary += f"✅ Active: {active_count}\n"
    summary += f"❌ Used: {used_count}\n"
    summary += f"⏰ Expired: {expired_count}\n"
    summary += f"📊 Total: {active_count + used_count + expired_count}"

    # Split message if too long
    if len(message + summary) > 4000:
        # Send codes first
        await update.message.reply_text(message[:3500] + "...", parse_mode='Markdown')
        # Send summary separately
        await update.message.reply_text(summary, parse_mode='Markdown')
    else:
        await update.message.reply_text(message + summary, parse_mode='Markdown')

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

async def broadcast(update: Update, context):
    user = update.effective_user
    if user.id != OWNER_ID:
        await update.message.reply_text("This command is for the owner only.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("""📢 **Broadcast Usage:**

- `/broadcast groups <message>` - Send to all groups
- `/broadcast users <message>` - Send to all users
- `/broadcast group <group_id> <message>` - Send to specific group
- `/broadcast preview <type> <message>` - Preview broadcast

**Formatting Options:**
- Use `**bold**` for bold text
- Use `*italic*` for italic text
- Use `` `code` `` for inline code
- Use ``` for code blocks
- Use [text](url) for links

**Examples:**
- `/broadcast groups Hello everyone!`
- `/broadcast users **Important update:** New features available!`
- `/broadcast group -1001234567890 Hello specific group!`
- `/broadcast preview groups Hello world!`""", parse_mode='Markdown')
        return

    broadcast_type = context.args[0].lower()
    message = ' '.join(context.args[1:])

    if broadcast_type == 'preview':
        if len(context.args) < 3:
            await update.message.reply_text("Usage: /broadcast preview <type> <message>")
            return

        preview_type = context.args[1].lower()
        preview_message = ' '.join(context.args[2:])

        # Show preview
        preview_text = f"""📋 **Broadcast Preview**

🎯 **Target:** {preview_type.title()}
📝 **Message:**
{preview_message}

✅ **Send this broadcast?**
• Reply with `yes` to confirm
• Reply with `no` to cancel"""

        await update.message.reply_text(preview_text, parse_mode='Markdown')

        # Store broadcast data for confirmation
        context.user_data['pending_broadcast'] = {
            'type': preview_type,
            'message': preview_message,
            'timestamp': datetime.datetime.now().isoformat()
        }
        return

    # Handle direct broadcast (without preview)
    await perform_broadcast(update, context, broadcast_type, message)

async def confirm_broadcast(update: Update, context):
    user = update.effective_user
    if user.id != OWNER_ID:
        return

    if update.message.text.lower() in ['yes', 'y', 'confirm']:
        if 'pending_broadcast' not in context.user_data:
            await update.message.reply_text("❌ No pending broadcast found.")
            return

        broadcast_data = context.user_data['pending_broadcast']
        await perform_broadcast(update, context, broadcast_data['type'], broadcast_data['message'])

        # Clear pending broadcast
        del context.user_data['pending_broadcast']

    elif update.message.text.lower() in ['no', 'n', 'cancel']:
        if 'pending_broadcast' in context.user_data:
            del context.user_data['pending_broadcast']
        await update.message.reply_text("❌ Broadcast cancelled.")
    else:
        return  # Not a confirmation response

async def perform_broadcast(update: Update, context, broadcast_type, message):
    try:
        # Get target list based on type
        if broadcast_type == 'groups':
            targets = await get_all_groups(context.bot)
            target_name = "groups"
        elif broadcast_type == 'users':
            targets = await get_all_users()
            target_name = "users"
        elif broadcast_type == 'group':
            # Extract group ID from message
            parts = message.split(' ', 1)
            if len(parts) < 2:
                await update.message.reply_text("❌ Usage: /broadcast group <group_id> <message>")
                return
            group_id = parts[0]
            message = parts[1]
            targets = [int(group_id)]
            target_name = f"group {group_id}"
        else:
            await update.message.reply_text("❌ Invalid broadcast type. Use: groups, users, or group")
            return

        if not targets:
            await update.message.reply_text(f"❌ No {target_name} found to broadcast to.")
            return

        # Start broadcast
        status_msg = await update.message.reply_text(f"📢 Starting broadcast to {len(targets)} {target_name}...")

        success_count = 0
        fail_count = 0
        failed_targets = []

        # Send to each target
        for i, target in enumerate(targets):
            try:
                if broadcast_type in ['groups', 'group']:
                    await context.bot.send_message(chat_id=target, text=message, parse_mode='Markdown')
                else:  # users
                    await context.bot.send_message(chat_id=target, text=message, parse_mode='Markdown')

                success_count += 1

                # Update progress every 10 sends or at the end
                if (i + 1) % 10 == 0 or i == len(targets) - 1:
                    progress = (i + 1) / len(targets) * 100
                    await status_msg.edit_text(
                        f"📢 Broadcasting... {i + 1}/{len(targets)} ({progress:.1f}%)\n"
                        f"✅ Success: {success_count}\n"
                        f"❌ Failed: {fail_count}"
                    )

            except Exception as e:
                fail_count += 1
                failed_targets.append(f"{target} ({str(e)[:50]})")

        # Final status
        final_message = f"""📢 **Broadcast Complete!**

🎯 **Target:** {target_name}
📊 **Results:**
✅ **Success:** {success_count}
❌ **Failed:** {fail_count}
📈 **Success Rate:** {success_count/(success_count+fail_count)*100:.1f}%

📝 **Message Sent:**
{message}"""

        if failed_targets:
            final_message += f"\n\n⚠️ **Failed Targets:**\n" + "\n".join(failed_targets[:5])  # Show first 5 failures
            if len(failed_targets) > 5:
                final_message += f"\n... and {len(failed_targets) - 5} more"

        await status_msg.edit_text(final_message, parse_mode='Markdown')

        # Log broadcast
        log_broadcast(broadcast_type, message, success_count, fail_count, len(targets))

    except Exception as e:
        await update.message.reply_text(f"❌ Broadcast failed: {str(e)}")

async def get_all_groups(bot):
    """Get all group chats the bot is in"""
    groups = []
    try:
        # Get bot's chat list (this is a simplified approach)
        # In a real implementation, you'd need to track groups in database
        # For now, we'll use a placeholder that returns some example groups
        # You should implement proper group tracking in your database

        conn = sqlite3.connect(database.DATABASE_PATH)
        cursor = conn.cursor()

        # Get unique chat_ids from users table where chat_id is not None
        cursor.execute("SELECT DISTINCT chat_id FROM users WHERE chat_id IS NOT NULL")
        group_rows = cursor.fetchall()
        conn.close()

        groups = [row[0] for row in group_rows if row[0] < 0]  # Negative IDs are groups/channels

    except Exception as e:
        print(f"Error getting groups: {e}")

    return groups

async def get_all_users():
    """Get all users who have interacted with the bot"""
    users = []
    try:
        conn = sqlite3.connect(database.DATABASE_PATH)
        cursor = conn.cursor()

        # Get all unique user IDs
        cursor.execute("SELECT DISTINCT id FROM users")
        user_rows = cursor.fetchall()
        conn.close()

        users = [row[0] for row in user_rows]

    except Exception as e:
        print(f"Error getting users: {e}")

    return users

def log_broadcast(broadcast_type, message, success_count, fail_count, total_count):
    """Log broadcast details to database"""
    try:
        conn = sqlite3.connect(database.DATABASE_PATH)
        cursor = conn.cursor()

        # Create broadcasts table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS broadcasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                message TEXT,
                success_count INTEGER,
                fail_count INTEGER,
                total_count INTEGER,
                timestamp TEXT
            )
        ''')

        # Log the broadcast
        cursor.execute('''
            INSERT INTO broadcasts (type, message, success_count, fail_count, total_count, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (broadcast_type, message, success_count, fail_count, total_count, datetime.datetime.now().isoformat()))

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error logging broadcast: {e}")

async def broadcast_history(update: Update, context):
    user = update.effective_user
    if user.id != OWNER_ID:
        await update.message.reply_text("This command is for the owner only.")
        return

    try:
        conn = sqlite3.connect(database.DATABASE_PATH)
        cursor = conn.cursor()

        # Get recent broadcasts
        cursor.execute('''
            SELECT type, success_count, fail_count, total_count, timestamp
            FROM broadcasts
            ORDER BY timestamp DESC LIMIT 10
        ''')
        broadcasts = cursor.fetchall()
        conn.close()

        if not broadcasts:
            await update.message.reply_text("📋 No broadcast history found.")
            return

        message = "📋 **Broadcast History (Last 10):**\n\n"

        for broadcast in broadcasts:
            broadcast_type, success, fail, total, timestamp = broadcast
            success_rate = success / (success + fail) * 100 if (success + fail) > 0 else 0

            # Format timestamp
            dt = datetime.datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%Y-%m-%d %H:%M")

            message += f"📢 **{broadcast_type.title()}** - {time_str}\n"
            message += f"✅ {success}/{total} ({success_rate:.1f}% success)\n\n"

        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Error retrieving broadcast history: {e}")

# Handler
contact_handler = CommandHandler("contact_owner", contact_owner)
owner_reply_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, owner_reply)
generate_code_handler = CommandHandler("generate_code", generate_code)
set_custom_title_handler = CommandHandler("set_title", set_custom_title)
delete_code_handler = CommandHandler("delete_code", delete_code)
list_codes_handler = CommandHandler("list_codes", list_codes)
ban_user_handler = CommandHandler("ban_user", ban_user)
unban_user_handler = CommandHandler("unban_user", unban_user)
broadcast_handler = CommandHandler("broadcast", broadcast)
broadcast_confirm_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_broadcast)
broadcast_history_handler = CommandHandler("broadcast_history", broadcast_history)
