import os
import sys

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from dotenv import load_dotenv
import telebot
from telebot import types
from telebot import apihelper

# На бесплатном тарифе PythonAnywhere требуется прокси для Telegram API
if 'PYTHONANYWHERE_DOMAIN' in os.environ or 'PYTHONANYWHERE_SITE' in os.environ or os.path.exists('/etc/pythonanywhere'):
    apihelper.proxy = {'https': 'http://proxy.server:3128'}


# Загружаем переменные окружения из .env файла
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
# URL вашего Mini App (например, https://ваша-ссылка.ngrok-free.app или Vercel/GitHub Pages)
WEB_APP_URL = os.getenv("WEB_APP_URL", "http://localhost:8080")

if not BOT_TOKEN:
    print("[ERROR] Токен бота не найден в файле .env!")
    print("Укажите BOT_TOKEN=ваш_токен_от_BotFather")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_name = message.from_user.first_name or "Гонщик"
    print(f"[OK] Получена команда /start от {user_name} (@{message.from_user.username or message.from_user.id})")
    
    # Кнопка под сообщением
    markup = types.InlineKeyboardMarkup()
    play_button = types.InlineKeyboardButton(
        text="🏎️ ИГРАТЬ В ГОНКУ!", 
        web_app=types.WebAppInfo(url=WEB_APP_URL)
    )
    markup.add(play_button)

    welcome_text = (
        f"👋 Привет, <b>{user_name}</b>!\n\n"
        f"🏎️ Добро пожаловать в <b>Cyber Racer</b> — динамичную аркадную гонку прямо в Telegram!\n\n"
        f"🎮 <b>Как играть:</b>\n"
        f"• Уворачивайся от трафика и грузовиков 🚗\n"
        f"• Собирай золотые монеты 🟡\n"
        f"• Хватай ⚡ <b>Нитро</b>, 🛡️ <b>Щит</b> и 🧲 <b>Магнит</b>\n"
        f"• Ставь новые рекорды скорости!\n\n"
        f"<i>Нажми кнопку ниже, чтобы завести мотор!</i> 👇"
    )

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

    # Настраиваем постоянную кнопку "Меню" внизу чата
    try:
        bot.set_chat_menu_button(
            chat_id=message.chat.id,
            menu_button=types.MenuButtonWebApp(
                type="web_app",
                text="🎮 Играть",
                web_app=types.WebAppInfo(url=WEB_APP_URL)
            )
        )
    except Exception as e:
        print(f"Замечание по MenuButton: {e}")

if __name__ == "__main__":
    print(f"[OK] Бот запущен! WEB_APP_URL: {WEB_APP_URL}")
    print("Ожидание сообщений в Telegram (Ctrl+C для остановки)...")
    bot.infinity_polling(skip_pending=True)
