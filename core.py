import socket
from json import dumps, loads


class Connection(object):
    def __init__(self, ip, port=9265):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addres = (ip, port,)
        self.id = None

    def connect(self) -> int:
        request = {
            "request": "connect",
            "client_data": {}
        }
        self.socket.sendto(dumps(request).encode(), self.addres)
        self.id = loads(self.socket.recv(1024).decode())['response']

        print(self.id)

    @property
    def online(self):
        request = {
            "request": "push_data",
            "client_data": {
                "id": 832,
            }
        }
