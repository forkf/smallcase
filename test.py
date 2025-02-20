import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QLabel


class SecondUI(QDialog):  # This is the second UI (Dialog Window)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Second UI")
        self.setGeometry(200, 200, 300, 150)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("This is the second UI.\nClose me to return to the main UI."))
        self.setLayout(layout)


class FirstUI(QMainWindow):  # This is the main UI
    def __init__(self):
        super().__init__()
        self.setWindowTitle("First UI")
        self.setGeometry(100, 100, 400, 200)

        self.button = QPushButton("Open Second UI", self)
        self.button.setGeometry(100, 50, 200, 50)
        self.button.clicked.connect(self.open_second_ui)

    def open_second_ui(self):
        self.second_ui = SecondUI()
        self.second_ui.exec_()  # This waits until SecondUI is closed


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = FirstUI()
    main_window.show()
    sys.exit(app.exec_())
