#主伺服器
from threading import Thread
from Database.MemberSystem import *
from SocketServer.SocketServer import SocketServer
from Database.DBConnection import DBConnection
from Database.DBInitializer import DBInitializer

#所有指令
action_list = {
    "login":login,
    "regist":regist,
    "member_info" :member_info,
    "get_member_trades":get_member_trades,
    "insert_a_trade":insert_a_trade,
    "update_member_money":update_member_money,
    "change_member_password":change_member_password,
    "delete":delete,
    "get_member_income":get_member_income
}

class MainServer:
    def __init__(self):
        DBConnection.db_file_path = "python_final.db"
        DBInitializer().execute()
    def execute(self, command, parameters):
        execute_result = action_list[command](parameters)
        return execute_result

if __name__ == '__main__':
    mainserver = MainServer()
    server = SocketServer(mainserver)
    server.setDaemon=True
    server.serve()
    while True:
        command = input()
        if command == "finish":
            break
    server.server_socket.close()
    mainserver.done()
    print("leaving ....... ")
