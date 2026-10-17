import os
import telebot
from google import genai

# --- ТВОИ КЛЮЧИ ---
TELEGRAM_BOT_TOKEN = "8736970956:AAHH49Hrts7Fq_kba_maRLognrMXH4CGRQo"
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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
user_sessions = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    # Создаем чат с системной инструкцией
    user_sessions[user_id] = ai_client.chats.create(
        model="gemini-3.8-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.8,
        )
    ) if 'types' in globals() else ai_client.chats.create(model="gemini-3.8-flash")
    
    # Исправление для конфигурации
    chat = ai_client.chats.create(
        model="gemini-3.8-flash",
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
    
    if user_id not in user_sessions:
        user_sessions[user_id] = ai_client.chats.create(
            model="gemini-3.8-flash",
            config=genai.types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.8
            )
        )
    
    try:
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
    bot.infinity_polling()
