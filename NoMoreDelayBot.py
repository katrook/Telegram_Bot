import telebot
import random
from telebot import types

token = 'xxxxx'
bot = telebot.TeleBot(token)

START = '''
Привет! Я бот, который поможет тебе занять свое свободное время делами, которые ты откладываешь.

Просто запиши дела и укажи время на их выполнение. 💡Время указывается в текстовом формате, поэтому ты можешь писать любое значение, например "полчаса".

Когда у тебя появится свободная минутка, нажми кнопку 🎲Чем заняться. Я спрошу сколько у тебя есть времени и подберу тебе что ты можешь успеть сделать.

Поехали! 🚀
'''

HELP = '''
📝️Добавить задачу – добавить задачу в список дел. Все значения запоминаются в текстовом значении, поэтому для указания времени можно использовать слова (например "полчаса").

🗒️Список задач – выводит список задач, которые были добавлены.

🎲 Чем заняться? – случайная задача из списка согласно времени. 🚨Задача автоматически удаляется из списка задач.
'''

todos = {}

# todos = {
#     "1 час": ["поиграть", "побегать", "заняться спортом"],
#     "пол часа": ["почитать книгу"],
#     "2 часа": ["посмотреть кино", "учить Python"]
# }

def get_commands_keyboard():
    commands_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    button1 = types.KeyboardButton('💡Помощь')
    button2 = types.KeyboardButton('📝️Добавить задачу')
    button3 = types.KeyboardButton('🗒️Список задач')
    button4 = types.KeyboardButton('🎲 Чем заняться?')
    commands_keyboard.add(button1, button2, button3, button4)
    return commands_keyboard

def add_todo(chat_id, time, task):
    time = time.lower()
    if todos.get(chat_id) is None:
        todos[chat_id] = {}
    if todos[chat_id].get(time) is not None:
        todos[chat_id][time].append(task)
    else:
        todos[chat_id][time] = [task]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, START, reply_markup=get_commands_keyboard())

@bot.message_handler(content_types=['text'])
def help(message):
    chat_id = message.chat.id
    if message.text == '💡Помощь':
        bot.send_message(chat_id, HELP, reply_markup=get_commands_keyboard())
    elif message.text == '🗒️Список задач':
        if not todos.get(chat_id):
            msg = bot.send_message(chat_id, 'Список задач пуст. Добавь задачи', reply_markup=get_commands_keyboard())
        else:
            tasks_show = ''
            todos_sorted = sorted(todos[chat_id].items())
            for key, value in todos_sorted:
                tasks_show += str(key) + ': ' + str(value).strip("]'[").replace("'", "") + '\n'
            msg = bot.send_message(chat_id, tasks_show, reply_markup=get_commands_keyboard())
    elif message.text == '🎲 Чем заняться?':
        if not todos[chat_id]:
            msg = bot.send_message(chat_id, 'Список задач пуст. Добавь задачи', reply_markup=get_commands_keyboard())
        else:
            markup = types.InlineKeyboardMarkup()
            markup.row_width = 2
            for key_time in list(todos[chat_id]):
                markup.add(types.InlineKeyboardButton(key_time, callback_data=key_time))
            bot.send_message(chat_id, f'Сколько есть свободного времени?', reply_markup=markup)
    elif message.text == '📝️Добавить задачу':
        msg = bot.send_message(chat_id, 'Что хочешь сделать?')
        bot.register_next_step_handler(msg, add_task)

def add_task(message):
    task = message.text.lower()
    msg = bot.send_message(message.chat.id, 'Сколько времени займет?')
    bot.register_next_step_handler(msg, add_time, task)

def add_time(message, task):
    chat_id = message.chat.id
    time = message.text.lower()
    add_todo(chat_id, time, task)
    text = '✅ Добавил в список "' + task + '" за ' + time
    bot.send_message(chat_id, text, reply_markup=get_commands_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def random_task(call):
    chat_id = call.message.chat.id
    time = call.data
    if time in todos[chat_id]:
        random_task = random.choice(todos[chat_id][time])
        for tasks in todos[chat_id].values():
            if random_task in tasks:
                tasks.remove(random_task)
        if todos[chat_id].get(time) is not None and len(todos[chat_id][time]) == 0:
            todos[chat_id].pop(time)
    else:
        random_task = 'Такого времени нет'
    bot.send_message(chat_id, f'✅ Ты можешь «{random_task}»', reply_markup=get_commands_keyboard())


bot.polling(none_stop=True)
