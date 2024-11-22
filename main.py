import sys
import sqlite3
import traceback
from dbm import error
from idlelib.iomenu import encoding
from sys import excepthook

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt6.QtCore import QPropertyAnimation, QPoint, QTimer, Qt
from PyQt6.QtGui import QScreen
from PyQt6.uic import loadUi


class MainWindow(QMainWindow):
    def __init__(self, name, user_id):
        super().__init__()
        self.user_id = user_id
        self.name = name
        self.loadUi()
        self.load_config()


    def loadUi(self):
        uic.loadUi('mainWindow.ui', self)
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()

        self.welcomLabel.setText(f"Здравствуйте, {self.name}!")
        self.move((screen_geometry.width() - self.width() // 1) // 2, (screen_geometry.height() - 20 - self.height() // 1) // 2)

        # Прописываем отображение информации о счетах пользователя, если они у него есть
        self.connect_db()
        sql = '''SELECT account_name, balance, currency FROM accounts WHERE user_id = ?'''
        response = self.cursor.execute(sql, (int(self.user_id[0][0]),)).fetchall()
        if response:
            self.nameAccOneLabel.setText(response[0][0])
            self.nameAccTwoLabel.setText(response[1][0])

            self.balanceOneLabel.setText(f"Баланс: {response[0][1]} {response[0][2]}")
            self.balanceTwoLabel.setText(f"Баланс: {response[1][1]} {response[0][2]}")
        self.connect.close()

        self.createNewAccountButton.clicked.connect(self.create_new_account)
        self.checkAccountsButton.clicked.connect(self.check_all_accounts)
        self.editAccountButton.clicked.connect(self.edit_account)
        self.transferFundsButton.clicked.connect(self.transfer_funds)
        self.exchangeCurrencyButton.clicked.connect(self.exchange_currency)
        self.checkHistoryButton.clicked.connect(self.check_history)
        self.blackThemeButton.clicked.connect(self.changed_color)
        self.whiteThemeButton.clicked.connect(self.changed_color)

    def changed_color(self): # Функция изменения цвета программы
        config_writer = open("userInformation/config", "w", encoding="utf-8")
        sender = self.sender()
        if sender == self.blackThemeButton:
            self.backgroundFrame.setStyleSheet('''
            QFrame {
                background-color: rgb(43, 45, 48);
            }
            QLabel, QPushButton {
                color: rgb(225,225,225);
            }''')
            config_writer.write("dark")
        else:
            self.backgroundFrame.setStyleSheet('''
            QFrame {
                background-color: rgb(253,217,181);
            }   
            QLabel, QPushButton {
                color: rgb(0,0,0);
            }''')
            config_writer.write("light")
        config_writer.close()

    def load_config(self):
        # Прописываем получение и утсановление цвета, который пользователь выбрал перед выходом из программы
        with open("userInformation/config", "r", encoding="utf-8") as f:
            background_theme = f.read().strip()
            if background_theme == "dark":
                self.backgroundFrame.setStyleSheet('''
                            QFrame {
                                background-color: rgb(43, 45, 48);
                            }
                            QLabel, QPushButton{
                                color: rgb(225,225,225);
                            }''')
            else:
                self.backgroundFrame.setStyleSheet('''
                            QFrame {
                                background-color: rgb(253,217,181);
                            }   
                            QLabel, QPushButton {
                                color: rgb(0,0,0);
                             }''')

    def create_new_account(self):
        pass

    def check_all_accounts(self):
        pass

    def edit_account(self):
        self.app = EditAccount()
        self.app.show()

    def transfer_funds(self):
        self.app = Transfer()
        self.app.show()

    def exchange_currency(self):
        self.app = ChangeCurrency()
        self.app.show()

    def check_history(self):
        self.app = CheckHistory()
        self.app.show()

    def connect_db(self):
        self.connect = sqlite3.connect("Bank")
        self.cursor = self.connect.cursor()


class Transfer(QWidget):
    def __init__(self):
        super().__init__()
        self.loadUi()

    def loadUi(self):
        uic.loadUi('transfer.ui', self)


class ChangeCurrency(QWidget):
    def __init__(self):
        super().__init__()
        self.loadUi()

    def loadUi(self):
        uic.loadUi('changeCurrency.ui', self)


class EditAccount(QWidget):
    def __init__(self):
        super().__init__()
        self.loadUi()

    def loadUi(self):
        uic.loadUi('editAccount.ui', self)


class CheckHistory(QWidget):
    def __init__(self):
        super().__init__()
        self.loadUi()

    def loadUi(self):
        uic.loadUi('checkHistory.ui', self)


class AuthorizationWindow(QWidget): # 920x562
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

    # Анимации
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

    def register(self): # Функция регистрации
        name = self.nameRegEdit.text()
        surname = self.surnameRegEdit.text()
        patronymic = self.patronymicRegEdit.text()
        passport_details = self.passportDetailsRegEdit.text()
        age = self.ageRegEdit.text()
        if self.check_data(name, surname, patronymic, passport_details, age, who_called_check="registerFunc"):
            self.connect_db()
            sql = '''INSERT INTO users(name, surname, patronymic, passport_details, age)
                     VALUES (?, ?, ?, ?, ?);'''
            self.cursor.execute(sql, (name, surname, patronymic, passport_details, age))
            self.open_login_frame()
            self.connect.commit()
            self.connect.close()
        else:
            self.errorLabelReg.setText("Данные для регистрации введены в неверном формате")
            self.timer_error_text(self.errorLabelReg)

    def log_in(self): # Функция логина
        name = self.userNameEdit.text()
        surname = self.userSurnameEdit.text()
        passport_details = self.passportDetailsEdit.text()
        if self.check_data(name, surname, passport_details, who_called_check="loginFunc"):
            self.connect_db()
            sql = '''SELECT user_id
                     FROM users
                     WHERE name = ? AND surname = ? AND passport_details = ?'''
            response = self.cursor.execute(sql, (name, surname, passport_details)).fetchall()
            if response:
                self.connect.close()
                self.close()
                self.ex = MainWindow(name, response)
                self.ex.show()
            else:
                self.errorLabel.setText("Аккаунта с такими данными не существует")
                self.timer_error_text(self.errorLabel)
        else:
            self.errorLabel.setText("Данные для входа введены в неверном формате")
            self.timer_error_text(self.errorLabel)

    def check_data(self, *kwargs, who_called_check):
        if who_called_check == "loginFunc":
            passport_details = kwargs[2]
            name = kwargs[0]
            surname = kwargs[1]
            if len(passport_details) != 11:
                return False
            if " " not in passport_details and passport_details.index(" ") != 4:
                return False
            if len(name) == 0 or len(surname) == 0:
                return False
            return True
        elif who_called_check == "registerFunc":
            name = kwargs[0]
            surname = kwargs[1]
            patronymic = kwargs[2]
            passport_details = kwargs[3]
            age = kwargs[4]
            if len(name) == 0 or len(surname) == 0 or len(patronymic) == 0:
                return False
            if " " not in passport_details and passport_details.index(" ") != 4:
                return False
            if not age.isdigit():
                return False
            return True

    def connect_db(self):
        self.connect = sqlite3.connect("Bank")
        self.cursor = self.connect.cursor()

    def timer_error_text(self, widget):
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)  # Таймер срабатывает один раз
        self.timer.timeout.connect(lambda: widget.clear())  # Используем лямбда-функцию для очистки текста
        self.timer.start(3000)


class DevicePasswordWindow(QWidget): # 301x238
    def __init__(self):
        super().__init__()
        self.loadUi()

    def loadUi(self):
        uic.loadUi("passwordDevice.ui", self)
        with open("userInformation/passwordDivice", encoding="utf-8") as file:
            password = file.read().strip()
            if not password == "":
                self.label.setText("Введите пин-код")
            else:
                self.label.setText("Придумайте пин-код")

        self.oneButton.clicked.connect(self.pass_input)
        self.twoButton.clicked.connect(self.pass_input)
        self.threeButton.clicked.connect(self.pass_input)
        self.fourButton.clicked.connect(self.pass_input)
        self.fiveButton.clicked.connect(self.pass_input)
        self.sixButton.clicked.connect(self.pass_input)
        self.sevenButton.clicked.connect(self.pass_input)
        self.eightButton.clicked.connect(self.pass_input)
        self.nineButton.clicked.connect(self.pass_input)
        self.zeroButton.clicked.connect(self.pass_input)
        self.deleteButton.clicked.connect(self.delete_symbol)
        self.enterButton.clicked.connect(self.check_password)

    def pass_input(self):
        start_meaning = self.passwordEdit.text()
        new_meaning = self.sender().text()
        self.passwordEdit.setText(f"{start_meaning}{new_meaning}")

    def delete_symbol(self):
        text = self.passwordEdit.text()[:-1]
        self.passwordEdit.setText(text)

    def check_password(self):
        with open("userInformation/passwordDivice", "r+", encoding="utf-8") as file:
            password = file.read().strip()
            if not password == "":
                if password == self.passwordEdit.text():
                    self.close() # Закрытие текущего окна
                    self.ex = AuthorizationWindow()
                    self.ex.show()
                else:
                    self.passwordEdit.setText("")
            else:
                file.write(self.passwordEdit.text())
                self.close()
                self.ex = AuthorizationWindow()
                self.ex.show()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_1:
            self.oneButton.click()
        elif key == Qt.Key.Key_2:
            self.twoButton.click()
        elif key == Qt.Key.Key_3:
            self.threeButton.click()
        elif key == Qt.Key.Key_4:
            self.fourButton.click()
        elif key == Qt.Key.Key_5:
            self.fiveButton.click()
        elif key == Qt.Key.Key_6:
            self.sixButton.click()
        elif key == Qt.Key.Key_7:
            self.sevenButton.click()
        elif key == Qt.Key.Key_8:
            self.eightButton.click()
        elif key == Qt.Key.Key_9:
            self.nineButton.click()
        elif key == Qt.Key.Key_0:
            self.zeroButton.click()
        elif key == Qt.Key.Key_Backspace:
            self.deleteButton.click()
        elif key == Qt.Key.Key_Return:
            self.check_password()


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("Oбнаружена ошибка !:", tb)


if __name__ == '__main__':
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    ex = AuthorizationWindow()
    ex.show()
    sys.exit(app.exec())