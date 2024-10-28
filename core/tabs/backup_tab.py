from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QInputDialog, QFileDialog
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from core.database.database import DB_PATH
import os

# Constants for AES encryption
SALT_SIZE = 16
KEY_SIZE = 32
ITERATIONS = 100000

class BackupTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setup_ui()
        self.setLayout(self.layout)

        # Initialize variables
        self.creds = None
        self.drive_service = None

    def setup_ui(self):
        # Instructions label
        self.login_label = QLabel("Click 'Backup Database' to use Google Drive API or create a local backup")
        self.layout.addWidget(self.login_label)

        # Password input for encryption/decryption
        self.password_label = QLabel("Enter Password for Backup:")
        self.layout.addWidget(self.password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input)

        # Google Drive Backup button
        self.drive_backup_button = QPushButton("Backup to Google Drive")
        self.drive_backup_button.clicked.connect(self.handle_drive_backup)
        self.layout.addWidget(self.drive_backup_button)

        # Local Backup button
        self.local_backup_button = QPushButton("Backup to Local")
        self.local_backup_button.clicked.connect(self.handle_local_backup)
        self.layout.addWidget(self.local_backup_button)

        # Restore from Google Drive button
        self.restore_drive_button = QPushButton("Restore from Google Drive")
        self.restore_drive_button.clicked.connect(self.handle_restore_drive)
        self.layout.addWidget(self.restore_drive_button)

        # Restore from Local button
        self.restore_local_button = QPushButton("Restore from Local")
        self.restore_local_button.clicked.connect(self.handle_restore_local)
        self.layout.addWidget(self.restore_local_button)

    def derive_key(self, password, salt):
        return PBKDF2(password.encode(), salt, dkLen=KEY_SIZE, count=ITERATIONS)

    def encrypt_file(self, file_path, password):
        try:
            with open(file_path, 'rb') as f:
                plaintext = f.read()

            salt = get_random_bytes(SALT_SIZE)
            key = self.derive_key(password, salt)

            cipher = AES.new(key, AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(plaintext)

            encrypted_data = salt + cipher.nonce + tag + ciphertext
            encrypted_file_path = file_path + ".enc"
            with open(encrypted_file_path, 'wb') as f:
                f.write(encrypted_data)

            return encrypted_file_path
        except Exception as e:
            QMessageBox.warning(self, "Error", f"File encryption failed: {e}")
            return None

    def decrypt_file(self, encrypted_file_path, password):
        try:
            save_path = QFileDialog.getSaveFileName(self, "Save Decrypted Database", os.path.basename(encrypted_file_path).replace(".enc", ""), "All Files (*)")[0]

            if not save_path:
                QMessageBox.warning(self, "Error", "No save location selected.")
                return None

            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()

            salt = encrypted_data[:SALT_SIZE]
            nonce = encrypted_data[SALT_SIZE:SALT_SIZE+16]
            tag = encrypted_data[SALT_SIZE+16:SALT_SIZE+32]
            ciphertext = encrypted_data[SALT_SIZE+32:]

            key = self.derive_key(password, salt)
            cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)

            with open(save_path, 'wb') as f:
                f.write(plaintext)

            return save_path
        except Exception as e:
            QMessageBox.warning(self, "Error", f"File decryption failed: {e}")
            return None

    def authenticate_with_google(self):
        oauth_file = QFileDialog.getOpenFileName(self, "Select OAuth Credentials JSON", "", "JSON Files (*.json);;All Files (*)")[0]
        if not oauth_file:
            QMessageBox.warning(self, "Error", "OAuth credentials JSON file is required.")
            return False

        try:
            SCOPES = ['https://www.googleapis.com/auth/drive.file']
            flow = InstalledAppFlow.from_client_secrets_file(oauth_file, SCOPES)
            self.creds = flow.run_local_server(port=0)

            self.drive_service = build('drive', 'v3', credentials=self.creds)
            return True
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Google OAuth failed: {e}")
            return False

    def upload_to_google_drive(self, file_path):
        try:
            if not self.drive_service:
                if not self.authenticate_with_google():
                    return

            file_metadata = {'name': os.path.basename(file_path)}
            media = MediaFileUpload(file_path, mimetype='application/octet-stream')

            file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            file_url = f"https://drive.google.com/file/d/{file.get('id')}/view?usp=sharing"
            QMessageBox.information(self, "Success", f"File uploaded to Google Drive: {file_url}")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Google Drive upload failed: {e}")

    def handle_drive_backup(self):
        if not self.authenticate_with_google():
            return
        self.backup_database()

    def handle_local_backup(self):
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, "Error", "Please enter a backup password.")
            return

        confirm_password, ok = QInputDialog.getText(self, "Confirm Backup Password", "Re-enter Backup Password:", QLineEdit.Password)
        if not ok or confirm_password != password:
            QMessageBox.warning(self, "Error", "Passwords do not match. Please try again.")
            return

        if not os.path.exists(DB_PATH):
            QMessageBox.warning(self, "Error", "Database file not found.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Save Encrypted Backup", "password_manager.db.enc", "Encrypted Files (*.enc)")
        if not save_path:
            QMessageBox.warning(self, "Error", "No save location selected.")
            return

        encrypted_file_path = self.encrypt_file(DB_PATH, password)
        if encrypted_file_path:
            os.rename(encrypted_file_path, save_path)
            QMessageBox.information(self, "Success", f"Backup saved at {save_path}")

    def handle_restore_drive(self):
        if not self.authenticate_with_google():
            return
        self.restore_database()

    def handle_restore_local(self):
        encrypted_file_path, _ = QFileDialog.getOpenFileName(self, "Select Encrypted Backup File", "", "Encrypted Files (*.enc)")
        if not encrypted_file_path:
            QMessageBox.warning(self, "Error", "No file selected.")
            return

        password, ok = QInputDialog.getText(self, "Decryption Password", "Enter password to decrypt the backup:", QLineEdit.Password)
        if not ok or not password:
            return

        decrypted_file_path = self.decrypt_file(encrypted_file_path, password)
        if decrypted_file_path:
            QMessageBox.information(self, "Restore", f"Database restored successfully at {decrypted_file_path}.")
        else:
            QMessageBox.warning(self, "Error", "Failed to restore the database. Check the password.")

    def restore_database(self):
        files = self.list_files_in_drive()
        if not files:
            QMessageBox.warning(self, "Error", "No files found in Google Drive.")
            return

        file_names = [file.get('name') for file in files]
        file_choice, ok = QInputDialog.getItem(self, "Select Backup File", "Choose a file to restore:", file_names, 0, False)

        if not ok or not file_choice:
            return

        selected_file_id = next((file['id'] for file in files if file['name'] == file_choice), None)
        if not selected_file_id:
            QMessageBox.warning(self, "Error", "Failed to identify the selected file.")
            return

        encrypted_file_path = self.download_file_from_drive(selected_file_id, file_choice)
        if not encrypted_file_path:
            return

        password, ok = QInputDialog.getText(self, "Decryption Password", "Enter password to decrypt the backup:", QLineEdit.Password)
        if not ok or not password:
            return

        decrypted_file_path = self.decrypt_file(encrypted_file_path, password)
        if decrypted_file_path:
            QMessageBox.information(self, "Restore", f"Database restored successfully at {decrypted_file_path}.")
        else:
            QMessageBox.warning(self, "Error", "Failed to restore the database. Check the password.")

    def list_files_in_drive(self):
        if not self.drive_service:
            if not self.authenticate_with_google():
                return []

        try:
            results = self.drive_service.files().list(pageSize=10, fields="files(id, name)").execute()
            files = results.get('files', [])
            return files
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to list files: {e}")
            return []

    def download_file_from_drive(self, file_id, file_name):
        if not self.drive_service:
            if not self.authenticate_with_google():
                return None

        try:
            request = self.drive_service.files().get_media(fileId=file_id)
            download_path, _ = QFileDialog.getSaveFileName(self, "Save Encrypted File", file_name, "Encrypted Files (*.enc)")

            if not download_path:
                QMessageBox.warning(self, "Error", "No download location selected.")
                return None

            with open(download_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()

            QMessageBox.information(self, "Success", f"File downloaded: {download_path}")
            return download_path
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Google Drive file download failed: {e}")
            return None
