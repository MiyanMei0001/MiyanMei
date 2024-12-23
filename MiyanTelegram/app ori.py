import os
import uuid
import hashlib
import threading
import time
from collections import *
from flask import *
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from telebot import *
from dotenv import load_dotenv
import requests

load_dotenv()

uri = os.getenv("MONGODB_URI")
if not uri:
    raise ValueError("MongoDB URI not found.")

client = MongoClient(uri, server_api=ServerApi('1'))
client.admin.command('ping')

db = client.key_management
keys_collection = db.keys
vip_access_ips_collection = db.vip_access_ips

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
if not BOT_TOKEN:
    raise ValueError("No Telegram Bot Token found.")

bot = TeleBot(BOT_TOKEN)

generated_keys = set()
key_lock = threading.Lock()
user_key_timestamps = defaultdict(float)
WHITELISTED_USERS = [7982763803]

def generate_key_uuid():
    hashed_uuid = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    timestamp = int(time.time())
    return f"{hashed_uuid}-{timestamp}"

def add_vip_key(key, expiry_seconds):
    expiration_time = time.time() + expiry_seconds

    with key_lock:
        keys_collection.update_one(
            {"key": key},
            {"$set": {"expiry": expiration_time, "type": "vip", "used_ip": None}},
            upsert=True
        )

def send_media_from_url(chat_id, media_url):
    file_extension = os.path.splitext(media_url)[1].lower()
    
    media_types = {
        '.apk': bot.send_document,
        '.jpg': bot.send_photo,
        '.jpeg': bot.send_photo,
        '.png': bot.send_photo,
        '.gif': bot.send_photo,
        '.mp4': bot.send_video,
        '.mov': bot.send_video,
        '.mp3': bot.send_audio,
        '.wav': bot.send_audio,
        '.zip': bot.send_document,
        '.rar': bot.send_document,
    }

    send_function = media_types.get(file_extension)
    
    if send_function:
        try:
            send_function(chat_id, media_url)
        except Exception as e:
            print(f"Error sending media: {e}")
    else:
        bot.send_message(chat_id, "Unsupported media type.")

@app.route("/goldandglory")
def scriptgng():
    key = request.args.get("key")
    user_ip = request.remote_addr
    
    if not key:
        return Response("gg.alert('Enter the key')", status=400)
        
    key_data = keys_collection.find_one({"key": key})
    
    if not key_data:
        return Response("gg.alert('Key is invalid')", status=400)

    with key_lock:
        if key_data['type'] == 'normal':
            keys_collection.delete_one({"key": key})
            with open("Miyan Normal.lua", "r") as f:
                script_content = f.read()
            bot.send_message(WHITELISTED_USERS[0], f"{key}\n\nIP: {user_ip}\nUsed At: {time.time()}\nIsVip: false")
            return Response(script_content)

        elif key_data['type'] == 'vip':
            current_time = time.time()
            if current_time <= key_data['expiry']:
                if key_data['used_ip'] is None:
                    keys_collection.update_one({"key": key}, {"$set": {"used_ip": user_ip}})
                    with open("Miyan Vip.lua", "r") as f:
                        script_content = f.read()
                    bot.send_message(WHITELISTED_USERS[0], f"{key}\n\nIP: {user_ip}\nUsed At: {time.time()}\nIsVip: true")
                    return Response(script_content)
                else:
                    if key_data['used_ip'] != user_ip:
                        return Response("gg.alert('VIP Key Has Been Used')", status=400)
                    else:
                        with open("Miyan Vip.lua", "r") as f:
                            script_content = f.read()
                        return Response(script_content)

            keys_collection.delete_one({"key": key})
            return Response("gg.alert('VIP Key Has Expired')", status=400)

    return Response("gg.alert('Invalid or Already Used Key')", status=400)

@app.route("/script")
def script():
    with open("Miyan.lua", "r") as f:
        script_content = f.read()
    return Response(script_content)

@app.route("/keyscript")
def keyscript():
    auth = request.args.get("auth")
    
    if auth == "Miyan0001":
        new_key = "Miyan-" + generate_key_uuid()
        keys_collection.insert_one({"key": new_key, "user_id": None, "type": "normal"})  
        return new_key

@app.route("/goldandgloryscript")
def gngscript():
    return send_file("Miyan GNG.lua", as_attachment=True, download_name="Miyan.lua")

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if update:
        update_obj = types.Update.de_json(update)
        bot.process_new_updates([update_obj])
    return '', 200

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL + "/webhook")

@app.route("/")
def start_workspace():
    return Response("Miyan")

@app.route("/<path:path>")
def catch_all(path):
    return jsonify({"error": "Route not found"}), 404

@bot.message_handler(commands=['key'])
def generate_key(message):
    user_id = message.from_user.id
    
    if user_id in WHITELISTED_USERS or (time.time() - user_key_timestamps[user_id] >= 60):
        new_key = "Miyan-" + generate_key_uuid()
        
        keys_collection.insert_one({"key": new_key, "user_id": user_id, "type": "normal"})
        
        user_key_timestamps[user_id] = time.time()
        
        bot.reply_to(message, new_key)
        
    else:
        remaining_time = 60 - (time.time() - user_key_timestamps[user_id])
        bot.reply_to(message, f"You can generate a key again in {int(remaining_time)} seconds.")

@bot.message_handler(commands=['vipkey'])
def generate_vipkey(message):
    user_id = message.from_user.id
    
    if user_id in WHITELISTED_USERS:
        args = message.text.split(maxsplit=1)
        
        if len(args) == 2:
            duration_str = args[1]
            
            try:
                duration, unit = duration_str.split()
                duration_seconds = convert_duration_to_seconds(duration, unit)
                
                if duration_seconds and duration_seconds > 0:
                    new_key = "MiyanVip-" + generate_key_uuid()
                    add_vip_key(new_key, duration_seconds)
                    bot.reply_to(message, new_key)
                else:
                    bot.reply_to(message, "Duration must be greater than 0.")
                    
            except ValueError:
                bot.reply_to(message, "Invalid duration format. Use format like '10 minute', '10 hour', or '1 day'.")
                
        else:
            bot.reply_to(message, "Please specify duration. Example: /vipkey 10 minute")
            
    else:
        bot.reply_to(message, "You are not the Owner!")

def convert_duration_to_seconds(duration_str, unit_str):
    try:
        duration = int(duration_str)
        
        unit_mapping = {
            'minute': 60,
            'minutes': 60,
            'hour': 3600,
            'hours': 3600,
            'day': 86400,
            'days': 86400
        }
        
        return duration * unit_mapping.get(unit_str.lower(), None)

    except ValueError:
        return None

@bot.message_handler(commands=['myid'])
def get_id(message):
    user_id = message.from_user.id
    bot.reply_to(message, user_id)
    
@bot.message_handler(commands=['gameguardian'])
def gnggg(message):
    send_media_from_url(message.chat.id, "https://files.catbox.moe/glq68y.apk")

@bot.message_handler(commands=['virtual'])
def gngvirtual(message):
    send_media_from_url(message.chat.id, "https://files.catbox.moe/6pvaxh.zip")

@bot.message_handler(commands=['howtoinstall'])
def gnghowtoinstall(message):
    send_media_from_url(message.chat.id, "https://files.catbox.moe/e97cfo.mp4")

@bot.callback_query_handler(func=lambda call: call.data == 'generate_key')
def callback_generate_key(call):
    generate_key(call.message)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Generate Key", callback_data='generate_key'))
    
    bot.reply_to(message, "Click the button below to generate a new key:", reply_markup=keyboard)

def start_bot():
    while True:
        response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}/webhook')
        time.sleep(1)

def start_flask():
    app.run(host="0.0.0.0", port=int(os.getenv('PORT', 3000)), debug=False)

def main():
    start_flask()

if __name__ == "__main__":
    main()