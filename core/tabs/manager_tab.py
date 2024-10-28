from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QInputDialog, QMessageBox
from core.database.database import get_manager_data, connect_db
from core.encryption.encryption import decrypt_aes


class ManagerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setup_ui()
        self.load_manager_data()
        self.setLayout(self.layout)

    def setup_ui(self):
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search URL...")
        self.search_bar.textChanged.connect(self.filter_data)
        self.layout.addWidget(self.search_bar)

        # Table for displaying data
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # Update to 6 columns to include 'ID'
        self.table.setHorizontalHeaderLabels(["ID", "URL", "Username/Email", "Password", "2FA", "Note"])
        self.layout.addWidget(self.table)

        # Buttons layout
        button_layout = QHBoxLayout()
        self.view_button = QPushButton("Unmask")
        self.view_button.clicked.connect(self.unmask_entry)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_entry)
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_manager_data)

        button_layout.addWidget(self.view_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)
        self.layout.addLayout(button_layout)

    def load_manager_data(self):
        self.table.setRowCount(0)
        entries = get_manager_data()
        for row_num, (entry_id, url, username_email, password, two_fa, note) in enumerate(entries):
            self.table.insertRow(row_num)
            self.table.setItem(row_num, 0, QTableWidgetItem(str(entry_id)))  # Display ID
            self.table.setItem(row_num, 1, QTableWidgetItem(url))
            self.table.setItem(row_num, 2, QTableWidgetItem('*' * 8))  # Masked Username/Email
            self.table.setItem(row_num, 3, QTableWidgetItem('*' * 8))  # Masked Password
            self.table.setItem(row_num, 4, QTableWidgetItem(two_fa))
            self.table.setItem(row_num, 5, QTableWidgetItem('*' * 8))  # Masked Note

    def filter_data(self):
        filter_text = self.search_bar.text().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)  # Check the URL column
            self.table.setRowHidden(row, filter_text not in item.text().lower())

    def unmask_entry(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select an entry to unmask.")
            return

        entry_id = self.table.item(selected_row, 0).text()  # Get ID from the table
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT username_email, password, two_factor_auth, note FROM manager WHERE id=?', (entry_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            encrypted_user, encrypted_pass, _, encrypted_note = result
            decryption_key, ok = QInputDialog.getText(self, "Decryption Key", "Enter decryption key:",
                                                      QLineEdit.Password)
            if ok and decryption_key:
                decrypted_user = decrypt_aes(encrypted_user, decryption_key)
                decrypted_pass = decrypt_aes(encrypted_pass, decryption_key)
                decrypted_note = decrypt_aes(encrypted_note, decryption_key) if encrypted_note else ""

                if decrypted_user and decrypted_pass:
                    self.table.setItem(selected_row, 2, QTableWidgetItem(decrypted_user))
                    self.table.setItem(selected_row, 3, QTableWidgetItem(decrypted_pass))
                    self.table.setItem(selected_row, 5, QTableWidgetItem(decrypted_note))
                else:
                    QMessageBox.warning(self, "Decryption Failed", "Invalid key or corrupted data.")

    def delete_entry(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select an entry to delete.")
            return

        entry_id = self.table.item(selected_row, 0).text()  # Get ID from the table
        confirm = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete entry ID: {entry_id}?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if confirm == QMessageBox.Yes:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM manager WHERE id=?', (entry_id,))
            conn.commit()
            conn.close()
            self.load_manager_data()
