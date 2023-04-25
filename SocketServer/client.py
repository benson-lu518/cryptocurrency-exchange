import socket 
import json


host = "127.0.0.1"
port = 20001
BUFFER_SIZE = 1940


    

class SocketClient:
    def __init__(self, host, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.client_socket.connect((host, port))
        self.last_response = []

    def send_command(self, command,parameters):
        send_data = {'command': command,'parameters':parameters}
        self.client_socket.send(json.dumps(send_data).encode())
        print("     The client send data => {}".format(send_data))

    def wait_response(self):
        data = self.client_socket.recv(BUFFER_SIZE)
        raw_data = json.loads(data)
        print("     The client received data => {}".format(raw_data))
        self.last_response = raw_data
        if raw_data == "closing":
            return False
        return True

    




# if __name__ == '__main__':
#     client = SocketClient(host, port)
#     function = {"add":client.add,"show":client.showall,"modify":client.modify,"del":client.del_stu}
#     keep_going = True
#     while keep_going:
#         print_menu()
#         command = input(">>>")
#         if command == "exit":
#             break
#         try:
#             parameters = function[command]()
#         except:
#              print("input error")
#              continue 


