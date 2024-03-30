from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import QEvent


class OwnMessageBox(QMessageBox):
    def __init__(self, *args, **kwargs):
        super(OwnMessageBox, self).__init__(*args, **kwargs)

    def showEvent(self, event):
        # 在这里设置对话框的理想大小
        self.setFixedSize(1000, 100)  # 设定固定大小
        super(OwnMessageBox, self).showEvent(event)
