from json import dumps, loads
from uuid import uuid4
from typing import Union
from hashlib import md5
from time import time

from codes import Status

import socket

class ServerError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Connection(object):
    def __init__(self, ip, port=9265):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addres = (ip, port,)
        self.max_map_packet_size = 1048576
        self.id = None
        self.key = uuid4().hex

    @staticmethod
    def status_dispatcher(status: int) -> Union[int, None]:
        do = {


            Status.unknown: ServerError("Unknown error!"),
            Status.ipacket: ServerError("Invalid packet"),
            Status.ikey:    ServerError("Connection is corrupted. Invalid key"),
            Status.iid:     ServerError("Connection is corruped. Invalid id"),
            Status.mconns_error: ServerError(
                "Maximum connected clients to server"
            ),
            Status.permission_denied: PermissionError("permission denied")

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
        print(resp)
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

    def get_data(self):
        request = {
            "request": "get_data",
            "client_data": {}
        }
        self.socket.sendto(dumps(request).encode(), self.addres)
        
        resp = loads(self.socket.recv(1024))
        self.status_dispatcher(resp['status'])
        return resp["response"]

    def get_map(self) -> bytearray:
        request = {
            "request": "get_map",
            "client_data": {}
        }
        self.socket.sendto(dumps(request).encode(), self.addres)
        
        resp = loads(self.socket.recv(self.max_map_packet_size))

        self.status_dispatcher(resp['status'])
        
        map = bytearray(resp["response"]["map"])

        if resp["response"]["checksum"] != md5(bytes(map)).hexdigest():
            raise TypeError("checksum is invalid")

        return map

    def ping(self) -> int:
        request = {
            "request": "ping",
            "client_data": {
            }
        }
        
        S1 = time()
        
        self.socket.sendto(dumps(request).encode(), self.addres)
        resp = loads(self.socket.recv(1024))
        
        exc_time_ms = round((time() - S1) * 1000)
        
        self.status_dispatcher(resp['status'])
        return exc_time_ms
    
    def push_data(self, posx, posy, rot, turret_rot):
        
        request = {
            "request": "push_data",
            "request_body": {
                "posx": posx,
                "posy": posy,
                "rot": rot,
                "turret_rot": turret_rot
            },
            "client_data": {
                "id": self.id,
                "key": self.key
            }
        }
        self.socket.sendto(dumps(request).encode(), self.addres)

        resp = loads(self.socket.recv(1024))
        self.status_dispatcher(resp['status'])
        return resp
