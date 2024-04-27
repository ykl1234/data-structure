import sys

import pandas as pd
import os
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QLineEdit, QTextEdit, QDialog, QMessageBox, QMainWindow
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from first_windows import Ui_first_windows
from main_windows import Ui_MainWindow
from sign_in_windows import Ui_sign_in_windows
from sign_up_windows import Ui_sign_up_windows_2
from diary import Ui_diaryWindows
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
        if os.path.exists('./accounts/last_user.csv'):
            last_user = pd.read_csv('./accounts/last_user.csv')
            if last_user.iloc[0]['autologin']:
                self.ui.autoLogin.setChecked(True)
                username = last_user.iloc[0]['name']
                password = last_user.iloc[0]['password']
                print(username, password)
                if not (pd.isna(username) or pd.isna(password)):
                    self.ui.lineEdit.setText(username)
                    self.ui.lineEdit_2.setText(password)
            else:
                self.ui.autoLogin.setChecked(False)
        else:
            pd.DataFrame({'name': None, 'password': None, 'autologin': False}, index=[0]).to_csv('./accounts'
                                                                                                 '/last_user.csv',
                                                                                                 index=False)
        self.ui.autoLogin.stateChanged.connect(self.updateBool)
        self.ui.pushButton.clicked.connect(self.login)
        self.ui.pushButton_2.clicked.connect(self.close)

    def updateBool(self):
        if self.ui.autoLogin.checkState() == Qt.Checked:
            self.auto_login = True
            if os.path.exists('./accounts/last_user.csv'):
                last_user = pd.read_csv('./accounts/last_user.csv')
                # if not last_user.empty:
                last_user.iloc[0, last_user.columns.get_loc('autologin')] = True
                print(last_user)
                last_user.to_csv('./accounts/last_user.csv', index=False)
        else:
            self.auto_login = False
            if os.path.exists('./accounts/last_user.csv'):
                # last_user = pd.DataFrame(columns=['name', 'password', 'autologin'], index=[0])
                pd.DataFrame({'name': None, 'password': None, 'autologin': False}, index=[0]).to_csv(
                    './accounts/last_user.csv', index=False)

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

        self.ui.searchButton.clicked.connect(self.searchDiary)
        self.ui.createButton.clicked.connect(self.createDiary)
        self.ui.diaryTitleList.itemClicked.connect(self.showDiaryDetails)
        # self.ui.myDiaryTitleList.itemClicked.connect(self.showDiaryDetails)

    def searchDiary(self):
        keyword = self.ui.searchKeyword.text()
        success, results = tour_diary.SearchDiary(keyword)
        if success:
            self.ui.diaryTitleList.clear()
            for index, row in results.iterrows():
                item = QListWidgetItem(f"{tour_diary.DiaryName(int(row['diary_id']))}")
                item.setData(Qt.UserRole, row['diary_id'])
                self.ui.diaryTitleList.addItem(item)
        else:
            showMessageBox("搜索结果", results)

    def showDiaryDetails(self, item):
        diaryId = item.data(Qt.UserRole)
        self.diaryWindow = DiaryWindow(diaryId)
        self.diaryWindow.show()

    def createDiary(self):
        title = self.ui.newDiaryTitle.text()
        content = self.ui.newDiaryContent.toPlainText()
        success, msg = tour_diary.CreateDiary(title, content)
        showMessageBox("创建结果", msg)


class DiaryWindow(QMainWindow):
    def __init__(self, diary_id, parent=None):
        super().__init__(parent)
        self.ui = Ui_diaryWindows()
        self.ui.setupUi(self)
        self.displayDiary(diary_id)

    def displayDiary(self, diary_id):
        success, content = tour_diary.ShowDiary(diary_id)  # 假设这是获取日记内容的函数
        if success:
            self.ui.diaryContent1.setText(content)  # 假设Ui_diaryWindows有一个textEdit来显示日记内容
            # self.ui.diaryTitle.setText()  # 获取标题
        else:
            showMessageBox("错误", "无法加载日记内容。")


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 启用高DPI缩放
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # 启用高DPI图标
    app = QApplication(sys.argv)
    user_info = UserInfo()  # 创建 UserInfo 实例
    tour_diary = TourDiary(user_info)
    firstWindow = FirstWindow()
    firstWindow.show()
    sys.exit(app.exec_())
