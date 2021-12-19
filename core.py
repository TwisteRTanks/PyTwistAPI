import socket
from json import dumps, loads
from uuid import uuid4


class Connection(object):
    def __init__(self, ip, port=9265):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addres = (ip, port,)
        self.id = None
        self.key = uuid4().hex

    def disconnect(): ...

    def connect(self):
        request = {
            "request": "connect",
            "client_data": {
                "key": self.key,
                "id": None
            }
        }
        self.socket.sendto(dumps(request).encode(), self.addres)

        resp = loads(self.socket.recv(1024))
        print(resp)
        if resp['status'] == -1:
            raise ConnectionError("ooops!")

        self.id = resp['response']

    @property
    def online(self):
        request = {
            "request": "get_online",
            "client_data": {
            }
        }
        self.socket.sendto(dumps(request).encode(), self.addres)

        resp = loads(self.socket.recv(1024))

        if resp['status'] == -1:
            raise ConnectionError("ooops!")

        return resp['response']
