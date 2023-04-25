#登入畫面
from PyQt5 import QtWidgets, QtGui, QtCore
from Widgets.WidgetComponents import LabelComponent, LineEditComponent, ButtonComponent
import SocketServer.ServiceController as ServiceController
import json
from PyQt5.QtGui import QIntValidator
import time
class UserWidget(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal(str) #控制畫面跳轉的signal
    def __init__(self):
        super().__init__()
        self.service_controller = ServiceController.ServiceController()
        self.setObjectName("UserWidget")
       
        layout = QtWidgets.QGridLayout()
        header_label = LabelComponent(16, "登入\註冊")
        account_label = LabelComponent(14, "帳號")
        password_label = LabelComponent(14, "密碼")
        self.show_label = LabelComponent(14, "")
        self.account_editor_label = LineEditComponent("帳號",font_size = 12)
        self.password_editor_label = LineEditComponent("密碼",font_size = 12)
        self.Login_button = ButtonComponent("登入")
        self.Regist_button = ButtonComponent("註冊")

        #按鈕功能
        self.account_editor_label.mousePressEvent = self.clear_account_editor_label_content
        self.password_editor_label.mousePressEvent = self.clear_password_editor_label_content
        self.Login_button.clicked.connect(self.query)
        self.Regist_button.clicked.connect(self.regist)

        #美化
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            """
                QWidget#UserWidget{{
                    color: white;
                    border-image: url(\"{}\");
                }};
            """.format("./resources/bg3.jpg")
        )     
        self.setWindowOpacity(0.9) # 透明度
        self.Login_button.setStyleSheet("QPushButton{background-color:#f44336}QPushButton:hover{background-color:#cc0000}")
        self.Regist_button.setStyleSheet("QPushButton{background-color:#b4a7d6}QPushButton:hover{background-color:#674ea7}")
        header_label.setStyleSheet("color: white")
        account_label.setStyleSheet("color: white")
        password_label.setStyleSheet("color: white")
        self.show_label.setStyleSheet("color: white")

        #排版
        layout.addWidget(header_label,1,1,1,1)
        layout.addWidget(self.show_label,2,3,2,1)
        layout.addWidget(account_label,2,1,1,1)
        layout.addWidget(self.account_editor_label,2,2,1,1)
        layout.addWidget(password_label,3,1,1,1)
        layout.addWidget(self.password_editor_label,3,2,1,1)
        layout.addWidget(self.Login_button,4,1,1,1)
        layout.addWidget(self.Regist_button,4,2,1,1)
        layout.setColumnStretch(0, 10)
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 4)
        layout.setColumnStretch(3, 10)
        layout.setRowStretch(0, 10)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 1)
        layout.setRowStretch(3, 1)
        layout.setRowStretch(4, 1)
        layout.setRowStretch(5, 10)
        self.setLayout(layout)

    def load(self):
        print("User_Widget")

    #按鈕功能
    def clear_account_editor_label_content(self, event):
        self.account_editor_label.clear()

    def clear_password_editor_label_content(self, event):
        self.password_editor_label.clear()

    def query(self):#嘗試登入
        self.service_controller.login({"account":self.account_editor_label.text(),"password":self.password_editor_label.text()}).connect(self.process_Qresult)

    def process_Qresult(self,result): #從資料庫解析登入的成功與否
        result = json.loads(result)
        print(result)
        if result["status"] == "OK":
            self.show_label.setText("登入成功")
            self.switch_window.emit(self.account_editor_label.text())
        else:
            self.show_label.setText("登入失敗，請檢查帳號密碼")
    def regist(self,event):
        self.switch_window.emit("")
