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

def clearMessages(upd, ctx):
	""" Clears all messages which ids are stored in ctx.chat_data[MSGIDS] """
	logger.debug('>> clearMessages(upd, ctx)')
	msgu = upd.message

	if inann(ctx.chat_data, DK_MSGIDS):
		for msgId in ctx.chat_data[DK_MSGIDS]:
			try: ctx.bot.delete_message(msgu.chat_id, msgId)
			except: pass

	ctx.chat_data[DK_MSGIDS] = []
	# TODO: decide here about intro depending on ctx.chat_data[DK_MODE]
	msg = msgu.reply_text(MSGC_INTRO_LOGGEDIN)
	ctx.chat_data[DK_EDITMSG] = msg
	return STATE_RECEIVE_MSG

def getReplyFunc(upd, ctx):
	""" Returns either reply_text or edit_text functions to be 1-line-used for reply in handlers
		and updates ctx.chat_data[DK_EDITMSG] """
	msgc = upd.message
	replyFunc = msgc.reply_text # Contains either .reply_text or .edit_text functions that r used later to reply
	if inann(ctx.chat_data, DK_EDITMSG):
		msgc = ctx.chat_data[DK_EDITMSG]
		replyFunc = msgc.edit_text

	# Function to be returned. The only purpose of such a system to implicitly update ctx.chat_data[DK_EDITMSG]
	# whenever sending a reply
	def retReplyFunction(*args, **kwargs):
		# Parsing text-field from the given arguments
		txt = None
		if len(args) > 0: txt = args[0]
		elif 'text' in kwargs: txt = kwargs['text']
		else: logger.debug('No text passed into replyFunc function!!')

		# If text is different: edit, otherwise just return message itself
		msg = msgc
		if txt != msgc.text:
			msg = replyFunc(*args, **kwargs)

		ctx.chat_data[DK_EDITMSG] = msg
		return msg

	return retReplyFunction

def everySignal(upd, ctx):
	""" Checks and actions needed to be performed on each atomic signal received from user """
	logger.debug('>> every_signal_checks(upd, ctx)')
	msgu = upd.message

	# Leave all groups/channels and stay only in private chats
	if not msgu.chat.type == msgu.chat.PRIVATE:
		logger.warning("Added to group #{0}! Leaving...".format(upd.message.chat_id))
		msgu.bot.leave_chat(msgu.chat_id)

	# Collect all message-ids in context in order to remove everything on logout
	storeMsgId(ctx.chat_data, msgu)




def helpMsg(upd, ctx):
	""" Generates `string` out of helpDict dictionary object """
	# (reason is that helpDict is also used to construct list of MessageHandlers in main.py)
	msg = '`'
	maxCmdLen = len(max(helpDict, key=lambda x: x))
	for key in sorted(helpDict):
		val = helpDict[key]
		msg += '  /{0}{1} - {2}\n'.format(key, ' ' * (maxCmdLen - len(key)), val[1])
	upd.message.reply_text(msg + '`', parse_mode=ParseMode.MARKDOWN)

def start(upd, ctx):
	""" Called at the very beginning or by /start. Initializes chat_data vars and asks for a password """
	logger.debug('>> start(upd, ctx)')
	msgu = upd.message

	# TODO: DB without need to ask new password every time the bot is reloaded
	# TODO: option to generate password

	# Initialize context.chat_data variables
	ctx.chat_data[DK_SETPWD] = True  # First thing is to create password
	ctx.chat_data[DK_MODE] = MODE_ENCODE  # Initial bot-mode is for 'encoding' messages
	if ninann(ctx.chat_data, DK_MSGIDS): # List for all received&sent messages
		ctx.chat_data[DK_MSGIDS] = []

	# TODO: clear history before (or better check where does this call come from and tell about /clear cmd)
	# Send welcome message
	msg = msgu.reply_text(MSGC_INTRO_LOGGEDOFF)
	ctx.chat_data[DK_EDITMSG] = msg
	storeMsgId(ctx.chat_data, msg)

	msgu.delete()

	return STATE_RECEIVE_PWD

def setPassword(upd, ctx):
	""" Called by /password. Initiates password changing procedure """
	logger.debug('>> setPassword(upd, ctx)')
	msgu = upd.message

	ctx.chat_data[DK_SETPWD] = True

	msg = msgu.reply_text(MSGC_SETPWD_NEW)
	storeMsgId(ctx.chat_data, msg)

	return STATE_RECEIVE_PWD

def receivePassword(upd, ctx):
	""" Receives password whether for authorization or in password changing procedure """
	logger.debug('>> receivePassword(upd, ctx)')
	msgu = upd.message

	# This is needed bcuz we don't know if the message still exist (or user has already deleted it) (-1-)
	replyFunc = getReplyFunc(upd, ctx)  # Contains either .reply_text or .edit_text functions that r used later to reply

	# TODO: check for only text messages!
	# TODO: add cancel option (if user doesnt want change pwd anymore)

	# If password is to be changed
	if inann(ctx.chat_data, DK_SETPWD) and ctx.chat_data[DK_SETPWD] == True:
		# TODO: check for weakness!

		hash = get_hash(msgu.text)
		msgu.delete()
		ctx.chat_data[DK_PASSWORD] = hash

		# Explained in (-1-), repeats along all handlers
		msg = replyFunc(MSGC_SETPWD_REPEAT, reply_markup=mup_pwdConfirm)
		storeMsgId(ctx.chat_data, msg)

		return STATE_CONFIRM_PWD

	return STATE_RECEIVE_MSG

def cancelRepeatPassword(upd, ctx):
	logger.debug('>> cancelRepeatPassword(upd, ctx)')
	query = upd.callback_query
	msgu = query.message

	query.edit_message_text(text="{0}\n(Callback queries are not supported yet)".format(msgu.text))

def confirmPassword(upd, ctx):
	""" Received password confirmation in password change procedure """
	logger.debug('>> confirmPassword(upd, ctx)')
	msgu = upd.message

	replyFunc = getReplyFunc(upd, ctx)

	# Sanity check for being in password change procedure
	if inann(ctx.chat_data, DK_SETPWD) and ctx.chat_data[DK_SETPWD] == True:
		hash = get_hash(msgu.text)
		msgu.delete()

		# If passwords mismatch
		if ctx.chat_data[DK_PASSWORD] != hash:
			# TODO: distinguish here if the new password procedure has been initiated by user or is mandatory due to /start

			# msg = replyFunc(MSGC_SETPWD_MISMATCH, reply_markup=mup_pwdConfirm)
			msg = replyFunc(MSGC_SETPWD_MISMATCH)
			storeMsgId(ctx.chat_data, msg)

			return STATE_RECEIVE_PWD
		# Password successfully created
		else:
			ctx.chat_data[DK_MODE] = MODE_ENCODE

			# TODO: change text depending on current ctx.chat_data[DK_MODE]

			msg = replyFunc(MSGC_SETPWD_SUCCESS)
			storeMsgId(ctx.chat_data, msg)

			return STATE_RECEIVE_MSG

	return STATE_RECEIVE_MSG

def receiveMsg(upd, ctx):
	""" Receives message that is needed to be encrypted """
	logger.debug('>> receiveMsg(upd, ctx)')
	msgu = upd.message

	replyFunc = getReplyFunc(upd, ctx)

	# Sanity check for ctx.chat_data[DK_MODE] existance
	if ninann(ctx.chat_data, DK_MODE):
		ctx.chat_data[DK_MODE] = MODE_ENCODE
		logger.warning('Key "mode" was not found in ctx.chat_data. Reinitialized with mode=="encode"')

	# Function for either encrypt or decrypt
	msgTransformFunc = encrypt_string if ctx.chat_data[DK_MODE] == MODE_ENCODE else decrypt_string

	msgBytes = msgTransformFunc(msgu.text, ctx.chat_data[DK_PASSWORD])
	msgu.delete()

	# Handle case when could not decrypt
	if msgBytes is None:
		msg = replyFunc(MSGC_DEC_FAILED)
		storeMsgId(ctx.chat_data, msg)
	else:
		# Reply first with micro-intro message
		msg = replyFunc(MSGC_ENC_INTRO if ctx.chat_data[DK_MODE] == MODE_ENCODE else MSGC_DEC_INTRO)
		storeMsgId(ctx.chat_data, msg)
		# And send result in a separate message
		msg = msgu.reply_text(msgBytes)
		storeMsgId(ctx.chat_data, msg)

		# Start new communication batch
		ctx.chat_data[DK_EDITMSG] = None

	return STATE_RECEIVE_MSG

def encodeMode(upd, ctx):
	logger.debug('>> encodeMode(upd, ctx)')
	msgu = upd.message

	replyFunc = getReplyFunc(upd, ctx)
	msgu.delete()

	ctx.chat_data[DK_MODE] = MODE_ENCODE

	msg = replyFunc('Encode mode on. Send me message to encrypt')
	storeMsgId(ctx.chat_data, msg)

	return STATE_RECEIVE_MSG

def decodeMode(upd, ctx):
	msgu = upd.message
	logger.debug('>> decodeMode(upd, ctx)')

	replyFunc = getReplyFunc(upd, ctx)
	msgu.delete()

	ctx.chat_data[DK_MODE] = MODE_DECODE

	msg = replyFunc('Decode mode on. Send me message to decrypt')
	storeMsgId(ctx.chat_data, msg)

	return STATE_RECEIVE_MSG

def logOut(upd, ctx):
	msgu = upd.message
	logger.debug('>> logOut(upd, ctx)')

	msg = msgu.reply_text('/logOut command is not implemented yet')
	storeMsgId(ctx.chat_data, msg)

def logIn(upd, ctx):
	msgu = upd.message
	logger.debug('>> logIn(upd, ctx)')

	msg = msgu.reply_text('/login command is not implemented yet')
	storeMsgId(ctx.chat_data, msg)



helpDict = {
	'password': (setPassword, 'change password'),
	'encode': (encodeMode, 'turn on encode mode'),
	'decode': (decodeMode, 'turn on decode mode'),
	'help': (helpMsg, 'show this message'),
	'clear': (clearMessages, 'clears all messages from history'),
	'login': (logIn, 'logs in with a password'),
	'logout': (logOut, 'logs out'),
}

def error(upd, ctx):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', upd, ctx.error)