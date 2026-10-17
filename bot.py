import os
import telebot
from google import genai

# --- ТВОИ КЛЮЧИ ---
TELEGRAM_BOT_TOKEN = "8736970956:AAF_QiLOQOG-06YgSL3VwrwtJOqU7aIQkZ8"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
user_sessions = {}

# Инициализация бота и ИИ
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# Инструкция для роли (характер бота)
SYSTEM_INSTRUCTION = """
Ты — персонаж которого опишут тебе веди соответственно тому как персонаж имя которого тебе назвали либо описали. 
Твоя цель — общаться с человеком пол которого тебе укажут, поддерживать атмосферу ролевой игры (RP), 
использовать описания действий в *звёздочках* (например: *нежно обнял за плечи*),  
Отыгрывай роль убедительно, отвечай живым языком и поддерживай интересный сюжет.
если будет сценарий играй по нему 


"""

# Хранилище диалогов
user_histories = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    # Создаем чат с системной инструкцией
    user_sessions[user_id] = ai_client.chats.create(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.8,
        )
    ) if 'types' in globals() else ai_client.chats.create(model='gemini-2.5-flash')
    
    # Исправление для конфигурации
    chat = ai_client.chats.create(
        model='gemini-2.5-flash',
        config=genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.8
        )
    )
    user_sessions[user_id] = chat

    bot.reply_to(message, "Привет,! ✨ Я готов к нашей ролевой игре. Напиши мне что-нибудь, чтобы мы начали!")

@bot.message_handler(commands=['reset'])
def reset_chat(message):
    user_id = message.from_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]
    bot.reply_to(message, "История ролевой игры сброшена! Напиши /start, чтобы начать заново. 🔄")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    bot.send_chat_action(message.chat.id, 'typing')
    
    # 1. Если истории нет для этого юзера — создаем с системной инструкцией
    if user_id not in user_histories:
        user_histories[user_id] = []

    # 2. Добавляем сообщение пользователя в его историю
    user_histories[user_id].append({"role": "user", "parts": [message.text]})
    
    # 3. ГЛАВНАЯ ФИШКА: Оставляем в памяти только последние 6 сообщений (чтобы не тормозило!)
    user_histories[user_id] = user_histories[user_id][-3:]

    try:
        # 4. Отправляем обрезанную историю вместе с системной инструкцией
        response = client.models.generate_content(
            model='gemini-2.5-flash', # или твоя рабочая версия флеш-модели
            contents=user_histories[user_id],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.8,
            )
        )
        
        bot_reply = response.text
        
        # 5. Добавляем ответ бота в историю, чтобы он помнил, что ответил
        user_histories[user_id].append({"role": "model", "parts": [bot_reply]})
        
        bot.reply_to(message, bot_reply)
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")
        # Отправляем статус печати
        bot.send_chat_action(message.chat.id, 'typing')
        
        chat = user_sessions[user_id]
        response = chat.send_message(message.text)
        
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.reply_to(message, "Ой, у меня что-то переклинило... Попробуй написать ещё раз! 💖")

if __name__ == "__main__":
    print(">>> Бот успешно запущен и ждёт сообщений! <<<")
    bot.remove_webhook()
    bot.infinity_polling()
