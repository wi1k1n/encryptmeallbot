# States for ConversationHangler
STATE_RECEIVE_MSG, \
STATE_RECEIVE_PWD, \
STATE_CONFIRM_PWD = range(3)

# Chat_data keys
DK_MSGIDS = 'msg_ids'
DK_SETPWD = 'set_pwd'
DK_MODE = 'mode'
DK_PASSWORD = 'password'
DK_EDITMSG = 'edit_msg'

# Mode values
MODE_ENCODE, \
MODE_DECODE = range(2)

# Reply messages
MSGC_INTRO_LOFF = "Hi! I can encrypt/decrypt your messages!\nPlease, send me password to protect your data"
MSGC_INTRO_LIN = "Hi! I can encrypt/decrypt your messages!"
MSGC_SETPWD_NEW = "Please send me new password"
MSGC_SETPWD_REPEAT = "Please repeat your password"
MSGC_SETPWD_MISMATCH = "Entered passwords do not match. Enter new password"
MSGC_SETPWD_SUCCESS = "New password created successfully! You can now send me message for encryption.\n" \
					  "Remember: your message will be immediately deleted I've receive it!"