from telegram import Update, Poll, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import CommandHandler, InlineQueryHandler
from config import AUTO_DELETE_TIME, OWNER_ID, REDEEM_CODES, RANKS
import database
from handlers.promotions import rank_permissions

async def rules(update: Update, context):
    rules_text = """
📜 Group Rules (Managed by the Bot) 📜

Respect Everyone

No harassment, hate speech, personal attacks, or discrimination.

Treat all members with courtesy.

No Spam or Flooding

Avoid repeated messages, irrelevant links, or excessive emojis.

Do not spam mentions or flood chats.

Relevant Content Only

Stay on-topic as per the group’s purpose.

Off-topic or promotional content requires moderator approval.

No NSFW or Illegal Content

Strictly prohibited: adult content, pirated material, hacking, or anything illegal.

Follow Moderator Instructions

Respect decisions made by admins/mods.

Arguing with moderators may lead to penalties.

No Self-Promotion Without Permission

Advertising, external links, or group invites are only allowed with owner/admin approval.

Report Misconduct

Use /report @user reason to notify moderators of rule-breaking behavior.

Bot & Feature Respect

Do not misuse commands or disrupt bot functions.

Abusing bot features can lead to warnings or bans.

Privacy & Security

Do not share personal data, doxxing, or sensitive info.

Stay safe — the group is not responsible for personal transactions.

Consequences

Warnings → Temporary Ban → Permanent Ban (based on severity).

Final authority lies with the Owner (@Oeba7).

✨ These rules are enforced automatically and manually by the Group Management Bot to maintain a safe and respectful environment.
    """
    await update.message.reply_text(rules_text)

async def announce(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat
    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command is for groups only.")
        return

    # Check if owner or admin
    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if user.id != OWNER_ID and chat_member.status not in ['administrator', 'creator']:
        await update.message.reply_text("You don't have permission to announce.")
        return

    message = ' '.join(context.args)
    if not message:
        await update.message.reply_text("Usage: /announce your message")
        return

    await context.bot.send_message(chat.id, f"📢 Announcement: {message}")

async def poll_command(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat
    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command is for groups only.")
        return

    # Check permissions
    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if user.id != OWNER_ID and chat_member.status not in ['administrator', 'creator']:
        await update.message.reply_text("You don't have permission to create polls.")
        return

    args = context.args
    if len(args) < 3:
        await update.message.reply_text("Usage: /poll question option1 option2 ...")
        return

    question = args[0]
    options = args[1:]

    poll = await context.bot.send_poll(chat.id, question, options)
    # Note: Poll results can be handled separately if needed

async def ranks_command(update: Update, context):
    ranks_text = """
⚔️ Group Management Bot – Ranking System ⚔️
Inspired by Solo Leveling, each rank unlocks greater powers within the group.

🪶 E-Rank (Lowest)
Basic admin abilities.
🗑️ Delete messages
🔗 Invite users via group link

🔥 D-Rank (Includes all E-Rank powers)
📌 Pin messages
🎥 Manage live streams

⚡ A-Rank (Includes all D + E powers)
📖 Manage stories
🎥 Full control of live streams
🚫 Ban and restrict users

👑 S-Rank (Includes all A + D + E powers)
➕ Add and assign new admins
🚫 Ban and restrict users

🌌 Monarch-Rank (Highest) (Includes all S + A + D + E powers)
🛡️ Ultimate authority in the group
⚙️ Full control over group settings and management

🔒 Private Owner (Special rank for private groups)
👑 Full access in private groups
⚙️ Limited level but complete control in private chats

✨ A hierarchy built for order, power, and balance — only the worthy ascend.
🔑 Redeem special codes with /redeem for exclusive ranks in private groups!
✍️ Created by @Oeba7
    """
    await update.message.reply_text(ranks_text)

async def inline_query(update: Update, context):
    query = update.inline_query.query.lower()
    results = []

    if query == 'rules':
        rules_text = """
        Group Rules:
        1. No spam or flooding.
        2. No links without permission.
        3. Respect all members.
        4. Report issues to mods.
        """
        results.append(InlineQueryResultArticle(
            id='rules',
            title='Group Rules',
            input_message_content=InputTextMessageContent(rules_text)
        ))
    elif query == 'stats':
        stats_text = "Group Stats: Use /stats command for detailed stats."
        results.append(InlineQueryResultArticle(
            id='stats',
            title='Group Stats',
            input_message_content=InputTextMessageContent(stats_text)
        ))
    elif query == 'ranks':
        ranks_text = """
⚔️ Group Management Bot – Ranking System ⚔️
Inspired by Solo Leveling, each rank unlocks greater powers within the group.

🪶 E-Rank (Lowest)
Basic admin abilities.
🗑️ Delete messages
🔗 Invite users via group link

🔥 D-Rank (Includes all E-Rank powers)
📌 Pin messages
🎥 Manage live streams

⚡ A-Rank (Includes all D + E powers)
📖 Manage stories
🎥 Full control of live streams

👑 S-Rank (Includes all A + D + E powers)
➕ Add and assign new admins
🚫 Ban and restrict users

🌌 Monarch-Rank (Highest) (Includes all S + A + D + E powers)
🛡️ Ultimate authority in the group
⚙️ Full control over group settings and management

🔒 Private Owner (Special rank for private groups)
👑 Full access in private groups
⚙️ Limited level but complete control in private chats

✨ A hierarchy built for order, power, and balance — only the worthy ascend.
✍️ Created by @Oeba7
        """
        results.append(InlineQueryResultArticle(
            id='ranks',
            title='Ranking System',
            input_message_content=InputTextMessageContent(ranks_text)
        ))

    await update.inline_query.answer(results)

async def redeem(update: Update, context):
    user = update.effective_user
    chat = update.effective_chat

    # Validate command usage
    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("❌ This command is for groups only.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("❌ Usage: /redeem CODE\n\nExample: /redeem ABC123XYZ")
        return

    code = context.args[0].upper().strip()

    # Validate code format
    if not (4 <= len(code) <= 20 and code.isalnum()):
        await update.message.reply_text("❌ Invalid code format!\n\nRequirements:\n• 4-20 characters\n• Alphanumeric only (A-Z, 0-9)")
        return

    # Check if group is private (no username)
    if chat.username:
        await update.message.reply_text("❌ This command is only for private groups.\n\nPrivate groups don't have usernames and are invite-only.")
        return

    # Get code from database
    try:
        code_data = database.get_redeem_code(code)
    except Exception as e:
        await update.message.reply_text(f"❌ Database error: {e}")
        return

    if not code_data:
        await update.message.reply_text(f"❌ Code `{code}` not found.\n\nMake sure you entered the code correctly.")
        return

    # Check if code is banned/deleted
    if code_data[6] == 1:  # banned column
        await update.message.reply_text("❌ This code has been deactivated by the owner.")
        return

    # Check if code is already used
    if code_data[5] == 1:  # used column
        await update.message.reply_text("❌ This code has already been redeemed by another user.")
        return

    # Check if code is expired
    import datetime
    if code_data[4]:
        try:
            # Handle different date formats that might exist in the database
            expires_at_str = str(code_data[4]).strip()
            if expires_at_str.lower() in ['none', 'null', '']:
                # No expiration date set
                pass
            else:
                # Try to parse the date
                try:
                    expires_at = datetime.datetime.fromisoformat(expires_at_str)
                except ValueError:
                    # Try alternative formats if isoformat fails
                    try:
                        expires_at = datetime.datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S.%f")
                    except ValueError:
                        try:
                            expires_at = datetime.datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            # If all parsing fails, treat as not expired to avoid blocking valid codes
                            print(f"Warning: Could not parse expiration date '{expires_at_str}' for code {code}, treating as not expired")
                            pass
                        else:
                            if expires_at < datetime.datetime.now():
                                await update.message.reply_text("❌ This code has expired.")
                                return
                    else:
                        if expires_at < datetime.datetime.now():
                            await update.message.reply_text("❌ This code has expired.")
                            return
                else:
                    if expires_at < datetime.datetime.now():
                        await update.message.reply_text("❌ This code has expired.")
                        return
        except Exception as e:
            # If any other error occurs, treat as not expired to avoid blocking valid codes
            print(f"Warning: Error checking expiration for code {code}: {e}, treating as not expired")
            pass

    # Get the specific rank from the code
    rank = code_data[2]  # rank column from database
    if rank not in RANKS:
        await update.message.reply_text("❌ Invalid rank associated with this code.")
        return

    # Mark code as used (do this early to prevent race conditions)
    try:
        database.mark_redeem_code_used(code)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to process code: {e}")
        return

    # Update user rank in database
    try:
        database.update_user_rank(user.id, rank)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to update rank: {e}")
        return

    # Check if user is already the owner of the group
    try:
        chat_member = await context.bot.get_chat_member(chat.id, user.id)
        if chat_member.status == 'creator':
            # User is already the owner, just update database and notify
            rank_name = RANKS.get(rank, "member")
            await context.bot.send_message(
                chat.id,
                f"🎉 @{user.username or user.first_name} has redeemed a code and been promoted to {rank_name}!"
            )
            await update.message.reply_text(f"✅ Redeemed successfully!\n\nYou are now {rank_name} in this private group.")
            return
    except Exception as e:
        # If we can't check membership, log the error but continue
        print(f"Warning: Could not check chat membership for user {user.id}: {e}")

    # Try to promote with permissions
    promotion_success = False
    if rank in rank_permissions:
        try:
            await context.bot.promote_chat_member(
                chat.id,
                user.id,
                **rank_permissions[rank]
            )
            promotion_success = True
        except Exception as e:
            error_message = str(e).lower()
            if "can't remove chat owner" in error_message or "can't demote chat creator" in error_message:
                # User is owner, promotion not needed
                promotion_success = True
            else:
                print(f"Warning: Failed to promote user {user.id} to {rank}: {e}")
                # Continue anyway since database was updated

    # Send success message to group
    rank_name = RANKS.get(rank, "member")
    if promotion_success:
        await context.bot.send_message(
            chat.id,
            f"🎉 @{user.username or user.first_name} has redeemed a code and been promoted to {rank_name}!\n\nWelcome to your new rank! 🚀"
        )
    else:
        await context.bot.send_message(
            chat.id,
            f"🎉 @{user.username or user.first_name} has redeemed a code!\n\nRank updated to {rank_name} (some permissions may need manual adjustment)."
        )

    # Send confirmation to user
    success_message = f"""✅ **Code Redeemed Successfully!**

🎊 **Congratulations!**
👑 **New Rank:** {rank_name}
📍 **Group:** {chat.title}

⚡ **Your new powers are now active!**

💡 **Tip:** Use /ranks to see what you can do with your new rank."""

    await update.message.reply_text(success_message, parse_mode='Markdown')

# Handlers
rules_handler = CommandHandler("rules", rules)
announce_handler = CommandHandler("announce", announce)
poll_handler = CommandHandler("poll", poll_command)
ranks_handler = CommandHandler("ranks", ranks_command)
inline_handler = InlineQueryHandler(inline_query)
redeem_handler = CommandHandler("redeem", redeem)
