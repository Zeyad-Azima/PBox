from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from core.tabs.manager_tab import ManagerTab
from core.tabs.add_tab import AddTab
from core.tabs.edit_tab import EditTab
from core.tabs.settings_tab import SettingsTab
from core.tabs.backup_tab import BackupTab
from core.tabs.info_tab import InfoTab
from core.ui.styles import DARK_STYLE
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PBox Password Manager v1.0")
        self.setWindowIcon(QIcon(r"C:\Users\azima\Desktop\PBox\PBox\logo.png"))
        self.setGeometry(100, 100, 800, 400)

        self.setStyleSheet(DARK_STYLE)

        self.layout = QVBoxLayout()

        # Tabs
        self.tabs = QTabWidget()
        self.manager_tab = ManagerTab()
        self.add_tab = AddTab()
        self.edit_tab = EditTab()
        self.settings_tab = SettingsTab()
        self.backup_tab = BackupTab()  # Add the BackupTab
        self.info_tab = InfoTab()

        self.tabs.addTab(self.manager_tab, "Manager")
        self.tabs.addTab(self.add_tab, "Add")
        self.tabs.addTab(self.edit_tab, "Edit")
        self.tabs.addTab(self.settings_tab, "Settings")
        self.tabs.addTab(self.backup_tab, "Backup")  # Add Backup tab before Info
        self.tabs.addTab(self.info_tab, "Info")

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
