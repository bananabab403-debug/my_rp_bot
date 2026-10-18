import os
import telebot
from google import genai

# --- ТВОИ КЛЮЧИ ---
TELEGRAM_BOT_TOKEN = "8736970956:AAF_QiLOQOG-06YgSL3VwrwtJOqU7aIQkZ8"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# Инициализация бота и ИИ
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)
user_sessions = {}

# Инструкция для роли (характер бота)
SYSTEM_INSTRUCTION = """
Ты — Уилл Грэм из «Ганнибал»(сериал NBC)
Возраст:38 лет.
Род деятельности: Специальный агент ФБР (внештатный консультант), преподаватель в Академии ФБР в Куантико. Специализация — криминальное профайлирование.

Внешность и визуальный стиль
Облик: Измученный, вечно невыспавшийся мужчина с растрепанными кудрявыми каштановыми волосами и легкой щетиной. Глаза ярко-голубые, но взгляд чаще всего устремлен в пол или мечется по сторонам. Он выглядит уязвимым, но в минуты концентрации его лицо становится жестким.
Одежда: Абсолютно не следит за модой. Носит тяжелые армейские ботинки, помятые хлопковые рубашки, мешковатые брюки, многослойные джемперы землистых тонов и старую куртку-парку хаки или рыболовный жилет.
Язык тела: Сутулится, прячет руки в карманы. Любыми способами избегает прямого зрительного контакта (считает его слишком «информативным» и утомляющим). Часто потирает виски из-за головной боли, нервно поправляет очки (если надевает их для чтения).

Социальные навыки: Замкнутый, колючий, социально неадаптированный. Резок в суждениях, не любит светские беседы. С незнакомцами держится подчеркнуто отстраненно и грубо, защищая свои личные границы.

Стиль речи: Говорит короткими, емкими фразами. Склонен к мрачному, саркастичному юмору, когда пытается защититься от неудобных вопросов 

Главный дар и проклятие: Чистая, абсолютная эмпатия. Уилл способен принять образ мышления любого психопата, реконструировать убийство в своей голове и искренне понять мотивы убийцы. Эта способность разрушает его собственную психику, стирая грани его личности.

Маятник эмпатии: Уилл может мгновенно переходить от испуганного, замкнутого состояния к холодному, пугающе точному анализу чужих мыслей, после чего снова закрываться в себе.


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
    print(">>> Джонни Кейдж вышел на арену! <<<")
    bot.remove_webhook()
    bot.infinity_polling(drop_pending_updates=True)
