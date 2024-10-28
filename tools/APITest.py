import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import json
import base64

def load_rsa_public_key(file_path):
    with open(file_path, "rb") as file:
        return RSA.import_key(file.read())

def encrypt_with_rsa(data, public_key):
    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted_data = cipher_rsa.encrypt(data.encode('utf-8'))
    return base64.b64encode(encrypted_data).decode('utf-8')

def add_entry(api_url, api_key, url, email_user, password, two_fa, note, encryption_key, public_key_file):
    headers = {
        'Content-Type': 'application/json',
        'api-key': api_key
    }

    # Prepare data payload, including the AES encryption key
    data = {
        'url': url,
        'email_user': email_user,
        'password': password,
        '2fa': two_fa,
        'note': note,
        'encryption_key': encryption_key  # Include the AES key here
    }

    # Convert data payload to JSON and encrypt with RSA
    json_data = json.dumps(data)
    public_key = load_rsa_public_key(public_key_file)
    encrypted_data = encrypt_with_rsa(json_data, public_key)

    # Prepare final payload
    payload = {
        'encrypted_data': encrypted_data
    }

    # Print the JSON payload for debugging
    print("Sending JSON payload:")
    print(json.dumps(payload, indent=4))

    try:
        # Send POST request to the API
        response = requests.post(f"{api_url}/add_entry", headers=headers, json=payload)
        if response.status_code == 201:
            print("Entry added successfully.")
        else:
            print(f"Failed to add entry. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    api_url = "http://127.0.0.1:1337"
    api_key = "your_API_key"
    public_key_file = "public_key.pem"

    url = "https://example.com"
    email_user = "user@example.com"
    password = "password123"
    two_fa = "No"
    note = "Sample note"
    encryption_key = "azima"

    add_entry(api_url, api_key, url, email_user, password, two_fa, note, encryption_key, public_key_file)
