import os
import sys

import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QMainWindow, QMenu
from PyQt5.QtWidgets import QListWidgetItem

from diary import Ui_diaryWindows
from first_windows import Ui_first_windows
from main_windows import Ui_MainWindow
from sign_in_windows import Ui_sign_in_windows
from sign_up_windows import Ui_sign_up_windows_2
from tour_diary import TourDiary
from user_info import UserInfo


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
        self.ui = Ui_MainWindow()  # 假设已经从其他地方导入了 Ui_MainWindow
        self.ui.setupUi(self)

        self.searchType = 0

        self.ui.searchButton.clicked.connect(self.searchDiary)
        self.ui.createButton.clicked.connect(self.createDiary)
        self.ui.diaryTitleList.itemClicked.connect(self.showDiaryDetails)
        self.ui.searchSelect.currentIndexChanged.connect(self.selection_change)
        self.ui.diaryTitleList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.diaryTitleList.customContextMenuRequested.connect(self.openContextMenu)

    def keyPressEvent(self, event):
        if (self.ui.tabWidget.currentIndex() == 1 and
                self.ui.tabWidget_3.currentIndex() == 0):
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.searchDiary()

    def selection_change(self, index):
        self.searchType = index

    def searchDiary(self):
        keyword = self.ui.searchKeyword.text()
        if self.searchType == 0:
            self.success, self.results = tour_diary.SearchDiary(keyword)
        elif self.searchType == 1:
            self.success, self.results = tour_diary.SearchDiary(keyword, 1)
        elif self.searchType == 2:
            self.success, self.results = tour_diary.SearchDiary(keyword, 2)

        if self.success:
            self.ui.diaryTitleList.clear()
            for index, row in self.results.iterrows():
                item = QListWidgetItem(f"{tour_diary.DiaryName(int(row['diary_id']))}")
                item.setData(Qt.UserRole, row['diary_id'])
                self.ui.diaryTitleList.addItem(item)
        else:
            showMessageBox("删除结果", self.results)

    def showDiaryDetails(self, item):
        diaryId = item.data(Qt.UserRole)
        self.diaryWindow = DiaryWindow(diaryId)
        self.diaryWindow.show()

    def createDiary(self):
        title = self.ui.newDiaryTitle.text()
        content = self.ui.newDiaryContent.toPlainText()
        success, msg = tour_diary.CreateDiary(title, content)
        showMessageBox("创建结果", msg)

    def openContextMenu(self, position):
        menu = QMenu()
        deleteAction = menu.addAction("删除日记")
        deleteAction.triggered.connect(self.deleteItem)
        menu.exec_(self.ui.diaryTitleList.viewport().mapToGlobal(position))

    def deleteItem(self):
        current_item = self.ui.diaryTitleList.currentItem()
        if current_item:
            diaryId = current_item.data(Qt.UserRole)
            success, msg = tour_diary.DeleteDiary(diaryId)
            if success:  # 假设 DeleteDiary 正确实现了
                row = self.ui.diaryTitleList.row(current_item)
                self.ui.diaryTitleList.takeItem(row)
                showMessageBox("删除结果", msg)
            else:
                showMessageBox("删除结果", msg)



class DiaryWindow(QMainWindow):
    def __init__(self, diary_id, parent=None):
        super().__init__(parent)
        self.ui = Ui_diaryWindows()
        self.ui.setupUi(self)
        self.displayDiary(diary_id)

    def displayDiary(self, diary_id):
        success, content = tour_diary.ShowDiary(diary_id)  # 假设这是获取日记内容的函数
        if success:
            max_length = 350  # 假设diaryContent1可以容纳300个字符
            if len(content) > max_length:
                part1 = content[:max_length]
                part2 = content[max_length:]
                self.ui.diaryContent1.setText(part1)
                self.ui.diaryContent2.setText(part2)
            else:
                self.ui.diaryContent1.setText(content)
                self.ui.diaryContent2.clear()  # 清空第二个文本框，以防之前有内容

            self.ui.diaryTitle.setText(tour_diary.DiaryName(int(diary_id)))  # 获取标题
            self.ui.diaryAuthor.setText("——" + tour_diary.AuthorName(int(diary_id)))
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
