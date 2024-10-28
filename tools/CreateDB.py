import sqlite3


db_path = "database_name.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')

# Create a trigger to prevent more than one row in the 'users' table
cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS limit_users_insert
    BEFORE INSERT ON users
    WHEN (SELECT COUNT(*) FROM users) >= 1
    BEGIN
        SELECT RAISE(FAIL, 'Cannot add more than one user');
    END;
''')

# Create a trigger to prevent updates to the 'users' table when it has one row
cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS prevent_users_update
    BEFORE UPDATE ON users
    WHEN (SELECT COUNT(*) FROM users) = 1
    BEGIN
        SELECT RAISE(FAIL, 'Cannot modify the users table when it has one user');
    END;
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        name TEXT NOT NULL,
        url TEXT UNIQUE NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS manager (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        username_email TEXT NOT NULL,
        password TEXT NOT NULL,
        two_factor_auth TEXT,
        note TEXT,
        group_name TEXT,
        FOREIGN KEY (group_name) REFERENCES groups(name)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS API (
        api_key TEXT NOT NULL,
        rsa_public_key TEXT
    )
''')

conn.commit()
conn.close()

print("Database and tables created successfully at", db_path)
