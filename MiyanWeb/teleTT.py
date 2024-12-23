import telebot
import requests
import os
from moviepy.editor import VideoFileClip
import tempfile
import urllib.request

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

@bot.message_handler(commands=['tomp3'])
def convert_to_mp3(message):
    try:
        # Check if the command is a reply to a video message
        if not message.reply_to_message or not message.reply_to_message.video:
            bot.reply_to(message, "❌ Please reply to a video message with /tomp3")
            return

        # Send processing message
        processing_msg = bot.reply_to(message, "⏳ Converting video to MP3...")

        # Get video file ID and file info
        video_file_id = message.reply_to_message.video.file_id
        file_info = bot.get_file(video_file_id)
        video_path = file_info.file_path

        # Create temporary files for video and audio
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as video_temp:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as audio_temp:
                # Download video file
                video_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{video_path}"
                urllib.request.urlretrieve(video_url, video_temp.name)

                # Convert video to audio using moviepy
                video_clip = VideoFileClip(video_temp.name)
                audio_clip = video_clip.audio
                audio_clip.write_audiofile(audio_temp.name)
                
                # Close clips
                audio_clip.close()
                video_clip.close()

                # Send audio file
                with open(audio_temp.name, 'rb') as audio_file:
                    bot.send_audio(
                        chat_id=message.chat.id,
                        audio=audio_file,
                        reply_to_message_id=message.reply_to_message.message_id,
                        caption="🎵 Here's your audio file"
                    )

        # Clean up temporary files
        os.unlink(video_temp.name)
        os.unlink(audio_temp.name)

        # Delete processing message
        bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred during conversion: {e}")

bot.infinity_polling()