import sqlite3
from config import DATABASE_PATH

def create_tables():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            rank TEXT DEFAULT 'member',
            custom_title TEXT,
            rating INTEGER DEFAULT 0,
            join_date TEXT,
            last_active TEXT,
            messages_count INTEGER DEFAULT 0,
            chat_id INTEGER,
            last_message_time TEXT
        )
    ''')

    # Add missing columns if they don't exist
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN chat_id INTEGER')
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        cursor.execute('ALTER TABLE users ADD COLUMN last_message_time TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Bans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            reason TEXT,
            duration INTEGER,  -- in seconds, 0 for permanent
            moderator_id INTEGER,
            timestamp TEXT,
            group_id INTEGER
        )
    ''')

    # Reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reporter_id INTEGER,
            reported_id INTEGER,
            reason TEXT,
            timestamp TEXT,
            group_id INTEGER,
            status TEXT DEFAULT 'pending'
        )
    ''')

    # Actions table for logging mod actions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            moderator_id INTEGER,
            action_type TEXT,  -- ban, kick, mute, etc.
            user_id INTEGER,
            reason TEXT,
            timestamp TEXT,
            group_id INTEGER
        )
    ''')

    # Stats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            messages_count INTEGER DEFAULT 0,
            date TEXT
        )
    ''')

    # Invite links table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invite_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link TEXT,
            creator_id INTEGER,
            used_by INTEGER,
            timestamp TEXT,
            group_id INTEGER
        )
    ''')

    # Redeem codes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS redeem_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            rank TEXT DEFAULT 'private_owner',  -- specific rank to grant
            duration INTEGER,  -- in seconds, 0 for permanent
            created_at TEXT,
            expires_at TEXT,
            used INTEGER DEFAULT 0,
            banned INTEGER DEFAULT 0
        )
    ''')

    # Banned users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS banned_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            reason TEXT,
            banned_at TEXT,
            banned_by INTEGER
        )
    ''')

    # Warnings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            chat_id INTEGER,
            reason TEXT,
            warned_by INTEGER,
            warned_at TEXT
        )
    ''')

    # Filters table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS filters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            trigger_word TEXT,
            reply_text TEXT,
            created_by INTEGER,
            created_at TEXT
        )
    ''')

    # Group settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER UNIQUE,
            welcome_enabled INTEGER DEFAULT 1,
            welcome_message TEXT DEFAULT 'Welcome {user} to {chat}!',
            goodbye_enabled INTEGER DEFAULT 1,
            goodbye_message TEXT DEFAULT 'Goodbye {user}!',
            rules_text TEXT DEFAULT 'Please follow the group rules.',
            private_rules INTEGER DEFAULT 0,
            disabled_commands TEXT DEFAULT '',
            disable_admin INTEGER DEFAULT 0
        )
    ''')



    # Mutes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mutes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            chat_id INTEGER,
            reason TEXT,
            muted_by INTEGER,
            muted_at TEXT,
            unmute_at TEXT
        )
    ''')

    conn.commit()
    conn.close()

def migrate_database():
    """Migrate database schema to latest version"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check if redeem_codes table has rank column
    try:
        cursor.execute("SELECT rank FROM redeem_codes LIMIT 1")
    except sqlite3.OperationalError:
        # rank column doesn't exist, need to recreate table
        print("Migrating redeem_codes table to add rank column...")

        # Backup existing data
        cursor.execute("SELECT code, duration, created_at, expires_at, used FROM redeem_codes")
        old_data = cursor.fetchall()

        # Drop and recreate table
        cursor.execute("DROP TABLE redeem_codes")

        cursor.execute('''
            CREATE TABLE redeem_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                rank TEXT DEFAULT 'private_owner',
                duration INTEGER,
                created_at TEXT,
                expires_at TEXT,
                used INTEGER DEFAULT 0,
                banned INTEGER DEFAULT 0
            )
        ''')

        # Restore data with default rank
        for row in old_data:
            code, duration, created_at, expires_at, used = row
            cursor.execute('''
                INSERT INTO redeem_codes (code, rank, duration, created_at, expires_at, used, banned)
                VALUES (?, 'private_owner', ?, ?, ?, ?, 0)
            ''', (code, duration, created_at, expires_at, used))

        print("Migration completed successfully!")

    conn.commit()
    conn.close()

# Helper functions for database operations
def add_user(user_id, username, first_name, join_date):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (id, username, first_name, join_date) VALUES (?, ?, ?, ?)',
                   (user_id, username, first_name, join_date))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_rank(user_id, rank):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET rank = ? WHERE id = ?', (rank, user_id))
    conn.commit()
    conn.close()

def get_user_rank(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT rank FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def update_user_custom_title(user_id, custom_title):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET custom_title = ? WHERE id = ?', (custom_title, user_id))
    conn.commit()
    conn.close()

def get_user_custom_title(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT custom_title FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def add_ban(user_id, reason, duration, moderator_id, group_id, timestamp):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO bans (user_id, reason, duration, moderator_id, timestamp, group_id) VALUES (?, ?, ?, ?, ?, ?)',
                   (user_id, reason, duration, moderator_id, timestamp, group_id))
    conn.commit()
    conn.close()

def add_report(reporter_id, reported_id, reason, group_id, timestamp):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO reports (reporter_id, reported_id, reason, group_id, timestamp) VALUES (?, ?, ?, ?, ?)',
                   (reporter_id, reported_id, reason, group_id, timestamp))
    conn.commit()
    conn.close()

def log_action(moderator_id, action_type, user_id, reason, group_id, timestamp):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO actions (moderator_id, action_type, user_id, reason, group_id, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
                   (moderator_id, action_type, user_id, reason, group_id, timestamp))
    conn.commit()
    conn.close()

def add_redeem_code(code, rank, duration, created_at, expires_at):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO redeem_codes (code, rank, duration, created_at, expires_at) VALUES (?, ?, ?, ?, ?)',
                   (code, rank, duration, created_at, expires_at))
    conn.commit()
    conn.close()

def get_redeem_code(code):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM redeem_codes WHERE code = ?', (code,))
    result = cursor.fetchone()
    conn.close()
    return result

def mark_redeem_code_used(code):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE redeem_codes SET used = 1 WHERE code = ?', (code,))
    conn.commit()
    conn.close()

def update_user_message_count(user_id, chat_id, message_time):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check if user exists in this chat
    cursor.execute('SELECT messages_count FROM users WHERE id = ? AND chat_id = ?', (user_id, chat_id))
    result = cursor.fetchone()

    if result:
        # Update existing user
        cursor.execute('''
            UPDATE users
            SET messages_count = messages_count + 1, last_message_time = ?
            WHERE id = ? AND chat_id = ?
        ''', (message_time, user_id, chat_id))
    else:
        # Add new user for this chat
        cursor.execute('''
            INSERT INTO users (id, chat_id, messages_count, last_message_time, join_date)
            VALUES (?, ?, 1, ?, ?)
        ''', (user_id, chat_id, message_time, message_time))

    conn.commit()
    conn.close()

def get_user_stats(user_id, chat_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT messages_count, last_message_time FROM users WHERE id = ? AND chat_id = ?',
                   (user_id, chat_id))
    result = cursor.fetchone()
    conn.close()
    return result

# New helper functions for additional features

def add_warning(user_id, chat_id, reason, warned_by, warned_at):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO warnings (user_id, chat_id, reason, warned_by, warned_at) VALUES (?, ?, ?, ?, ?)',
                   (user_id, chat_id, reason, warned_by, warned_at))
    conn.commit()
    conn.close()

def get_user_warnings(user_id, chat_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM warnings WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def remove_user_warnings(user_id, chat_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM warnings WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
    conn.commit()
    conn.close()

def add_filter(chat_id, trigger_word, reply_text, created_by, created_at):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO filters (chat_id, trigger_word, reply_text, created_by, created_at) VALUES (?, ?, ?, ?, ?)',
                   (chat_id, trigger_word, reply_text, created_by, created_at))
    conn.commit()
    conn.close()

def get_filters(chat_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT trigger_word, reply_text FROM filters WHERE chat_id = ?', (chat_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def remove_filter(chat_id, trigger_word):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM filters WHERE chat_id = ? AND trigger_word = ?', (chat_id, trigger_word))
    conn.commit()
    conn.close()

def get_group_settings(chat_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM group_settings WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_group_settings(chat_id, **kwargs):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check if settings exist
    cursor.execute('SELECT id FROM group_settings WHERE chat_id = ?', (chat_id,))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO group_settings (chat_id) VALUES (?)', (chat_id,))

    # Update settings
    set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
    values = list(kwargs.values()) + [chat_id]
    cursor.execute(f'UPDATE group_settings SET {set_clause} WHERE chat_id = ?', values)
    conn.commit()
    conn.close()



def add_mute(user_id, chat_id, reason, muted_by, muted_at, unmute_at):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO mutes (user_id, chat_id, reason, muted_by, muted_at, unmute_at) VALUES (?, ?, ?, ?, ?, ?)',
                   (user_id, chat_id, reason, muted_by, muted_at, unmute_at))
    conn.commit()
    conn.close()

def get_active_mute(user_id, chat_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mutes WHERE user_id = ? AND chat_id = ? AND unmute_at > datetime("now")',
                   (user_id, chat_id))
    result = cursor.fetchone()
    conn.close()
    return result

def remove_mute(user_id, chat_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM mutes WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
    conn.commit()
    conn.close()

# Initialize database
create_tables()
migrate_database()
