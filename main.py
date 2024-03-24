import sys
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QMainWindow
from first_windows import Ui_first_windows
from sign_in_windows import Ui_sign_in_windows
from sign_up_windows import Ui_sign_up_windows_2
from main_windows import Ui_main_windows
from user_info import UserInfo

class FirstWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_first_windows()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.showSignInWindow)
        self.ui.pushButton_2.clicked.connect(self.showSignUpWindow)

    def showSignInWindow(self):
        self.signInWindow = SignInWindow()
        self.signInWindow.loginSuccess.connect(self.close)
        self.signInWindow.show()

    def showSignUpWindow(self):
        self.signUpWindow = SignUpWindow()
        self.signUpWindow.signupSuccess.connect(self.close)
        self.signUpWindow.show()

class SignInWindow(QDialog):
    loginSuccess = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_sign_in_windows()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.login)
        self.ui.pushButton_2.clicked.connect(self.close)

    def login(self):
        username = self.ui.lineEdit.text()
        password = self.ui.lineEdit_2.text()
        success, msg = user_info.SignIn(username, password)
        QMessageBox.information(self, "登录结果", msg)
        if success:
            self.loginSuccess.emit()
            self.mainWindow = MainWindow()
            self.mainWindow.show()
            self.close()

class SignUpWindow(QDialog):
    signupSuccess = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_sign_up_windows_2()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.signup)
        self.ui.pushButton_2.clicked.connect(self.close)

    def signup(self):
        username = self.ui.lineEdit.text()
        password = self.ui.sign_up_windows.text()
        success, msg = user_info.SignUp(username, password)
        QMessageBox.information(self, "注册结果", msg)
        if success:
            self.signupSuccess.emit()
            self.mainWindow = MainWindow()
            self.mainWindow.show()
            self.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_main_windows()
        self.ui.setupUi(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    user_info = UserInfo()  # Create an instance of UserInfo
    firstWindow = FirstWindow()
    firstWindow.show()
    sys.exit(app.exec_())
