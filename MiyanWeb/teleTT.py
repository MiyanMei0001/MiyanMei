import telebot
import requests
import os

API_TOKEN = '7510887805:AAEXvIUp3CyNC92nrtG8zJsUI9s0mZ9V26Y'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['tiktok'])
def download_tiktok(message):
    try:
                tiktok_url = message.text.split()[1]
        
                response = requests.get(f'http://localhost:5000/tiktok?url={tiktok_url}')
                
                video_data = response.json()

                video_url = video_data['data']['play']

                bot.send_video(message.chat.id, video_url)
        
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

@bot.message_handler(commands=['tiktokhd'])
def download_tiktok_hd(message):
    try:
                tiktok_url = message.text.split()[1]
        
                response = requests.get(f'http://localhost:5000/tiktok?url={tiktok_url}')
               
                video_data = response.json()

                video_url = video_data['data']['hdplay']

                bot.send_video(message.chat.id, video_url)

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

bot.infinity_polling()