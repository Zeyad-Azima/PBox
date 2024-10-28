from flask import Flask, request, jsonify
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from base64 import b64decode, b64encode
from core.database.database import add_manager_entry, get_api_key
import json
import os
app = Flask(__name__)

# Constants for AES encryption
SALT_SIZE = 16
KEY_SIZE = 32
ITERATIONS = 100000

def load_rsa_private_key(file_path):
    with open(file_path, "rb") as file:
        return RSA.import_key(file.read())

current_dir = os.path.dirname(os.path.abspath(__file__))
private_key_path = r"C:\Users\user\Desktop\PBox\PBox\core\api\private_key.pem"

private_key = load_rsa_private_key(private_key_path)

def derive_key(password, salt):
    return PBKDF2(password, salt, dkLen=KEY_SIZE, count=ITERATIONS)

def decrypt_with_rsa(encrypted_data, private_key):
    try:
        encrypted_bytes = b64decode(encrypted_data)
        cipher_rsa = PKCS1_OAEP.new(private_key)
        decrypted_data = cipher_rsa.decrypt(encrypted_bytes)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        print(f"RSA decryption failed: {e}")
        return None

def encrypt_aes(plain_text, password):
    if plain_text is None or password is None:
        print("AES encryption failed: one of the inputs is None")
        return None

    try:
        # Generate a random salt
        salt = get_random_bytes(SALT_SIZE)

        # Derive the AES key from the password and salt
        key = derive_key(password.encode(), salt)

        # Initialize AES cipher in EAX mode
        cipher = AES.new(key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(pad(plain_text.encode(), AES.block_size))

        # Concatenate salt, nonce, tag, and ciphertext, then base64 encode
        encrypted_data = b64encode(salt + cipher.nonce + tag + ciphertext).decode('utf-8')
        return encrypted_data
    except Exception as e:
        print(f"AES encryption failed: {e}")
        return None

def validate_api_key():
    api_key = request.headers.get('api-key')
    stored_api_key = get_api_key()
    if not api_key or api_key != stored_api_key:
        return False
    return True

@app.route('/add_entry', methods=['POST'])
def add_entry_api():
    if not validate_api_key():
        return jsonify({'error': 'Invalid or missing API key'}), 403

    payload = request.json
    if not payload:
        return jsonify({'error': 'Missing or invalid request body'}), 400

    encrypted_data = payload.get('encrypted_data')

    # Decrypt the RSA-encrypted data payload
    decrypted_data = decrypt_with_rsa(encrypted_data, private_key)
    if not decrypted_data:
        return jsonify({'error': 'Failed to decrypt RSA data'}), 400

    # Parse the decrypted JSON data
    try:
        data = json.loads(decrypted_data)
        url = data.get('url')
        email_user = data.get('email_user')
        password = data.get('password')
        two_fa = data.get('2fa')
        note = data.get('note')
        encryption_key = data.get('encryption_key')

        if not all([url, email_user, password, encryption_key]):
            print(f"Missing required field(s). Data received: {data}")
            return jsonify({'error': 'Missing required field(s)'}), 400

    except Exception as e:
        print(f"Error parsing decrypted data: {e}")
        return jsonify({'error': 'Failed to parse decrypted data'}), 400

    # Encrypt specified fields with the derived AES key
    encrypted_user = encrypt_aes(email_user, encryption_key)
    encrypted_pass = encrypt_aes(password, encryption_key)
    encrypted_note = encrypt_aes(note, encryption_key)

    if not all([encrypted_user, encrypted_pass]):
        return jsonify({'error': 'Encryption failed'}), 400

    # Insert into the database
    entry_id = add_manager_entry(url, encrypted_user, encrypted_pass, two_fa, encrypted_note)
    if entry_id:
        return jsonify({'message': 'Entry added successfully', 'id': entry_id}), 201
    else:
        return jsonify({'error': 'Database operation failed'}), 500

def run_flask_app():
    app.run(host='127.0.0.1', port=1337)
