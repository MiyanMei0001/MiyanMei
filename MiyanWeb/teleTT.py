import telebot
import requests
import os

API_TOKEN = '7510887805:AAEXvIUp3CyNC92nrtG8zJsUI9s0mZ9V26Y'
bot = telebot.TeleBot(API_TOKEN)

# Function to handle the /tiktok command
@bot.message_handler(commands=['tiktok'])
def download_tiktok(message):
    try:
        # Extract the TikTok URL from the message
        tiktok_url = message.text.split()[1]
        
        # Request the TikTok video data from your API
        response = requests.get(f'http://localhost:5000/tiktok?url={tiktok_url}')
        video_data = response.json()

        # Get the video URL from the response data
        video_url = video_data['data']['play']

        # Download the video file
        video_response = requests.get(video_url)
        video_path = 'tiktok_video.mp4'
        with open(video_path, 'wb') as video_file:
            video_file.write(video_response.content)

        # Send the video file back to the user
        with open(video_path, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)
        
        # Remove the video file after sending
        os.remove(video_path)

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

# Function to handle the /tiktokhd command
@bot.message_handler(commands=['tiktokhd'])
def download_tiktok_hd(message):
    try:
        # Extract the TikTok URL from the message
        tiktok_url = message.text.split()[1]
        
        # Request the TikTok video data from your API
        response = requests.get(f'http://localhost:5000/tiktok?url={tiktok_url}')
        video_data = response.json()

        # Get the HD video URL from the response data
        video_url = video_data['data']['hdplay']

        # Download the HD video file
        video_response = requests.get(video_url)
        video_path = 'tiktok_hd_video.mp4'
        with open(video_path, 'wb') as video_file:
            video_file.write(video_response.content)

        # Send the HD video file back to the user
        with open(video_path, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)

        # Remove the video file after sending
        os.remove(video_path)

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

# Start the bot with infinity polling
bot.infinity_polling()