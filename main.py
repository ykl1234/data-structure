import os
import sys

import pandas as pd
from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QMainWindow, QMenu, QFileDialog, QLabel, QWidget, \
    QGraphicsOpacityEffect
from PyQt5.QtWidgets import QListWidgetItem
from skimage import io

from diary import Ui_diaryWindows
from first_windows import Ui_first_windows
from gg3 import find_shortest_path, create_graph, plot_graph, load_data
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


def showOptionMessageBox(title, message):
    msgBox = QMessageBox()
    msgBox.setWindowTitle(title)
    msgBox.setText(message)

    # 定义按钮
    button_confirm = msgBox.addButton("确认", QMessageBox.AcceptRole)
    button_cancel = msgBox.addButton("取消", QMessageBox.RejectRole)

    # 设置 QMessageBox 的样式，包括按钮样式
    msgBox.setStyleSheet("""
        QMessageBox { background-color: #ffffff; font-family: 'Microsoft YaHei'; font-size: 9pt; }
        QPushButton { width: 100px; height: 20px; background-color: #262B4B; color: white; font-family: 'Microsoft YaHei'; }
    """)
    msgBox.exec_()

    # 判断哪个按钮被点击并返回对应的标识
    if msgBox.clickedButton() == button_confirm:
        return "confirm"
    elif msgBox.clickedButton() == button_cancel:
        return "cancel"


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
            self.firstwindow = FirstWindow()
            self.firstwindow.show()
            self.close()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()  # 假设已经从其他地方导入了 Ui_MainWindow
        self.ui.setupUi(self)
        self.images = []
        self.searchType = 0
        self.image_labels = [self.ui.picture1, self.ui.picture2, self.ui.picture3, self.ui.picture4]
        self.current_image_index = 0
        self.ui.showMyDiary.clicked.connect(self.showOwnDiary)
        self.ui.searchButton.clicked.connect(self.searchDiary)
        self.ui.createButton.clicked.connect(self.createDiary)
        self.ui.deleteUserData.clicked.connect(self.deleteUser)
        self.ui.addImage.clicked.connect(self.addImage)
        self.ui.deletePicture.clicked.connect(self.deleteImage)
        self.ui.diaryTitleList.itemClicked.connect(self.showDiaryDetails)
        self.ui.myDiaryTitleList.itemClicked.connect(self.showDiaryDetails)
        self.ui.searchSelect.currentIndexChanged.connect(self.selection_change)
        self.ui.diaryTitleList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.diaryTitleList.customContextMenuRequested.connect(self.openContextMenu)
        self.updateDeletePictureButtonVisibility()
        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)
        # 路径推荐模块
        self.populate_combo_box()
        self.ui.school.currentIndexChanged.connect(lambda: self.combo_box_changed('source'))
        self.ui.school.currentIndexChanged.connect(lambda: self.combo_box_changed('des'))
        self.ui.searchRoad.clicked.connect(self.searchRoad)
        # 首页模块
        self.showFirst()

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
            showMessageBox("搜索结果", self.results)
            self.ui.diaryTitleList.clear()

    def showDiaryDetails(self, item):
        diaryId = item.data(Qt.UserRole)
        self.diaryWindow = DiaryWindow(diaryId)
        self.diaryWindow.show()

    def createDiary(self):
        title = self.ui.newDiaryTitle.text()
        content = self.ui.newDiaryContent.toPlainText()
        success, msg = tour_diary.CreateDiary(title, content, None, self.images)
        showMessageBox("创建结果", msg)
        self.ui.newDiaryTitle.clear()
        self.ui.newDiaryContent.clear()

        # 清空图片标签和图片列表
        for i in range(len(self.image_labels)):
            self.image_labels[i].clear()
        self.images.clear()
        self.current_image_index = 0

        # 将添加图片按钮归位
        self.ui.addImage.move(20, 260)
        # 更新删除图片按钮可见性
        self.updateDeletePictureButtonVisibility()

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

    def deleteUser(self):
        # 显示消息框并接收返回值
        user_choice = showOptionMessageBox("注销选择", "是否注销该账号")
        if user_choice == "confirm":
            uid = user_info.GetCurrentUser()
            success, msg = user_info.DeleteUserData(uid)
            if uid != -1:
                # 调用 UserInfo 类的 deleteUser 方法
                user_info.DeleteUserData(uid)
                showMessageBox("删除结果", msg)
                self.close()
                self.firstWindows = FirstWindow()
                self.firstWindows.show()
                self.close()
            else:
                showMessageBox("删除结果", msg)

    def addImage(self):
        if self.current_image_index >= len(self.image_labels):
            showMessageBox("图片添加失败", "图片数量已达到最大")
            return  # 如果所有标签都已经填满，则不再添加图片

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "",
                                                   "Images (*.png *.xpm *.jpg *.jpeg *.bmp);;All Files (*)",
                                                   options=options)

        if file_path:
            # 传回来一个图片文件的路径
            self.images.append(io.imread(file_path))
            pixmap = QPixmap(file_path)
            self.image_labels[self.current_image_index].setPixmap(pixmap)
            self.image_labels[self.current_image_index].setScaledContents(True)

            # 更新当前图片标签索引
            self.current_image_index += 1

            # 右移添加图片按钮
            self.ui.addImage.move(self.ui.addImage.x() + 71, self.ui.addImage.y())
            self.ui.deletePicture.move(self.image_labels[self.current_image_index - 1].x(), self.ui.deletePicture.y())
        # 更新删除图片按钮可见性
        self.updateDeletePictureButtonVisibility()

    def showOwnDiary(self):
        user_id = user_info.GetCurrentUser()
        success, results = tour_diary.UserDiary(user_id)
        if success:
            for index in range(len(results)):
                diary_id = results[index]  # 怎么得到日记id
                item = QListWidgetItem(f"{tour_diary.DiaryName(int(diary_id))}")
                item.setData(Qt.UserRole, diary_id)
                self.ui.myDiaryTitleList.addItem(item)
        else:
            showMessageBox("查看结果", results)

    def on_tab_changed(self, index):
        print(f"Tab changed to index: {index}")
        if index == 3:  # 检查是否是第四个选项卡
            self.showOwnDiary()

    def updateDeletePictureButtonVisibility(self):
        if self.current_image_index == 0:
            self.ui.deletePicture.hide()
        else:
            self.ui.deletePicture.show()

    def deleteImage(self):
        if self.current_image_index > 0:
            # 删除最后一张图片
            self.current_image_index -= 1
            self.image_labels[self.current_image_index].clear()
            self.images.pop()

            # 左移添加图片按钮
            self.ui.addImage.move(self.ui.addImage.x() - 71, self.ui.addImage.y())
            self.ui.deletePicture.move(self.ui.deletePicture.x() - 71, self.ui.deletePicture.y())
        # 更新删除图片按钮可见性
        self.updateDeletePictureButtonVisibility()

        # 路径推荐模块

    def populate_combo_box(self):
        # 指定目录
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "id_to_name")

        # 清空 ComboBox
        self.ui.school.clear()

        # 获取所有 CSV 文件
        csv_files = [f[:-15] for f in os.listdir(directory) if f.endswith('.csv')]

        # 将文件名添加到 ComboBox 中
        self.ui.school.addItems(csv_files)
        self.ui.school.setCurrentIndex(-1)

    def combo_box_changed(self, list_name):
        print("combo_box_changed called")  # 调试输出，确认方法被调用

        # 获取当前选中的文件名
        selected_file = self.ui.school.currentText()
        if not selected_file:
            return

        print(f"Selected file: {selected_file}")

        # 指定目录
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "id_to_name")

        # 构建文件路径
        file_path = os.path.join(directory, f"{selected_file}_id_to_name.csv")

        # 读取 CSV 文件
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return

        # 根据传入的列表项名称清空相应的列表
        list_widget = getattr(self.ui, list_name)
        list_widget.clear()

        # 添加 CSV 文件中的地点名称到 QListWidget
        for name in df['名称']:
            list_widget.addItem(name)
        list_widget.setCurrentIndex(-1)

    def searchRoad(self):
        university_name = self.ui.school.currentText()
        start_node = self.ui.source.currentText()
        end_node = self.ui.des.currentText()
        edges_data, id_to_name = load_data(university_name)
        G = create_graph(edges_data, id_to_name)
        path, path_length = find_shortest_path(G, start_node, end_node)
        print(f"The shortest path is {path} with a distance of {path_length}")
        plot_graph(G, path, university_name)
        showMessageBox("路径结果", f"The shortest path is {path} with a distance of {path_length}")

    # 首页
    def showFirst(self):
        # 图片路径和文字内容列表（替换为本地图片路径和对应文字）
        self.images = ["images/donk.jpg", "images/th.jpg", "images/donk.jpg", "images/th.jpg"]
        self.texts = ["First Image Text", "Second Image Text", "Third Image Text", "Fourth Image Text"]
        self.current_index = 0

        self.set_content(self.current_index)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_content)
        self.timer.start(8000)

    def set_content(self, index):
        pixmap = QPixmap(self.images[index])
        self.ui.tempPic.setPixmap(pixmap)
        self.ui.tempPic.setScaledContents(True)

        self.ui.tempText.setText(self.texts[index])
        self.ui.tempText.setAlignment(Qt.AlignCenter)

        # 设置文字渐变效果
        self.text_opacity_effect = QGraphicsOpacityEffect()
        self.ui.tempText.setGraphicsEffect(self.text_opacity_effect)
        self.fade_animation_in_text = QPropertyAnimation(self.text_opacity_effect, b"opacity")
        self.fade_animation_in_text.setDuration(3000)
        self.fade_animation_in_text.setStartValue(0.0)
        self.fade_animation_in_text.setEndValue(1.0)
        self.fade_animation_in_text.setEasingCurve(QEasingCurve.OutCubic)

        # 创建图片渐变效果，从左端进入
        self.fade_animation_in_image = QPropertyAnimation(self.ui.tempPic, b"geometry")
        self.fade_animation_in_image.setDuration(3000)
        self.fade_animation_in_image.setStartValue(
            QRect(-self.ui.tempPic.width(), 0, self.ui.tempPic.width(), self.ui.tempPic.height()))
        self.fade_animation_in_image.setEndValue(QRect(0, 0, self.ui.tempPic.width(), self.ui.tempPic.height()))
        self.fade_animation_in_image.setEasingCurve(QEasingCurve.OutCubic)

        # 启动渐变效果
        self.fade_animation_in_image.start()
        self.fade_animation_in_text.start()

    def next_content(self):
        # 创建图片渐变效果，从右端离开
        self.fade_animation_out_image = QPropertyAnimation(self.ui.tempPic, b"geometry")
        self.fade_animation_out_image.setDuration(3000)
        self.fade_animation_out_image.setStartValue(QRect(0, 0, self.ui.tempPic.width(), self.ui.tempPic.height()))
        self.fade_animation_out_image.setEndValue(
            QRect(self.width(), 0, self.ui.tempPic.width(), self.ui.tempPic.height()))
        self.fade_animation_out_image.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation_out_image.start()

        # 创建文字渐变效果，从不透明到透明
        self.text_opacity_effect = QGraphicsOpacityEffect()
        self.ui.tempText.setGraphicsEffect(self.text_opacity_effect)
        self.fade_animation_out_text = QPropertyAnimation(self.text_opacity_effect, b"opacity")
        self.fade_animation_out_text.setDuration(3000)
        self.fade_animation_out_text.setStartValue(1.0)
        self.fade_animation_out_text.setEndValue(0.0)
        self.fade_animation_out_text.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation_out_text.start()

        # 延迟一段时间后，切换到下一张图片和文字并启动左端进入的渐变效果
        QTimer.singleShot(3000, lambda: self.set_content((self.current_index + 1) % len(self.images)))
        self.current_index = (self.current_index + 1) % len(self.images)


class DiaryWindow(QMainWindow):
    def __init__(self, diary_id, parent=None):
        super().__init__(parent)
        self.ui = Ui_diaryWindows()
        self.ui.setupUi(self)
        self.image_labels = [self.ui.pic1, self.ui.pic2, self.ui.pic3, self.ui.pic4]
        self.displayDiary(diary_id)
        self.ui.likeButton.clicked.connect(self.likeDiary)
        # 点赞
        self.ui.likeButton.setStyleSheet("background: transparent; border: none;")
        self.update_like_button_style(diary_id)
        self.ui.likeButton.clicked.connect(self.likeDiary)

    def displayDiary(self, diary_id):
        success, content = tour_diary.ShowDiary(diary_id)
        if success:
            tour_diary.ReadDiary(diary_id)
            self.ui.diaryContent1.setText(content)
            self.ui.diaryTitle.setText(tour_diary.DiaryName(int(diary_id)))
            self.ui.diaryAuthor.setText("——" + tour_diary.AuthorName(int(diary_id)))

            img_list = tour_diary.GetImageList(int(diary_id))
            print(f"Image list: {img_list}")  # 输出图片列表，以便调试

            if img_list:
                for current_image_index, img_path in enumerate(img_list):
                    if current_image_index < len(self.image_labels):
                        print(f"Loading image {current_image_index + 1}: {img_path}")  # 输出正在加载的图片路径，以便调试

                        pixmap = QPixmap(img_path)
                        if not pixmap.isNull():  # 检查 pixmap 是否有效
                            self.image_labels[current_image_index].setPixmap(pixmap)
                            self.image_labels[current_image_index].setScaledContents(True)
                        else:
                            print(f"Failed to load image: {img_path}")  # 输出加载失败的图片路径，以便调试
                    else:
                        print(f"Too many images: {img_path}")  # 输出图片过多的警告信息，以便调试
            else:
                print("No images found")  # 输出未找到图片的警告信息，以便调试
        else:
            showMessageBox("错误", "无法加载日记内容。")

    # 点赞

    def likeDiary(self, diary_id):
        tour_diary.LikeDiary(diary_id)
        self.update_like_button_style(diary_id)

    def update_like_button_style(self, diary_id):
        if tour_diary.LikedDiary(diary_id):
            # 样式 1
            self.ui.likeButton.setIcon(QIcon("images/like.png"))
        else:
            # 样式 2
            self.ui.likeButton.setIcon(QIcon("images/newlike.png"))


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 启用高DPI缩放
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # 启用高DPI图标
    app = QApplication(sys.argv)
    user_info = UserInfo()  # 创建 UserInfo 实例
    tour_diary = TourDiary(user_info)
    firstWindow = FirstWindow()
    firstWindow.show()
    sys.exit(app.exec_())
