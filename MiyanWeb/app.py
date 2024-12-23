import telebot
import time
import hashlib
from flask import Flask, request, jsonify
from threading import Thread
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

# Load environment variables
load_dotenv()

def validate_env():
    required_vars = {
        'TELEGRAM_BOT_TOKEN': 'Telegram Bot Token is required',
        'MONGO_URI': 'MongoDB URI is required'
    }
    
    missing_vars = []
    for var, message in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(message)
    
    if missing_vars:
        raise EnvironmentError(
            "Missing required environment variables:\n" +
            "\n".join(f"- {msg}" for msg in missing_vars)
        )

# Validate environment variables
validate_env()

# Environment variables
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
KEY_EXPIRY_HOURS = int(os.getenv('KEY_EXPIRY_HOURS', 24))

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Initialize Flask app
app = Flask(__name__)

# Initialize MongoDB
client = MongoClient(MONGO_URI)
db = client['miyanbot']
keys_collection = db['keys']

# Helper function to format time duration
def format_time_duration(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    
    if not parts:
        return "0 seconds"
    
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    else:
        return f"{parts[0]}, {parts[1]} and {parts[2]}"

# MongoDB helper functions
def save_key(key, chat_id):
    expiry_time = datetime.now() + timedelta(hours=KEY_EXPIRY_HOURS)
    return keys_collection.insert_one({
        'key': key,
        'chat_id': chat_id,
        'created_at': datetime.now(),
        'expires_at': expiry_time,
        'is_used': False
    }).inserted_id

def validate_key(key):
    result = keys_collection.find_one_and_update(
        {
            'key': key,
            'is_used': False,
            'expires_at': {'$gt': datetime.now()}
        },
        {'$set': {'is_used': True, 'used_at': datetime.now()}},
        return_document=True
    )
    return result is not None

def clean_expired_keys():
    return keys_collection.delete_many({
        '$or': [
            {'expires_at': {'$lt': datetime.now()}},
            {'is_used': True}
        ]
    })

# Helper function to generate key
def generate_key(chat_id):
    timestamp = int(time.time())
    key = f"Miyan-{hashlib.md5(str(chat_id).encode()).hexdigest()}-{timestamp}"
    return key

# Bot command handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
    👋 Welcome to MiyanBot!
    
    Available commands:
    /help - Show this help message
    /key - Generate a unique access key
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
    📚 MiyanBot Commands:
    
    /start - Start the bot
    /help - Show this help message
    /key - Generate a unique access key
    /status - Check bot status
    /mykeys - View your active keys
    """
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['key'])
def key_command(message):
    key = generate_key(message.chat.id)
    save_key(key, message.chat.id)
    
    expiry_duration = KEY_EXPIRY_HOURS * 3600  # Convert hours to seconds
    formatted_expiry = format_time_duration(expiry_duration)
    
    response = f"""
    🔑 Your unique key has been generated!
    
    Key: `{key}`
    
    ⚠️ This key will expire in {formatted_expiry}.
    """
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def status_command(message):
    active_keys = keys_collection.count_documents({
        'is_used': False,
        'expires_at': {'$gt': datetime.now()}
    })
    
    status_text = f"""
    🟢 Bot Status: Online
    🕒 Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    🔑 Active Keys: {active_keys}
    """
    bot.reply_to(message, status_text)

@bot.message_handler(commands=['mykeys'])
def my_keys_command(message):
    user_keys = keys_collection.find({
        'chat_id': message.chat.id,
        'is_used': False,
        'expires_at': {'$gt': datetime.now()}
    })
    
    keys_list = list(user_keys)
    if not keys_list:
        bot.reply_to(message, "You have no active keys.")
        return
    
    response = "🔑 Your active keys:\n\n"
    for key_doc in keys_list:
        expires_in = key_doc['expires_at'] - datetime.now()
        seconds_remaining = expires_in.total_seconds()
        formatted_time = format_time_duration(seconds_remaining)
        response += f"• `{key_doc['key']}`\n  Expires in: {formatted_time}\n\n"
    
    bot.reply_to(message, response, parse_mode='Markdown')

# Handle unknown commands
# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
    # bot.reply_to(message, "❓ Unknown command. Use /help to see available commands.")

# Flask routes
@app.route('/login', methods=['GET'])
def login():
    key = request.args.get('key')
    
    if not key:
        return jsonify({"error": "No key provided"}), 400
        
    if validate_key(key):
        return "MiyanMei", 200
    else:
        return jsonify({"error": "Invalid or expired key"}), 401

@app.route('/health', methods=['GET'])
def health_check():
    try:
        db.command('ping')
        mongo_status = "connected"
    except Exception as e:
        mongo_status = f"error: {str(e)}"
    
    active_keys = keys_collection.count_documents({
        'is_used': False,
        'expires_at': {'$gt': datetime.now()}
    })
    
    return jsonify({
        "status": "healthy",
        "mongo_status": mongo_status,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "active_keys": active_keys
    }), 200

# Periodic task to clean expired keys
def clean_keys_periodic():
    while True:
        clean_expired_keys()
        time.sleep(3600)  # Run every hour

def run_bot():
    bot.infinity_polling()

def run_flask():
    app.run(host=FLASK_HOST, port=FLASK_PORT)

if __name__ == "__main__":
    # Start bot polling in a separate thread
    bot_thread = Thread(target=run_bot)
    bot_thread.start()
    
    # Start key cleaning in a separate thread
    cleaner_thread = Thread(target=clean_keys_periodic)
    cleaner_thread.daemon = True
    cleaner_thread.start()
    
    # Run Flask application
    run_flask()