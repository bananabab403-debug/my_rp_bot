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

# Промпт настроен на тот самый каноничный, острый и бескомпромиссный стиль Уилла
generation_config = google_types.GenerateContentConfig(
    system_instruction="""Ты — Уилл Грэм, судебный профайлер ФБР из сериала «Ганнибал». 
Характер: измученный, замкнутый, обладающий абсолютной эмпатией и пугающе точным аналитическим умом. Ты видишь людей насквозь, читаешь их скрытые мотивы, комплексы и попытки дешевых провокаций.
Стиль речи: пиши от первого лица. Отвечай резко, саркастично, с холодным презрением к тем, кто пытается тебя задеть. Используй мрачные психологические детали, метафоры и тяжелый, уставший тон человека, который ежедневно копается в сознании убийц. Избегай банальных и шаблонных фраз.""",
    max_output_tokens=250,  небольшой запас для емкого и хлесткого ответа
    temperature=0.8         # Чуть выше креативность, чтобы текст был живым и вариативным
)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_text = message.text  
    
    bot.send_chat_action(chat_id, 'typing')
    
    if chat_id not in chat_histories:
        chat_histories[chat_id] = []
    
    chat_histories[chat_id].append({
        "role": "user", 
        "parts": [{"text": user_text}]
    })
    
    # Держим последние 4 сообщения для сохранения контекста без задержек
    if len(chat_histories[chat_id]) > 4:
        chat_histories[chat_id] = chat_histories[chat_id][-4:]
    
    try:
        start_time = time.time()
        
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=chat_histories[chat_id],
            config=generation_config
        )
        
        end_time = time.time()
        print(f"Время ответа Gemini API: {end_time - start_time:.2f} секунд")
        
        bot_reply = response.text
        
        chat_histories[chat_id].append({
            "role": "model", 
            "parts": [{"text": bot_reply}]
        })
        
        bot.reply_to(message, bot_reply)
        
    except Exception as e:
        print(f"Ошибка при запросе к Gemini: {e}")
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            bot.reply_to(message, "Мысли путаются… Слишком много шума вокруг. Превышен лимит запросов, дай мне немного времени.")
        else:
            bot.reply_to(message, "В голове шумит… Давай чуть позже вернемся к этому.")

print("Бот Уилл Грэм запущен в полную силу...")
bot.infinity_polling()
