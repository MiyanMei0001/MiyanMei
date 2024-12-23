import logging
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from urllib.parse import urlparse
from pathlib import Path

# Konfigurasi logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Token bot Telegram Anda
TOKEN = "7858645302:AAGjPZ_1ND3ixU53gBi0C8tjpO1Z9LJpkns"

# Direktori untuk menyimpan file sementara
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

# Fungsi untuk mendownload file dari URL
def download_file(url: str, file_path: str) -> bool:
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading file: {e}")
        return False

# Fungsi untuk menentukan jenis media berdasarkan ekstensi file
def get_media_type(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
        return 'photo'
    elif ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
        return 'video'
    elif ext in ['.mp3', '.wav', '.ogg', '.flac']:
        return 'audio'
    else:
        return 'document'

# Handler untuk perintah /start
async def start(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Halo! Kirimkan URL media dan saya akan mengubahnya menjadi media yang sesuai.")

# Handler untuk pesan teks (URL)
async def handle_url(update: Update, context: CallbackContext):
    url = update.message.text
    chat_id = update.effective_chat.id

    try:
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            await context.bot.send_message(chat_id=chat_id, text="URL tidak valid.")
            return

        file_name = os.path.basename(parsed_url.path)
        if not file_name:
            file_name = "file"
        file_path = os.path.join(TEMP_DIR, file_name)

        await context.bot.send_message(chat_id=chat_id, text="Sedang mendownload file...")

        if download_file(url, file_path):
            media_type = get_media_type(file_path)
            await context.bot.send_message(chat_id=chat_id, text="File berhasil didownload, sedang mengirim...")
            try:
                if media_type == 'photo':
                    await context.bot.send_photo(chat_id=chat_id, photo=open(file_path, 'rb'))
                elif media_type == 'video':
                    await context.bot.send_video(chat_id=chat_id, video=open(file_path, 'rb'))
                elif media_type == 'audio':
                    await context.bot.send_audio(chat_id=chat_id, audio=open(file_path, 'rb'))
                else:
                    await context.bot.send_document(chat_id=chat_id, document=open(file_path, 'rb'))
            except Exception as e:
                logging.error(f"Error sending media: {e}")
                await context.bot.send_message(chat_id=chat_id, text="Gagal mengirim media.")
            finally:
                os.remove(file_path)
        else:
            await context.bot.send_message(chat_id=chat_id, text="Gagal mendownload file.")
    except Exception as e:
        logging.error(f"Error processing URL: {e}")
        await context.bot.send_message(chat_id=chat_id, text="Terjadi kesalahan saat memproses URL.")

# Fungsi utama untuk menjalankan bot
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Handler untuk perintah /start
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # Handler untuk pesan teks (URL)
    url_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url)
    application.add_handler(url_handler)

    # Menjalankan bot
    application.run_polling()

if __name__ == '__main__':
    main()