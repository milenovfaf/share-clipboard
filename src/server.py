import sys
from socket import *
from transport import JsonTransportProtocol
import socket
import threading
import socketserver
import logging
from logging import handlers
import time

log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class ServerApp:
    def __init__(self):
        self.server_version = 0.3
        self.lock = threading.RLock()
        self.client_data = {}
        self.client_id_map = {}
        self.client_data_map = {}

    def register_client(self, client_id, name, handler):
        log.debug(f'(register_client) -- РЕГИСТРАЦИЯ -- (Аргументы) ИМЯ: {name} - HANDLER: {handler}')
        with self.lock:
            #
            self.client_id_map[handler] = client_id
            self.client_data[name] = handler
            self.client_data_map[handler] = name
            log.debug(f'(register_client) -- РЕГИСТРАЦИЯ -- Зарегистрированные клиенты: (client_data): {self.client_data}')
            log.debug(f'(register_client) -- РЕГИСТРАЦИЯ -- Зарегистрированные клиенты: (client_data_map): {self.client_data_map}')
            log.debug(f'------------------------------------------------------')

    def remove_client_index(self, handler):
        log.debug(f'(remove_client_index) -- УДАЛЕНИЕ КЛИЕНТА -- (Аргументы) HANDLER: {handler}')
        assert isinstance(handler, ThreadedTCPRequestHandler)
        with self.lock:
            if handler not in self.client_data_map:
                log.debug(f'(remove_client_index) -- УДАЛЕНИЕ КЛИЕНТА -- Этот HANDLER НЕ ЗАРЕГИСТРИРОВАН - RETURN -: {handler}')
                return
                #
            log.debug(f'(remove_client_index) -- УДАЛЕНИЕ КЛИЕНТА -- Зарегистрированные клиенты ПЕРЕД удалением: (client_data): {self.client_data}')
            log.debug(f'(remove_client_index) -- УДАЛЕНИЕ КЛИЕНТА -- Зарегистрированные клиенты ПЕРЕД удалением: (client_data_map): {self.client_data_map}')
            name = self.client_data_map.pop(handler)
            log.debug(f'(remove_client_index) -- УДАЛЕНИЕ КЛИЕНТА -- POP - HANDLER: {handler}')
            log.debug(f'(remove_client_index) -- УДАЛЕНИЕ КЛИЕНТА -- POP - ИМЯ: {name} которое вернул POP')
            self.client_data.pop(name)
            self.client_id_map.pop(handler)
            log.debug(f'(remove_client_index) -- УДАЛЕНИЕ КЛИЕНТА -- Зарегистрированные клиенты ПОСЛЕ удаления: (client_data): {self.client_data}')
            log.debug(f'(remove_client_index) -- УДАЛЕНИЕ КЛИЕНТА -- Зарегистрированные клиенты ПОСЛЕ удаления: (client_data_map): {self.client_data_map}')
        #
        log.debug(f'------------------------------------------------------')

    def get_handler(self, client_name):
        log.debug(f'(get_handler) -- ПОЛУЧИТЬ HANDLER -- (Аргументы) ИМЯ: {client_name}')
        log.debug(f'(get_handler) -- ПОЛУЧИТЬ HANDLER -- Зарегистрированные клиенты: (client_data): {self.client_data}')
        log.debug(f'(get_handler) -- ПОЛУЧИТЬ HANDLER -- Зарегистрированные клиенты: (client_data_map): {self.client_data_map}')
        handler = self.client_data.get(client_name, None)
        log.debug(f'(get_handler) -- ПОЛУЧИТЬ HANDLER -- Полученный HANDLER: {handler}')
        return handler

    def get_client_id(self, handler):
        handler = self.client_id_map.get(handler, None)
        return handler

# ------------------------------------------------------------------------------


class ThreadedTCPRequestHandler:
    def __init__(self, request, client_address, server, app):
        self.client_address = client_address
        assert isinstance(request, socket.socket)
        assert isinstance(server, ThreadedTCPServer)
        assert isinstance(app, ServerApp)

        self.app = app
        self.transport = JsonTransportProtocol(request)
        self.authorize_lock = threading.RLock()
    # --------------------------------------------------------------------------

    def send_data(self, data):
        log.debug(f'(send_data) -- SEND DATA -- DATA: {data} - {self.client_address} HANDLER: {self}')
        self.transport.sender(data)

    def authorize(self, handler) -> bool:
        assert isinstance(handler, ThreadedTCPRequestHandler)
        client_data: dict = self.transport.recv()
        # ------------------------- #
        client_id = client_data.get('client_id')
        client_name = client_data.get('client_name')
        client_version = client_data.get('client_version')
        log.debug(f'(authorize) -- АВТОРИЗАЦИЯ -- ИМЯ: {client_name}')
        log.debug(f'(authorize) -- АВТОРИЗАЦИЯ -- HANDLER: {handler}')
        # ------------------------- #
        if client_version > self.app.server_version:
            self.app.server_version = client_version
        #
        # if client_version == round(self.app.server_version - 0.1, 1):
        #     self.send_data({
        #         'status': 'notification',
        #         'msg': f'Доступна новая версия клиента: {self.app.server_version}'
        #     })
        # if client_version < round(self.app.server_version - 0.1, 1):
        #     self.send_data({
        #         'status': 'error',
        #         'msg': f'Версия клиента устарела, доступна версия: {self.app.server_version}'
        #     })
            # return False
        # ------------------------- #
        log.debug(f'------------------------------------------------------')
        with self.authorize_lock:
            exist_handler = self.app.get_handler(client_name)
            if exist_handler:
                exist_client_uuid = self.app.get_client_id(exist_handler)
                if exist_client_uuid != client_id:
                    log.debug(f'(authorize) -- АВТОРИЗАЦИЯ -- ИМЯ НЕДОСТУПНО: {client_name}')
                    self.send_data({
                        'status': 'error',
                        'msg': f'Имя {client_name} недоступно',
                    })
                    return False

                assert isinstance(exist_handler, self.__class__)
                exist_handler.logout()

            self.app.register_client(client_id, client_name, handler)

        log.debug(f'------------------------------------------------------')
        self.send_data({
            'status':      'success',
            'client_name':  client_name,
        })
        return True
    # --------------------------------------------------------------------------

    def communication_loop(self):
        while True:
            client_data: dict = self.transport.recv()
            log.debug(f'(handle) -- HANDLE -- client_data: {client_data} {self.client_address} HANDLER: {self}')

            if not client_data:
                break

            client_status = client_data.get('status')
            if client_status == 'ping':
                self.send_data({
                    'status': 'pong',
                })
                continue

            if client_status == 'disconnect':
                break

            target_client_names = client_data.get('target_client_name')
            if not target_client_names:
                continue

            for target_name in target_client_names:
                if self.app.get_handler(target_name) is None:
                    continue
                #
                self.app.get_handler(target_name).send_data(
                    client_data
                )

        log.debug('(handle) end loop/')

    def logout(self):
        log.debug(f'(handle) -- FINISH -- {self.client_address} HANDLER: {self}')
        self.app.remove_client_index(self)
        try:
            self.send_data({
                'status': 'disconnect',
                'msg': 'Клиент удалён',
            })
            time.sleep(3)  # wait sending/delivering data
        except:
            pass

    def handle(self):
        try:
            if self.authorize(self) is False:
                log.debug(f'(handle) -- HANDLE -- АВТОРИЗАЦИЯ НЕ ПРОШЛА ДЛЯ: {self.client_address} HANDLER: {self}')
                return

            log.debug(f'(handle) -- HANDLE -- УСПЕШНАЯ АВТОРИЗИРОВАН: {self.client_address} HANDLER: {self}')
            # - - -
            self.communication_loop()
        finally:
            self.logout()

# ------------------------------------------------------------------------------


def init_logging():
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


def main():
    init_logging()
    log.debug(f'main BEGIN ')
    app = ServerApp()

    HOST, PORT = '0.0.0.0', 7006

    log.debug(f'main HOST, PORT {HOST, PORT} ')

    def _socket_handler(request, client_address, server):
        handler = ThreadedTCPRequestHandler(request, client_address, server, app)
        try:
            return handler.handle()
        finally:
            request.close()  # important

    with ThreadedTCPServer((HOST, PORT), _socket_handler) as server:
        log.debug(f'main serve_forever ')
        try:
            server.serve_forever()
        except Exception as e:
            log.exception(e)
            raise e
        finally:
            log.debug(f'main END. ')


if __name__ == "__main__":
    print('BEGIN')
    main()
    print('END.')



