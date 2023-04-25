#會員中心的畫面
from PyQt5 import QtWidgets, QtGui, QtCore
from Widgets.WidgetComponents import LabelComponent, LineEditComponent, ButtonComponent
import SocketServer.ServiceController as ServiceController
import json
from PyQt5.QtGui import QIntValidator
import sys
class MemberWidget(QtWidgets.QWidget):
    def __init__(self, account):
        super().__init__()
        self.setObjectName("MemberWidget")
        layout = QtWidgets.QVBoxLayout()
        header_label = LabelComponent(16, "Member Center")
        self.member_content = MemberContent(account)
        layout.addWidget(header_label)
        layout.addWidget(self.member_content)
        self.setLayout(layout)
    def load(self):
        self.member_content.load()

class MemberContent(QtWidgets.QWidget):
    def __init__(self,account):
        super().__init__()
        self.member_id = ""
        self.account = account
        self.TWD = 0
        self.password = ""
        self.service_controller = ServiceController.ServiceController()
        self.service_controller.member_info({"account":account}).connect(self.refresh_info)  #更新資訊
        self.SendedData = {}

        layout = QtWidgets.QGridLayout()
        #基本資料
        self.id_L = LabelComponent(14,"會員編號: ")
        self.account_L = LabelComponent(14,"帳號: ")
        self.id_C = LabelComponent(14,"")
        self.account_C = LabelComponent(14,"")
        self.TWD_L = LabelComponent(14,"餘額: ")
        self.password_L = LabelComponent(14,"密碼")
        self.TWD_C = LabelComponent(14,"")
        self.password_C = LineEditComponent("",font_size = 12)
        self.password_C.mousePressEvent=self.clear_password_C_label
        #按鈕
        self.Reset_button = ButtonComponent("重設密碼")
        self.Reset_button.clicked.connect(self.change_password)
        self.Money_button = ButtonComponent("加值")
        self.Money_button.clicked.connect(self.input_money)
        self.Del_button = ButtonComponent("刪除帳號")
        self.Del_button.clicked.connect(self.delete_member)
        self.Money_L = LineEditComponent("0",font_size = 12)
        self.Money_L.mousePressEvent=self.clear_Money_L_label
        #美化
        self.Reset_button.setStyleSheet("QPushButton{background-color:#f44336}QPushButton:hover{background-color:#e06666}")
        self.Money_button.setStyleSheet("QPushButton{background-color:#b6d7a8}QPushButton:hover{background-color:#6aa84f}")
        self.Del_button.setStyleSheet("QPushButton{background-color:#c27ba0}QPushButton:hover{background-color:#741b47}")
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
        layout.setRowStretch(6, 1)
        layout.setRowStretch(7, 10)
        layout.addWidget(self.id_L,1,1,1,1)
        layout.addWidget(self.account_L,2,1,1,1)
        layout.addWidget(self.TWD_L,3,1,1,1)
        layout.addWidget(self.password_L,4,1,1,1)
        layout.addWidget(self.id_C,1,2,1,2)
        layout.addWidget(self.account_C,2,2,1,1)
        layout.addWidget(self.TWD_C,3,2,1,1)
        layout.addWidget(self.password_C,4,2,1,1)
        layout.addWidget(self.Reset_button,5,1,1,1)
        layout.addWidget(self.Del_button,5,2,1,1)
        layout.addWidget(self.Money_L,6,1,1,1)
        layout.addWidget(self.Money_button,6,2,1,1)
        self.setLayout(layout)

    def load(self):
        self.service_controller.member_info({"account":self.account}).connect(self.refresh_info)  #更新資訊
 
    def refresh_info(self,data): #從資料庫取得的資料進行資訊更新
        data = json.loads(data)
        self.member_id = data['parameters']["member_id"]
        self.TWD = data['parameters']["TWD"]
        self.password = data['parameters']["password"]
        self.id_C.setText(str(self.member_id))
        self.account_C.setText(self.account)
        self.TWD_C.setText(str(round(self.TWD , 2))) # 解決小數點溢位問題
        self.password_C.setText(str(self.password))
    #點擊儲值
    def input_money(self,event):
        self.service_controller.insert_money({"account":self.account,"amount":-1*float(self.Money_L.text())}).connect(self.load)
    #點擊更變密碼
    def change_password(self,event):
        self.service_controller.change_password({"account":self.account,"password":self.password_C.text()}).connect(self.load)
    #點擊刪除帳號
    def delete_member(self,event):
        self.service_controller.delete({"account":self.account}).connect(self.load)
        sys.exit()  # 關閉程式
    #點擊刪除金額
    def clear_Money_L_label(self,event):
        self.Money_L.clear()
    #點擊刪除密碼
    def clear_password_C_label(self,event):
        self.password_C.clear()