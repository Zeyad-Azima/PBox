import base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

SALT_SIZE = 16
KEY_SIZE = 32
ITERATIONS = 100000

def derive_key(password, salt):
    return PBKDF2(password, salt, dkLen=KEY_SIZE, count=ITERATIONS)

def encrypt_aes(plain_text, password):
    try:
        salt = get_random_bytes(SALT_SIZE)
        key = derive_key(password.encode(), salt)
        cipher = AES.new(key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(plain_text.encode('utf-8'))
        return base64.b64encode(salt + cipher.nonce + tag + ciphertext).decode('utf-8')
    except Exception as e:
        return None

def decrypt_aes(encrypted_text, password):
    try:
        data = base64.b64decode(encrypted_text)
        salt = data[:SALT_SIZE]
        nonce = data[SALT_SIZE:SALT_SIZE+16]
        tag = data[SALT_SIZE+16:SALT_SIZE+32]
        ciphertext = data[SALT_SIZE+32:]
        key = derive_key(password.encode(), salt)
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
    except Exception as e:
        return None
