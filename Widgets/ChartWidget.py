#圖表的介面
from datetime import datetime, timedelta, date
from itertools import cycle
import os
import sys
import traceback
from PyQt5 import QtWidgets, QtGui, QtCore

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import numpy as np

import pyqtgraph as pg
import requests
import requests_cache

#爬蟲的api金鑰
CRYPTOCOMPARE_API_KEY = 'f2208401985d383cdf9d265ef9d90eea44bf33d8f7f6c4b192cf212448290f3b'

#查詢的幣種(台幣、美金、歐元)
DEFAULT_BASE_CURRENCY = 'TWD'
AVAILABLE_BASE_CURRENCIES = ['USD', 'EUR', 'TWD']

#查詢的虛擬貨幣種
AVAILABLE_CRYPTO_CURRENCIES = ['BTC', 'ETH', 'LTC', 'EOS', 'XRP', 'BCH'] #
CURRENCY_IN_CHINESE = {'BTC':"比特幣",'ETH':"乙太幣","LTC":"萊特幣",'EOS':"柚子幣",'XRP':'瑞波幣','BCH':'比特幣現金'}
DEFAULT_DISPLAY_CURRENCIES = ['BTC', 'ETH', 'LTC']

#查詢的時間範圍(我們設30天)
NUMBER_OF_TIMEPOINTS = 30

#線的顏色
BREWER12PAIRED = cycle(['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c', '#fdbf6f', '#ff7f00',
                  '#cab2d6', '#6a3d9a', '#ffff99', '#b15928' ])

#圖的背景
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

#處理爬蟲的狀況
class WorkerSignals(QObject):
    finished = pyqtSignal() #查詢結束
    error = pyqtSignal(tuple) #出現的錯誤
    progress = pyqtSignal(int) #查詢進度
    data = pyqtSignal(dict) #爬到的資料
    cancel = pyqtSignal() #取消爬蟲

#爬蟲的class
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
            rates = {} #幣值
            for n, crypto in enumerate(AVAILABLE_CRYPTO_CURRENCIES, 1):
                url = 'https://min-api.cryptocompare.com/data/histoday?fsym={fsym}&tsym={tsym}&limit={limit}'
                r = requests.get(
                    url.format(**{
                        'fsym': crypto,
                        'tsym': self.base_currency,
                        'limit': NUMBER_OF_TIMEPOINTS-1,
                        'format': 'json',
                    }),
                    headers=auth_header,
                )
                r.raise_for_status()
                rates[crypto] = r.json().get('Data')
                self.signals.progress.emit(int(100 * n / len(AVAILABLE_CRYPTO_CURRENCIES))) #更新查詢進度(百分比)
                if self.is_interrupted:
                    return
        except Exception as e:
            self.signals.error.emit((e, traceback.format_exc()))
            return
        self.signals.data.emit(rates)
        self.signals.finished.emit()
    def cancel(self):
        self.is_interrupted = True

class ChartWidget(QtWidgets.QWidget):
    def __init__(self,account):
        super().__init__()
        self.account = account
        layout = QGridLayout()
        self.setObjectName("chart_widget")
        
        #畫布
        self.ax = pg.PlotWidget()
        self.ax.showGrid(True, True)
        self.line = pg.InfiniteLine(
            pos=-20,
            pen=pg.mkPen('k', width=3),
            movable=False 
        )
        self.ax.addItem(self.line)
        self.ax.setLabel('left', text='匯率')
        self.p1 = self.ax.getPlotItem()
        self.p1.scene().sigMouseMoved.connect(self.mouse_move_handler) #當滑鼠指標在上面移動
        self.base_currency = DEFAULT_BASE_CURRENCY
        self._data_lines = dict()
        self._data_items = dict()
        self._data_colors = dict()
        self._data_visible = DEFAULT_DISPLAY_CURRENCIES #預設被勾選顯示的虛擬貨幣
        self.listView = QTableView() #旁邊的TABLE
        self.model = QStandardItemModel() 
        self.model.setHorizontalHeaderLabels(["幣別", "匯率"]) #第一列是幣別、第二列是匯率
        self.listView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) #依照內容物大小伸縮
        self.model.itemChanged.connect(self.check_check_state) #只要有東西被更新(自訂欄位或是勾選)，都去檢查勾選狀況
        self.listView.setModel(self.model) 
        self.threadpool = QThreadPool()
        self.worker = False
        layout.addWidget(self.ax,1,0,1,1)
        layout.addWidget(self.listView,1,1,1,1)
        self.listView.setFixedSize(250, 400)
        self.setFixedSize(650, 400)
        toolbar = QToolBar("Main")
        layout.addWidget(toolbar,0,0,1,1)
        self.currencyList = QComboBox()
        toolbar.addWidget(self.currencyList)
        self.update_currency_list(AVAILABLE_BASE_CURRENCIES) #更新選擇的幣值的幣別
        self.currencyList.setCurrentText(self.base_currency)
        self.currencyList.currentTextChanged.connect(self.change_base_currency)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        toolbar.addWidget(self.progress)
        self.refresh_historic_rates()
        self.setWindowTitle("PYTHON OOP 2022S")
        self.setLayout(layout)
        #使用者定義的PART
        self.user_defined_currency = QStandardItem()
        self.user_defined_currency.setForeground(QBrush(QColor(
            self.get_currency_color(self.user_defined_currency.text()))))
        self.user_defined_currency.setColumnCount(2)
        self.user_defined_currency.setCheckable(True)
        self.user_defined_Value = QStandardItem()
        self.user_defined_Value.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.model.setColumnCount(2)
        self.model.appendRow([self.user_defined_currency, self.user_defined_Value])

    def update_currency_list(self, currencies): #更新虛擬貨幣的種類
        for currency in currencies:
            self.currencyList.addItem(currency)

    def clear_chart(self): #清除畫布
         for items  in self._data_visible:
            if items not in ['BTC', 'ETH', 'LTC', 'EOS', 'XRP', 'BCH']:
                self._data_visible.remove(items)

    def check_check_state(self, i):
        if not i.isCheckable():  #沒有被勾選就不理他
            return
        try: #嘗試轉成中文(自定義的就沒辦法)
            currency = AVAILABLE_CRYPTO_CURRENCIES[list(CURRENCY_IN_CHINESE.values()).index(i.text())]
        except: 
            self.clear_chart() #代表有更新到自定義的虛擬貨幣別，所以把畫布中舊的虛擬貨幣的曲線清乾淨
            currency = i.text()
            if currency not in AVAILABLE_CRYPTO_CURRENCIES:
                AVAILABLE_CRYPTO_CURRENCIES.append(i.text())
            self.refresh_historic_rates()
        checked = i.checkState() == Qt.Checked
        #根據勾選狀況更新可視的曲線
        if currency in self._data_visible:
            if not checked:
                self._data_visible.remove(currency)
                self.redraw()
        else:
            if checked:
                self._data_visible.append(currency)
                self.redraw()
    #選顏色
    def get_currency_color(self, currency):
        if currency not in self._data_colors:
            self._data_colors[currency] = next(BREWER12PAIRED)
        return self._data_colors[currency]

    #根據虛擬貨幣別更新幣值
    def get_or_create_data_row(self, currency):
        if currency == self.user_defined_currency.text(): #如果是自定義的虛擬幣
            if self.user_defined_currency == "未知": #判斷貨幣存不存在
                self.user_defined_Value.setText("未知")
            self._data_items[currency] = self.user_defined_currency,self.user_defined_Value
        if currency not in self._data_items:
            self._data_items[currency] = self.add_data_row(currency)
        return self._data_items[currency]

    def add_data_row(self, currency): #回傳一個包好的QStandardItem
        citem = QStandardItem()
        if currency in list(CURRENCY_IN_CHINESE.keys()):
            citem.setText(CURRENCY_IN_CHINESE[currency])
        citem.setForeground(QBrush(QColor(
            self.get_currency_color(currency)
        )))
        citem.setColumnCount(2)
        citem.setCheckable(True)
        if currency in DEFAULT_DISPLAY_CURRENCIES:
            citem.setCheckState(Qt.Checked)
        vitem = QStandardItem()
        vitem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.model.setColumnCount(2)
        self.model.appendRow([citem, vitem])
        return citem, vitem

    def mouse_move_handler(self, pos):#從指到的x座標去更新他的幣值(把x換算成天數)
        pos = self.ax.getViewBox().mapSceneToView(pos)
        self.line.setPos(pos.x())
        self.update_data_viewer(int(pos.x()))

    def update_data_viewer(self, i):#更新table
        if i not in range(NUMBER_OF_TIMEPOINTS):
            return
        for currency, data in self.data.items():
            if currency in AVAILABLE_CRYPTO_CURRENCIES:
                self.update_data_row(currency, data[i])

    def update_data_row(self, currency, data): #更新table
        citem, vitem = self.get_or_create_data_row(currency)
        if citem.text()!="未知":
            vitem.setText("%.4f" % data['close'])

    def change_base_currency(self, currency): #換幣別(台幣美金英鎊)
        self.base_currency = currency
        self.refresh_historic_rates()

    def refresh_historic_rates(self): #呼叫爬蟲
        if self.worker:
            self.worker.signals.cancel.emit()
        self.data = {}
        self.volume = []
        self.worker = UpdateWorker(self.base_currency)
        self.worker.signals.data.connect(self.result_data_callback)
        self.worker.signals.finished.connect(self.refresh_finished)
        self.worker.signals.progress.connect(self.progress_callback)
        self.worker.signals.error.connect(self.notify_error)
        self.threadpool.start(self.worker)

    def result_data_callback(self, rates): #爬完蟲的資料處理
        self.data = rates
        self.redraw() #畫圖
        delete = ""
        for currency, data in self.data.items():
            if data == {}:
                delete = currency
                try:
                    AVAILABLE_CRYPTO_CURRENCIES.remove(currency)
                except:
                    pass
                self.user_defined_currency.setText("未知")
                self.user_defined_Value.setText("未知")
        self.update_data_viewer(NUMBER_OF_TIMEPOINTS-1)

    def progress_callback(self, progress):
        self.progress.setValue(progress)

    def refresh_finished(self):
        self.worker = False
        self.redraw()

    def notify_error(self, error):
        e, tb = error
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(e.__class__.__name__)
        msg.setInformativeText(str(e))
        msg.setDetailedText(tb)
        msg.exec_()

    def redraw(self): #畫圖
        y_min, y_max = sys.maxsize, 0
        x = np.arange(NUMBER_OF_TIMEPOINTS)
        for currency, data in self.data.items():
            if currency == "未知" or data == "未知":
                continue
            if data:
                _, close, high, low = zip(*[
                    (v['time'], v['close'], v['high'], v['low']) #時間、當天高點、低點、收盤
                    for v in data
                ])

                if currency in self._data_visible:
                    if currency not in self._data_lines:
                        self._data_lines[currency] = {}
                        self._data_lines[currency]['high'] = self.ax.plot(
                            x, high, 
                            pen=pg.mkPen(self.get_currency_color(currency), width=2, style=Qt.DotLine)
                        )
                        self._data_lines[currency]['low'] = self.ax.plot(
                            x, low, 
                            pen=pg.mkPen(self.get_currency_color(currency), width=2, style=Qt.DotLine)
                        )
                        self._data_lines[currency]['close'] = self.ax.plot(
                            x, close,  
                            pen=pg.mkPen(self.get_currency_color(currency), width=3)
                        )
                    else:
                        self._data_lines[currency]['high'].setData(x, high)
                        self._data_lines[currency]['low'].setData(x, low)
                        self._data_lines[currency]['close'].setData(x, close)
                    y_min, y_max = min(y_min, *low), max(y_max, *high)
                else:
                    if currency in self._data_lines:
                        self._data_lines[currency]['high'].clear()
                        self._data_lines[currency]['low'].clear()
                        self._data_lines[currency]['close'].clear()
        self.ax.setLimits(yMin=y_min * 0.9, yMax=y_max * 1.1, xMin=min(x), xMax=max(x))

    def load(self):
        self.refresh_historic_rates()


