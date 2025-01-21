
import telebot
from telebot import types

BOT_TOKEN = [YOUR_TOKEN]  # Ваш токен
ADMIN_ID = [ADMIN_ID]

bot = telebot.TeleBot(BOT_TOKEN)

# Словарь для хранения голосов
votes = {
    "info_bot": {"yes": 0, "no": 0},
    "appeal_bot": {"yes": 0, "no": 0},
    "event_calendar": {"yes": 0, "no": 0},
    "survey_bot": {"yes": 0, "no": 0},
    "notification_bot": {"yes": 0, "no": 0},
    "faq_bot": {"yes": 0, "no": 0},
    "unified_bot": {"yes": 0, "no": 0}
}

user_states = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = main_menu(message)
    bot.send_message(message.chat.id,
                     "Добро пожаловать! Пожалуйста, проголосуйте, нужны ли нашему дому боты - помощники.",
                     reply_markup=markup)

def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Голосовать за ботов")
    item2 = types.KeyboardButton("Инструкция по голосованию")
    markup.add(item1, item2)

    if ADMIN_ID == message.from_user.id:
        item3 = types.KeyboardButton("Посмотреть результаты")
        markup.add(item3)

    return markup

@bot.message_handler(func=lambda message: message.text == "Инструкция по голосованию")
def show_instructions(message):
    instructions = (
        "Инструкция по голосованию:\n"
        "1. Нажмите на кнопку 'Голосовать за ботов'.\n"
        "2. Выберите нужного бота и нажмите 'ДА' или 'НЕТ'.\n"
        "3. Ваш голос будет учтен.\n"
    )
    bot.send_message(message.chat.id, instructions)

@bot.message_handler(func=lambda message: message.text == "Голосовать за ботов")
def send_notification(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Информационный бот", callback_data="info_bot_info"))
    markup.add(types.InlineKeyboardButton(text="Чат-бот для обращений", callback_data="appeal_bot_info"))
    markup.add(types.InlineKeyboardButton(text="Календарь событий", callback_data="event_calendar_info"))
    markup.add(types.InlineKeyboardButton(text="Бот для опросов", callback_data="survey_bot_info"))
    markup.add(types.InlineKeyboardButton(text="Бот для уведомлений", callback_data="notification_bot_info"))
    markup.add(types.InlineKeyboardButton(text="Бот для FAQ", callback_data="faq_bot_info"))
    markup.add(types.InlineKeyboardButton(text="Создать единого бота", callback_data="unified_bot_info"))

    bot.send_message(message.chat.id, "Выберите бота для получения информации:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.endswith("_info"))
def show_bot_info(call):
    bot_info_map = {
        "info_bot_info": (
            "Информационный бот.\nФункции: Предоставление информации о контактных данных обслуживающих организаций.",
            "info_bot"),
        "appeal_bot_info": (
            "Чат-бот для обращений.\nФункции: Позволяет жильцам отправлять обращения или жалобы.", "appeal_bot"),
        "event_calendar_info": (
            "Календарь событий.\nФункции: Информирование жильцов о предстоящих мероприятиях.", "event_calendar"),
        "survey_bot_info": ("Бот для опросов и голосований.\nФункции: Проведение опросов среди жильцов.", "survey_bot"),
        "notification_bot_info": ("Бот для уведомлений.\nФункции: Уведомления о важных событиях.", "notification_bot"),
        "faq_bot_info": ("Бот для FAQ.\nФункции: Ответы на часто задаваемые вопросы.", "faq_bot"),
        "unified_bot_info": ("Создать единого бота.\nФункции: Объединение всех функций в одном боте.", "unified_bot"),
    }

    bot_info, vote_key = bot_info_map[call.data]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="ДА", callback_data=f"vote_{vote_key}_yes"))
    markup.add(types.InlineKeyboardButton(text="НЕТ", callback_data=f"vote_{vote_key}_no"))

    bot.send_message(call.message.chat.id, bot_info, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("vote_"))
def handle_vote(call):
    vote_type = call.data.split("_")[1]
    vote_value = call.data.split("_")[2]

    if vote_type in votes:
        if vote_value == "yes":
            votes[vote_type]["yes"] += 1
        elif vote_value == "no":
            votes[vote_type]["no"] += 1

        bot.answer_callback_query(call.id, "Ваш голос учтен!")
        bot.send_message(call.message.chat.id, "Спасибо за голосование!")

        finish_markup = types.InlineKeyboardMarkup()
        finish_markup.add(types.InlineKeyboardButton(text="Завершить", callback_data="finish_voting"))
        bot.send_message(call.message.chat.id, "Вы можете завершить голосование или ознакомиться с функциями других ботов и проголосовать за них (прокрутите список вверх).", reply_markup=finish_markup)
    else:
        bot.answer_callback_query(call.id, "Ошибка: голосование не найдено.")

@bot.callback_query_handler(func=lambda call: call.data == "finish_voting")
def finish_voting(call):
    chat_id = call.message.chat.id
    bot.send_message(chat_id, "Спасибо, Ваш голос учтен!")
    bot.send_message(chat_id, "Все вопросы и предложения по работе бота @LexxDramma")
    user_states[chat_id] = None

@bot.message_handler(func=lambda message: message.text == "Посмотреть результаты")
def show_results(message):
    if message.from_user.id == ADMIN_ID:
        results = "\n".join([f"{key.replace('_', ' ').title()}: Да - {value['yes']}, Нет - {value['no']}" for key, value in votes.items()])
        bot.send_message(message.chat.id, f"Результаты опроса:\n{results}")
    else:
        bot.send_message(message.chat.id, "У Вас нет доступа к результатам.")

# Запуск бота
if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        import sys
        sys.exit(1)  # Завершение программы с кодом ошибки
