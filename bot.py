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

# Запуск встроенного веб-сервера для Render / хостингов с проверкой порта (Health Check)
if os.getenv("PORT"):
    import threading
    from http.server import HTTPServer, BaseHTTPRequestHandler
    class SimpleHealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        def log_message(self, format, *args):
            pass
    def start_http():
        port = int(os.getenv("PORT", 8080))
        httpd = HTTPServer(('0.0.0.0', port), SimpleHealthHandler)
        httpd.serve_forever()
    threading.Thread(target=start_http, daemon=True).start()



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
    user_name = message.from_user.first_name or "Пользователь"
    print(f"[OK] Получена команда /start от {user_name} (@{message.from_user.username or message.from_user.id})")
    
    # Нейтральный текст и кнопка (можно переопределять через Render Environment Variables)
    button_text = os.getenv("BUTTON_TEXT", "🚀 Запустить")
    default_text = f"👋 Привет, <b>{user_name}</b>!\n\nДля старта просто нажми на эту кнопку! 👇"
    welcome_text = os.getenv("WELCOME_TEXT", default_text)
    
    # Кнопка под сообщением
    markup = types.InlineKeyboardMarkup()
    play_button = types.InlineKeyboardButton(
        text=button_text, 
        web_app=types.WebAppInfo(url=WEB_APP_URL)
    )
    markup.add(play_button)

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

    # Настраиваем постоянную кнопку "Меню" внизу чата
    try:
        menu_text = os.getenv("MENU_BUTTON_TEXT", "🚀 Открыть")
        bot.set_chat_menu_button(
            chat_id=message.chat.id,
            menu_button=types.MenuButtonWebApp(
                type="web_app",
                text=menu_text,
                web_app=types.WebAppInfo(url=WEB_APP_URL)
            )
        )
    except Exception as e:
        print(f"Замечание по MenuButton: {e}")

if __name__ == "__main__":
    print(f"[OK] Бот запущен! WEB_APP_URL: {WEB_APP_URL}")
    print("Ожидание сообщений в Telegram (Ctrl+C для остановки)...")
    bot.infinity_polling(skip_pending=True)
