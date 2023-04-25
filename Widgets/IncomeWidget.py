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
import time

import numpy as np
import SocketServer.ServiceController as ServiceController

import pyqtgraph as pg
import requests
import requests_cache
from PyQt5.QtGui import QDoubleValidator

CRYPTOCOMPARE_API_KEY = 'f2208401985d383cdf9d265ef9d90eea44bf33d8f7f6c4b192cf212448290f3b'

AVAILABLE_CRYPTO_CURRENCIES = ['BTC', 'ETH', 'LTC', 'EOS', 'XRP', 'BCH' ] #

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
            'Apikey': CRYPTOCOMPARE_API_KEY, 'Cache-Control': 'no-cache'
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
                self.signals.progress.emit(int(100 * n / len(AVAILABLE_CRYPTO_CURRENCIES)))
                if self.is_interrupted:
                    return

        except Exception as e:
            self.signals.error.emit((e, traceback.format_exc()))
            return

        self.signals.data.emit(value)
        self.signals.finished.emit()

    def cancel(self):
        self.is_interrupted = True

class InComeWidget(QtWidgets.QWidget):
    def __init__(self, account):
        super().__init__()

        self.service_controller = ServiceController.ServiceController()
        self.own_crypto = {}
        self.account = account
        layout = QtWidgets.QGridLayout()
        header_label = LabelComponent(24, "Income Statement")
        self.loading_label  = LabelComponent(15, "")
        self.loading_label.setStyleSheet("color:red")
        self.income_label = LabelComponent(14, "")
        self.table_widget = Income_table(self.account, self.income_label, self.loading_label)
        self.check = False

        layout.addWidget(header_label, 0, 0, 1, 2)
        layout.addWidget(self.loading_label, 0, 1, 2, 1)
        layout.addWidget(self.income_label, 1, 0 ,1 ,2)
        layout.addWidget(self.table_widget, 2, 0, 5, 5)

        layout.setColumnStretch(0, 5)
        layout.setColumnStretch(1, 2)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 3)
        layout.setRowStretch(2, 8)
        self.setLayout(layout)

    def load(self):
        print("Income Statement")
        self.table_widget.load()

            

class Income_table(QtWidgets.QWidget):
    def __init__(self, account, label, loading_label):
        super().__init__()
        self.own_crypto = {}
        self.account = account
        self.loading_label = loading_label
        self.income_label = label
        self.check = False
        self.table = QTableWidget()
        layout = QtWidgets.QVBoxLayout()
        self.worker = UpdateWorker("TWD")
        self.threadpool = QThreadPool()
        self.crypto_table = []
        self.crypto_buy_value = []
        self.crypto_buy_amount = []
        self.crypto_market_value = []
        self.income_value = []
        self.market_value = 0.0
        self.total_income = 0.0
        self.total_market_value = 0.0
        self.ROI = 0.0

        self.service_controller = ServiceController.ServiceController()
        self.service_controller.calculate_income({"account":self.account}).connect(self.get_own_crypto)
        self.worker = False
        self.income_label.setText("總損益：{}  總市值：{}  總報酬率：{} %".format(self.total_income, self.total_market_value, self.ROI))
        self.table.horizontalHeader().setFixedHeight(50)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setColumnCount(5)
        self.table.setRowCount(10)
        self.table.setHorizontalHeaderLabels(['幣別','買入價格','擁有數量','市價','損益'])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)#禁止編輯
        self.table.setFixedSize(500, 300)

        layout.addWidget(self.table, stretch=1)

        self.setLayout(layout)
    
    def get_own_crypto(self, result):
        result = json.loads(result)
        for crypto in result['parameter']:
            self.own_crypto[crypto[0]] = {}
            if crypto[0] in AVAILABLE_CRYPTO_CURRENCIES:
                pass
            else:
                AVAILABLE_CRYPTO_CURRENCIES.append(crypto[0])
        self.refresh_historic_rates()
        self.service_controller.calculate_income({"account":self.account}).connect(self.get_income)
        

    def get_income(self, result):
        result = json.loads(result)
        for crypto in result['parameter']:
            self.own_crypto[crypto[0]] = {}
            self.own_crypto[crypto[0]]['value'] = crypto[1]
        self.set_crypto()
        self.set_crypto_buy_value()
        self.service_controller.trade_info({"account":self.account}).connect(self.get_amount)


    def set_crypto(self):
        for crypto in self.own_crypto.keys():
            self.crypto_table.append(QTableWidgetItem(crypto))
        i = 0
        for crypto_item in self.crypto_table:
            self.table.setItem(i, 0, crypto_item)
            i = i + 1

    def set_crypto_buy_value(self):
        for crypto in self.own_crypto.keys():
            self.crypto_buy_value.append(QTableWidgetItem(str(self.own_crypto[crypto]['value'])))
        j = 0
        for crypto_value_item in self.crypto_buy_value:
            self.table.setItem(j, 1, crypto_value_item)
            j = j + 1

    def refresh_historic_rates(self):
        if self.worker:
            self.worker.signals.cancel.emit()

        self.worker = UpdateWorker("TWD")
        self.worker.signals.data.connect(self.result_data_callback)
        self.worker.signals.finished.connect(self.refresh_finished)
        self.worker.signals.progress.connect(self.progress_callback)
        self.worker.signals.error.connect(self.notify_error)
        self.threadpool.start(self.worker)

    def result_data_callback(self, value):
        self.value = value
        self.currentPrice = value
        print("=========================")
        print(self.value)
        self.set_market_value(self.value)
        self.set_income_value()
        try:
            self.set_ROI()
        except:
            pass
        self.check = True

    def refresh_finished(self):
        self.worker = False

    def progress_callback(self, progress):
        if progress != 100:
            self.loading_label.setText("Loading...{}%".format(progress))
        else:
            self.loading_label.setText("")

    def notify_error(self, error):
        e, tb = error
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(e.__class__.__name__)
        msg.setInformativeText(str(e))
        msg.setDetailedText(tb)
        msg.exec_()

    def get_amount(self, result):
        result = json.loads(result)
        if result["status"] == "OK":
            for crypto in self.own_crypto.keys():
                Sum = 0.0
                for trades in result["parameters"]:
                    if trades["info"]["currency"] == crypto:
                        Sum += trades["info"]["amount"]
                self.own_crypto[crypto]['amount'] = Sum   
        self.set_crypto_amount()  

        
    def set_crypto_amount(self):
        for crypto in self.own_crypto.keys():
            self.crypto_buy_amount.append(QTableWidgetItem(str(self.own_crypto[crypto]['amount'])))
        x = 0
        for crypto_amount in self.crypto_buy_amount:
            self.table.setItem(x, 2, crypto_amount)
            x = x + 1

    def set_market_value(self, value):
        self.crypto_market_value = []
        for crypto in self.own_crypto.keys():
            market_value = value[crypto]['TWD']*self.own_crypto[crypto]['amount']
            self.crypto_market_value.append(QTableWidgetItem(str(market_value)))
            self.total_market_value += market_value
        y = 0
        for market_value in self.crypto_market_value:
            self.table.setItem(y, 3, market_value)
            y = y + 1

    def set_market_value_load(self, value):
        self.crypto_market_value = []
        for crypto in self.own_crypto.keys():
            market_value = value[crypto]['TWD']*self.own_crypto[crypto]['amount']
            self.crypto_market_value.append(QTableWidgetItem(str(market_value)))
            self.total_market_value += market_value        
        y = 0
        for market_value in self.crypto_market_value:
            self.table.setItem(y, 3, market_value)
            y = y + 1

    def set_income_value(self):
        self.income_value = []
        self.total_income = 0.0
        for crypto in self.own_crypto.keys():
            red = QBrush(Qt.red)
            green = QBrush(Qt.green)
            income = (self.value[crypto]['TWD']-self.own_crypto[crypto]['value'])*self.own_crypto[crypto]['amount']
            self.total_income += income
            income_item = QTableWidgetItem(str(income))
            if income > 0:
                income_item.setForeground(red)
            else:
                income_item.setForeground(green)
            self.income_value.append(income_item)
        z = 0
        for income_value in self.income_value:
            self.table.setItem(z, 4, income_value)
            z = z + 1
    
    def set_ROI(self):
        cost = 0
        for crypto in self.own_crypto.keys():
            cost += self.own_crypto[crypto]['value'] * self.own_crypto[crypto]['amount']
        self.ROI = (self.total_income / cost) * 100
        self.income_label.setText("總損益：{}  \n總市值：{}  總報酬率：{} %".format(round(self.total_income, 2), round(self.total_market_value, 2), round(self.ROI, 3)))


    def load(self):
        if self.check == True:
            self.own_crypto = {}
            self.crypto_table = []
            self.crypto_buy_value = []
            self.crypto_buy_amount = []
            self.crypto_market_value = []
            self.income_value = []
            self.table.clear()
            self.table.setHorizontalHeaderLabels(['幣別','買入價格','擁有數量','市價','損益'])
            self.service_controller.calculate_income({"account":self.account}).connect(self.get_own_crypto)
        self.check = True