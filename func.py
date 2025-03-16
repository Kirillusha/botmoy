from aiogram import Bot, types
import random
import sqlite3
from keyboards.keyboards import *
from data.config import *

bot = Bot(TOKEN, parse_mode=types.ParseMode.HTML)

line = '➖➖➖➖➖➖➖➖➖➖➖➖'

#Прислать меню
async def menu(user_id):
	await bot.send_sticker(chat_id= user_id, sticker=r"CAACAgIAAxkBAAEJx0ZkvDBML2DCMJNHvztqecj2ZNR-GAACAQEAAladvQoivp8OuMLmNC8E")
	await bot.send_message(chat_id = user_id, text = f'<b>🎧 Добро пожаловать!</b>\n{line}\n<b>💰 Ваш баланс:</b> <i>{await get_user_balance(user_id)} RUB</i>', reply_markup = await menu_keyboard(user_id))

async def CHECK_IN_BASE(us_id):
	conn = sqlite3.connect("data/db.db", check_same_thread=False)
	cur = conn.cursor()
	in_base = cur.execute('SELECT user_id FROM users WHERE user_id = (?)', (us_id,)).fetchone()
	return in_base

async def profile(message):
	balance = await get_user_balance(message.from_user.id)
	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.add(
		types.InlineKeyboardButton(text="💲 Накрутка реакций", callback_data="nak_reak"),
		types.InlineKeyboardButton(text='💸 Накрутка голосов на опрос', callback_data='nak_gol'),	
		types.InlineKeyboardButton(text='💸 Накрутка подписчиков', callback_data='nak_podpis'),		
		)
	await bot.send_sticker(chat_id= message.from_user.id, sticker=r"CAACAgIAAxkBAAEJx0RkvC-R2k14VXO2ed6M2lHRynIv2AACSQIAAladvQoqlwydCFMhDi8E")
	await bot.send_message(chat_id = message.from_user.id, text=
'''
<b>👤 Ваш ID:</b> <code>{0}</code>
<b>💰 Ваш баланс:</b> <i>{1} RUB</i>

<b>Выберите услугу</b>
'''.format(message.from_user.id, balance), reply_markup = keyboard)


async def get_subscribers_cost(count):
    cost = count * podpis
    return cost

async def get_poll_votes_cost(count):
    cost = count * golos
    return cost

async def get_likes_cost(count):
    cost = count * like
    return cost


#Получить баланс
async def get_user_balance(user_id):
	conn = sqlite3.connect('data/db.db', check_same_thread=False)
	cursor = conn.cursor()
	try:
		cursor.execute('SELECT balance FROM users WHERE user_id = (?)', (user_id,))
		balance = cursor.fetchone()[0]
	except:
		balance = 0
	conn.close()
	round_balance = round(balance, 2)
	return round_balance

async def get_admin_status(user_id):
	conn = sqlite3.connect('data/db.db', check_same_thread=False)
	cursor = conn.cursor()
	if user_id in admin:
		return 1
	else:
		status = cursor.execute('SELECT admin FROM users WHERE user_id = (?)', (user_id,)).fetchone()[0]
		return status


#///////////////////////////////ПОПОЛНЕНИЕ\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
async def CARD_PAY(summa, user_id):
	try:
		with open('data/reki.txt', 'r', encoding='utf-8') as file:
			reki = file.read()
		random_number = random.randint(0, 99999)
		desc = f'PaymentID:{user_id}:{random_number}'
		keyboard = types.InlineKeyboardMarkup(row_width = 2)
		buttons = [
		types.InlineKeyboardButton(text="✅ Отправить чек", callback_data=f'CheckCard_{random_number}_{summa}'),
		]
		keyboard.add(*buttons)
		await bot.send_message(chat_id = user_id, text = f'''<b><i>💴 Сумма к оплате: {summa} RUB</i></b>

<b>Отправьте {summa} RUB по реквезитам и в комментариях укажите {desc}:
<code>{reki}</code>

{line}

После перевода сохраните чек, нажмите кнопку "Отправить чек" и отправиьте чек в виде фото</b>''', parse_mode='HTML', reply_markup = keyboard)
	except Exception as e:
		print(e)
		for ADMIN in admin:
			await bot.send_message(chat_id = ADMIN, text = f'Ошибка пополнения\n{e}')
		await menu(user_id)
		await bot.send_message(chat_id = user_id, text ='<b><i>Депозит временно недоступно...\nМы уже занимаемся этим вопросом</i></b>')

#///////////////////////////////////////////////////АДМИНМЕНЮ\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

async def adminmenu(user_id):
	conn = sqlite3.connect('data/db.db', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(1) FROM users")
	all_users = cursor.fetchone()[0]
	all_balance = cursor.execute('SELECT SUM(balance) FROM users').fetchone()[0]
	conn.close()
	await bot.send_message(chat_id = user_id, text = f'''{line}
🙆‍♂️ <b>Количество пользователей:</b> <i>{all_users} шт</i>
🏦 <b>Общий баланс:</b> <i>{all_balance} RUB</i>
''', parse_mode='HTML',reply_markup = await admin_keyboard())
