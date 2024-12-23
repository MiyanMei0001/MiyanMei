import telebot
import requests
import os

API_TOKEN = '7510887805:AAEXvIUp3CyNC92nrtG8zJsUI9s0mZ9V26Y'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['tiktok'])
def download_tiktok(message):
    try:
        # Send a "processing" message first
        processing_msg = bot.reply_to(message, "⏳ Processing your request...")
        
        tiktok_url = message.text.split()[1]
        response = requests.get(f'http://localhost:5000/tiktok?url={tiktok_url}')
        video_data = response.json()
        video_url = video_data['data']['play']
        video_title = video_data['data']['title']

        # Send video as reply to original message with the video title as caption
        bot.send_video(
            chat_id=message.chat.id,
            video=video_url,
            reply_to_message_id=message.message_id,
            caption=f"📝 {video_title}"
        )
        
        # Delete the processing message
        bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
        
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {e}")

@bot.message_handler(commands=['tiktokhd'])
def download_tiktok_hd(message):
    try:
        # Send a "processing" message first
        processing_msg = bot.reply_to(message, "⏳ Processing your HD request...")
        
        tiktok_url = message.text.split()[1]
        response = requests.get(f'http://localhost:5000/tiktok?url={tiktok_url}')
        video_data = response.json()
        video_url = video_data['data']['hdplay']
        video_title = video_data['data']['title']

        # Send HD video as reply to original message with the video title as caption
        bot.send_video(
            chat_id=message.chat.id,
            video=video_url,
            reply_to_message_id=message.message_id,
            caption=f"📝 {video_title}"
        )
        
        # Delete the processing message
        bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
        
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {e}")

bot.infinity_polling()