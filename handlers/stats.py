from telegram import Update
from telegram.ext import CommandHandler
import database
import sqlite3
from config import DATABASE_PATH
import io

async def stats(update: Update, context):
    chat = update.effective_chat
    if not chat or chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command is for groups only.")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Get chat member count
    try:
        chat_info = await context.bot.get_chat(chat.id)
        member_count = chat_info.members_count
    except:
        member_count = "Unable to fetch"

    # Top active users in this chat
    cursor.execute('''
        SELECT username, messages_count FROM users
        WHERE chat_id = ? AND messages_count > 0
        ORDER BY messages_count DESC LIMIT 10
    ''', (chat.id,))
    top_users = cursor.fetchall()

    # Rank distribution
    cursor.execute('''
        SELECT rank, COUNT(*) as count FROM users
        WHERE chat_id = ? AND rank IS NOT NULL
        GROUP BY rank ORDER BY count DESC
    ''', (chat.id,))
    rank_distribution = cursor.fetchall()

    # Total messages in this chat
    cursor.execute('SELECT SUM(messages_count) FROM users WHERE chat_id = ?', (chat.id,))
    total_messages = cursor.fetchone()[0] or 0

    # Active users count (users with messages > 0)
    cursor.execute('SELECT COUNT(*) FROM users WHERE chat_id = ? AND messages_count > 0', (chat.id,))
    active_users = cursor.fetchone()[0] or 0

    # Recent activity (last 24 hours)
    cursor.execute('''
        SELECT COUNT(*) FROM users
        WHERE chat_id = ? AND last_message_time > datetime('now', '-1 day')
    ''', (chat.id,))
    recent_active = cursor.fetchone()[0] or 0

    conn.close()

    # Build comprehensive stats message
    stats_text = f"📊 **Group Statistics for {chat.title}**\n\n"

    # Basic info
    stats_text += f"👥 **Members:** {member_count}\n"
    stats_text += f"💬 **Total Messages:** {total_messages:,}\n"
    stats_text += f"🎯 **Active Users:** {active_users}\n"
    stats_text += f"⚡ **Recent Activity (24h):** {recent_active}\n\n"

    # Top active users
    if top_users:
        stats_text += "🏆 **Top Active Users:**\n"
        for i, (username, count) in enumerate(top_users, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "⭐"
            stats_text += f"{medal} {i}. {username or 'Unknown'}: {count:,} messages\n"
        stats_text += "\n"

    # Rank distribution
    if rank_distribution:
        stats_text += "👑 **Rank Distribution:**\n"
        for rank, count in rank_distribution:
            rank_name = rank.replace('_', ' ').title()
            stats_text += f"• {rank_name}: {count} users\n"
        stats_text += "\n"

    # Activity insights
    if member_count != "Unable to fetch" and active_users > 0:
        activity_rate = (active_users / member_count) * 100
        stats_text += f"📈 **Activity Rate:** {activity_rate:.1f}%\n"

    stats_text += f"⏰ **Generated:** {update.message.date.strftime('%Y-%m-%d %H:%M:%S UTC')}"

    await update.message.reply_text(stats_text, parse_mode='Markdown')

    # Generate detailed stats file
    detailed_stats = f"""📊 DETAILED GROUP STATISTICS
Group: {chat.title}
Generated: {update.message.date.strftime('%Y-%m-%d %H:%M:%S UTC')}

=== BASIC METRICS ===
Members: {member_count}
Total Messages: {total_messages:,}
Active Users: {active_users}
Recent Activity (24h): {recent_active}

=== TOP ACTIVE USERS ===
"""
    for i, (username, count) in enumerate(top_users, 1):
        detailed_stats += f"{i}. {username or 'Unknown'}: {count:,} messages\n"

    detailed_stats += "\n=== RANK DISTRIBUTION ===\n"
    for rank, count in rank_distribution:
        rank_name = rank.replace('_', ' ').title()
        detailed_stats += f"{rank_name}: {count} users\n"

    # Send as file
    stats_file = io.BytesIO(detailed_stats.encode('utf-8'))
    stats_file.name = f'{chat.title}_stats.txt'.replace(' ', '_')
    await update.message.reply_document(
        document=stats_file,
        filename=f'{chat.title}_stats.txt'.replace(' ', '_'),
        caption="📄 Detailed statistics file"
    )

# Handler
stats_handler = CommandHandler("stats", stats)
