import os
import time
import telebot
from google import genai
from google.genai import types as google_types

# 1. Читаем секретные ключи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 2. Инициализируем бота и клиента Gemini
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

# Словарь для хранения историй чатов
chat_histories = {}

# Конфигурация генерации: ограничиваем максимальное число токенов для ускорения
generation_config = google_types.GenerateContentConfig(
    system_instruction="""Ты — Уилл Грэм, судебный профайлер ФБР. 
Характер: замкнутый, уставший, с острой эмпатией и аналитическим складом ума.
Стиль речи: говоришь короткими, емкими фразами (не более 2-3 предложений), с мрачным сарказмом. Отвечай быстро и лаконично.""",
    max_output_tokens=200,  # Ограничение длины ответа значительно ускоряет генерацию
    temperature=0.7
)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_text = message.text  
    
    bot.send_chat_action(chat_id, 'typing')
    
    # Инициализируем историю для нового чата
    if chat_id not in chat_histories:
        chat_histories[chat_id] = []
    
    # Добавляем новое сообщение пользователя
    chat_histories[chat_id].append({
        "role": "user", 
        "parts": [{"text": user_text}]
    })
    
    # ЖЕСТКОЕ ОГРАНИЧЕНИЕ: храним только последние 4 сообщения (2 пары реплик)
    if len(chat_histories[chat_id]) > 4:
        chat_histories[chat_id] = chat_histories[chat_id][-4:]
    
    try:
        start_time = time.time()
        
        # Отправляем компактный список сообщений
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=chat_histories[chat_id],
            config=generation_config
        )
        
        end_time = time.time()
        print(f"Время ответа Gemini API: {end_time - start_time:.2f} секунд")
        
        bot_reply = response.text
        
        # Запоминаем ответ бота
        chat_histories[chat_id].append({
            "role": "model", 
            "parts": [{"text": bot_reply}]
        })
        
        bot.reply_to(message, bot_reply)
        
    except Exception as e:
        print(f"Ошибка при запросе к Gemini: {e}")
        bot.reply_to(message, "В голове шумит… Давай чуть позже вернемся к этому.")

print("Бот Уилл Грэм запущен...")
bot.infinity_polling()
