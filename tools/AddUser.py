import sqlite3
import hashlib

# Function to hash the password using MD5
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Connect to the SQLite3 database
conn = sqlite3.connect(r'C:\Users\azima\Desktop\PBox\PBox\tools\database_name.db')
cursor = conn.cursor()

# Prompt user for input
username = input("Enter a username: ")
password = input("Enter a password: ")

# Hash the password
hashed_password = hash_password(password)

# Insert into 'users' table
try:
    cursor.execute('''
    INSERT INTO users (username, password) VALUES (?, ?)
    ''', (username, hashed_password))
    conn.commit()
    print("User inserted successfully.")
except Exception as e:
    print("Error inserting user:", e)

# Close the connection
conn.close()
