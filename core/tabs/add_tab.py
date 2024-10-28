from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QInputDialog, QMessageBox
from core.database.database import add_manager_entry
from core.encryption.encryption import encrypt_aes

class AddTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setup_ui()
        self.setLayout(self.layout)

    def setup_ui(self):
        # URL input
        url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        self.layout.addWidget(url_label)
        self.layout.addWidget(self.url_input)

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

        # Add button
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_entry)
        self.layout.addWidget(add_button)

    def add_entry(self):
        url = self.url_input.text()
        username_email = self.user_input.text()
        password = self.pass_input.text()
        two_fa = self.two_fa_dropdown.currentText()
        note = self.note_input.text()

        if not url or not username_email or not password:
            QMessageBox.warning(self, "Error", "Please fill in all required fields.")
            return

        encryption_key, ok = QInputDialog.getText(self, "Encryption Key", "Enter encryption key:", QLineEdit.Password)
        if not ok or not encryption_key:
            return

        encrypted_user = encrypt_aes(username_email, encryption_key)
        encrypted_pass = encrypt_aes(password, encryption_key)
        encrypted_note = encrypt_aes(note, encryption_key) if note else None

        success = add_manager_entry(url, encrypted_user, encrypted_pass, two_fa, encrypted_note)

        if success:
            QMessageBox.information(self, "Success", "Entry added successfully.")
            self.clear_inputs()
        else:
            QMessageBox.warning(self, "Error", "Failed to add entry to the database.")

    def clear_inputs(self):
        self.url_input.clear()
        self.user_input.clear()
        self.pass_input.clear()
        self.two_fa_dropdown.setCurrentIndex(0)
        self.note_input.clear()
