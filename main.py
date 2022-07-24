#!/usr/bin/python3

import random
import wikipedia
import re
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

def start(update, context) -> None:
	"""Displays a greeting and keyboard"""
	chat = update.effective_chat
	user = update.message.from_user
	context.bot.send_message(chat_id=chat.id,
							 text='Приветствую, ' + user.first_name + '!')
	keyboard = [
		[InlineKeyboardButton('Хочу цитату!', callback_data='1')],
		[
			InlineKeyboardButton('Узнать больше об авторе', callback_data='2'),
			InlineKeyboardButton('Узнать больше о книге', callback_data='3'),
		],
	]
	reply_markup = InlineKeyboardMarkup(keyboard)
	update.message.reply_text('Чем могу быть полезен?',
								reply_markup=reply_markup)
	logging.info(
		'Bot started by user {} {} (@{})'.format(
			user.first_name,
			user.last_name,
			user.username
		)
	)

def help(update, context) -> None:
	"""Displays help"""
	chat = update.effective_chat
	context.bot.send_message(chat_id=chat.id,
							 text='/start - запуск\n/help - помощь\n/quote - случайная цитата')

def button(update, context) -> None:
	"""Processes clicks on the buttons"""
	query = update.callback_query
	query.answer()
	choice = query.data
	if choice == '1':
		query.edit_message_text(text='Отправляю цитату...')
		quote(update, context)
	if choice == '2':
		query.edit_message_text(text='Как зовут автора?')
		wiki_result(update, context)
	if choice == '3':
		query.edit_message_text(text='Как называется книга?')
		wiki_result(update, context)

def quote(update, context) -> None:
	"""Displays random quote"""
	chat = update.effective_chat
	with open('quotes.txt', 'r') as f:
		data = f.readlines()
	quote = data[random.randint(0, len(data)-1)]
	context.bot.send_message(chat_id=chat.id,
							 text=quote)
	keyboard = [
		[InlineKeyboardButton('Еще одну цитату', callback_data='1')],
		[
			InlineKeyboardButton('Узнать больше об авторе', callback_data='2'),
			InlineKeyboardButton('Узнать больше о книге', callback_data='3'),
		],
	]
	reply_markup = InlineKeyboardMarkup(keyboard)
	context.bot.send_message(chat_id=chat.id,
							 text='Чем могу быть полезен?',
							 reply_markup=reply_markup)

def wiki_result(update, context) -> None:
	"""Displays information from Wikipedia"""
	chat = update.effective_chat
	wiki_image, wiki_text = wiki(update.message.text)
	try:
		context.bot.send_photo(chat_id=chat.id,
								 photo=wiki_image,
								 caption=wiki_text)
	except Exception as e:
		context.bot.send_message(chat_id=chat.id,
								 text=wiki_text)
	keyboard = [
		[InlineKeyboardButton('Хочу цитату!', callback_data='1')],
		[
			InlineKeyboardButton('Узнать больше об авторе', callback_data='2'),
			InlineKeyboardButton('Узнать больше о книге', callback_data='3'),
		],
	]
	reply_markup = InlineKeyboardMarkup(keyboard)
	context.bot.send_message(chat_id=chat.id,
							 text='Вот, что мне удалось найти! ' +
							 	  'Если это не совсем то, можно попробовать ' +
								  'другой запрос. Чем могу быть полезен?',
							 reply_markup=reply_markup)

def wiki(string) -> None:
	"""Searches Wikipedia"""
	try:
		wikipedia.set_lang('ru')
		wiki_text = wikipedia.page(string).content[:1000].split('.')[:-1]
		wiki_image = wikipedia.page(string).images[-1]
		wiki_text_result = ''
		for x in wiki_text:
			if not('==' in x):
				if(len((x.strip())) > 3):
					wiki_text_result = wiki_text_result + x + '.'
			else:
				break
		wiki_text_result = re.sub('\([^()]*\)', '', wiki_text_result)
		wiki_text_result = re.sub('\([^()]*\)', '', wiki_text_result)
		wiki_text_result = re.sub('\{[^\{\}]*\}', '', wiki_text_result)
		return wiki_image, wiki_text_result
	except Exception as e:
		logging.exception('Exception occurred')
		return (':(', ':(')

def main() -> None:
	"""Starts a bot"""
	# Message to the terminal
	print('The bot is launched. Click Ctrl+C to stop')
	# Set logging
	format = '%(asctime)s %(levelname)s: %(message)s'
	logging.basicConfig(filename='applog.log', level=logging.INFO, format=format)
	# Token from BotFather
	token = ''
	# Create Updater
	updater = Updater(token)
	# Get Dispather for creating handlers
	dispatcher = updater.dispatcher
	# The handler of the command /start
	dispatcher.add_handler(CommandHandler('start', start))
	# The handler of the command /help
	dispatcher.add_handler(CommandHandler('help', help))
	# The handler of the command /quote
	dispatcher.add_handler(CommandHandler('quote', quote))
	# The handler of the buttons
	dispatcher.add_handler(CallbackQueryHandler(button))
	# The handler of the new messages
	dispatcher.add_handler(MessageHandler(Filters.text, wiki_result))
	# Launch of listening messages
	updater.start_polling()
	# The handler of Ctrl+C
	updater.idle()

if __name__ == '__main__':
	main()
