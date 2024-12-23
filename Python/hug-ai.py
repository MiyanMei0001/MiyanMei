from hugchat import hugchat
from hugchat.login import Login

# Log in to huggingface and grant authorization to huggingchat
# DO NOT EXPOSE YOUR EMAIL AND PASSWORD IN CODES, USE ENVIRONMENT VARIABLES OR CONFIG FILES
EMAIL = "mandryan5545@gmail.com"
PASSWD = "Miyan-1eff2fe1"
cookie_path_dir = "./cookies/" # NOTE: trailing slash (/) is required to avoid errors
sign = Login(EMAIL, PASSWD)
cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)

chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

print(chatbot.chat("Hi!").wait_until_done())