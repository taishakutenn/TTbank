import sys
import sqlite3
import traceback
import datetime
from dbm import error
from distutils.command.check import check
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
        self.load_page()

        self.createNewAccountButton.clicked.connect(self.create_new_account)
        self.checkAccountsButton.clicked.connect(self.check_all_accounts)
        self.editAccountButton.clicked.connect(self.edit_account)
        self.transferFundsButton.clicked.connect(self.transfer_funds)
        self.exchangeCurrencyButton.clicked.connect(self.exchange_currency)
        self.checkHistoryButton.clicked.connect(self.check_history)
        self.blackThemeButton.clicked.connect(self.changed_color)
        self.whiteThemeButton.clicked.connect(self.changed_color)
        self.leaveAccountButton.clicked.connect(self.leave_account)
        self.loadPageButton.clicked.connect(self.load_page)

    def changed_color(self): # Функция изменения цвета программы
        config_writer = open("dist/userInformation/config", "w", encoding="utf-8")
        sender = self.sender()
        if sender == self.blackThemeButton:
            self.backgroundFrame.setStyleSheet('''
            QFrame {
                background-color: rgb(43, 45, 48);
                border-radius: 10px;
            }
            QLabel, QPushButton {
                color: rgb(225,225,225);
                border-radius: 10px;
            }''')
            config_writer.write("dark")
        else:
            self.backgroundFrame.setStyleSheet('''
            QFrame {
                background-color: rgb(253,217,181);
                border-radius: 10px;
            }   
            QLabel, QPushButton {
                color: rgb(0,0,0);
                border-radius: 10px;
            }''')
            config_writer.write("light")
        config_writer.close()

    def load_config(self):
        # Прописываем получение и утсановление цвета, который пользователь выбрал перед выходом из программы
        with open("dist/userInformation/config", "r", encoding="utf-8") as f:
            background_theme = f.read().strip()
            if background_theme == "dark":
                self.backgroundFrame.setStyleSheet('''
                            QFrame {
                                background-color: rgb(43, 45, 48);
                                border-radius: 10px;
                            }
                            QLabel, QPushButton{
                                color: rgb(225,225,225);
                                border-radius: 10px;
                            }''')
            else:
                self.backgroundFrame.setStyleSheet('''
                            QFrame {
                                background-color: rgb(253,217,181);
                                border-radius: 10px;
                            }   
                            QLabel, QPushButton {
                                color: rgb(0,0,0);
                                border-radius: 10px;
                             }''')
    def load_page(self):
        # Прописываем отображение информации о счетах пользователя
        self.connect_db()
        sql = '''SELECT account_name, balance, currency FROM accounts WHERE user_id = ?'''
        response = self.cursor.execute(sql, (int(self.user_id[0][0]),)).fetchall()
        if len(response) > 1:  # Для отображения, если аккаунтов множество
            self.nameAccTwoLabel.setVisible(True)
            self.balanceTwoLabel.setVisible(True)
            self.balanceOneLabel.setVisible(True)
            self.nameAccOneLabel.setText(response[0][0])
            self.nameAccTwoLabel.setText(response[1][0])

            self.balanceOneLabel.setText(f"Баланс: {response[0][1]} {response[0][2]}")
            self.balanceTwoLabel.setText(f"Баланс: {response[1][1]} {response[1][2]}")

        elif len(response) == 1:  # Для отображения, если аккаунт один
            self.nameAccTwoLabel.setVisible(True)
            self.balanceTwoLabel.setVisible(True)
            self.balanceOneLabel.setVisible(True)
            self.nameAccOneLabel.setText(response[0][0])
            self.balanceOneLabel.setText(f"Баланс: {response[0][1]} {response[0][2]}")

            self.nameAccTwoLabel.setVisible(False)
            self.balanceTwoLabel.setVisible(False)

        else:  # Если аккаунтов нет
            self.nameAccOneLabel.setText("У вас пока нет ни дного счёта")
            self.nameAccTwoLabel.setVisible(False)
            self.balanceTwoLabel.setVisible(False)
            self.balanceOneLabel.setVisible(False)
        self.connect.close()

    def create_new_account(self):
        self.app = CreateNewAcc(int(self.user_id[0][0]))
        self.app.show()

    def check_all_accounts(self):
        self.connect_db()
        sql = '''SELECT account_name, balance, currency FROM accounts WHERE user_id = ?'''
        response = self.cursor.execute(sql, (int(self.user_id[0][0]),)).fetchall()
        self.connect.close()

        self.app = AllAccounts(response)
        self.app.show()

    def edit_account(self):
        self.connect_db()
        sql = '''SELECT account_name FROM accounts WHERE user_id = ?'''
        response = self.cursor.execute(sql, (int(self.user_id[0][0]),)).fetchall()
        self.connect.close()

        self.app = EditAccount(response)
        self.app.show()

    def transfer_funds(self):
        self.connect_db()
        sql = '''SELECT account_name FROM accounts WHERE user_id = ?'''
        response = self.cursor.execute(sql, (int(self.user_id[0][0]),)).fetchall()
        self.connect.close()

        self.app = Transfer(response, int(self.user_id[0][0]))
        self.app.show()

    def exchange_currency(self):
        self.connect_db()
        sql = '''SELECT account_name FROM accounts WHERE user_id = ?'''
        response = self.cursor.execute(sql, (int(self.user_id[0][0]),)).fetchall()
        self.connect.close()

        self.app = ChangeCurrency(response)
        self.app.show()

    def check_history(self):
        self.connect_db()
        sql = '''SELECT account_name FROM accounts WHERE user_id = ?'''
        response = self.cursor.execute(sql, (int(self.user_id[0][0]),)).fetchall()
        self.app = CheckHistory(response)
        self.app.show()

    def leave_account(self):
        with open("dist/userInformation/rememberMe.txt", "w", encoding="utf-8") as file:
            pass

        self.close()
        self.app = AuthorizationWindow()
        self.app.show()

    def connect_db(self):
        self.connect = sqlite3.connect("dist/bank")
        self.cursor = self.connect.cursor()


class AllAccounts(QWidget):
    def __init__(self, response):
        super().__init__()
        self.response = response
        self.loadUi()

    def loadUi(self):
        uic.loadUi('allAccounts.ui', self)
        if len(self.response) > 0:
            for item in self.response:
                self.allAccountsList.addItem(f"Название: {item[0]}\nБаланс: {item[1]} {item[2]}\n")
        else:
            self.allAccountsList.addItem(f"На данный момент у вас нет ни одного аккаунта")


class Transfer(QWidget):
    def __init__(self, response, user_id):
        super().__init__()
        self.response = response
        self.user_id = user_id
        self.loadUi()

    def loadUi(self):
        uic.loadUi('transfer.ui', self)
        self.transferMoneyButton.clicked.connect(self.transfer_money)

        for value in self.response:
            self.accountsBox.addItem(value[0])

    def transfer_money(self):
        transfer_summ = self.transferSummEdit.text()
        number = self.numberRecipientEdit.text()
        if self.check(number):
            if transfer_summ and int(transfer_summ) > 0:
                current_account = self.accountsBox.currentText()
                self.connect_db()
                sql = '''SELECT balance FROM accounts WHERE account_name = ?;'''
                on_balance = self.cursor.execute(sql, (current_account,)).fetchall()
                if int(on_balance[0][0]) > int(transfer_summ):
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    # Обновляем счёт отправителя
                    sql = '''UPDATE accounts
                             SET balance = balance - ?
                             WHERE account_name = ?;'''
                    self.cursor.execute(sql, (int(transfer_summ), current_account))
                    self.connect.commit()

                    # Добавляем запись о переводе, связанную со счётом отправителя
                    sql = '''INSERT INTO operations(account_name, date_operation, summ_operation, operation)
                             VALUES(?, ?, ?, "-")'''
                    self.cursor.execute(sql, (current_account, current_time, int(transfer_summ)))
                    self.connect.commit()

                    # Обновляем аккаунт получателя
                    sql = '''UPDATE accounts
                             SET balance = balance + ?
                             WHERE account_id = (
                             SELECT MIN(account_id)
                             FROM accounts
                             WHERE user_id = (SELECT user_id FROM users WHERE phone_number = ?))'''
                    self.cursor.execute(sql, (int(transfer_summ), number))
                    self.connect.commit()

                    # Получаем имя аккаунта получателя (по умолчанию самый первый аккаунт)
                    sql='''SELECT account_name
                           FROM accounts
                           WHERE user_id = (SELECT user_id FROM users WHERE phone_number = ?)
                           LIMIT 1;'''
                    recipient_account = self.cursor.execute(sql, (number, )).fetchall()

                    # Добавляем в operation запись о получении средств, связанную со счётом получателя
                    sql = '''INSERT INTO operations(account_name, date_operation, summ_operation, operation)
                             VALUES(?, ?, ?, "+")'''
                    self.cursor.execute(sql, (recipient_account[0][0], current_time, int(transfer_summ)))
                    self.connect.commit()
                    self.connect.close()
                    self.close()
                else:
                    self.errorLabel.setText("На счёте не хватает сдердств")
                    self.timer_error_text(self.errorLabel)
                    self.transferSummEdit.setText("")
            else:
                self.errorLabel.setText("Вы не ввели сумму перевода")
                self.timer_error_text(self.errorLabel)
                self.transferSummEdit.setText("")
        else:
            self.errorLabel.setText("Номер телефона введён неверно")
            self.timer_error_text(self.errorLabel)
            self.numberRecipientEdit.setText("")


    def check(self, number):
        number = "".join(number.split())
        if not number.startswith("+7") and not number.startswith("8"):
            return False
        if "--" in number:
            return False
        if number.endswith("-"):
            return False
        number = number.replace("-", "")

        brackets_left = number.find("(")
        brackets_right = number.find(")")

        if brackets_left > -1:
            if brackets_right < brackets_left:
                return False
            if number.count("(") != 1 or number.count(")") != 1:
                return False
        else:
            if brackets_right > -1:
                return False

        number = number.replace("(", "").replace(")", "")

        if number[0] == "8" and number[0]:
            number = "+7" + number[1:]
        if len(number) != 12:
            return False
        if not number[1:].isdigit():
            return False

        sql = '''SELECT user_id FROM users WHERE phone_number = ?'''
        self.connect_db()
        res = self.cursor.execute(sql, (number, )).fetchall()
        if not res:
            return False

        self.connect.close()

        return True

    def timer_error_text(self, widget):
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda: widget.clear())
        self.timer.start(3000)

    def connect_db(self):
        self.connect = sqlite3.connect("dist/bank")
        self.cursor = self.connect.cursor()


class ChangeCurrency(QWidget):
    def __init__(self, response):
        super().__init__()
        self.response = response
        self.loadUi()

    def loadUi(self):
        uic.loadUi('changeCurrency.ui', self)
        self.changeButton.clicked.connect(self.change_currency)

        for value in self.response:
            self.accountsBox.addItem(value[0])

    def change_currency(self):
        current_account = self.accountsBox.currentText()
        current_currency = self.currencyBox.currentText()
        sql = '''UPDATE accounts SET currency = ?, balance = balance / ? WHERE account_name = ?'''
        self.connect_db()
        if current_currency == "Долар":
            self.cursor.execute(sql, ("Дол", 100, current_account))
        elif current_currency == "Евро":
            self.cursor.execute(sql, ("Евро", 130, current_account))
        self.connect.commit()
        self.connect.close()
        self.close()

    def connect_db(self):
        self.connect = sqlite3.connect("dist/bank")
        self.cursor = self.connect.cursor()


class EditAccount(QWidget):
    def __init__(self, response):
        super().__init__()
        self.response = response
        self.loadUi()

    def loadUi(self):
        uic.loadUi('editAccount.ui', self)

        self.deleteAccount.clicked.connect(self.delete_account)
        self.confirmChangeButton.clicked.connect(self.edit)

        for value in self.response:
            self.accountsBox.addItem(value[0])

    def delete_account(self):
        current_account = self.accountsBox.currentText()
        self.connect_db()
        # Удаляем запись из таблицы счетов
        sql = '''DELETE from accounts WHERE account_name = ?'''
        self.cursor.execute(sql, (current_account, ))
        self.connect.commit()

        # Удаляем запись из таблицы операций
        sql = '''DELETE FROM operations WHERE account_name = ?'''
        self.cursor.execute(sql, (current_account, ))
        self.connect.commit()
        self.connect.close()
        self.close()

    def edit(self):
        new_account_name = self.nameAccountEdit.text()
        current_account = self.accountsBox.currentText()
        if len(new_account_name) > 0:
            self.connect_db()
            # Обновляем записи в таблице счетов
            sql = '''UPDATE accounts SET account_name = ? WHERE account_name = ?'''
            self.cursor.execute(sql, (new_account_name, current_account))
            self.connect.commit()

            # Обновляем записи в таблице операций
            sql = '''UPDATE operations SET account_name = ? WHERE account_name = ?'''
            self.cursor.execute(sql, (new_account_name, current_account))
            self.connect.commit()
            self.connect.close()
            self.close()

    def connect_db(self):
        self.connect = sqlite3.connect("dist/bank")
        self.cursor = self.connect.cursor()


class CheckHistory(QWidget):
    def __init__(self, response):
        super().__init__()
        self.response = response
        self.loadUi()

    def loadUi(self):
        uic.loadUi('checkHistory.ui', self)

        self.checkAccountHistoryButton.clicked.connect(self.check_history)

        for value in self.response:
            self.accountsBox.addItem(value[0])

    def check_history(self):
        self.connect = sqlite3.connect("dist/bank")
        self.cursor = self.connect.cursor()
        current_account = self.accountsBox.currentText()

        sql = '''SELECT date_operation, summ_operation, operation
                 FROM operations
                 WHERE account_name = ?'''

        history_data = self.cursor.execute(sql, (current_account, )).fetchall()
        for value in history_data:
            self.HistoryList.addItem(f"{value[2]}{value[1]}\n{value[0]}\n")
        self.connect.close()


class CreateNewAcc(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.loadUi()

    def loadUi(self):
        uic.loadUi('CreateNewAcc.ui', self)

        self.createNewAccButton.clicked.connect(self.create_new_account)

    def create_new_account(self):
        account_name = self.nameNewAccEdit.text()
        if account_name and not account_name.isdigit():
            connect = sqlite3.connect("dist/bank")
            cursor = connect.cursor()
            sql = '''INSERT INTO accounts(account_name, user_id, balance, currency)
                     VALUES(?, ?, 0, "Руб")'''
            cursor.execute(sql, (account_name, self.user_id))
            connect.commit()
            connect.close()
            self.close()
        else:
            pass


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
        phone_number = self.registrationFrame.text()
        if self.check_data(name, surname, patronymic, passport_details, age, who_called_check="registerFunc"):
            self.connect_db()
            sql = '''INSERT INTO users(name, surname, patronymic, passport_details, age, phone_number)
                     VALUES (?, ?, ?, ?, ?, ?);'''
            self.cursor.execute(sql, (name, surname, patronymic, passport_details, age, phone_number))
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
                if self.rememberMeBox.isChecked(): # Если выбрано "запомнить меня" в файл записываем данные для входа
                    with open("dist/userInformation/rememberMe.txt", "w", encoding="utf-8") as file:
                        file.write(f"{name}\n{surname}\n{passport_details}")

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
        self.connect = sqlite3.connect("dist/bank")
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
        with open("dist/userInformation/passwordDivice", encoding="utf-8") as file:
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
        with open("dist/userInformation/passwordDivice", "r+", encoding="utf-8") as file:
            password = file.read().strip()
            if not password == "":
                if password == self.passwordEdit.text():
                    file = open("dist/userInformation/rememberMe.txt", "r", encoding="utf-8")
                    data = file.read().split("\n")
                    if len(data) == 3:
                        self.connect_db()
                        sql = '''SELECT user_id
                                         FROM users
                                         WHERE name = ? AND surname = ? AND passport_details = ?'''
                        response = self.cursor.execute(sql, (data[0], data[1], data[2])).fetchall()
                        self.connect.close()

                        self.app = MainWindow(data[0], response)
                        self.app.show()
                    else:
                        self.ex = AuthorizationWindow()
                        self.ex.show()
                    self.close()  # Закрытие текущего окна
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

    def connect_db(self):
        self.connect = sqlite3.connect("dist/bank")
        self.cursor = self.connect.cursor()


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("Oбнаружена ошибка !:", tb)


if __name__ == '__main__':
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    ex = DevicePasswordWindow()
    ex.show()
    sys.exit(app.exec())