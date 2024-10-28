from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QInputDialog, QMessageBox
from core.database.database import connect_db, get_manager_data
from core.encryption.encryption import encrypt_aes, decrypt_aes

class EditTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setup_ui()
        self.setLayout(self.layout)

    def setup_ui(self):
        # URL dropdown list
        url_label = QLabel("Select Entry:")
        self.url_dropdown = QComboBox()
        self.url_dropdown.setPlaceholderText("Select entry to edit")
        self.load_entries()
        self.layout.addWidget(url_label)
        self.layout.addWidget(self.url_dropdown)

        # Load button
        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load_entry)
        self.layout.addWidget(load_button)

        # Username/Email input
        user_label = QLabel("Username/Email:")
        self.user_input = QLineEdit()
        self.layout.addWidget(user_label)
        self.layout.addWidget(self.user_input)

        # Password input
        pass_label = QLabel("Password:")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(pass_label)
        self.layout.addWidget(self.pass_input)

        # 2FA dropdown
        two_fa_label = QLabel("2FA Enabled:")
        self.two_fa_dropdown = QComboBox()
        self.two_fa_dropdown.addItems(["No", "Yes"])
        self.layout.addWidget(two_fa_label)
        self.layout.addWidget(self.two_fa_dropdown)

        # Note input
        note_label = QLabel("Note:")
        self.note_input = QLineEdit()
        self.layout.addWidget(note_label)
        self.layout.addWidget(self.note_input)

        # Update button
        update_button = QPushButton("Update")
        update_button.clicked.connect(self.update_entry)
        self.layout.addWidget(update_button)

    def load_entries(self):
        self.url_dropdown.clear()
        entries = get_manager_data()
        for entry_id, url, _, _, _, _ in entries:
            self.url_dropdown.addItem(f"{entry_id}: {url}")

    def load_entry(self):
        selected_entry = self.url_dropdown.currentText()
        entry_id = selected_entry.split(":")[0]

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT username_email, password, two_factor_auth, note FROM manager WHERE id=?', (entry_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            encrypted_user, encrypted_pass, two_fa, encrypted_note = result
            decryption_key, ok = QInputDialog.getText(self, "Decryption Key", "Enter decryption key:", QLineEdit.Password)
            if ok and decryption_key:
                decrypted_user = decrypt_aes(encrypted_user, decryption_key)
                decrypted_pass = decrypt_aes(encrypted_pass, decryption_key)
                decrypted_note = decrypt_aes(encrypted_note, decryption_key) if encrypted_note else ""

                if decrypted_user and decrypted_pass:
                    self.user_input.setText(decrypted_user)
                    self.pass_input.setText(decrypted_pass)
                    self.two_fa_dropdown.setCurrentText(two_fa)
                    self.note_input.setText(decrypted_note)
                else:
                    QMessageBox.warning(self, "Decryption Failed", "Invalid key or corrupted data.")

    def update_entry(self):
        selected_entry = self.url_dropdown.currentText()
        entry_id = selected_entry.split(":")[0]

        username_email = self.user_input.text()
        password = self.pass_input.text()
        two_fa = self.two_fa_dropdown.currentText()
        note = self.note_input.text()

        if not username_email or not password:
            QMessageBox.warning(self, "Error", "Please fill in all required fields.")
            return

        encryption_key, ok = QInputDialog.getText(self, "Encryption Key", "Enter encryption key:", QLineEdit.Password)
        if not ok or not encryption_key:
            return

        encrypted_user = encrypt_aes(username_email, encryption_key)
        encrypted_pass = encrypt_aes(password, encryption_key)
        encrypted_note = encrypt_aes(note, encryption_key) if note else None

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE manager 
            SET username_email=?, password=?, two_factor_auth=?, note=? 
            WHERE id=?
        ''', (encrypted_user, encrypted_pass, two_fa, encrypted_note, entry_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Entry updated successfully.")
