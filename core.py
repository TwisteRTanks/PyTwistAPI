import socket
from json import dumps, loads
from uuid import uuid4
from typing import Union


class ServerError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Connection(object):
    def __init__(self, ip, port=9265):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addres = (ip, port,)
        self.id = None
        self.key = uuid4().hex

    @staticmethod
    def status_dispatcher(status: int) -> Union[int, None]:
        do = {

            -127: ServerError("Unknown error!"),
            - 21: ServerError("Connection is corrupted. Invalid key"),
            - 20: ServerError("Connection is corruped. Invalid id"),
            - 1:  ServerError("Maximum connected clients to server")

        }

        if status < 0:
            raise do[status]

        return status

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

        self.status_dispatcher(resp['status'])

        self.id = resp['response']

    def disconnect(self):
        request = {
            "request": "disconnect",
            "client_data": {
                "key": self.key,
                "id": self.id
            }
        }

        self.socket.sendto(dumps(request).encode(), self.addres)

        resp = loads(self.socket.recv(1024))
        print(resp)
        self.status_dispatcher(resp['status'])

    @property
    def online(self):
        request = {
            "request": "get_online",
            "client_data": {}
        }
        self.socket.sendto(dumps(request).encode(), self.addres)

        resp = loads(self.socket.recv(1024))

        # Не хендлим статус, так как зачем, запрос то анонимный
        # The status does not need to be handled.

        return resp['response']
