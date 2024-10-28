from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QDesktopServices, QFont
from PyQt5.QtCore import Qt, QUrl

class InfoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setup_ui()
        self.setLayout(self.layout)

    def setup_ui(self):
        # Center alignment for the layout
        self.layout.setAlignment(Qt.AlignCenter)

        # Developer info
        developer_info = QLabel("Zeyad Azima")
        developer_info.setAlignment(Qt.AlignCenter)
        developer_info.setFont(QFont('Segoe UI', 12, QFont.Bold))

        # Version info
        version_info = QLabel("PBox Password Manager v1.0")
        version_info.setAlignment(Qt.AlignCenter)
        version_info.setFont(QFont('Segoe UI', 12))

        # Slogan info
        slogan_info = QLabel("Killing User's Experience for the Sake of User's Security")
        slogan_info.setAlignment(Qt.AlignCenter)
        slogan_info.setFont(QFont('Segoe UI', 12, QFont.StyleItalic))
        slogan_info.setStyleSheet("color: #dcdcdc;")  # Set text color for visibility

        # Website link
        website_info = QLabel('<a href="https://zeyadazima.com">https://zeyadazima.com</a>')
        website_info.setOpenExternalLinks(True)  # Enable hyperlink
        website_info.setAlignment(Qt.AlignCenter)
        website_info.setFont(QFont('Segoe UI', 12))

        # Website link
        github_info = QLabel('<a href="https://github.com/Zeyad-Azima/PBox">https://github.com/Zeyad-Azima/PBox</a>')
        github_info.setOpenExternalLinks(True)  # Enable hyperlink
        github_info.setAlignment(Qt.AlignCenter)
        github_info.setFont(QFont('Segoe UI', 12))

        # Email link
        contact_info = QLabel('<a href="mailto:contact@zeyadazima.com">contact@zeyadazima.com</a>')
        contact_info.setOpenExternalLinks(True)  # Enable mailto link
        contact_info.setAlignment(Qt.AlignCenter)
        contact_info.setFont(QFont('Segoe UI', 12))

        # Add widgets to layout
        self.layout.addWidget(developer_info)
        self.layout.addWidget(version_info)
        self.layout.addWidget(slogan_info)  # Add slogan to layout
        self.layout.addWidget(website_info)
        self.layout.addWidget(github_info)
        self.layout.addWidget(contact_info)
