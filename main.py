import sys
import sqlite3

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QPropertyAnimation, QPoint


class Authorization(QWidget): # 920x562
    def __init__(self):
        super().__init__()

        # Коннет к бд
        self.connect = sqlite3.connect("Bank.sqlite")
        self.cursor = self.connect.cursor()

        uic.loadUi('registrationWindow.ui', self)

        # Вызов анимации
        self.registrationButton.clicked.connect(self.open_register_frame)
        self.comeBackButton.clicked.connect(self.open_login_frame)

        self.loginButton.clicked.connect(self.log_in)

    def open_register_frame(self):
        animation_login_frame = QPropertyAnimation(self.animationFrame, b"pos", self)
        animation_login_frame.setDuration(1000)
        animation_login_frame.setStartValue(QPoint(500, -500))
        animation_login_frame.setEndValue(QPoint(500, 40))
        animation_login_frame.start()

    def open_login_frame(self):
        animation_login_frame = QPropertyAnimation(self.animationFrame, b"pos", self)
        animation_login_frame.setDuration(1000)
        animation_login_frame.setStartValue(QPoint(500, 40))
        animation_login_frame.setEndValue(QPoint(500, -500))
        animation_login_frame.start()

    def log_in(self):
        print("login")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Authorization()
    ex.show()
    sys.exit(app.exec())