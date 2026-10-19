import os
import time
import telebot
from google import genai
from google.genai import types as google_types

# 1. Читаем секретные ключи из переменных окружения (безопасно для GitHub)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 2. Инициализируем бота и клиента Gemini
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

# Словарь для хранения активных сессий чата с историей для каждого пользователя
active_chats = {}

# 3. Обработчик входящих сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_text = message.text  
    
    # Мгновенно показываем пользователю статус "печатает..."
    bot.send_chat_action(chat_id, 'typing')
    
    # Если для этого пользователя еще нет запущенного чата — создаем его
    if chat_id not in active_chats:
        active_chats[chat_id] = client.chats.create(
            model="gemini-3.8-flash",
            config=google_types.GenerateContentConfig(
                system_instruction="""Ты — Уилл Грэм, судебный профайлер ФБР. 
Характер: замкнутый, уставший, с острой эмпатией и аналитическим складом ума. Ты умеешь проникать в чужие мысли и мотивы, но это сильно тебя утомляет.
Стиль речи: говоришь короткими, емкими фразами, иногда с мрачным сарказмом. Держишься отстраненно и защищаешь личные границы, но видишь людей насквозь."""
            )
        )
    
    try:
        start_time = time.time()  # Замеряем скорость ответа
        
        # Отправляем сообщение (история сохраняется автоматически под капотом)
        response = active_chats[chat_id].send_message(user_text)
        
        end_time = time.time()
        print(f"Время ответа Gemini API: {end_time - start_time:.2f} секунд")
        
        # Отправляем ответ пользователю в Telegram
        bot.reply_to(message, response.text)
        
    except Exception as e:
        print(f"Ошибка при запросе к Gemini: {e}")
        bot.reply_to(message, "В голове шумит… Давай чуть позже вернемся к этому.")

# 4. Запуск бота
print("Бот Уилл Грэм запущен и готов к работе...")
bot.infinity_polling()

print("Бот запущен и готов к работе...")
bot.infinity_polling()
