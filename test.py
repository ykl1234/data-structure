from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QTextEdit, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置主窗口的标题和大小
        self.setWindowTitle("PyQt5 Text Update Example")
        self.setGeometry(100, 100, 400, 200)

        # 创建一个 QWidget 和 QVBoxLayout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建 QLineEdit
        self.lineEdit = QLineEdit("初始文本", self)
        layout.addWidget(self.lineEdit)

        # 创建 QTextEdit
        self.textEdit = QTextEdit("初始文本", self)
        layout.addWidget(self.textEdit)

        # 创建一个按钮，点击后更新文本
        update_button = QPushButton("更新文本", self)
        update_button.clicked.connect(self.update_texts)
        layout.addWidget(update_button)

    def update_texts(self):
        # 更新 QLineEdit 和 QTextEdit 的内容
        self.lineEdit.setText("更新后的 QLineEdit 文本")
        self.textEdit.setPlainText("更新后的 QTextEdit 文本")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
