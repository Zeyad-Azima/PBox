import sys
import threading
from PyQt5.QtWidgets import QApplication
from core.ui.login_window import LoginWindow
from core.api.api import run_flask_app

if __name__ == "__main__":
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    # Start PyQt5 app
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
