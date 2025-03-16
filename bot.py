
#//////////////////////////////////////////// https://t.me/lolzteam_lolz \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3
import logging
import time
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove

from data.config import *
from func import *


bot = Bot(TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot,storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


line = '➖➖➖➖➖➖➖➖➖➖➖➖'

class NakrutkaState(StatesGroup):
    GET_NAKRUTKA_SUBSCRIBERS = State()
    GET_NAKRUTKA_POLL_VOTES = State()
    GET_NAKRUTKA_LIKES = State()
    CONFIRM_NAKRUTKA = State()
    
class CARD(StatesGroup):
    money = State()

class CheckoutForm(StatesGroup):
    waiting_for_photo = State()

class TRANSFER(StatesGroup):
    user = State()
    money = State()

class GET_TEXT_RASSILKA(StatesGroup):
    TEXT = State()

class GET_PHOTO_RASSILKA(StatesGroup):
    PHOTO = State()
    TEXT = State()
    START = State()

class GET_USERS_BALANCE(StatesGroup):
    US_ID = State()
    SUMMA = State()


async def anti_flood(*args, **kwargs):
    m = args[0]
    try:
        await m.answer("📛 Не флуди!", show_alert =True)
    except:
        await m.answer("📛 Не флуди!")

@dp.callback_query_handler(text = 'menu')
async def get_menu(call):
    await menu(call.from_user.id)
#Старт
@dp.message_handler(commands=['start'])
@dp.throttled(anti_flood,rate=0)
async def start(message):
        conn = sqlite3.connect('data/db.db', check_same_thread = False)
        cursor = conn.cursor()
        in_base = await CHECK_IN_BASE(message.from_user.id)
        if in_base != None:
            await menu(message.from_user.id)
        else:
            cursor.execute('INSERT INTO users (user_id) VALUES (?)', (message.from_user.id,))
            conn.commit()
            await menu(message.from_user.id)

@dp.message_handler(text = '👨‍💻 Услуги')
@dp.throttled(anti_flood,rate=0)
async def get_profile(message):
    await get_nakrutka(message)

@dp.message_handler(text = 'Баланс')
@dp.throttled(anti_flood,rate=0)
async def get_menu(message):
    await get_money(message)

@dp.message_handler(text = 'get_money')
@dp.throttled(anti_flood,rate=0)
async def get_money(message):
    await message.answer(text=f'<b>👤 Ваш ID:<code>{message.from_user.id}</code>\n💰 Ваш баланс:</b> <i>{await get_user_balance(message.from_user.id)} RUB</i>', reply_markup = await payments_keyboard())

@dp.callback_query_handler(text_contains = 'Popa')
async def CARD_METHOD(call):
    await CARD.money.set()
    await call.message.answer(text=
        '— Минимум: <b>10 RUB</b>\n\n'
        f'<b>💸 Введите сумму пополнения в рублях</b>',)

@dp.message_handler(state=CARD.money)
async def get_summa(message: types.Message, state: FSMContext):
    try:
        if float(message.text) >= 10:
            await CARD_PAY(message.text, message.from_user.id)
        else:
            await message.answer(
                '<b>⚠️ Минимум: 10 RUB!</b>'
            )
    except ValueError:
        await message.answer(
            '<b>❗️Сумма для пополнения должна быть в числовом формате!</b>'
        )
    await state.finish()

@dp.callback_query_handler(text_contains='CheckCard_')
async def check_card_func(call):
    await CheckoutForm.waiting_for_photo.set()
    await call.message.answer('<b>Отправьте чек</b>')

@dp.message_handler(content_types=types.ContentTypes.PHOTO, state=CheckoutForm.waiting_for_photo)
async def handle_photo(message: types.Message, state: FSMContext, callback_data: dict = None):
    photo_file_id = message.photo[-1].file_id
    chat_id = message.from_user.id
    await bot.send_photo(LOG_DIALOG, photo_file_id, caption=f'💸💸Пользователь {chat_id} отправил оплату')
    
    await state.finish()
    await menu(message.from_user.id)
    await message.answer('<b>Ожидайте...</b>')
    

@dp.message_handler(text='Накрутка')
async def get_nakrutka(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard = True)
    keyboard.add(types.KeyboardButton(text='👨🏼Подписчики'),
                types.KeyboardButton(text='🗣Голоса на опрос')),
    keyboard.add(types.KeyboardButton(text='👍Лайки')),
    await message.answer('<b>Выберите тип накрутки:</b>', reply_markup=keyboard)

@dp.message_handler(Text(equals='👨🏼Подписчики'))
async def get_nakrutka_subscribers(message, state: FSMContext):
    await message.answer('<b>Введите количество подписчиков, которое необходимо накрутить:</b>')
    await NakrutkaState.GET_NAKRUTKA_SUBSCRIBERS.set()

@dp.message_handler(Text(equals='🗣Голоса на опрос'))
async def get_nakrutka_poll_votes(message, state: FSMContext):
    await message.answer('<b>Введите количество голосов, которое необходимо накрутить:</b>')
    await NakrutkaState.GET_NAKRUTKA_POLL_VOTES.set()

@dp.message_handler(Text(equals='👍Лайки'))
async def get_nakrutka_likes(message, state: FSMContext):
    await message.answer('<b>Введите количество лайков, которое необходимо накрутить:</b>')
    await NakrutkaState.GET_NAKRUTKA_LIKES.set()

@dp.message_handler(lambda message: message.text.isdigit(), state=NakrutkaState.GET_NAKRUTKA_SUBSCRIBERS)
@dp.message_handler(lambda message: message.text.isdigit(), state=NakrutkaState.GET_NAKRUTKA_POLL_VOTES)
@dp.message_handler(lambda message: message.text.isdigit(), state=NakrutkaState.GET_NAKRUTKA_LIKES)
async def process_nakrutka(message, state: FSMContext):
    count = int(message.text)
    current_state = await state.get_state()
    service_types = None
    if current_state == NakrutkaState.GET_NAKRUTKA_SUBSCRIBERS.state:
        cost = await get_subscribers_cost(count)
        service_types = 'подписчиков 👨🏼'
    elif current_state == NakrutkaState.GET_NAKRUTKA_POLL_VOTES.state:
        cost = await get_poll_votes_cost(count)
        service_types = 'голосов 🗣'
    elif current_state == NakrutkaState.GET_NAKRUTKA_LIKES.state:
        cost = await get_likes_cost(count)
        service_types = '👍лайков'
    else:
        await message.answer('❌ <b>Неизвестный тип накрутки. Повторите попытку.</b>')
        await state.finish()
        await menu(message.from_user.id)
        return
    cena = round(cost, 2)
    await message.answer(f'<b>Накрутка {service_types} будет стоить {cena} руб. Подтвердите накрутку:</b>',
                         reply_markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(
                             types.KeyboardButton(text='Да'),
                             types.KeyboardButton(text='Отмена')
                         ))
    await state.update_data(count=count, cost=cost, service_types=service_types)
    await NakrutkaState.CONFIRM_NAKRUTKA.set()

@dp.message_handler(Text(equals='Да'), state=NakrutkaState.CONFIRM_NAKRUTKA)
async def confirm_nakrutka(message, state: FSMContext):
    data = await state.get_data()
    conn = sqlite3.connect('data/db.db', check_same_thread = False)
    cursor = conn.cursor()
    service_type = data.get('service_types')
    cost = data.get('cost')
    cena = round(cost, 2)
    conn = sqlite3.connect('data/db.db', check_same_thread = False)
    cursor = conn.cursor()
    user_id=message.from_user.id
    balance = float(await get_user_balance(user_id))
    if balance < (float(cena)):
        await message.answer(f'<b>Ваш баланс меньше суммы заказа.</b>',
                         reply_markup=ReplyKeyboardRemove())
        await state.finish()
        await menu(message.from_user.id)
    else:
        cursor.execute('UPDATE users SET balance = balance - (?) WHERE user_id = (?)', (cena, user_id))
        conn.commit()
        await message.answer(f'<b>Вы заказали накрутку <i>{service_type}</i> за {cena} руб. Ожидайте выполнения.</b>',
                            reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=LOG_DIALOG, text=f'‼️ {user_id} заказал накрутку <i>{service_type}</i> за {cena} руб.\n\nРаботаем.')
        await state.finish()
        await menu(message.from_user.id)

@dp.message_handler(Text(equals='Отмена'), state=NakrutkaState.CONFIRM_NAKRUTKA)
async def cancel_nakrutka(message, state: FSMContext):
    await message.answer('Накрутка отменена.', reply_markup=ReplyKeyboardRemove())
    await state.finish()
    await menu(message.from_user.id)

#////////////////////////////////////////////АДМИНКА\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


@dp.message_handler(text_contains="Админка")
@dp.throttled(anti_flood,rate=0)
async def get_adminmenu(message):
    adminka = await get_admin_status(message.from_user.id)
    if adminka == 1:
        await adminmenu(message.from_user.id)

#Выдача баланса
@dp.message_handler(text_contains="Выдать/Забрать баланс")
@dp.throttled(anti_flood,rate=0)
async def get_for_user_balance(message):
    adminka = await get_admin_status(message.from_user.id)
    if adminka == 1:
        await message.answer('Введите id пользователя')
        await GET_USERS_BALANCE.US_ID.set()


@dp.message_handler(state=GET_USERS_BALANCE.US_ID)
@dp.throttled(anti_flood,rate=0)
async def get_summa_for_user_balance(message, state):
    conn = sqlite3.connect('data/db.db', check_same_thread=False)
    cursor = conn.cursor()
    info = cursor.execute('SELECT * FROM users WHERE user_id = (?)', (message.text,)).fetchall()
    if info == []:
        await message.answer('Такого пользователя не существует')
        await state.finish()
        await adminmenu(message.from_user.id)
    else:
        await message.answer('<i>Чтобы отнять сумму от баланса введите число с минусом (Например -1000)</i>\n\n<b>Введите сумму:</b>')
        await state.update_data(us_id = message.text)
        await GET_USERS_BALANCE.SUMMA.set()
    conn.close()

@dp.message_handler(state=GET_USERS_BALANCE.SUMMA)
@dp.throttled(anti_flood,rate=0)
async def start_get_balance(message, state):
    adminka = await get_admin_status(message.from_user.id)
    if adminka == 1:
        if message.text.startswith('-'):
            money = message.text[1:]
            if money.isdigit():
                user_data = await state.get_data()
                us_id = user_data['us_id']
                conn = sqlite3.connect('data/db.db', check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET balance = balance + (?) WHERE user_id = (?)', (message.text, us_id))
                conn.commit()
                await message.answer(f'Успешно!\nБаланс {us_id} теперь {await get_user_balance(us_id)} RUB')
                await adminmenu(message.from_user.id)
        elif message.text.isdigit():
            user_data = await state.get_data()
            us_id = user_data['us_id']
            conn = sqlite3.connect('data/db.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET balance = balance + (?) WHERE user_id = (?)', (message.text, us_id))
            conn.commit()
            await bot.send_message(chat_id = us_id, text = f'Зачислено {message.text} RUB на баланс!')
            await message.answer(f'Успешно!\nБаланс {us_id} теперь {await get_user_balance(us_id)} RUB')
            await adminmenu(message.from_user.id)
        else:
            await message.answer('Значение должно быть целым числом!')
            await adminmenu(message.from_user.id)
    await state.finish()

#///////////////////////////////////////Рассылка\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

#Только текст
@dp.message_handler(regexp="Сделать рассылку")
@dp.throttled(anti_flood,rate=0)
async def get_rassilka(message):
    adminka = await get_admin_status(message.from_user.id)
    if adminka == 1:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard=True, row_width = 2)
        buttons = [
        types.KeyboardButton(text='С фото'),
        types.KeyboardButton(text='Без фото'),
        types.KeyboardButton(text='Меню')
        ]
        keyboard.add(*buttons)
        await message.answer('Выберите тип рассылки:', reply_markup = keyboard)

@dp.message_handler(regexp="Без фото")
async def get_text_rassilka(message):
    adminka = await get_admin_status(message.from_user.id)
    if adminka == 1:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard=True, row_width = 1)
        btn1 = types.KeyboardButton(text = 'Меню')
        keyboard.add(btn1)
        await message.answer('Введите текст:', reply_markup = keyboard)
        await GET_TEXT_RASSILKA.TEXT.set()

@dp.message_handler(state=GET_TEXT_RASSILKA.TEXT)
async def start_text_rassilka(message, state):
    adminka = await get_admin_status(message.from_user.id)
    if adminka == 1:
        if message.text != 'Меню':
            conn = sqlite3.connect('data/db.db', check_same_thread=False)
            cursor = conn.cursor()
            row = cursor.execute('SELECT user_id FROM users').fetchall()
            succ = 0
            unsucc = 0
            for user in row:
                try:
                    await bot.send_message(chat_id = user[0], text = message.text)
                    succ +=1
                except:
                    unsucc +=1
            conn.close()
            await message.answer(f'Рассылка завершена!\nУспешно: {succ}\nНе Успешно: {unsucc}')
            await state.finish()
        else:
            await state.finish()
            await adminmenu(message.from_user.id)

# С фото
@dp.message_handler(regexp="С фото")
async def get_photo_rassilka(message):
    adminka = await get_admin_status(message.from_user.id)
    if adminka == 1:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard=True, row_width = 1)
        btn1 = types.KeyboardButton(text = 'Меню')
        keyboard.add(btn1)
        await GET_PHOTO_RASSILKA.PHOTO.set()
        await message.answer('Отправьте фото:')


@dp.message_handler(content_types=["photo"],state=GET_PHOTO_RASSILKA.PHOTO)
async def get2_photo_rassilka(message, state):
    adminka = await get_admin_status(message.from_user.id)
    if adminka == 1:
        photo_id = message.photo[-1].file_id
        await GET_PHOTO_RASSILKA.TEXT.set()
        await state.update_data(rasilka_photo = photo_id)
        await message.answer('Отправьте текст:')



@dp.message_handler(state=GET_PHOTO_RASSILKA.TEXT)
async def start_photo_rassilka(message, state):
    conn = sqlite3.connect('data/db.db', check_same_thread=False)
    cursor = conn.cursor()
    row = cursor.execute('SELECT user_id FROM users').fetchall()
    succ = 0
    unsucc = 0
    user_data = await state.get_data()
    photo = user_data['rasilka_photo']
    for user in row:
        try:
            await bot.send_photo(chat_id = user[0], photo = f'{photo}', caption = message.text)
            succ +=1
        except:
            unsucc +=1
    conn.close()
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard=True, row_width = 1)
    btn1 = types.KeyboardButton(text = 'Меню')
    keyboard.add(btn1)
    await state.finish()
    await message.answer(f'Рассылка завершена!\nУспешно: {succ}\nНе Успешно: {unsucc}')
    await adminmenu(message.from_user.id)


while True:
    try:
        if __name__ == "__main__":
            executor.start_polling(dp, skip_updates=True)
        break

    except:
        time.sleep(1)