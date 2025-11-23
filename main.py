import telebot
import time
import threading
import random
from telebot.handler_backends import State, StatesGroup
from telebot import types

bot = telebot.TeleBot('8270145696:AAEu-dFxnyOlyqpbwlYPQysCjRCrZqS5pxY')

class PetStats:
    pet_name = 'Пи-Пи'
    pet_food = 50
    pet_mood = 50
    is_alive = True
    pet_state = 0  # 0 - дефолт 1 - весели 2 - грусни 3 - помир

class GameStates(StatesGroup):
    game_menu = State()
    tictactoe_playing = State()
    dice_playing = State()


photos = [
    'C:/Users/user/Desktop/тгботяры/hakaton/дефолт1.png',
    'C:/Users/user/Desktop/тгботяры/hakaton/весели1.png',
    'C:/Users/user/Desktop/тгботяры/hakaton/грусни1.png',
    'C:/Users/user/Desktop/тгботяры/hakaton/помир1.png',
]

editing_name = {}  # Словарь для отслеживания пользователей, которые меняют имя

def auto_decrease_stats():
    while True:
        time.sleep(120)  
        if PetStats.is_alive:
            # Снижаем показатели
            PetStats.pet_food -= 5
            PetStats.pet_mood -= 5
            
            # Обновляем состояние питомца
            update_pet_state()
            
            # Проверяем не умер ли питомец
            if PetStats.pet_food <= 0 or PetStats.pet_mood <= 0:
                PetStats.is_alive = False
                PetStats.pet_state = 3

def update_pet_state():
    """Обновляем состояние питомца в зависимости от показателей"""
    if not PetStats.is_alive:
        PetStats.pet_state = 3
    elif PetStats.pet_food > 70 and PetStats.pet_mood > 70:
        PetStats.pet_state = 1  # весели
    elif PetStats.pet_food < 30 or PetStats.pet_mood < 30:
        PetStats.pet_state = 2  # грусни
    else:
        PetStats.pet_state = 0  # дефолт

# Запускаем фоновый поток
auto_thread = threading.Thread(target=auto_decrease_stats, daemon=True)
auto_thread.start()

@bot.message_handler(commands=['admin'])
def admin(message):
    print(editing_name)

@bot.message_handler(commands=['start'])
def start(message):
    # Сбрасываем статистику питомца
    PetStats.pet_name = 'Пи-Пи'
    PetStats.pet_food = 50
    PetStats.pet_mood = 50
    PetStats.is_alive = True
    PetStats.pet_state = 0
    
    # Inline кнопки
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Изменить имя ✏️', callback_data="edit_name")
    btn2 = types.InlineKeyboardButton('Статус 📊', callback_data="status")
    markup.row(btn1, btn2)
    
    # Reply кнопки
    rep_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    rep_btn1 = types.KeyboardButton(f'Показать {PetStats.pet_name}')
    rep_btn2 = types.KeyboardButton('Статус 📊')
    rep_btn3 = types.KeyboardButton('Покормить 🍔')
    rep_btn4 = types.KeyboardButton('Поиграть 🎮')
    rep_btn5 = types.KeyboardButton('Сюрприз 🎁')
    rep_btn6 = types.KeyboardButton('🎮 Мини-игры')

    rep_markup.row(rep_btn1)
    rep_markup.row(rep_btn2, rep_btn3, rep_btn4)
    rep_markup.row(rep_btn5, rep_btn6)
    
    bot.send_photo(
        message.chat.id, open(photos[PetStats.pet_state],'rb'),
        caption=f'🎉 Привет!\n\nЭто ваш питомчик "{PetStats.pet_name}"!\n\nКормите и играйте с ним, чтобы он не помер 😘', 
        reply_markup=markup
    )
    bot.send_message(
        message.chat.id, 
        'Используйте кнопочки для управления питомцем ☺️', 
        reply_markup=rep_markup
    )

# Обработчик для reply кнопки "Показать {имя}"
@bot.message_handler(func=lambda message: message.text == f'Показать {PetStats.pet_name}')
def show_pet(message):
    if not PetStats.is_alive:
        pet_die_message(message)
        return
        
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Изменить имя ✏️', callback_data="edit_name")
    btn2 = types.InlineKeyboardButton('Статус 📊', callback_data="status")
    markup.row(btn1, btn2)
    
    bot.send_photo(
        message.chat.id, open(photos[PetStats.pet_state],'rb'),
        caption=f'🐾 Ваш питомчик "{PetStats.pet_name}"!\n\nКормите и играйте с ним, чтобы он не помер 😘', 
        reply_markup=markup
    )

# ======== Обработчики inline кнопок ========
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == 'edit_name':
        handle_edit_name(call)
    elif call.data == 'status':
        show_status(call.message)

def handle_edit_name(call):
    if not PetStats.is_alive:
        bot.send_message(call.message.chat.id, '💀 Ваш питомец умер! Используйте /start чтобы завести нового.')
        return
        
    editing_name[call.from_user.id] = True
    bot.send_message(call.message.chat.id, 'Введите новое имя для вашего питомца...')

@bot.message_handler(func=lambda message: editing_name.get(message.from_user.id, False))
def handle_new_name(message):
    editing_name[message.from_user.id] = False
    
    if not PetStats.is_alive:
        pet_die_message(message)
        return
        
    PetStats.pet_name = message.text
    
    # Обновляем reply кнопку с новым именем
    rep_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    rep_btn1 = types.KeyboardButton(f'Показать {PetStats.pet_name}')
    rep_btn2 = types.KeyboardButton('Статус 📊')
    rep_btn3 = types.KeyboardButton('Покормить 🍔')
    rep_btn4 = types.KeyboardButton('Поиграть 🎮')
    rep_btn5 = types.KeyboardButton('Сюрприз 🎁')
    rep_markup.row(rep_btn1)
    rep_markup.row(rep_btn2, rep_btn3, rep_btn4)
    rep_markup.row(rep_btn5)
    
    bot.send_message(
        message.chat.id, 
        f'Твоего питомца теперь зовут "{PetStats.pet_name}"!', 
        reply_markup=rep_markup
    )

# ======== Сюрприз с рандомными эффектами ========
@bot.message_handler(commands=['surprise'])
def surprise_command(message):
    surprise_effect(message)

@bot.message_handler(func=lambda message: message.text == 'Сюрприз 🎁')
def surprise_button(message):
    surprise_effect(message)

def surprise_effect(message):
    if not PetStats.is_alive:
        pet_die_message(message)
        return
    
    effects = [
        {
            "text": "🎁 Питомец нашел вкусняшку под диваном! Еда +20", 
            "food": 20, "mood": 0
        },
        {
            "text": "💥 Соседи начали ремонт! Питомец испугался шума. Настроение -10", 
            "food": 0, "mood": -10
        },
        {
            "text": "🌈 За окном появилась радуга! Настроение +25", 
            "food": 0, "mood": 25
        },
        {
            "text": "🍀 Вам сегодня везет! Все показатели +10", 
            "food": 10, "mood": 10
        },
        {
            "text": "😴 Питомец случайно уснул и пропустил обед. Еда -5", 
            "food": -5, "mood": 0
        },
        {
            "text": "🎉 Фестиваль еды в городе! Еда +30, Настроение +15", 
            "food": 30, "mood": 15
        },
        {
            "text": "🌧 Внезапный дождь испортил прогулку. Настроение -15", 
            "food": 0, "mood": -15
        },
        {
            "text": "⭐️ Соседка похвалила вашего питомца! Настроение +20", 
            "food": 0, "mood": 20
        },
        {
            "text": "🚗 Поездка к ветеринару... Еда -10, Настроение -10", 
            "food": -10, "mood": -10
        },
        {
            "text": "🏆 Питомец выиграл конкурс красоты! Еда +15, Настроение +25", 
            "food": 15, "mood": 25
        }
    ]

    effect = random.choice(effects)
    PetStats.pet_food += effect["food"]
    PetStats.pet_mood += effect["mood"]
    
    # Обновляем состояние после сюрприза
    update_pet_state()
    
    bot.send_message(message.chat.id, f"🎲 Сюрприз: {effect['text']}")
    check_pet_health(message)

# ======== Статусы и их изменения ========
def pet_die_message(message):
    PetStats.pet_state = 3 
    bot.send_photo(message.chat.id, open(photos[PetStats.pet_state],'rb'), caption='💀 Ваш питомец умер! Используйте /start чтобы завести нового.')

def show_status(message):
    if not PetStats.is_alive:
        pet_die_message(message)
        return
        
    # Определяем состояние питомца
    status_emoji = "😊"
    if PetStats.pet_food < 20 or PetStats.pet_mood < 20:
        status_emoji = "😟"
    if PetStats.pet_food < 10 or PetStats.pet_mood < 10:
        status_emoji = "😨"
        
    bot.send_message(
        message.chat.id, 
        f"{status_emoji} Питомец {PetStats.pet_name}\n"
        f"🍔 Еда: {PetStats.pet_food}\n"
        f"🎮 Настроение: {PetStats.pet_mood}"
    )

def feed_pet(message):
    if not PetStats.is_alive:
        pet_die_message(message)
        return
        
    PetStats.pet_food += 15
    PetStats.pet_mood -= 5
    
    # Обновляем состояние после кормления
    update_pet_state()
    
    bot.send_message(
        message.chat.id, 
        f"Ням-ням! 😋🍔\nЕда +15, Настроение -5"
    )
    
    check_pet_health(message)

def play_with_pet(message):
    if not PetStats.is_alive:
        pet_die_message(message)
        return
        
    PetStats.pet_mood += 15
    PetStats.pet_food -= 5
    
    # Обновляем состояние после игры
    update_pet_state()
    
    bot.send_message(
        message.chat.id, 
        f"Ураа играем! 😜🎮\nНастроение +15, Еда -5"
    )
    
    check_pet_health(message)

def check_pet_health(message):
    """Проверяем состояние питомца и объявляем смерть если нужно"""
    if PetStats.pet_food <= 0 or PetStats.pet_mood <= 0:
        PetStats.is_alive = False
        PetStats.pet_state = 3
        pet_die_message(message)
        return True
    return False

# ======== Обработчики команд ========
@bot.message_handler(commands=['status'])
def status_command(message):
    show_status(message)

@bot.message_handler(commands=["play"])
def play_command(message):
    play_with_pet(message)

@bot.message_handler(commands=["feed"])
def feed_command(message):
    feed_pet(message)

# Обработчики для reply кнопок
@bot.message_handler(func=lambda message: message.text == 'Статус 📊')
def status_button(message):
    show_status(message)

@bot.message_handler(func=lambda message: message.text == 'Покормить 🍔')
def feed_button(message):
    feed_pet(message)

@bot.message_handler(func=lambda message: message.text == 'Поиграть 🎮')
def play_button(message):
    play_with_pet(message)




#=========== Развлечения ==========
@bot.message_handler(func=lambda message: message.text == '🎮 Мини-игры')
def mini_games_button(message):
    game_menu(message)

@bot.message_handler(commands=['game'])
def game_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🎲 Dice-игры 🎰')
    btn2 = types.KeyboardButton('Крестики-нолики')
    btn3 = types.KeyboardButton('🏆 Выйти из игр')
    markup.row(btn1, btn2)
    markup.row(btn3)
    
    bot.send_message(message.chat.id, 'Выберите игру ⬇️', reply_markup=markup)

# Обработчики для меню игр (без состояний)
@bot.message_handler(func=lambda message: message.text == '🎲 Dice-игры 🎰')
def dice_games_button(message):
    dice_menu(message)

@bot.message_handler(func=lambda message: message.text == 'Крестики-нолики')
def tictactoe_button(message):
    tictactoe_menu(message)

@bot.message_handler(func=lambda message: message.text == '🏆 Выйти из игр')
def exit_games_button(message):
    bot.send_message(message.chat.id, 'Игровой центр закрыт!')
    start(message)

def tictactoe_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Начать новую игру 🔄')
    btn2 = types.KeyboardButton('Выйти в меню игр')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Выйти в меню игр')
def back_to_game_menu(message):
    game_menu(message)

@bot.message_handler(func=lambda message: message.text == 'Начать новую игру 🔄')
def start_tictactoe(message):
    # Инициализируем игру
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['board'] = [['_','_','_'], ['_','_','_'], ['_','_','_']]
        data['step'] = 0
        data['game_active'] = True
    
    # Показываем первое поле
    vInput(message, data['board'], data['step'])

def vInput(message, board, step):
    markup = types.InlineKeyboardMarkup()
    # Показываем номера на пустых клетках, символы на занятых
    btn1 = types.InlineKeyboardButton('_' if board[0][0] == '_' else board[0][0], callback_data="move_1")
    btn2 = types.InlineKeyboardButton('_' if board[0][1] == '_' else board[0][1], callback_data="move_2")
    btn3 = types.InlineKeyboardButton('_' if board[0][2] == '_' else board[0][2], callback_data="move_3")
    btn4 = types.InlineKeyboardButton('_' if board[1][0] == '_' else board[1][0], callback_data="move_4")
    btn5 = types.InlineKeyboardButton('_' if board[1][1] == '_' else board[1][1], callback_data="move_5")
    btn6 = types.InlineKeyboardButton('_' if board[1][2] == '_' else board[1][2], callback_data="move_6")
    btn7 = types.InlineKeyboardButton('_' if board[2][0] == '_' else board[2][0], callback_data="move_7")
    btn8 = types.InlineKeyboardButton('_' if board[2][1] == '_' else board[2][1], callback_data="move_8")
    btn9 = types.InlineKeyboardButton('_' if board[2][2] == '_' else board[2][2], callback_data="move_9")
    
    markup.row(btn1, btn2, btn3)
    markup.row(btn4, btn5, btn6)
    markup.row(btn7, btn8, btn9)
    
    current_player = 'O' if step == 0 else 'X'
    bot.send_message(message.chat.id, f'Выберите поле для хода ({current_player})', reply_markup=markup)
# Обработчик для 'dice' игр
# Обработчик для полученных dice сообщений
@bot.message_handler(content_types=['dice'])
def handle_dice_result(message):
    if not PetStats.is_alive:
        bot.send_message(message.chat.id, '💀 Питомец умер! Сначала оживите его через /start')
        return
        
    # Штраф за попытку
    PetStats.pet_food -= 1
    check_pet_health(message)
    
    value = message.dice.value
    emoji = message.dice.emoji
    
    responses = {
        '🎲': (f"🎲 На кубике выпало: {value}!", value == 6),
        '🎯': (f"🎯 Попадание в {value} сектор!", value == 6),
        '🏀': (f"🏀 Ну бро", value >= 4),
        '⚽': (f"⚽ Ну бро", value >= 3),
        '🎰': (f"🎰 Ну..", value in [1, 22, 43, 64])
    }
    
    if emoji in responses:
        text, is_win = responses[emoji]
        if is_win:
            # Награда за победу
            if emoji == '🎰':
                PetStats.pet_mood += 10
                text += " 🎰 Джекпот реально! +10 настроения!"
            else:
                PetStats.pet_mood += 5
                text += " +5 настроения!"
        else:
            text += " Попробуй еще!"
            
        bot.reply_to(message, text)
        update_pet_state()
    else:
        bot.reply_to(message, f"🎮 Игровой бросок: {value}")
@bot.message_handler(func=lambda message: message.text in ['🎲', '🎯', '🏀', '⚽', '🎰'])
def handle_dice_selection(message):
    # Отправляем соответствующий dice
    if message.text == '🎲':
        bot.send_dice(message.chat.id, '🎲')
    elif message.text == '🎯':
        bot.send_dice(message.chat.id, '🎯')
    elif message.text == '🏀':
        bot.send_dice(message.chat.id, '🏀')
    elif message.text == '⚽':
        bot.send_dice(message.chat.id, '⚽')
    elif message.text == '🎰':
        bot.send_dice(message.chat.id, '🎰')

def dice_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🎲')
    btn2 = types.KeyboardButton('🎯')
    btn3 = types.KeyboardButton('🏀')
    btn4 = types.KeyboardButton('⚽')
    btn5 = types.KeyboardButton('🎰')
    btn6 = types.KeyboardButton('Выйти в меню игр')
    markup.row(btn1, btn2, btn3)
    markup.row(btn4, btn5, btn6)
    bot.send_message(message.chat.id, '🎮 Выберите игровой бросок 🎮', reply_markup=markup)

# Обработчик callback для крестиков-ноликов (без состояния)
#dice
@bot.callback_query_handler(func=lambda call: call.data.startswith('move_'))
@bot.callback_query_handler(func=lambda call: call.data.startswith('move_'))
def handle_move(call):
    # Проверяем, есть ли активная игра
    try:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            if 'game_active' not in data or not data['game_active']:
                bot.answer_callback_query(call.id, "Начните новую игру!")
                return
                
            board = data['board']
            step = data['step']
    except:
        bot.answer_callback_query(call.id, "Начните новую игру!")
        return
    
    v = int(call.data.split('_')[1])
    i = (v-1) // 3
    j = (v-1) % 3
    
    if board[i][j] != '_':
        bot.answer_callback_query(call.id, "Эта клетка уже занята! Выберите другую.")
        return
    
    # Ход игрока
    current_player = 'O' if step == 0 else 'X'
    board[i][j] = current_player
    
    # Сразу обновляем данные
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['board'] = board
        
        if WinCheck(board):
            data['game_active'] = False
            update_board_display(call, board, f'🎉 Победитель: {current_player}!')
            bot.answer_callback_query(call.id, f"Победа! {current_player} выиграл!")
            bot.send_message(call.message.chat.id, f'{current_player} Выиграл!\nGameOver')
            return
        
        # Проверяем ничью
        if all(cell != '_' for row in board for cell in row):
            data['game_active'] = False
            update_board_display(call, board, '🤝 Ничья!')
            bot.answer_callback_query(call.id, "Ничья!")
            bot.send_message(call.message.chat.id, 'Ничья!\nGameOver')
            return
        
        # Ход бота через 2 секунды
        data['step'] = 1 - step
        update_board_display(call, board, '🤖 Бот думает...')
        bot.answer_callback_query(call.id, "Ход принят!")
    
    threading.Timer(2.0, bot_move, [call.message.chat.id, call.from_user.id]).start()
def bot_move(chat_id, user_id):
    with bot.retrieve_data(user_id, chat_id) as data:
        if not data.get('game_active', True):
            return
            
        board = data['board']
        
        # Простой ИИ: случайный ход
        empty_cells = [(i, j) for i in range(3) for j in range(3) if board[i][j] == '_']
        if empty_cells:
            i, j = random.choice(empty_cells)
            board[i][j] = 'X'  # Бот всегда X
            
            if WinCheck(board):
                data['game_active'] = False
                bot.send_message(chat_id, '🤖 Бот выиграл!\nGameOver')
                return
            
            if all(cell != '_' for row in board for cell in row):
                data['game_active'] = False
                bot.send_message(chat_id, '🤝 Ничья!\nGameOver')
                return
            
            data['step'] = 0  # Переход хода к игроку
            
            # Обновляем поле
            markup = types.InlineKeyboardMarkup()
            buttons = []
            for v in range(1, 10):
                i = (v-1) // 3
                j = (v-1) % 3
                button_text = '_' if board[i][j] == '_' else board[i][j]
                buttons.append(types.InlineKeyboardButton(button_text, callback_data=f"move_{v}"))
            
            markup.row(buttons[0], buttons[1], buttons[2])
            markup.row(buttons[3], buttons[4], buttons[5])
            markup.row(buttons[6], buttons[7], buttons[8])
            
            bot.send_message(chat_id, 'Выберите поле для хода (O)', reply_markup=markup)
def WinCheck(a):
    for i in range(3):
        if a[i][0]==a[i][1]==a[i][2]!='_':
            return True
    for i in range(3):
        if a[0][i]==a[1][i]==a[2][i]!='_':
            return True
    if a[0][0]==a[1][1]==a[2][2]!='_':return True
    if a[0][2]==a[1][1]==a[2][0]!='_':return True
    return False
def update_board_display(call, board, text):
    #Обновляет сообщение с игровым полем
    markup = types.InlineKeyboardMarkup()
    # Создаем обновленные кнопки
    buttons = []
    for v in range(1, 10):
        i = (v-1) // 3
        j = (v-1) % 3
        button_text = '_' if board[i][j] == '_' else board[i][j]
        buttons.append(types.InlineKeyboardButton(button_text, callback_data=f"move_{v}"))
    
    markup.row(buttons[0], buttons[1], buttons[2])
    markup.row(buttons[3], buttons[4], buttons[5])
    markup.row(buttons[6], buttons[7], buttons[8])
    
    # Редактируем существующее сообщение
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )


print('ботик работает...')
bot.infinity_polling()