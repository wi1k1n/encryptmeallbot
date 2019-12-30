from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from constants import *

def createKeyboard(items):
	""" Takes list of tuples (label, data) (or list of lists of tuples) and returns InlineKeyboardMarkup"""
	ret = [0] * len(items)
	for i, it in enumerate(items):
		if type(it) == tuple:
			ret[i] = [InlineKeyboardButton(it[0], callback_data=it[1])]
			continue
		ret[i] = [0] * len(it)
		for j, it2 in enumerate(it):
			ret[i][j] = InlineKeyboardButton(it2[0], callback_data=it2[1])
	return InlineKeyboardMarkup(ret)

# MarkUp keyboards for different replies
mup_encryptDecrypt = createKeyboard([[('Encrypt', str(CBQ_ENCRYPT)), ('Decrypt', str(CBQ_DECRYPT))]])
mup_cancel = createKeyboard([('Cancel', CBQ_CANCEL)])
mup_delete = createKeyboard([('Delete', CBQ_DELETE)])
mup_cancelShow = createKeyboard([[('Cancel', CBQ_CANCEL), ('Show message', CBQ_SHOWMSG)]])
mup_finish = createKeyboard([('Close & delete', CBQ_FINISH)])