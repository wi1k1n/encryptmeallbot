#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Bot which asks for password and then encrypts/decrypts messages using given password
"""

# T O D O:	it seems to be impossible (with the current version of API) to check if user has deleted
# 			our message. It means that if he has, then editing this message will has no effect
# 			(he will not see any changes) and therefore communicating with the only msg is impossible.
# 			Solution: either to stack replies and delete them after they are not needed anymore or
# 			to just disregard user's stupidity and let him decide if he wants to delete our messages.

# TODO: communicate using editing via batches (e.g. batch for password changing, batch for encoding/decoding)
# 		but use ordinary replies inbetween batches
# TODO: setting which tells if original message should be insta-deleted
# TODO: check semantics (either all uses 'encode/decode' vocabulary or 'encrypt/decrypt')
# TODO: timer, which deletes encrypted messages

from telegram.ext import Updater, Filters, CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler
from api_token import TOKEN
from handlers import *

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
				MessageHandler(Filters.update, receivePassword)
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