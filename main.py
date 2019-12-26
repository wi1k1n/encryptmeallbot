#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Bot which takes messages
"""
import logging
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton as IKB
from telegram.ext import Updater, Filters, CommandHandler, ConversationHandler, MessageHandler
from api_token import TOKEN
from constants import *
from crypto import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(upd, ctx):
	logger.debug('>> start(upd, ctx)')

	# TODO: DB without need to ask new password every time the bot is reloaded
	# TODO: option to generate password
	ctx.chat_data['setpwd'] = True
	ctx.chat_data['mode'] = 'encode'
	msg = upd.message.reply_text('Hi. I can encrypt messages but first send me a password.')
	return STATE_RECEIVE_PWD

def setPassword(upd, ctx):
	logger.debug('>> setPassword(upd, ctx)')

	ctx.chat_data['setpwd'] = True

	msg = upd.message.reply_text('Please send me new password')
	return STATE_RECEIVE_PWD

def receivePassword(upd, ctx):
	logger.debug('>> receivePassword(upd, ctx)')

	# TODO: check for only text messages!
	# TODO: add cancel option (if user doesnt want change pwd anymore)
	if 'setpwd' in ctx.chat_data and ctx.chat_data['setpwd'] == True:
		# TODO: check for weakness!
		hash = get_hash(upd.message.text)
		upd.message.delete()
		ctx.chat_data['password'] = hash

		keyboard = [[IKB("Start over", callback_data='new_password')]]
		reply_markup = InlineKeyboardMarkup(keyboard)

		msg = upd.message.reply_text('Please repeat your password', reply_markup=reply_markup)
		return STATE_CONFIRM_PWD

def confirmPassword(upd, ctx):
	logger.debug('>> confirmPassword(upd, ctx)')

	if 'setpwd' in ctx.chat_data and ctx.chat_data['setpwd'] == True:
		hash = get_hash(upd.message.text)
		upd.message.delete()
		if ctx.chat_data['password'] != hash:
			msg = upd.message.reply_text('Entered passwords do not match. Enter new password')
			return STATE_RECEIVE_PWD
		else:
			ctx.chat_data['mode'] = 'encode'
			msg = upd.message.reply_text('New password created successfully! You can now send me message for encryption')
			return STATE_RECEIVE_MSG

def receiveMsg(upd, ctx):
	logger.debug('>> receiveMsg(upd, ctx)')

	if not 'mode' in ctx.chat_data:
		ctx.chat_data['mode'] = 'encode'
		logger.warning('Key "mode" was not found in ctx.chat_data. Initialized with mode=="encode"')

	foo = encrypt_string if ctx.chat_data['mode'] == 'encode' else decrypt_string

	msgBytes = foo(upd.message.text, ctx.chat_data['password'])
	upd.message.delete()
	msg = upd.message.reply_text(msgBytes)
	return STATE_RECEIVE_MSG

def encodeMode(upd, ctx):
	logger.debug('>> encodeMode(upd, ctx)')

	ctx.chat_data['mode'] = 'encode'
	msg = upd.message.reply_text('Encode mode on. Send me message to encrypt')
	return STATE_RECEIVE_MSG

def decodeMode(upd, ctx):
	logger.debug('>> decodeMode(upd, ctx)')

	ctx.chat_data['mode'] = 'decode'
	msg = upd.message.reply_text('Decode mode on. Send me message to decrypt')
	return STATE_RECEIVE_MSG

def error(upd, ctx):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', upd, ctx.error)

def helpMsg(upd, ctx):
	msg = ''
	for key in helpDict:
		val = helpDict[key]
		msg += '{0}     {1}\n'.format(key, val[1])
	upd.message.reply_text(msg)

helpDict = {
	'password': (setPassword, 'change password'),
	'encode': (encodeMode, 'turn on encode mode'),
	'decode': (decodeMode, 'turn on decode mode'),
	'help': (helpMsg, 'show this message')
}

def main():
	updater = Updater(TOKEN, use_context=True)
	dp = updater.dispatcher

	dp.add_handler(ConversationHandler(
		entry_points=[
			CommandHandler('start', start)
		],
		states={
			STATE_RECEIVE_MSG:
				[CommandHandler(k, helpDict[k][0]) for k in helpDict] + [
				MessageHandler(Filters.all, receiveMsg)
			],
			STATE_RECEIVE_PWD: [
				MessageHandler(Filters.all, receivePassword)
			],
			STATE_CONFIRM_PWD: [
				MessageHandler(Filters.all, confirmPassword)
			]
		},
		fallbacks=[]
	))

	# log all errors
	dp.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
	main()