from socket import *
import struct
import json


class TransportProtocol:
    def __init__(self, sock: socket):
        assert isinstance(sock, socket)
        self.sock = sock
        self._msg_counter = 0
    #

    def settimeout(self, timeout):
        return self.sock.settimeout(timeout)

    def sender(self, text):
        self._msg_counter = self._msg_counter + 1
        print(f'{self._msg_counter} sender {text}')
        text = bytes(text, 'utf-8')
        # Отправляем пакет 4 байта, хранящие длинну сообщения + само сообщение
        count_send = self.sock.sendall(
            # https://tirinox.ru/python-struct/
            struct.pack('>I', len(text)) + text
        )
        print(f'{self._msg_counter}// sender {count_send}')
    #

    # Вспомогательная функция
    def _recv_packets(self, n):
        self._msg_counter = self._msg_counter + 1
        received_data = b''
        # Пока не получим кусок данных необходимой длинны
        while len(received_data) < n:
            # Читаем кусок не более, чем недостаёт до длинны n
            packet = self.sock.recv(n - len(received_data))
            if not packet:
                print(f'not packet')
                return None
            received_data += packet
        #
        print(f'{self._msg_counter}//recv {n} bytes == {received_data}')
        return received_data
    #

    # Функция чтения принятых данных
    def recv(self):
        # Читаем участок содержащий длинну пакета
        length_target_data = self._recv_packets(4)
        if not length_target_data:
            return None
        # Переводим в питонячий тип
        payload_len = struct.unpack('>I', length_target_data)[0]
        # Декодируем
        result = self._recv_packets(payload_len)
        result = result.decode()
        return result
    #


class JsonTransportProtocol(TransportProtocol):
    def sender(self, data):
        dump = json.dumps(data)
        return super(JsonTransportProtocol, self).sender(dump)

    def recv(self):
        dump = super(JsonTransportProtocol, self).recv()
        if not dump:
            return None
        #
        return json.loads(dump)
