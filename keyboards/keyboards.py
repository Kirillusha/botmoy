from aiogram import types
from data.config import *


async def menu_keyboard(user_id):
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
	keyboard.add(
		types.KeyboardButton(text = '👨‍💻 Услуги'),
		types.KeyboardButton(text = 'Баланс')
		)
	from func import get_admin_status
	adminka = await get_admin_status(user_id)
	if adminka == 1:
		keyboard.add(
			types.KeyboardButton(text = '👁 Админка')
			)
	return keyboard

async def payments_keyboard():
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width = 1)
    keyboard.row(
		types.InlineKeyboardButton(text = '💳 Пополнить баланс', callback_data='Popa'),
    	types.InlineKeyboardButton('Меню',callback_data='menu')
    	)
    return keyboard

async def admin_keyboard():
	keyboard = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard=True, row_width = 2)
	buttons = [
	types.KeyboardButton(text='Сделать рассылку'),
	types.KeyboardButton(text='Выдать/Забрать баланс'),
	types.KeyboardButton(text = 'Меню')
	]
	keyboard.add(*buttons)
	return keyboard