import logging
import sys
from socket import *
from transport import JsonTransportProtocol
import socket
import threading
import socketserver
import logging
from logging import handlers
log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class ServerApp:
    def __init__(self):
        self.server_version = 0.3
        self.lock = threading.RLock()
        self.client_data = {}
        self.client_data_map = {}

    def register_client(self, name, handler):
        with self.lock:
            #
            self.client_data[name] = handler
            self.client_data_map[handler] = name
            log.debug(f'register_client - name: {name}, handler: {handler}, '
                      f'client_data:{self.client_data}, '
                      f'client_data_map: {self.client_data_map}')
        #

    def remove_client_index(self, handler):
        assert isinstance(handler, ThreadedTCPRequestHandler)
        with self.lock:
            if handler not in self.client_data_map:
                return
                #
            name = self.client_data_map.pop(handler)
            self.client_data.pop(name)
            log.debug(f'remove_client_index - name: {name}, handler: {handler} '
                      f'client_data: {self.client_data}, '
                      f'client_data_map: {self.client_data_map}')
        #

    def get_handler(self, client_name):
        handler = self.client_data.get(client_name, None)
        log.debug(f'get_handler - '
                  f'client_name: {client_name}, '
                  f'client_data: {self.client_data}, '
                  f'client_data_map: {self.client_data_map}, '
                  f'handler: {handler}')
        return handler
        #
# ------------------------------------------------------------------------------


class ThreadedTCPRequestHandler:
    def __init__(self, request, client_address, server, app):
        assert isinstance(request, socket.socket)
        assert isinstance(server, ThreadedTCPServer)
        assert isinstance(app, ServerApp)
        #
        self.app = app
        self.transport = JsonTransportProtocol(request)
    # --------------------------------------------------------------------------

    def authorize(self, handler) -> bool:
        assert isinstance(handler, ThreadedTCPRequestHandler)
        client_data: dict = self.transport.recv()
        # ------------------------- #
        client_name = client_data.get('client_name')
        client_version = client_data.get('client_version')
        # ------------------------- #
        if client_version > self.app.server_version:
            self.app.server_version = client_version
            #
        if client_version == round(self.app.server_version - 0.1, 1):
            self.send_data({
                'status': 'notification',
                'msg': f'Доступна новая версия клиента: {self.app.server_version}'
            })
        if client_version < round(self.app.server_version - 0.1, 1):
            self.send_data({
                'status': 'error',
                'msg': f'Версия клиента устарела, доступна версия: {self.app.server_version}'
            })
            # return False
        # ------------------------- #
        if self.app.get_handler(client_name) is not None:
            self.send_data({
                'status': 'error',
                'msg': f'Имя {client_name} недоступно',
            })
            return False
        self.app.register_client(client_name, handler)
        self.send_data({
            'status':      'success',
            'client_name':  client_name,
        })
        return True
    # --------------------------------------------------------------------------

    def handle(self):
        if self.authorize(self) is False:
            return
        #
        while True:
            client_data: dict = self.transport.recv()
            #
            client_status = client_data.get('status')
            if client_status == 'disconnect':
                self.app.remove_client_index(self)
                break
            #
            target_client_names = client_data.get('target_client_name')
            # if target_client_name is None:
            if not target_client_names:
                continue

            for target_name in target_client_names:
                if self.app.get_handler(target_name) is not None:
                    self.app.get_handler(target_name).send_data(
                        client_data
                    )

            # if self.app.get_handler(target_client_name) is None:
            #     self.send_data({
            #         'status': 'error',
            #         'msg': f'Клиент "{target_client_name}" не подключён к серверу'
            #     })
            #     continue
            #
            # self.app.get_handler(target_client_names).send_data(client_data)
        #

    def send_data(self, data):
        self.transport.sender(data)
        #

    def finish(self):
        self.app.remove_client_index(self)

# ------------------------------------------------------------------------------


def main():
    app = ServerApp()
    # ------------------------------------------------- #
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # ------------------------------------------------- #
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # ------------------------------------------------- #
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    # ------------------------------------------------- #
    file_handler = logging.handlers.RotatingFileHandler('server_logs.log', maxBytes=1024)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    # ------------------------------------------------- #
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    # ------------------------------------------------- #

    HOST, PORT = '0.0.0.0', 7006
    #

    def _socket_handler(request, client_address, server):
        handler = ThreadedTCPRequestHandler(request, client_address, server, app)
        try:
            return handler.handle()
        finally:
            handler.finish()
        #
    #
    with ThreadedTCPServer((HOST, PORT), _socket_handler) as server:
        server.serve_forever()
    #


if __name__ == "__main__":
    print('BEGIN')
    main()
    print('END.')



