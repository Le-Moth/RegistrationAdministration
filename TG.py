import telebot
from main import main
from database import clear_user_history
from database import save_message
bot = telebot.TeleBot(token="")
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать")
    clear_user_history(user_id=message.chat.id)
    system_prompt="Ты полезный ассистент который нужен чтобы смотреть в SQLite таблицу данные пользователя, отвечай кратко и по делу и проверяй информацию из таблицы"
    save_message(message.chat.id, "system", system_prompt)

@bot.message_handler(content_types = ["text"])
def echo_all(message):
    # message.chat.id - ID чата
    # message.text - текст сообщения
    message_id = message.chat.id
    user_text = message.text
    answer_from_lachuga = main(user_text, message_id)
    print(answer_from_lachuga)

    bot.reply_to(message, answer_from_lachuga or "Данные не найдены")

def restart(message):
    message.chat.id = []

bot.infinity_polling()
