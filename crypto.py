import re, base64, hashlib, os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

from api_token import SALT

# Tests given password for strength
def is_password_weak(pwd):
	return not re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', pwd)

# Calculates hash of password
def get_hash(pwd):
	password = pwd.encode()  # Convert to type bytes
	kdf = PBKDF2HMAC(
		algorithm=hashes.SHA256(),
		length=32,
		salt=SALT,
		iterations=100000,
		backend=default_backend()
	)
	key = base64.urlsafe_b64encode(kdf.derive(password))  # Can only use kdf once
	return key

def encrypt_string(data, key):
	f = Fernet(key)
	return f.encrypt(data.encode()).decode()

def decrypt_string(data, key):
	f = Fernet(key)
	return f.decrypt(data.encode()).decode()