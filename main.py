#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Bot which takes messages
"""
import logging
from telegram.ext import Updater, CommandHandler, ConversationHandler
from api_token import TOKEN

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(upd, ctx):
	chatId = upd.message.chat_id
	msg = upd.message.reply_text('Hi. I can encrypt your message. Just send it to me and I will encrypt it')


def main():
	updater = Updater(TOKEN, use_context=True)
	dp = updater.dispatcher

	dp.add_handler(ConversationHandler(
		entry_points=[
			CommandHandler('start', start)
		]
	))