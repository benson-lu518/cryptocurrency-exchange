import SocketServer.client as client
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
import json
import time
host = "127.0.0.1"
port = 20001

class ServiceController(QtCore.QThread):
    def __init__(self):
        super().__init__()
        
    def insert_money(self,parameters):
        self.insert_moneythread = self.InsertMoney(parameters)
        self.insert_moneythread.start()
        return self.insert_moneythread.return_sig
    def login(self,parameters):
        self.loginthread = self.Login(parameters)
        self.loginthread.start()
        return self.loginthread.return_sig
    def regist(self,parameters):
        self.registthread = self.Regist(parameters)
        self.registthread.start()
        return self.registthread.return_sig
    def member_info(self,parameters):
        self.memberthread = self.MemberInfo(parameters)
        self.memberthread.start()
        return self.memberthread.return_sig
    def trade_info(self,parameters):
        self.trade_infothread = self.TradeInfo(parameters)
        self.trade_infothread.start()
        return self.trade_infothread.return_sig
    def trade(self,parameters):
        self.tradethread = self.Trade(parameters)
        self.tradethread.start()
        return self.tradethread.return_sig
    #new
    def delete(self,parameters):
        self.deletethread = self.Delete(parameters)
        self.deletethread.start()
        return self.deletethread.return_sig

    def change_password(self,parameters):
        self.passwordthread = self.Password(parameters)
        self.passwordthread.start()
        return self.passwordthread.return_sig

    def calculate_income(self,parameters):
        self.calculate_incomethread = self.Calculate_Income(parameters)
        self.calculate_incomethread.start()
        return self.calculate_incomethread.return_sig
    #new end
    class Login(QtCore.QThread):
        return_sig = pyqtSignal(str)
        def __init__(self,parameters):
            super().__init__()
            self.client = client.SocketClient(host, port)
            self.parameters = parameters
        def run(self):
            self.client.send_command("login",self.parameters)
            if self.client.wait_response():
                self.return_sig.emit(json.dumps(self.client.last_response))
    class Regist(QtCore.QThread):
        return_sig = pyqtSignal(str)
        def __init__(self,parameters):
            super().__init__()
            self.client = client.SocketClient(host, port)
            self.parameters = parameters
        def run(self):
            self.client.send_command("regist",self.parameters)
            if self.client.wait_response():
                self.return_sig.emit(json.dumps(self.client.last_response))
    class MemberInfo(QtCore.QThread):
        return_sig = pyqtSignal(str)
        def __init__(self,parameters):
            super().__init__()
            self.client = client.SocketClient(host, port)
            self.parameters = parameters
        def run(self):
            self.client.send_command("member_info",self.parameters)
            if self.client.wait_response():
                self.return_sig.emit(json.dumps(self.client.last_response))
    class TradeInfo(QtCore.QThread):
        return_sig = pyqtSignal(str)
        def __init__(self,parameters):
            super().__init__()
            self.client = client.SocketClient(host, port)
            self.parameters = parameters
        def run(self):
            self.client.send_command("get_member_trades",self.parameters)
            if self.client.wait_response():
                self.return_sig.emit(json.dumps(self.client.last_response))

    class Trade(QtCore.QThread):
        return_sig = pyqtSignal(str)
        def __init__(self,parameters):
            super().__init__()
            self.client = client.SocketClient(host, port)
            self.parameters = parameters
        def run(self):
            self.client.send_command("insert_a_trade",self.parameters)
            if self.client.wait_response():
                self.return_sig.emit(json.dumps(self.client.last_response))
    class InsertMoney(QtCore.QThread):
        return_sig = pyqtSignal(str)
        def __init__(self,parameters):
            super().__init__()
            self.client = client.SocketClient(host, port)
            self.parameters = parameters
        def run(self):
            self.client.send_command("update_member_money",self.parameters)
            if self.client.wait_response():
                self.return_sig.emit(json.dumps(self.client.last_response))
    #new
    class Password(QtCore.QThread):
        return_sig = pyqtSignal(str)
        def __init__(self,parameters):
            super().__init__()
            self.client = client.SocketClient(host, port)
            self.parameters = parameters
        def run(self):
            self.client.send_command("change_member_password",self.parameters)
            if self.client.wait_response():
                self.return_sig.emit(json.dumps(self.client.last_response))

    class Delete(QtCore.QThread):
        return_sig = pyqtSignal(str)
        def __init__(self,parameters):
            super().__init__()
            self.client = client.SocketClient(host, port)
            self.parameters = parameters
        def run(self):
            self.client.send_command("delete",self.parameters)
            if self.client.wait_response():
                self.return_sig.emit(json.dumps(self.client.last_response))
                
    class Calculate_Income(QtCore.QThread):
        return_sig = pyqtSignal(str)
        def __init__(self,parameters):
            super().__init__()
            self.client = client.SocketClient(host, port)
            self.parameters = parameters
        def run(self):
            self.client.send_command("get_member_income",self.parameters)
            if self.client.wait_response():
                self.return_sig.emit(json.dumps(self.client.last_response))
    #new end
