import logging

from constants import *
from crypto import *
from keyboards import *
from util import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def storeMsgId(chd, msg):
	""" Takes chat_data dict and adds message_id for being able to delete all messages later on """
	if ninann(chd, MSGIDS):
		chd[MSGIDS] = []
	chd[MSGIDS].append(msg.message_id)

def clearMessages(upd, ctx):
	""" Clears all messages which ids are stored in ctx.chat_data[MSGIDS] """
	logger.debug('>> clearMessages(upd, ctx)')
	msg = upd.message

	if inann(ctx.chat_data, MSGIDS):
		for msgId in ctx.chat_data[MSGIDS]:
			try: ctx.bot.delete_message(msg.chat_id, msgId)
			except: pass

	ctx.chat_data[MSGIDS] = []


# Checks and actions needed to be performed on each atomic signal received from user
def everySignal(upd, ctx):
	msg = upd.message

	logger.debug('>> every_signal_checks(upd, ctx)')

	# Leave all groups/channels and stay only in private chats
	if not msg.chat.type == msg.chat.PRIVATE:
		logger.warning("Added to group #{0}! Leaving...".format(upd.message.chat_id))
		msg.bot.leave_chat(msg.chat_id)

	# Collect all message-ids in context in order to remove everything on logout
	storeMsgId(ctx.chat_data, msg)

def start(upd, ctx):
	msg = upd.message

	logger.debug('>> start(upd, ctx)')

	# TODO: DB without need to ask new password every time the bot is reloaded
	# TODO: option to generate password

	ctx.chat_data[SETPWD] = True
	ctx.chat_data[MODE] = MODE_ENCODE
	if ninann(ctx.chat_data, MSGIDS): ctx.chat_data[MSGIDS] = []

	msg = msg.reply_text('Hi. I can encrypt messages.\n But first create a password.')
	storeMsgId(ctx.chat_data, msg)

	return STATE_RECEIVE_PWD

def setPassword(upd, ctx):
	msg = upd.message

	logger.debug('>> setPassword(upd, ctx)')

	ctx.chat_data[SETPWD] = True

	msg = msg.reply_text('Please send me new password')
	storeMsgId(ctx.chat_data, msg)

	return STATE_RECEIVE_PWD

def receivePassword(upd, ctx):
	msg = upd.message

	logger.debug('>> receivePassword(upd, ctx)')

	# TODO: check for only text messages!
	# TODO: add cancel option (if user doesnt want change pwd anymore)
	if inann(ctx.chat_data, SETPWD) and ctx.chat_data[SETPWD] == True:
		# TODO: check for weakness!
		hash = get_hash(msg.text)
		msg.delete()
		ctx.chat_data[PASSWORD] = hash

		msg = msg.reply_text('Please repeat your password', reply_markup=mup_pwdConfirm)
		storeMsgId(ctx.chat_data, msg)

		return STATE_CONFIRM_PWD

def cancelRepeatPassword(upd, ctx):
	msg = upd.message

	query = upd.callback_query

	query.edit_message_text(text="Selected option: {}".format(query.data))

def confirmPassword(upd, ctx):
	msg = upd.message

	logger.debug('>> confirmPassword(upd, ctx)')

	if inann(ctx.chat_data, SETPWD) and ctx.chat_data[SETPWD] == True:
		hash = get_hash(msg.text)
		msg.delete()
		if ctx.chat_data[PASSWORD] != hash:
			msg = msg.reply_text('Entered passwords do not match. Enter new password')
			storeMsgId(ctx.chat_data, msg)

			return STATE_RECEIVE_PWD
		else:
			ctx.chat_data[MODE] = MODE_ENCODE
			msg = msg.reply_text('New password created successfully! You can now send me message for encryption')
			storeMsgId(ctx.chat_data, msg)

			return STATE_RECEIVE_MSG

def receiveMsg(upd, ctx):
	msg = upd.message

	logger.debug('>> receiveMsg(upd, ctx)')

	if ninann(ctx.chat_data, MODE):
		ctx.chat_data[MODE] = MODE_ENCODE
		logger.warning('Key "mode" was not found in ctx.chat_data. Initialized with mode=="encode"')

	foo = encrypt_string if ctx.chat_data[MODE] == MODE_ENCODE else decrypt_string

	msgBytes = foo(msg.text, ctx.chat_data[PASSWORD])
	msg.delete()

	msg = msg.reply_text(msgBytes)
	storeMsgId(ctx.chat_data, msg)

	return STATE_RECEIVE_MSG

def encodeMode(upd, ctx):
	msg = upd.message

	logger.debug('>> encodeMode(upd, ctx)')

	ctx.chat_data[MODE] = MODE_ENCODE

	msg = msg.reply_text('Encode mode on. Send me message to encrypt')
	storeMsgId(ctx.chat_data, msg)

	return STATE_RECEIVE_MSG

def decodeMode(upd, ctx):
	msg = upd.message

	logger.debug('>> decodeMode(upd, ctx)')

	ctx.chat_data[MODE] = MODE_DECODE

	msg = msg.reply_text('Decode mode on. Send me message to decrypt')
	storeMsgId(ctx.chat_data, msg)

	return STATE_RECEIVE_MSG

def error(upd, ctx):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', upd, ctx.error)