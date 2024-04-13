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
from tour_diary import TourDiary


def showMessageBox(title, message):
    msgBox = QMessageBox()
    msgBox.setWindowTitle(title)
    msgBox.setText(message)
    msgBox.setStyleSheet("""
        QMessageBox { background-color: #ffffff; font-family: 'Microsoft YaHei'; font-size: 9pt; }
        QPushButton { width: 200px; height: 20px; background-color: #262B4B; color: white; }
    """)
    msgBox.exec_()


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
        showMessageBox("登录结果", msg)
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
        showMessageBox("注册结果", msg)
        if success:
            self.signupSuccess.emit()
            self.mainWindow = MainWindow()
            self.mainWindow.show()
            self.close()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 连接搜索按钮的点击事件
        self.ui.searchButton.clicked.connect(self.searchDiary)
        # 连接创建日记按钮的点击事件
        self.ui.createButton.clicked.connect(self.createDiary)

    def searchDiary(self):
        keyword = self.ui.searchKeyword.text()
        success, results = tour_diary.SearchDiary(keyword)
        if success:
            if not results.empty:
                first_match_id = results.iloc[0]['id']
                successShow, content = tour_diary.ShowDiary(first_match_id)
                if successShow:
                    diary_title = results.iloc[0]['title']
                    self.ui.diaryTitle.setText(diary_title)
                    self.ui.diaryContent.setText(content)
                else:
                    showMessageBox("日记内容显示错误", content)
            else:
                showMessageBox("搜索结果", "未找到匹配的日记。")
        else:
            showMessageBox("搜索结果", results)  # results 为错误消息

    def createDiary(self):
        # 从 QLineEdit 和 QTextEdit 获取标题和内容
        title = self.ui.newDiaryTitle.text()
        content = self.ui.newDiaryContent.toPlainText()
        success, msg = tour_diary.CreateDiary(title, content)
        showMessageBox("创建结果", msg)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 启用高DPI缩放
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # 启用高DPI图标
    app = QApplication(sys.argv)
    user_info = UserInfo()  # 创建 UserInfo 实例
    tour_diary = TourDiary(user_info)
    firstWindow = FirstWindow()
    firstWindow.show()
    sys.exit(app.exec_())
