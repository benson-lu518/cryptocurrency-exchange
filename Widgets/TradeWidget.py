from datetime import datetime, timedelta, date
from itertools import cycle
import os
import sys
import traceback
from PyQt5 import QtWidgets, QtGui, QtCore
import json
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Widgets.WidgetComponents import LabelComponent, LineEditComponent, ButtonComponent

import numpy as np
import SocketServer.ServiceController as ServiceController

import pyqtgraph as pg
import requests
import requests_cache
from PyQt5.QtGui import QDoubleValidator

CRYPTOCOMPARE_API_KEY = 'f2208401985d383cdf9d265ef9d90eea44bf33d8f7f6c4b192cf212448290f3b'
DEFAULT_BASE_CURRENCY = 'TWD'

AVAILABLE_CRYPTO_CURRENCIES = ['BTC', 'ETH', 'LTC', 'EOS', 'XRP', 'BCH' ] #
CURRENCY_IN_CHINESE = {'BTC':"比特幣",'ETH':"乙太幣",'EOS':"柚子幣","LTC":"萊特幣",'XRP':'瑞波幣','BCH':'比特幣現金'}
DEFAULT_DISPLAY_CURRENCIES = ['BTC', 'ETH', 'LTC']

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    progress = pyqtSignal(int)
    data = pyqtSignal(dict)
    cancel = pyqtSignal()

class UpdateWorker(QRunnable):
    signals = WorkerSignals()
    def __init__(self, base_currency):
        super(UpdateWorker, self).__init__()
        self.is_interrupted = False
        self.base_currency = base_currency
        self.signals.cancel.connect(self.cancel)

    @pyqtSlot()
    def run(self):
        auth_header = {
            'Apikey': CRYPTOCOMPARE_API_KEY
        }
        try:
            value = {}
            for n, crypto in enumerate(AVAILABLE_CRYPTO_CURRENCIES, 1):
                url = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms={fsym}&tsyms=TWD'
                r = requests.get(
                    url.format(**{
                        'fsym': crypto,
                        'format': 'json',
                    }),
                    headers=auth_header,
                )
                r.raise_for_status()
                value[crypto] = r.json().get(crypto)

                if self.is_interrupted:
                    return

            

        except Exception as e:
            self.signals.error.emit((e, traceback.format_exc()))
            return

        self.signals.data.emit(value)
        self.signals.finished.emit()

    def cancel(self):
        self.is_interrupted = True


class TradeWidget(QtWidgets.QWidget):
    def __init__(self,account):
        super().__init__()
        
        self.service_controller = ServiceController.ServiceController()
        
        self.currentPrice = {}
        self.account = account
        layout = QGridLayout()
        self.setObjectName("trade_widget")
        self.currencyList = QComboBox()
        self.worker = UpdateWorker("TWD")
        self.threadpool = QThreadPool()
        self.refresh_historic_rates()
        self.value = dict()
        head_label = LabelComponent(16, "交易系統: ")
        amount_label = LabelComponent(12, "持有數量: ")
        current_label = LabelComponent(12, "現在價格: ")
        oper_lable = LabelComponent(12, "操作數量: ")
        self.ConfirmButton = ButtonComponent("確認")
        self.ConfirmButton.setStyleSheet("QPushButton{background-color:#f44336}QPushButton:hover{background-color:#cc0000}")
        self.SearchButton = ButtonComponent("搜尋")
        self.SearchButton.setStyleSheet("QPushButton{background-color:#6699cc}QPushButton:hover{background-color:#397fc4}")
        self.SearchButton.clicked.connect(self.search)
        self.amount_editor_label = LabelComponent(12,"數量")
        self.show_label = LabelComponent(14,"")
        self.current_editor_label = LabelComponent(12,"價格")
        self.oper_editor_label = LineEditComponent("0",font_size = 12)
        self.user_define_label = LineEditComponent("",font_size = 12)
        self.ConfirmButton.clicked.connect(self.confirm)
        self.radio_button_buy=QtWidgets.QRadioButton('購入')
        self.radio_button_sell=QtWidgets.QRadioButton('出售')
        self.radio_button_buy.toggled.connect(self.radio_button_on_clicked)
        self.radio_button_sell.toggled.connect(self.radio_button_on_clicked)
        self.oper_editor_label.setValidator(QDoubleValidator())
        self.oper_editor_label.mousePressEvent = self.clear_oper_editor_label_content

        

        self.refresh_historic_rates()
        self.worker = False
        layout.addWidget(head_label,1,1,1,2)
        layout.addWidget(self.show_label,1,2,2,2)
        layout.addWidget(self.currencyList,2,1,1,2)
        layout.addWidget(self.user_define_label,2,3,1,1)
        layout.addWidget(self.SearchButton,2,4,1,1)
        layout.addWidget(amount_label,3,1,1,1)
        layout.addWidget(self.amount_editor_label ,3,2,1,1)
        layout.addWidget(current_label,4,1,1,1)
        layout.addWidget(self.current_editor_label,4,2,1,1)
        layout.addWidget(oper_lable,5,1,1,1)
        layout.addWidget(self.oper_editor_label,5,2,1,1)
        layout.addWidget(self.radio_button_buy,6,1,1,1)
        layout.addWidget(self.radio_button_sell,6,2,1,1)
        layout.addWidget(self.ConfirmButton,7,1,1,2)
        self.currencyList.currentIndexChanged.connect(self.combo_box_select_changed)
        layout.setColumnStretch(0, 5)
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 4)
        layout.setColumnStretch(3, 4)
        layout.setColumnStretch(4, 4)
        layout.setColumnStretch(5, 5)
        
        layout.setRowStretch(0, 5)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 1)
        layout.setRowStretch(3, 1)
        layout.setRowStretch(4, 1)
        layout.setRowStretch(5, 1)
        layout.setRowStretch(6, 1)
        layout.setRowStretch(7, 1)
        layout.setRowStretch(8, 5)
        self.setLayout(layout)
        

    def radio_button_on_clicked(self):
        selected_button = self.sender()
        

    def refresh_historic_rates(self):
        
        if self.worker:
            self.worker.signals.cancel.emit()

        self.worker = UpdateWorker("TWD")
        self.worker.signals.data.connect(self.result_data_callback)
        self.worker.signals.finished.connect(self.refresh_finished)
        self.worker.signals.error.connect(self.notify_error)
        self.threadpool.start(self.worker)

    def clear_oper_editor_label_content(self, event):
        self.oper_editor_label.clear()

    def update_amount_editor_label(self,result):
        result = json.loads(result)
        Sum = 0.0
        if  result["status"] == "OK":
            if self.currencyList.currentText() != "自訂":
                for trades in result["parameters"]:
                    if trades["info"]["currency"] == self.currencyList.currentText():
                        Sum += trades["info"]["amount"]
                    if self.currencyList.findText(trades["info"]["currency"]) == -1:
                        self.currencyList.addItem(trades["info"]["currency"])
                    if self.currencyList.currentText() not in AVAILABLE_CRYPTO_CURRENCIES:
                        AVAILABLE_CRYPTO_CURRENCIES.append(trades["info"]["currency"])
                        self.refresh_historic_rates()
                self.amount_editor_label.setText(str(Sum)) 
        else:
            self.amount_editor_label.setText("0")

    def combo_box_select_changed(self, index):
        if self.currencyList.currentText() != "自訂":
            self.ConfirmButton.setEnabled(True)
            try:
                self.current_editor_label.setText(str(self.value[self.currencyList.currentText()]["TWD"]))
            except:
                pass
            self.service_controller.trade_info({"account":self.account}).connect(self.update_amount_editor_label)
            self.user_define_label.setEnabled(False)
            self.SearchButton.setEnabled(False)
        else:
            self.ConfirmButton.setEnabled(False)
            self.user_define_label.setEnabled(True)
            self.SearchButton.setEnabled(True)
            

                
    def result_data_callback(self, value):
        self.value = value
        self.currentPrice = value
        for key, price in self.value.items():
            if price  == None:
                try:
                    AVAILABLE_CRYPTO_CURRENCIES.remove(key)
                except:
                    pass
            else:
                if self.currencyList.findText(key) == -1:
                    self.currencyList.addItem(key)
        try:
            self.current_editor_label.setText(str(self.value[self.currencyList.currentText()]["TWD"]))
        except Exception as e:
            print(e)
    def refresh_finished(self):
        self.worker = False
        if self.currencyList.findText("自訂") == -1:
            self.currencyList.addItem("自訂")
        if self.currencyList.currentText() == "自訂":
            if  self.value[self.user_define_label.text()] != None:
                self.show_label.setText("搜尋完畢")
                self.current_editor_label.setText(str(self.value[self.user_define_label.text()]["TWD"]))
                self.ConfirmButton.setEnabled(True)
            else:
                self.show_label.setText("找不到該貨幣")
                self.current_editor_label.setText("NAN")
                self.ConfirmButton.setEnabled(False)
        self.show_label.setText("歡迎使用交易系統")

    def search_result(self,result):
        Sum = 0
        result = json.loads(result)
        if result["status"] == "OK":
            for trades in result["parameters"]:
                        if trades["info"]["currency"] == self.user_define_label.text():
                            Sum += trades["info"]["amount"]
            self.amount_editor_label.setText(str(Sum))
        

    def search(self,event):
        self.show_label.setText("請稍後")
        AVAILABLE_CRYPTO_CURRENCIES.append(self.user_define_label.text())
        self.refresh_historic_rates()
        self.service_controller.trade_info({"account":self.account}).connect(self.search_result)
        
        
    def notify_error(self, error):
        e, tb = error
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(e.__class__.__name__)
        msg.setInformativeText(str(e))
        msg.setDetailedText(tb)
        msg.exec_()

    def confirm(self,event):
        if self.oper_editor_label.text() == "" or self.oper_editor_label.text() == "0":
            self.show_label.setText("請輸入交易數量")
        elif self.radio_button_sell.isChecked():
            if self.currencyList.currentText() != "自訂":
                if float(self.amount_editor_label.text()) < float(self.oper_editor_label.text()):
                    self.show_label.setText("持有數量低於出售")
                else:
                    self.service_controller.trade({"account":self.account,"currency":self.currencyList.currentText(),"amount":float(self.oper_editor_label.text())*-1,"price":float(self.current_editor_label.text())}).connect(self.trade)
            else:
                if float(self.amount_editor_label.text()) < float(self.oper_editor_label.text()):
                    self.show_label.setText("持有數量低於出售")
                else:
                    self.service_controller.trade({"account":self.account,"currency":self.user_define_label.text(),"amount":float(self.oper_editor_label.text())*-1,"price":float(self.current_editor_label.text())}).connect(self.trade)

        elif self.radio_button_buy.isChecked():
            if self.currencyList.currentText() != "自訂":
                self.service_controller.trade({"account":self.account,"currency":self.currencyList.currentText(),"amount":float(self.oper_editor_label.text()),"price":float(self.current_editor_label.text())}).connect(self.trade)
            else:
                self.service_controller.trade({"account":self.account,"currency":self.user_define_label.text(),"amount":float(self.oper_editor_label.text()),"price":float(self.current_editor_label.text())}).connect(self.trade)
        pass
    def trade(self,result):
        result = json.loads(result)
        if result["status"] == "OK":

            self.service_controller.insert_money({"account":result["parameter"]["account"],"amount":(result["parameter"]["amount"]*result["parameter"]["price"])})
            self.service_controller.trade_info({"account":self.account}).connect(self.update_amount_editor_label)
            self.show_label.setText("操作成功")
        else:
            self.show_label.setText("餘額不足")
    
    def load(self):
        self.service_controller.trade_info({"account":self.account}).connect(self.update_amount_editor_label)
        self.oper_editor_label.setText("0")
        
    