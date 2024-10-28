from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from core.utils.utils import hash_password
from core.database.database import connect_db
from core.ui.main_window import MainWindow
import sqlite3
from core.ui.styles import DARK_STYLE

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PBox Login")
        self.setWindowIcon(QIcon(r"C:\Users\azima\Desktop\PBox\PBox\logo.png"))
        self.setGeometry(100, 100, 300, 200)

        self.setStyleSheet(DARK_STYLE)

        layout = QVBoxLayout()

        # Username input
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)

        # Password input
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)

        # Login button
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return

        hashed_password = hash_password(password)

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Debug: Check tables in the database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Tables in the database: {tables}")

            cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, hashed_password))
            result = cursor.fetchone()
            conn.close()

            if result:
                self.open_main_window()
            else:
                QMessageBox.warning(self, "Error", "Invalid username or password.")

        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            QMessageBox.critical(self, "Error", "Database error: Check if the 'users' table exists.")

    def open_main_window(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()
