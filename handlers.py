import logging

from telegram import ParseMode

from constants import *
from crypto import *
from keyboards import *
from util import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def storeMsgId(chd, msg):
	""" Takes chat_data dict and adds message_id for being able to delete all messages later on """
	if ninann(chd, DK_MSGIDS):
		chd[DK_MSGIDS] = []
	if not msg.message_id in chd[DK_MSGIDS]:
		chd[DK_MSGIDS].append(msg.message_id)


def everySignal(upd, ctx):
	""" Checks and actions needed to be performed on each atomic signal received from user """
	msgu = upd.message

	# Leave all groups/channels and stay only in private chats
	if not msgu.chat.type == msgu.chat.PRIVATE:
		logger.warning("Added to group #{0}! Leaving...".format(upd.message.chat_id))
		msgu.bot.leave_chat(msgu.chat_id)

	# Collect all message-ids in context in order to remove everything on logout
	storeMsgId(ctx.chat_data, msgu)

def clearMessages(upd, ctx):
	""" Clears all messages which ids are stored in ctx.chat_data[MSGIDS] """
	logger.debug('>> clearMessages(upd, ctx)')
	msgu = upd.message

	if inann(ctx.chat_data, DK_MSGIDS):
		for msgId in ctx.chat_data[DK_MSGIDS]:
			try: ctx.bot.delete_message(msgu.chat_id, msgId)
			except: pass

	ctx.chat_data[DK_MSGIDS] = []

def start(upd, ctx):
	""" Called at the very beginning or by /start. Initializes chat_data vars and asks for a password """
	logger.debug('>> start(upd, ctx)')

	# clearMessages(upd, ctx)

	# Set default mode to Encryption
	ctx.chat_data[DK_MODE] = MODE_ENCRYPT

	# TODO: clear history before (or better check where does this call come from and tell about /clear cmd)

	# Send welcome message
	if upd.message is None: # Came here from callbackquery [Cancel]
		msg = upd.callback_query.message.edit_text(MSGC_INTRO, reply_markup=mup_encryptDecrypt)
	else: # Cmd /start or very beginning of bot
		msg = upd.message.reply_text(MSGC_INTRO, reply_markup=mup_encryptDecrypt)
		upd.message.delete()

	storeMsgId(ctx.chat_data, msg)
	ctx.chat_data[DK_EDITMSG] = msg

	return STATE_RECEIVE_MSG

def modeEncryptOn(upd, ctx):
	"""  """
	query = upd.callback_query
	msgu = query.message

	# Set mode
	ctx.chat_data[DK_MODE] = MODE_ENCRYPT

	# Reply
	msg = msgu.edit_text(MSGC_INTRO_ENCRYPT, reply_markup=mup_cancel)
	storeMsgId(ctx.chat_data, msg)
	ctx.chat_data[DK_EDITMSG] = msg

	return STATE_RECEIVE_MSG


def modeDecryptOn(upd, ctx):
	"""  """
	query = upd.callback_query
	msgu = query.message

	# Set mode
	ctx.chat_data[DK_MODE] = MODE_DECRYPT

	# Reply
	msg = msgu.edit_text(MSGC_INTRO_DECRYPT, reply_markup=mup_cancel)
	storeMsgId(ctx.chat_data, msg)
	ctx.chat_data[DK_EDITMSG] = msg

	return STATE_RECEIVE_MSG


def receiveMsg(upd, ctx):
	""" Receives message that is needed to be encrypted """
	logger.debug('>> receiveMsg(upd, ctx)')
	msgu = upd.message

	# Sanity check, this supposed to never happen
	if ninann(ctx.chat_data, DK_MODE):
		ctx.chat_data[DK_MODE] = MODE_ENCRYPT

	ctx.chat_data[DK_MSG] = msgu.text
	msgu.delete()

	# TODO: do smth with repetitive code (same in receivePassword)
	# Prepare replyFunc, which decides if we create new msg or edit previous
	if inann(ctx.chat_data, DK_EDITMSG): replyFunc = ctx.chat_data[DK_EDITMSG].edit_text
	else: replyFunc = msgu.reply_text

	markup = mup_cancelShow
	if ctx.chat_data[DK_MODE] == MODE_DECRYPT:
		markup = mup_cancel

	try: msg = replyFunc(MSGC_MSGRECEIVED.format(len(msgu.text)), reply_markup=markup)
	except: msg = msgu.reply_text(MSGC_MSGRECEIVED.format(len(msgu.text)), reply_markup=markup)

	storeMsgId(ctx.chat_data, msg)
	ctx.chat_data[DK_EDITMSG] = msg

	return STATE_RECEIVE_PWD


def showMessage(upd, ctx):
	""" Sends to user a separate message with ctx.chat_data[DK_MSG] """
	query = upd.callback_query

	# Sanity check, this supposed to never happen
	if ninann(ctx.chat_data, DK_MSG):
		msg = query.message.reply_text(MSGC_NOMSGFOUND)
		storeMsgId(ctx.chat_data, msg)
		return

	msg = query.message.reply_text(ctx.chat_data[DK_MSG], reply_markup=mup_delete)
	storeMsgId(ctx.chat_data, msg)

def deleteMessage(upd, ctx):
	""" Deletes message from which the callbackQuery had been processed """
	upd.callback_query.message.delete()

def receivePassword(upd, ctx):
	""" Receives password whether for authorization or in password changing procedure """
	logger.debug('>> receivePassword(upd, ctx)')
	msgu = upd.message

	# Sanity check, this supposed to never happen
	if ninann(ctx.chat_data, DK_MSG):
		msg = upd.message.reply_text(MSGC_NOMSGFOUND)
		storeMsgId(ctx.chat_data, msg)
		return

	# TODO: check for only text messages!

	ctx.chat_data[DK_PASSWORD] = get_hash(msgu.text)
	msgu.delete()

	if inann(ctx.chat_data, DK_EDITMSG): replyFunc = ctx.chat_data[DK_EDITMSG].edit_text
	else: replyFunc = msgu.reply_text

	# Function for either encrypt or decrypt
	msgTransformFunc = encrypt_string if ctx.chat_data[DK_MODE] == MODE_ENCRYPT else decrypt_string
	msgBytes = msgTransformFunc(ctx.chat_data[DK_MSG], ctx.chat_data[DK_PASSWORD])

	# Handle case when could not decrypt
	if msgBytes is None:
		try:
			msg = ctx.chat_data[DK_EDITMSG]
			if ctx.chat_data[DK_EDITMSG].text != MSGC_DEC_FAILED:
				msg = replyFunc(MSGC_DEC_FAILED, reply_markup=mup_cancelShow)
		except:
			msg = msgu.reply_text(MSGC_DEC_FAILED, reply_markup=mup_cancelShow)
		storeMsgId(ctx.chat_data, msg)
		ctx.chat_data[DK_EDITMSG] = msg

		return STATE_RECEIVE_PWD
	else:
		# And send result in a separate message
		try: msg = replyFunc(msgBytes, reply_markup=mup_delete)
		except: msg = msgu.reply_text(msgBytes, reply_markup=mup_delete)
		storeMsgId(ctx.chat_data, msg)

		msg = msgu.reply_text(MSGC_INTRO, reply_markup=mup_encryptDecrypt)
		storeMsgId(ctx.chat_data, msg)
		ctx.chat_data[DK_EDITMSG] = msg

	return STATE_RECEIVE_MSG





def error(upd, ctx):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', upd, ctx.error)