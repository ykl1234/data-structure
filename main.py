import sys

from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog, QMessageBox, QMainWindow

from first_windows import Ui_first_windows
from main_windows import Ui_MainWindow
from sign_in_windows import Ui_sign_in_windows
from sign_up_windows import Ui_sign_up_windows_2
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
        msgBox = QMessageBox()
        msgBox.setWindowTitle("登录结果")
        msgBox.setText(msg)

        # 设置样式表
        msgBox.setStyleSheet("""
            QMessageBox { background-color: #ffffff;font-family: 'Microsoft YaHei'; font-size: 9pt;}
            QPushButton { width: 200px; height: 20px; background-color: #262B4B; color: white; }
        """)
        msgBox.exec_()
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
        msgBox = QMessageBox()
        msgBox.setWindowTitle("登录结果")
        msgBox.setText(msg)

        # 设置样式表
        msgBox.setStyleSheet("""
                    QMessageBox { background-color: #ffffff;font-family: 'Microsoft YaHei'; font-size: 9pt;}
                    QPushButton { width: 200px; height: 20px; background-color: #262B4B; color: white; }
                """)
        msgBox.exec_()
        if success:
            self.signupSuccess.emit()
            self.mainWindow = MainWindow()
            self.mainWindow.show()
            self.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 启用高DPI缩放
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # 启用高DPI图标
    app = QApplication(sys.argv)
    user_info = UserInfo()  # Create an instance of UserInfo
    firstWindow = FirstWindow()
    firstWindow.show()
    sys.exit(app.exec_())
