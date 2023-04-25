#處理畫面跳轉
from Widgets.UserWidget import UserWidget
from Widgets.MainWidget import MainWidget
from Widgets.RegistWidget import RegistWidget
from PyQt5.QtWidgets import QApplication
from PyQt5 import sip
import sys
import time

#畫面跳轉控制
class Controller:
    def __init__(self):
        pass

    def show_regist(self):
        self.regist = RegistWidget() #註冊介面
        self.regist.setFixedSize(900, 550)
        self.regist.switch_window.connect(self.show_main)
        self.regist.show()

    def show_user(self):
        self.user = UserWidget() #登入介面
        self.user.setFixedSize(850, 500)
        self.user.switch_window.connect(self.show_main)
        self.user.show()

    def show_main(self, text):
        if text == "": #點擊註冊按鈕
            self.user.close()
            self.show_regist()
        elif text=='return': #從註冊介面返回登入介面
            self.regist.close()
            self.show_user()
        else: #無論從註冊或是登入介面過來，text值會是使用者的account
            print("登入成功") 
            self.main = MainWidget(text)
            self.main.setFixedSize(850, 500)
            if(self.regist.isVisible()):
                self.regist.close()
            elif(self.user.isVisible()):
                self.user.close()
            self.main.show()

app = QApplication(sys.argv)
controller = Controller()
controller.show_user()
sys.exit(app.exec_())