import socket

# UDP сокет с некоторым дополнительным API
class UdpSocket(socket.socket):
    def __init__(self):
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self.__total_recv = 0
        self.__total_sent = 0

    @property
    def total_sent(self):
        return self.__total_sent

    @property
    def total_recv(self):
        return self.__total_recv

    def sendto(self, data, addres):
        self.__total_sent += len(data)
        super().sendto(data, addres)

    def recvfrom(self, buffersize):
        raw_data, addres = super().recvfrom(buffersize)

        self.__total_recv += len(raw_data)

        return raw_data, addres

    def resettimeout(self):
        self.settimeout(None)
