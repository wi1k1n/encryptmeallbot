#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Bot which takes messages
"""
from telegram.ext import Updater, Filters, CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler
from api_token import TOKEN
from handlers import *

helpDict = {
	'password': (setPassword, 'change password'),
	'encode': (encodeMode, 'turn on encode mode'),
	'decode': (decodeMode, 'turn on decode mode'),
	'help': (help, 'show this message'),
	'clear': (clearMessages, 'clears all messages from history')
}

def main():
	updater = Updater(TOKEN, use_context=True)
	dp = updater.dispatcher

	dp.add_handler(MessageHandler(Filters.all, everySignal), group=0)
	dp.add_handler(ConversationHandler(
		entry_points=[
			CommandHandler('start', start),
			MessageHandler(Filters.all, start)
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
				MessageHandler(Filters.all, confirmPassword),
				CallbackQueryHandler(cancelRepeatPassword)
			]
		},
		fallbacks=[]
	), group=1)

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