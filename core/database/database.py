import sqlite3

DB_PATH = r'C:\Users\user\Desktop\PBox\PBox\tools\database_name.db'



def connect_db():
    return sqlite3.connect(DB_PATH)


def add_api_key(api_key, rsa_public_key=None):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM API')  # Clear old key
        cursor.execute('INSERT INTO API (api_key, rsa_public_key) VALUES (?, ?)', (api_key, rsa_public_key))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error:
        return False


def get_api_key():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT api_key FROM API')
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def add_manager_entry(url, username_email, password, two_fa, note):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO manager (url, username_email, password, two_factor_auth, note)
            VALUES (?, ?, ?, ?, ?)
        ''', (url, username_email, password, two_fa, note))
        conn.commit()

        # Get the ID of the newly inserted row
        entry_id = cursor.lastrowid
        conn.close()
        return entry_id
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def get_manager_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, url, username_email, password, two_factor_auth, note FROM manager')
    results = cursor.fetchall()
    conn.close()
    return results