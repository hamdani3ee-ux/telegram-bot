import telebot
import requests
from flask import Flask
from threading import Thread

# ================= KEEP ALIVE =================
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ================= SETTINGS =================
TELEGRAM_TOKEN = '8662471569:AAFyOsRjptFC7sNtoaCxr6By0uLmeGC1E9M'
ADMIN_ID = 7670426534  

API_USER = '1336182302'
API_SECRET = 'YYrzatC2YoeZFMQEy8F24jYsGRxoQusV'

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)

print("🚀 BOT RUNNING 24/7")

# ================= API CHECK =================
def check_content_api(file_url):
    params = {
        'url': file_url,
        'models': 'nudity-2.0,wad,scam',
        'api_user': API_USER,
        'api_secret': API_SECRET
    }
    try:
        r = requests.get(
            'https://api.sightengine.com/1.0/check.json',
            params=params,
            timeout=15
        )
        output = r.json()

        if output.get('status') == 'success':
            nudity = output.get('nudity', {})

            if (
                nudity.get('sexual_activity', 0) >= 0.7 or 
                nudity.get('sexual_display', 0) >= 0.7 or 
                nudity.get('erotica', 0) >= 0.7
            ):
                return True

    except Exception as e:
        print(f"❌ API ERROR: {e}")

    return False

# ================= MONITOR =================
@bot.message_handler(content_types=['photo', 'video', 'animation'])
def monitor_content(message):

    if message.from_user and message.from_user.id == ADMIN_ID:
        return

    try:
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
        elif message.content_type == 'video':
            file_id = message.video.file_id
        elif message.content_type == 'animation':
            file_id = message.animation.file_id
        else:
            return

        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"

        if check_content_api(file_url):
            bot.delete_message(message.chat.id, message.message_id)

            try:
                name = message.from_user.first_name if message.from_user else "Unknown"
                bot.send_message(
                    ADMIN_ID,
                    f"⚠️ تم حذف محتوى إباحي من: {name}"
                )
            except:
                pass

    except Exception as e:
        print(f"❌ PROCESS ERROR: {e}")

# ================= START =================
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🔥 البوت شغال ويراقب المحتوى بنسبة 70%")

# ================= RUN =================
keep_alive()

while True:
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"❌ RESTARTING: {e}")
