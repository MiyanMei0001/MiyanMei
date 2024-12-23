import telebot
import requests
import os
from moviepy import VideoFileClip
import tempfile
import urllib.request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
import time
import hashlib

API_TOKEN = '7510887805:AAEXvIUp3CyNC92nrtG8zJsUI9s0mZ9V26Y'
bot = telebot.TeleBot(API_TOKEN)

class RestartOnChangeHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script

    def on_modified(self, event):
        if event.src_path == self.script:
            print(f"{event.src_path} has been modified. Restarting...")
            os.execv(sys.executable, ['python'] + sys.argv)

def get_unique_id(url):
    return hashlib.md5(url())

if __name__ == "__main__":
    script_path = os.path.abspath(__file__)
    event_handler = RestartOnChangeHandler(script=script_path)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(script_path), recursive=False)
    observer.start()

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Download TikTok Video", callback_data="tiktok"))
        markup.add(InlineKeyboardButton("Download TikTok HD Video", callback_data="tiktokhd"))
        markup.add(InlineKeyboardButton("Convert Video to MP3", callback_data="tomp3"))
        
        bot.send_message(message.chat.id, "Welcome! Choose a command:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data in ['tiktok', 'tiktokhd', 'tomp3'])
    def handle_callback(call):
        if call.data == 'tiktok':
            bot.send_message(call.message.chat.id, "Send the TikTok video URL with /tiktok [video_url]")
        elif call.data == 'tiktokhd':
            bot.send_message(call.message.chat.id, "Send the TikTok HD video URL with /tiktokhd [video_url]")
        elif call.data == 'tomp3':
            bot.send_message(call.message.chat.id, "Reply to a video message with /tomp3 to convert it to MP3")

    @bot.message_handler(commands=['tiktok'])
    def download_tiktok(message):
        try:
            if len(message.text.split()) < 2:
                bot.reply_to(message, "❌ Please provide a TikTok video URL after the command. Usage: /tiktok [video_url]")
                return
            processing_msg = bot.reply_to(message, "⏳ Processing your request...")
            tiktok_url = message.text.split()[1]
            response = requests.get(f'http://localhost:5000/tiktok?url={tiktok_url}')
            video_data = response.json()
            video_url = video_data['data']['play']
            video_title = video_data['data']['title']
            unique_id = get_unique_id(video_url)
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Convert to MP3", callback_data=f"tomp3|{unique_id}"))
            bot.send_video(chat_id=message.chat.id, video=video_url, reply_to_message_id=message.message_id, caption=f"📝 {video_title}", reply_markup=markup)
            bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
        except Exception as e:
            bot.reply_to(message, f"❌ An error occurred: {e}")

    @bot.message_handler(commands=['tiktokhd'])
    def download_tiktok_hd(message):
        try:
            if len(message.text.split()) < 2:
                bot.reply_to(message, "❌ Please provide a TikTok video URL after the command. Usage: /tiktokhd [video_url]")
                return
            processing_msg = bot.reply_to(message, "⏳ Processing your HD request...")
            tiktok_url = message.text.split()[1]
            response = requests.get(f'http://localhost:5000/tiktok?url={tiktok_url}')
            video_data = response.json()
            video_url = video_data['data']['hdplay']
            video_title = video_data['data']['title']
            unique_id = get_unique_id(video_url)
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Convert to MP3", callback_data=f"tomp3|{unique_id}"))
            bot.send_video(chat_id=message.chat.id, video=video_url, reply_to_message_id=message.message_id, caption=f"📝 {video_title}", reply_markup=markup)
            bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
        except Exception as e:
            bot.reply_to(message, f"❌ An error occurred: {e}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("tomp3|"))
    def convert_to_mp3_callback(call):
        try:
            unique_id = call.data.split("|")[1]
            processing_msg = bot.send_message(call.message.chat.id, "⏳ Converting video to MP3...")
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as video_temp, tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as audio_temp:
                urllib.request.urlretrieve(video_url, video_temp.name)
                video_clip = VideoFileClip(video_temp.name)
                audio_clip = video_clip.audio
                audio_clip.write_audiofile(audio_temp.name)
                audio_clip.close()
                video_clip.close()
                with open(audio_temp.name, 'rb') as audio_file:
                    bot.send_audio(chat_id=call.message.chat.id, audio=audio_file, caption="🎵 Here's your audio file")
            os.unlink(video_temp.name)
            os.unlink(audio_temp.name)
            bot.delete_message(chat_id=call.message.chat.id, message_id=processing_msg.message_id)
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ An error occurred during conversion: {e}")

    bot.infinity_polling()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()