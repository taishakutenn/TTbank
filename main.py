import sys
import sqlite3
import traceback
from sys import excepthook

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QPropertyAnimation, QPoint
from PyQt6.uic import loadUi


class Authorization(QWidget): # 920x562
    def __init__(self):
        super().__init__()
        self.loadUi()

    def loadUi(self):
        uic.loadUi('registrationWindow.ui', self)

        # Вызов анимации
        self.registrationButton.clicked.connect(self.open_register_frame)
        self.comeBackButton.clicked.connect(self.open_login_frame)

        self.loginButton.clicked.connect(self.log_in) # Залогиниться
        self.registrationRegButton.clicked.connect(self.register) # Зарегистрироваться

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

    def register(self):
        self.connect_db()

        name = self.nameRegEdit.text()
        surname = self.surnameRegEdit.text()
        patronymic = self.patronymicRegEdit.text()
        passport_details = self.passportDetailsRegEdit.text()
        age = self.ageRegEdit.text()

        sql = '''INSERT INTO users(name, surname, patronymic, passport_details, age)
                 VALUES (?, ?, ?, ?, ?)'''
        self.cursor.execute(sql, (name, surname, patronymic, passport_details, age))
        self.connect.commit()
        self.connect.close()

    def log_in(self):
        print("login")

    def connect_db(self):
        self.connect = sqlite3.connect("Bank")
        self.cursor = self.connect.cursor()

def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("Oбнаружена ошибка !:", tb)


if __name__ == '__main__':
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    ex = Authorization()
    ex.show()
    sys.exit(app.exec())