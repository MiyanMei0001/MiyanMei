import telebot
from telebot import *
import os
from dotenv import *
import hashlib
import time
from pymongo import *
import schedule
import threading
import time

load_dotenv()

# Konfigurasi Bot Telegram
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Konfigurasi MongoDB dari variabel lingkungan
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
client.admin.command('ping')
db = client.key_management
keys_collection = db.keys

# Dictionary untuk menyimpan timestamp terakhir user generate key
last_key_generation = {}

# Fungsi untuk menghasilkan key unik
def generate_key(message_id):
    timestamp = int(time.time())
    key_string = f"Miyan-{message_id}-{timestamp}"
    key_hash = hashlib.sha256(key_string.encode()).hexdigest()
    return key_hash

# Fungsi untuk menghapus semua key dari MongoDB
def clear_keys():
    keys_collection.delete_many({})
    print("Semua key telah dihapus dari database.")

# Penjadwalan penghapusan key setiap 30 menit
schedule.every(30).minutes.do(clear_keys)

# Fungsi untuk menjalankan scheduler dalam thread terpisah
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Handler untuk command /start
@bot.message_handler(commands=['start'])
def handle_start_command(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔑 /key", callback_data='show_key_command'))
    bot.send_message(message.chat.id, "Selamat datang! Berikut adalah command yang tersedia:", reply_markup=keyboard)

# Handler untuk callback query dari tombol /start
@bot.callback_query_handler(func=lambda call: call.data == 'show_key_command')
def handle_show_key_command_callback(call):
    bot.send_message(call.message.chat.id, "🔑 `/key` - Generate key untuk autentikasi.", parse_mode="Markdown")
    bot.answer_callback_query(call.id)

# Handler untuk command /key
@bot.message_handler(commands=['key'])
def handle_key_command(message):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Generate Key", callback_data='generate_key')
    keyboard.add(button)
    bot.send_message(message.chat.id, "Klik tombol di bawah untuk generate key:", reply_markup=keyboard)

# Handler untuk callback query dari tombol
@bot.callback_query_handler(func=lambda call: call.data == 'generate_key')
def handle_generate_key_callback(call):
    user_id = call.from_user.id
    current_time = time.time()

    if user_id in last_key_generation and current_time - last_key_generation[user_id] < 30:
        remaining_time = 30 - int(current_time - last_key_generation[user_id])
        bot.send_message(call.message.chat.id, f"Mohon tunggu {remaining_time} detik sebelum generate key lagi.")
        bot.answer_callback_query(call.id)
        return

    key = generate_key(call.message.message_id)
    keys_collection.insert_one({"key": key, "used": False})
    bot.send_message(call.message.chat.id, f"Key kamu: `{key}`\n\nSilakan gunakan key ini di route /auth dengan parameter `key={key}`", parse_mode="Markdown")
    last_key_generation[user_id] = current_time
    bot.answer_callback_query(call.id)

# Fungsi untuk autentikasi (tanpa Flask)
def auth(key):
    key_data = keys_collection.find_one({"key": key})
    if key_data:
        if not key_data["used"]:
            keys_collection.update_one({"key": key}, {"$set": {"used": True}})
            return {"message": "Autentikasi berhasil"}, 200
        else:
            return {"message": "Key sudah digunakan"}, 403
    else:
        return {"message": "Key tidak valid"}, 401

# Menjalankan scheduler dalam thread terpisah
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()

if __name__ == '__main__':
    bot.polling(none_stop=True)