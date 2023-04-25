
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
from Widgets.ChartWidget import ChartWidget 
from Widgets.MemberWidget import MemberWidget 
from Widgets.TradeWidget import TradeWidget
from Widgets.HistoryWidget import HistoryWidget
from Widgets.IncomeWidget import InComeWidget
from Widgets.WidgetComponents import *


class MainWidget(QtWidgets.QWidget):
    def __init__(self,account):
        super().__init__()
        self.setObjectName("main_widget")
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self.setStyleSheet(
            """
                QWidget#main_widget{{
                    color: white;
                    border-image: url(\"{}\");
                }};
            """.format("./resources/bg2.jpg")
        )     
        self.setWindowOpacity(0.9) # 透明度


        self.account = account
        layout = QtWidgets.QGridLayout()
        header_label = LabelComponent(24,"")  # "Crypto Trading System"
        header_label.setObjectName("header_label")
        header_label.setStyleSheet(
            """
              QLabel#header_label
              {{
                color: white;
                border-image: url(\"{}\");
              }}
            """.format("./resources/header.png")
        )
        self.show_label = LabelComponent(15, "Welcome {}".format(self.account ))
        function_widget = FunctionWidget(account)
        menu_widget = MenuWidget(function_widget.update_widget)


        layout.addWidget(header_label, 0, 0, 1, 2)
        layout.addWidget(self.show_label, 0, 2, 1, 1)
        layout.addWidget(menu_widget, 1, 0, 1, 1)
        layout.addWidget(function_widget, 1, 1, 1, 2)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 9)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 9)

        self.setLayout(layout)
        
class MenuWidget(QtWidgets.QWidget):
    def __init__(self, update_widget_callback):
        super().__init__()
        self.setObjectName("menu_widget")
        self.update_widget_callback = update_widget_callback

        layout = QtWidgets.QVBoxLayout()
        member_button = ButtonComponent("Member Center")

        member_button.clicked.connect(lambda: self.update_widget_callback("membercenter"))
        chart_button = ButtonComponent("History Chart")

        chart_button.clicked.connect(lambda: self.update_widget_callback("chart"))
        trade_button = ButtonComponent("Trade")
        history_button = ButtonComponent("History Trade")

        trade_button.clicked.connect(lambda: self.update_widget_callback("trade"))
        history_button.clicked.connect(lambda: self.update_widget_callback("history"))

        income_button = ButtonComponent("Income Statement")
        income_button.clicked.connect(lambda: self.update_widget_callback("income"))

        member_button.setStyleSheet("QPushButton{background-color:#9fc5e8}QPushButton:hover{background-color:#3d85c6}")
        chart_button.setStyleSheet("QPushButton{background-color:#d9d2e9}QPushButton:hover{background-color:#8e7cc3}")
        trade_button.setStyleSheet("QPushButton{background-color:#b6d7a8}QPushButton:hover{background-color:#6aa84f}")
        history_button.setStyleSheet("QPushButton{background-color:#ffe599}QPushButton:hover{background-color:#f1c232}")
        income_button.setStyleSheet("QPushButton{background-color:#f4cccc}QPushButton:hover{background-color:#e06666}")

        layout.addWidget(member_button, stretch=1)
        layout.addWidget(chart_button, stretch=1)
        layout.addWidget(trade_button, stretch=1)
        layout.addWidget(history_button, stretch=1)
        layout.addWidget(income_button, stretch=1)


        self.setLayout(layout)


class FunctionWidget(QtWidgets.QStackedWidget):
    def __init__(self,account):
        super().__init__()
        self.account = account
        self.widget_dict = {
            "membercenter": self.addWidget(MemberWidget(self.account)),
            "chart": self.addWidget(ChartWidget(self.account)),
            "trade":self.addWidget(TradeWidget(self.account)),
            "history":self.addWidget(HistoryWidget(self.account)),
            "income":self.addWidget(InComeWidget(self.account))
        }
        self.update_widget("membercenter")
    
    def update_widget(self, name):
        self.setCurrentIndex(self.widget_dict[name])
        current_widget = self.currentWidget()
        current_widget.load()
