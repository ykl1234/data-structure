# main.py
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from first_windows import Ui_Dialog as Ui_FirstWindow
from sign_in_windows import Ui_Dialog as Ui_SignInWindow
from sign_up_windows import Ui_Dialog as Ui_SignUpWindow
from main_windows import Ui_Dialog as Ui_MainWindow
from user_info import UserInfo


class AppWindow(QDialog):
    def __init__(self, ui_class, userInfo):
        super().__init__()
        self.ui = ui_class()
        self.ui.setupUi(self)
        self.userInfo = userInfo


class FirstWindow(AppWindow):
    def __init__(self, userInfo):
        super().__init__(Ui_FirstWindow, userInfo)
        self.ui.pushButton.clicked.connect(self.openSignInWindow)
        self.ui.pushButton_2.clicked.connect(self.openSignUpWindow)

    def openSignInWindow(self):
        self.window = SignInWindow(self.userInfo)
        self.window.show()

    def openSignUpWindow(self):
        self.window = SignUpWindow(self.userInfo)
        self.window.show()


class SignInWindow(AppWindow):
    def __init__(self, userInfo):
        super().__init__(Ui_SignInWindow, userInfo)
        self.ui.pushButton.clicked.connect(self.signIn)
        self.ui.pushButton_2.clicked.connect(self.close)

    def signIn(self):
        name = self.ui.textEdit.toPlainText()
        password = self.ui.textEdit_2.toPlainText()
        success, message = self.userInfo.SignIn(name, password)
        if success:
            self.window = MainWindow()
            self.window.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Error', message)


class SignUpWindow(AppWindow):
    def __init__(self, userInfo):
        super().__init__(Ui_SignUpWindow, userInfo)
        self.ui.pushButton.clicked.connect(self.signUp)
        self.ui.pushButton_2.clicked.connect(self.close)

    def signUp(self):
        name = self.ui.textEdit.toPlainText()
        password = self.ui.textEdit_2.toPlainText()
        success, message = self.userInfo.SignUp(name, password)
        if success:
            QMessageBox.information(self, 'Success', message)
            self.close()  # 关闭注册窗口
            self.openSignInWindow()  # 打开登录窗口
        else:
            QMessageBox.warning(self, 'Error', message)

    def openSignInWindow(self):
        self.signInWindow = SignInWindow(self.userInfo)
        self.signInWindow.show()


class MainWindow(AppWindow):
    def __init__(self):
        super().__init__(Ui_MainWindow, None)


# MainWindow doesn't require interaction with userInfo directly, so it passes None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    userInfo = UserInfo()
    firstWindow = FirstWindow(userInfo)
    firstWindow.show()
    sys.exit(app.exec_())
