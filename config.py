# Configuration file for the Telegram Group Management Bot

# Replace with your bot token from @BotFather
TOKEN = '8346185001:AAFWkmga4aOPxPKbMtjM-bnp3FGedw5UNlw'

# Owner's Telegram user ID (replace with actual ID)
OWNER_ID = 6198639708

# Database file path
DATABASE_PATH = 'bot_database.db'

# Other settings
LOG_LEVEL = 'INFO'
MAX_MESSAGE_LENGTH = 4096
CAPTCHA_TIMEOUT = 300  # seconds
AUTO_DELETE_TIME = 3600  # seconds for media auto-delete

# Custom ranks
RANKS = {
    'e_rank': 'E-Rank',
    'd_rank': 'D-Rank',
    'a_rank': 'A-Rank',
    's_rank': 'S-Rank',
    'monarch_rank': 'Monarch-Rank',
    'private_owner': 'Private Owner'
}

# Spam settings
SPAM_THRESHOLD = 5  # messages per minute
FLOOD_THRESHOLD = 10  # messages per 10 seconds

# Blacklist words (example)
BLACKLIST_WORDS = ['spam', 'badword1', 'badword2']

# Redeem codes for private owner rank
REDEEM_CODES = ['PRIVATEOWNER2023', 'SPECIALCODE123', 'GROUPMASTER456']
