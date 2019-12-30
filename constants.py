# States for ConversationHangler
STATE_RECEIVE_MSG, \
STATE_RECEIVE_PWD = range(2)

# Chat_data keys
DK_MODE = 'mode'
DK_MSG = 'message'
DK_EDITMSG = 'edit_msg'

DK_MSGIDS = 'msg_ids'
DK_SETPWD = 'set_pwd'
DK_PASSWORD = 'password'

# Mode values
MODE_ENCRYPT, \
MODE_DECRYPT = range(2)

# Data return by CallbackQueryHandlers
CBQ_ENCRYPT, \
CBQ_DECRYPT, \
CBQ_CANCEL, \
CBQ_SHOWMSG, \
CBQ_FINISH, \
CBQ_DELETE = range(6)

# Reply messages
MSGC_INTRO = "Hi! I can encrypt/decrypt your messages! Please choose, what you want"
MSGC_INTRO_ENCRYPT = "Please send me message to encrypt"
MSGC_INTRO_DECRYPT = "Please send me message to decrypt"

MSGC_MSGRECEIVED = "You've sent message of length {0}. Please, send me password now."
MSGC_PWDRECEIVED = "Your message of length {0} is encrypted with password of length {1}."

MSGC_DEC_FAILED = "Could not decrypt your message. Are you sure the password's correct? " \
				  "Have you copied the whole thing?\n\nTry another password"
MSGC_NOMSGFOUND = "Could not find your message due to internal error. This incident is reported!"



MSGC_SETPWD_NEW = "Please send me new password"
MSGC_SETPWD_REPEAT = "Please repeat your password"
MSGC_SETPWD_MISMATCH = "Entered passwords do not match. Enter new password"
MSGC_SETPWD_SUCCESS = "New password created successfully! You can now send me message for encryption.\n" \
					  "Remember: your message will be immediately deleted once I receive it!"
MSGC_ENC_INTRO = "Here is your encrypted message:"
MSGC_DEC_INTRO = "Here is your decrypted message:"