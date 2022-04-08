from json import dumps, loads
from urllib import request
from uuid import uuid4
from typing import List, Optional, Tuple, Union
from hashlib import md5
from time import time

from codes import Status
from udpsocket import UdpSocket
from base_types import * 


class ServerError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Connection(object):
    def __init__(self, ip, port=9265):
        self.socket: UdpSocket = UdpSocket()
        self.addres: Tuple[str, int] = (ip, port,)
        self.max_map_packet_size: int = 1048576
        self.id: Optional[int] = None
        self.key = uuid4().hex

    @staticmethod
    def status_dispatcher(status: int) -> int:
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

    def connect(self) -> None:
        request = {
            "request": "connect",
            "client_data": {
                "key": self.key,
                "id": None,
                "addres": [],
                "client_timeout_ms": 0,
            },
            "player_data": {},
            "request_body": {}
        }

        self.socket.sendto(dumps(request).encode(), self.addres)

        resp = loads(self.socket.recv(1024))
        print(resp)
        self.status_dispatcher(resp['status'])

        self.id = resp['response']

    def disconnect(self) -> None:
        request = {
            "request": "disconnect",
            "client_data": {
                "key": self.key,
                "id": self.id,
                "addres": [],
                "client_timeout_ms": -1
            },
            "player_data": {},
            "request_body": {}
        }

        self.socket.sendto(dumps(request).encode(), self.addres)

        resp = loads(self.socket.recv(1024))
        self.status_dispatcher(resp['status'])

    @property
    def online(self) -> int:
        request = {
            "request": "get_online",
            "client_data": {},
            "player_data": {},
            "request_body": {}
        }
        self.socket.sendto(dumps(request).encode(), self.addres)

        resp = loads(self.socket.recv(1024))

        # Не хендлим статус, так как зачем, запрос то анонимный
        # The status does not need to be handled.

        return resp['response']

    def get_data(self) -> Union[List[ClientData], List[ClientDataNullKeys]]:
        request = {
            "request": "get_data",
            "client_data": {},
            "player_data": {},
            "request_body": {},
        }
        self.socket.sendto(dumps(request).encode(), self.addres)
        
        resp = loads(self.socket.recv(1024))
        self.status_dispatcher(resp['status'])
        return resp["response"]

    def get_map(self) -> Map:
        request = {
            "request": "get_map",
            "client_data": {},
            "player_data": {},
            "request_body:": {}
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
            "client_data": {},
            "player_data": {},
            "request_body": {}
        }
        
        S1 = time()
        
        self.socket.sendto(dumps(request).encode(), self.addres)
        resp = loads(self.socket.recv(1024))
        
        exc_time_ms = round((time() - S1) * 1000)
        
        self.status_dispatcher(resp['status'])
        return exc_time_ms
    
    def push_data(self, posx: int, posy: int, rot: Union[int, float], turret_rot: Union[int, float]) -> None:
        
        request = {
            "request": "push_data",
            "client_data": {
                "id": self.id,
                "key": self.key,
                "client_timeout_ms": self.ping()
            },
            "player_data": {
                "posx": posx,
                "posy": posy,
                "rot": rot,
                "turret_rot": turret_rot
            },
            "request_body": {}
        }
        self.socket.sendto(dumps(request).encode(), self.addres)

        resp = loads(self.socket.recv(1024))
        self.status_dispatcher(resp['status'])

    def push_message(self, msg_conent: str, nick: str) -> None:
        request = {
            "request": "push_message",
            "client_data": {
                "key": self.key,
                "id": self.id,
                "addres": [],
                "client_timeout_ms": self.ping()
            },
            "player_data": {},
            "request_body": {
                "msg_content": msg_conent,
                "nick": nick
            }
        }
        
        self.socket.sendto(dumps(request).encode(), self.addres)

        resp = loads(self.socket.recv(1024))
        self.status_dispatcher(resp['status'])
        # return resp['response']
    
    def get_messages(self) -> List[list[str, str]]:
        request = {
            "request": "get_messages",
            "client_data": {
                "key": self.key,
                "id": self.id,
                "addres": [],
                "client_timeout_ms": self.ping()
            },
            "player_data": {},
            "request_body": {}

        }

        self.socket.sendto(dumps(request).encode(), self.addres)

        resp = loads(self.socket.recv(1024))
        self.status_dispatcher(resp['status'])
        return resp['response']
    
    def clear_chat(self) -> None:
        request = {
            "request": "clear_chat",
            "client_data": {
                "key": self.key,
                "id": self.id,
                "addres": [],
                "client_timeout_ms": self.ping()
            },
            "player_data": {},
            "request_body": {}
        }

        self.socket.sendto(dumps(request).encode(), self.addres)

        resp = loads(self.socket.recv(1024))
        self.status_dispatcher(resp['status'])
        return resp['response']