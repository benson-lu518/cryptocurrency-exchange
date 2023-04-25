from PyQt5 import QtWidgets, QtGui, QtCore
from Widgets.WidgetComponents import LabelComponent, LineEditComponent, ButtonComponent
import SocketServer.ServiceController as ServiceController
import json
from PyQt5.QtGui import QIntValidator
class HistoryWidget(QtWidgets.QWidget):
    def __init__(self,account):
        self.account = account
        super().__init__()
        self.setObjectName("history_widget")
        self.service_controller = ServiceController.ServiceController()

        layout = QtWidgets.QVBoxLayout()

        header_label = LabelComponent(20, "History Trade")


        self.scroll_area_content = ScrollAreaContentWidget()
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.scroll_area_content)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        layout.addWidget(header_label)
        layout.addWidget(scroll_area)

        self.setLayout(layout)
        

    def load(self):
        print("history trade")
        self.service_controller.trade_info({"account":self.account}).connect(self.SetText)
        
    def SetText(self,rcvdata):
        result = json.loads(rcvdata)
        if result["status"]=="Fail":
            return
        else:
            trade_list = result["parameters"]
            id = 0
            out = ""
            for trades in trade_list:
                id +=1
                out+="編號: {}\n".format(id)
                for key,value in trades["info"].items():
                    out+="  {}:{} ".format(key,value)
                out+="\n"
            print(out)
            self.scroll_area_content.SetText(out)

class ScrollAreaContentWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("show_scroll_area_widget")
        layout = QtWidgets.QVBoxLayout()
        self.title_lable = LabelComponent(18,"==== trade list ====")
        self.info_label = LabelComponent(12,"")
        layout.addWidget(self.title_lable)
        layout.addWidget(self.info_label)
        self.setLayout(layout)

    def SetText(self,text):
        self.info_label.setText(text)