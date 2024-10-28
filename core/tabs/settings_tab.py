from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QInputDialog, QMessageBox
from core.database.database import get_manager_data, connect_db, add_api_key, get_api_key
from core.encryption.encryption import encrypt_aes, decrypt_aes
import os

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setup_ui()
        self.setLayout(self.layout)

    def setup_ui(self):
        # New encryption password input
        new_key_label = QLabel("New Encryption Password:")
        self.new_key_input = QLineEdit()
        self.new_key_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(new_key_label)
        self.layout.addWidget(self.new_key_input)

        # Change encryption button
        change_button = QPushButton("Change")
        change_button.clicked.connect(self.change_encryption_key)
        self.layout.addWidget(change_button)

        # API Key input and buttons
        api_key_label = QLabel("API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setReadOnly(True)
        self.layout.addWidget(api_key_label)
        self.layout.addWidget(self.api_key_input)

        # Generate or Regenerate button
        self.api_button = QPushButton("Generate")
        self.api_button.clicked.connect(self.generate_or_regenerate_api_key)
        self.layout.addWidget(self.api_button)

        # Load existing API key if available
        self.load_existing_api_key()

    def load_existing_api_key(self):
        api_key = get_api_key()
        if api_key:
            self.api_key_input.setText(api_key)
            self.api_button.setText("Regenerate")

    def generate_or_regenerate_api_key(self):
        new_api_key = self.generate_random_key()
        if new_api_key:
            add_api_key(new_api_key)  # Update the database
            self.api_key_input.setText(new_api_key)
            self.api_button.setText("Regenerate")
            QMessageBox.information(self, "Success", "API Key generated successfully.")

    def generate_random_key(self, length=32):
        return os.urandom(length).hex()

    def change_encryption_key(self):
        new_key = self.new_key_input.text()

        if not new_key:
            QMessageBox.warning(self, "Error", "Please enter a new encryption password.")
            return

        # Ask for the old encryption key
        old_key, ok = QInputDialog.getText(self, "Old Encryption Key", "Enter the old encryption key:", QLineEdit.Password)
        if not ok or not old_key:
            return

        # Fetch all entries from the database
        entries = get_manager_data()
        if not entries:
            QMessageBox.warning(self, "Error", "No data available to re-encrypt.")
            return

        success = True
        conn = connect_db()
        cursor = conn.cursor()

        for url, encrypted_user, encrypted_pass, two_fa, encrypted_note in entries:
            # Decrypt current data with the old key
            decrypted_user = decrypt_aes(encrypted_user, old_key)
            decrypted_pass = decrypt_aes(encrypted_pass, old_key)
            decrypted_note = decrypt_aes(encrypted_note, old_key) if encrypted_note else None

            if not decrypted_user or not decrypted_pass:
                QMessageBox.warning(self, "Decryption Failed", "Incorrect old key or corrupted data.")
                success = False
                break

            # Re-encrypt data with the new key
            new_encrypted_user = encrypt_aes(decrypted_user, new_key)
            new_encrypted_pass = encrypt_aes(decrypted_pass, new_key)
            new_encrypted_note = encrypt_aes(decrypted_note, new_key) if decrypted_note else None

            # Update the database with new encrypted data
            try:
                cursor.execute('''
                    UPDATE manager
                    SET username_email=?, password=?, note=?
                    WHERE url=?
                ''', (new_encrypted_user, new_encrypted_pass, new_encrypted_note, url))
                conn.commit()
            except Exception as e:
                success = False
                break

        conn.close()

        if success:
            QMessageBox.information(self, "Success", "Encryption password changed successfully.")
            self.new_key_input.clear()
        else:
            QMessageBox.warning(self, "Error", "Failed to change the encryption password.")
