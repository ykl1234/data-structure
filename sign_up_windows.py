# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sign_up_windows.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_sign_up_windows_2(object):
    def setupUi(self, sign_up_windows_2):
        sign_up_windows_2.setObjectName("sign_up_windows_2")
        sign_up_windows_2.resize(496, 311)
        self.layoutWidget = QtWidgets.QWidget(sign_up_windows_2)
        self.layoutWidget.setGeometry(QtCore.QRect(90, 70, 321, 171))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setStyleSheet("color:white;\n"
"font-family: 微软雅黑;")
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit.setStyleSheet("font: 9pt \"微软雅黑\";")
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_2.addWidget(self.lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setStyleSheet("color: white;\n"
"font-family: 微软雅黑;")
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.sign_up_windows = QtWidgets.QLineEdit(self.layoutWidget)
        self.sign_up_windows.setStyleSheet("size: 9pt;")
        self.sign_up_windows.setEchoMode(QtWidgets.QLineEdit.Password)
        self.sign_up_windows.setObjectName("sign_up_windows")
        self.horizontalLayout_3.addWidget(self.sign_up_windows)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton.setStyleSheet("font: 9pt \"微软雅黑\";")
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_2.setStyleSheet("font: 9pt \"微软雅黑\";")
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.label_3 = QtWidgets.QLabel(sign_up_windows_2)
        self.label_3.setGeometry(QtCore.QRect(0, 0, 491, 311))
        self.label_3.setText("")
        self.label_3.setPixmap(QtGui.QPixmap("images/background.png"))
        self.label_3.setScaledContents(True)
        self.label_3.setObjectName("label_3")
        self.label_3.raise_()
        self.layoutWidget.raise_()
        self.label.setBuddy(self.lineEdit)
        self.label_2.setBuddy(self.sign_up_windows)

        self.retranslateUi(sign_up_windows_2)
        QtCore.QMetaObject.connectSlotsByName(sign_up_windows_2)

    def retranslateUi(self, sign_up_windows_2):
        _translate = QtCore.QCoreApplication.translate
        sign_up_windows_2.setWindowTitle(_translate("sign_up_windows_2", "用户注册界面"))
        self.label.setText(_translate("sign_up_windows_2", "请输入用户名"))
        self.label_2.setText(_translate("sign_up_windows_2", "输入密码       "))
        self.pushButton.setText(_translate("sign_up_windows_2", "注册"))
        self.pushButton_2.setText(_translate("sign_up_windows_2", "取消"))
