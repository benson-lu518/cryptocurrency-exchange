#註冊介面
from PyQt5 import QtWidgets, QtGui, QtCore
from Widgets.WidgetComponents import LabelComponent, LineEditComponent, ButtonComponent
import SocketServer.ServiceController as ServiceController
import json
from PyQt5.QtGui import QIntValidator
import time

class RegistWidget(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal(str) #切換畫面的signal
    def __init__(self):
        super().__init__()
        self.service_controller = ServiceController.ServiceController()
        self.setObjectName("RegistWidget")
        

        layout = QtWidgets.QGridLayout()
        header_label = LabelComponent(16, "註冊")
        account_label = LabelComponent(14, "帳號")
        password_label = LabelComponent(14, "密碼")
        Cpassword_label = LabelComponent(14, "確認密碼")
        self.show_label = LabelComponent(14, "")
        self.account_editor_label = LineEditComponent("帳號",font_size = 12)
        self.password_editor_label = LineEditComponent("密碼",font_size = 12)
        self.Cpassword_editor_label = LineEditComponent("確認密碼",font_size = 12)
        #按鈕
        self.ConfirmButton = ButtonComponent("註冊")
        self.returnButton=ButtonComponent("返回主畫面")
        #按鈕動作
        self.returnButton.clicked.connect(self.user)
        self.account_editor_label.mousePressEvent = self.clear_account_editor_label_content
        self.password_editor_label.mousePressEvent = self.clear_password_editor_label_content
        self.Cpassword_editor_label.mousePressEvent = self.clear_Cpassword_editor_label_content
        self.ConfirmButton.clicked.connect(self.confirm)
        #美化
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            """
                QWidget#RegistWidget{{
                    color: white;
                    border-image: url(\"{}\");
                }};
            """.format("./resources/bg1.jpg")
        )     
        self.setWindowOpacity(0.9) # 透明度
        header_label.setStyleSheet("color: white")
        account_label.setStyleSheet("color: white")
        password_label.setStyleSheet("color: white")
        Cpassword_label.setStyleSheet("color: white")
        self.show_label.setStyleSheet("color: white")
        self.ConfirmButton.setStyleSheet("QPushButton{background-color:#f44336}QPushButton:hover{background-color:#cc0000}")
        self.returnButton.setStyleSheet("QPushButton{background-color:#b4a7d6}QPushButton:hover{background-color:#674ea7}")

        layout.addWidget(header_label,1,1,1,1)
        layout.addWidget(self.show_label,2,3,2,1)
        layout.addWidget(account_label,2,1,1,1)
        layout.addWidget(self.account_editor_label,2,2,1,1)
        layout.addWidget(password_label,3,1,1,1)
        layout.addWidget(self.password_editor_label,3,2,1,1)
        layout.addWidget(Cpassword_label,4,1,1,1)
        layout.addWidget(self.Cpassword_editor_label,4,2,1,1)
        layout.addWidget(self.returnButton,5,1,1,1)
        layout.addWidget(self.ConfirmButton,5,2,1,1)
        #排版
        layout.setColumnStretch(0, 10)
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 4)
        layout.setColumnStretch(3, 10)
        layout.setRowStretch(0, 10)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 1)
        layout.setRowStretch(3, 1)
        layout.setRowStretch(4, 1)
        layout.setRowStretch(5, 1)
        layout.setRowStretch(6, 10)
        self.setLayout(layout)
    #按鈕動作
    def clear_account_editor_label_content(self, event):
        self.account_editor_label.clear()

    def clear_password_editor_label_content(self, event):
        self.password_editor_label.clear()

    def clear_Cpassword_editor_label_content(self, event):
        self.Cpassword_editor_label.clear()

    def user(self,event): #點返回主畫面的按鈕
        self.switch_window.emit("return")

    def confirm(self,event): #檢查帳號密碼
        if self.password_editor_label.text() != self.Cpassword_editor_label.text(): 
            self.show_label.setText("確認密碼與密碼不同")
            return
        elif self.account_editor_label.text() == "return":
            self.show_label.setText("帳號名稱不合法")
            return
        else:
            self.service_controller.regist({"account":self.account_editor_label.text(),"password":self.password_editor_label.text()}).connect(self.process_Cresult) #嘗試註冊

    def process_Cresult(self,result): #從資料庫得到資訊解析是否註冊成功
        result = json.loads(result)
        if result["status"] == "OK":
            self.show_label.setText("註冊成功")
            self.switch_window.emit(self.account_editor_label.text())
        else:
            self.show_label.setText("帳號已存在")

