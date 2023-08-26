import telebot
from random import*
import json
import requests
import sys
import os

API_TOKEN='YOUR_API'
bot = telebot.TeleBot(API_TOKEN)

phone_book_bot = {}
selected_contacts = []
current_contact = None

def load_contacts():
    if os.path.exists('phone_book_bot.json'):
        with open('phone_book_bot.json', 'r') as file:
            try:
                contacts_data = json.load(file)
                return contacts_data
            except json.JSONDecodeError:
                print("Ошибка чтения файла phone_book_bot.json")
    return {}

def save_contacts():
    with open('phone_book_bot.json', 'w') as file:
        json.dump(phone_book_bot, file, ensure_ascii=False, indent=4)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,greeting_message) 
greeting_message = (
    "Привет 👋!\n\n"
    "☎️ Это твой онлайн телефонный справочник\n\n"
    "➡️ Введи команду /menu, чтобы увидеть все команды и способности твоего карманного друга\n\n"
)

@bot.message_handler(commands=['menu'])
def menu_message(message):
    bot.send_message(message.chat.id,menu_list_message)
menu_list_message = (
    "📋 Вот список команд: \n\n"
    "/start - перезапустить бот\n\n"
    "/menu - увидеть все команды\n\n"
    "/all_contacts - увидеть все контакты\n\n"
    "/add_new_contact - добавить новый контакт\n\n"
    "/search_contact - найти данные контакта по имени\n\n"
    "/delete - удалить контакт\n\n"
    "/edit - изменить данный контакт\n\n"
    "/add_number_to_existing_contact - добавить номер к существующему контакту"
)

@bot.message_handler(commands=['all_contacts'])
def show_all_phone_book_bot(message):
    if phone_book_bot:
        response = "Вот весь список контактов👨‍💼:\n\n"
        for contact_name, contact_data in phone_book_bot.items():
            surname = contact_data.get('surname', 'Фамилия не указана')
            phone = contact_data.get('phone', 'Номер телефона не указан')
            phone_str = '\n'.join(phone)
            email = contact_data.get('email', 'Электронная почта не указана')
            contact_info = f"🪪 Имя: {contact_name}\n🪪 Фамилия: {surname}\n📞 Телефон: {phone_str}\n📧 Электронная почта: {email}\n\n"
            response += contact_info
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Список пока что пуст!🤷‍♀️")

@bot.message_handler(commands=['add_new_contact'])
def add_new_contact_command(message):
    global current_contact
    current_contact = {}
    add_new_contact_reply_message = (
        "Отлично!🎉 Рада, что у тебя появился новый друг 👍\n\n"
        "✍️ Скорее запиши его в свои контакты!\n\n"
        "🪪 Введите имя контакта:"
    )
    bot.send_message(message.chat.id, add_new_contact_reply_message)
    bot.register_next_step_handler(message, process_name_step)

def process_name_step(message):
    global current_contact
    contact_name = message.text
    if contact_name in phone_book_bot:
        bot.send_message(message.chat.id, "🚫 Контакт с таким именем уже существует. Введите другое имя:")
        bot.register_next_step_handler(message, process_name_step)
    else:
        current_contact['name'] = contact_name
        bot.send_message(message.chat.id, "🪪 Введи фамилию контакта:")
        bot.register_next_step_handler(message, process_surname_step)

def process_surname_step(message):
    global current_contact
    current_contact['surname'] = message.text
    bot.send_message(message.chat.id, "📞 Введи номер телефона контакта:")
    bot.register_next_step_handler(message, process_phone_step)

def process_phone_step(message):
    global current_contact
    current_contact['phone'] = [message.text]
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('📞 Завершить ввод номера телефона')
    bot.send_message(message.chat.id, "Введи дополнительный номер телефона (или нажми кнопку '📞 Завершить ввод номера телефона'):", reply_markup=markup)
    bot.register_next_step_handler(message, process_additional_phone_step)


def process_additional_phone_step(message):
    global current_contact
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('📞 Завершить ввод номера телефона')
    
    if message.text.lower() == '📞 завершить ввод номера телефона':
        if current_contact['phone']:
            bot.send_message(message.chat.id, "📞 Ввод номеров телефонов завершен.")
            bot.send_message(message.chat.id, "📧 Введи электронную почту контакта:")
            bot.register_next_step_handler(message, process_email_step)
        else:
            bot.send_message(message.chat.id, "📞 Вы не ввели ни одного номера телефона.")
            bot.register_next_step_handler(message, process_additional_phone_step)
    else:
        current_contact['phone'].append(message.text)
        bot.send_message(message.chat.id, "📞 Введи следующий номер телефона (или нажми кнопку '📞 Завершить ввод номера телефона'):", reply_markup=markup)
        bot.register_next_step_handler(message, process_additional_phone_step)

def process_email_step(message):
    global current_contact, phone_book_bot
    current_contact['email'] = message.text

    phone_book_bot[current_contact['name']] = current_contact

    save_contacts()
    
    bot.send_message(message.chat.id, "✅ Контакт сохранен!")

    current_contact = None
    phone_book_bot = load_contacts()

@bot.message_handler(commands=['search_contact'])
def search_contact_(message):
    bot.send_message(message.chat.id, "🔎 Введите имя контакта для поиска:")
    bot.register_next_step_handler(message, process_search_contact_step)


def process_search_contact_step(message):
    contact_name = message.text
    contact_data = phone_book_bot.get(contact_name)
    if contact_data:
        surname = contact_data.get('surname', 'Фамилия не указана')
        phone = contact_data.get('phone', 'Номер телефона не указан')
        email = contact_data.get('email','Электронная почта не указана' )
        response = f"🪪 Имя: {contact_name}\n🪪 Фамилия: {surname}\n📞 Телефон: {phone}\n📧 Электронная почта: {email}\n\n"
    else:
        response = "🤷‍♀️ Контакт не найден."
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['delete'])
def delete_contact(message):
    bot.send_message(message.chat.id, "🪪 Введите имя контакта для удаления:")
    bot.register_next_step_handler(message, process_delete_step)

def process_delete_step(message):
    contact_name = message.text
    if contact_name in phone_book_bot:
        del phone_book_bot[contact_name]
        save_contacts()
        bot.send_message(message.chat.id, f"💔 Контакт {contact_name} удален.")
    else:
        bot.send_message(message.chat.id, f"🤷‍♀️ Контакт {contact_name} не найден.")

@bot.message_handler(commands=['edit'])
def edit_contact(message):
    bot.send_message(message.chat.id, "🪪 Введи имя контакта, который нужно изменить:")
    bot.register_next_step_handler(message, process_edit_number_step)

def process_edit_number_step(message):
    contact_name = message.text
    if contact_name in phone_book_bot:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('🪪 Имя', '🪪 Фамилия', '📞 Номер телефона', '📧 Электронная почта', '✋🛑 Отмена')
        bot.send_message(message.chat.id, f"✍️  Выберите, что вы хотите изменить для контакта {contact_name}:", reply_markup=markup)
        bot.register_next_step_handler(message, lambda msg: process_edit_choice_step(msg, contact_name))

def process_edit_choice_step(message, contact_name):
    choice = message.text.lower()
    if choice in ['🪪 имя', '🪪 фамилия', '📞 номер телефона', '📧 электронная почта']:
        bot.send_message(message.chat.id, f"Введи новое значение для {choice} контакта:")
        bot.register_next_step_handler(message, lambda msg: process_edit_step(msg, contact_name, choice))
    elif choice == 'отмена':
        bot.send_message(message.chat.id, "✋🛑 Изменение отменено.")
    else:
        bot.send_message(message.chat.id, "Выберите один из вариантов:🪪 Имя, 🪪 Фамилия,📞 Номер телефона,📧 Электронная почта, Отмена")

def process_edit_step(message, contact_name, field):
    new_value = message.text
    contact_data = phone_book_bot[contact_name]
    if field == 'имя':
        phone_book_bot[new_value] = contact_data
        del phone_book_bot[contact_name]
    elif field == 'фамилия':
        contact_data['surname'] = new_value
    elif field == 'номер телефона':
        contact_data['phone'] = [new_value]
    elif field == 'электронная почта':
        contact_data['email'] = new_value

    save_contacts()
    bot.send_message(message.chat.id, f"✅ {field.capitalize()} контакта {contact_name} изменено на {new_value}.")
    bot.clear_step_handler_by_chat_id(message.chat.id)

@bot.message_handler(commands=['add_number_to_existing_contact'])
def add_number_to_existing_contact(message):
    bot.send_message(message.chat.id, "✍️ Введи имя контакта, к которому нужно добавить новый номер:")
    bot.register_next_step_handler(message, process_add_number_contact_step)

def process_add_number_contact_step(message):
    contact_name = message.text
    if contact_name in phone_book_bot:
        bot.send_message(message.chat.id, "📞 Введи дополнительный номер телефона для контакта:")
        bot.register_next_step_handler(message, lambda msg: process_add_number_step(msg, contact_name))
    else:
        bot.send_message(message.chat.id, "🤷‍♀️ Контакт с таким именем не найден.")

def process_add_number_step(message, contact_name):
    global phone_book_bot
    new_phone = message.text
    contact_data = phone_book_bot[contact_name]
    contact_data['phone'].append(new_phone)
    save_contacts()
    bot.send_message(message.chat.id, "✅📞 Дополнительный номер телефона добавлен к контакту.")

phone_book_bot = load_contacts()
bot.polling()
