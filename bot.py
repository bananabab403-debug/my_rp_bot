import os
import telebot
from telebot import types as telebot_types
from google import genai
from google.genai import types as google_types

# Читаем секретные ключи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Инициализируем бота и клиента Gemini
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

# Словарь для хранения истории сообщений каждого чата
chat_histories = {}

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_text = message.text  
    
    # 1. СРАЗУ показываем пользователю, что бот начал думать ("печатает...")
    bot.send_chat_action(chat_id, 'typing')
    
    # Инициализируем историю для нового чата
    if chat_id not in chat_histories:
        chat_histories[chat_id] = []
    
    # Добавляем сообщение пользователя в историю
    chat_histories[chat_id].append({
        "role": "user", 
        "parts": [user_text]
    })
    
    # Ограничиваем историю последними 6 сообщениями для скорости
    if len(chat_histories[chat_id]) > 6:
        chat_histories[chat_id] = chat_histories[chat_id][-6:]
    
    try:
        # 2. Отправляем запрос к Gemini (модель и так самая быстрая — flash)
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=chat_histories[chat_id],
            config=google_types.GenerateContentConfig(
                system_instruction="""Ты — Уилл Грэм из «Ганнибал» (сериал NBC). 
Пиши от первого лица, передавай его характер, эмпатию, тонкую психологию и способность воссоздавать картину чужими глазами."""
            )
        )
        
        bot_reply = response.text
        
        # Добавляем ответ бота в историю чата
        chat_histories[chat_id].append({
            "role": "model", 
            "parts": [bot_reply]
        })
        
        if len(chat_histories[chat_id]) > 3:
            chat_histories[chat_id] = chat_histories[chat_id][-6:]
        
        # Отправляем готовый ответ
        bot.reply_to(message, bot_reply)
        
    except Exception as e:
        print(f"Ошибка при запросе к Gemini: {e}")
        bot.reply_to(message, "В голове шумит… Давай чуть позже вернемся к этому.")

print("Бот запущен и готов к работе...")
bot.infinity_polling()
