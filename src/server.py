from socket import *
from transport import JsonTransportProtocol
import socket
import threading
import socketserver

# ------------------------------------------------------------------------------


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class ServerApp:
    def __init__(self):
        self.lock = threading.RLock()
        self.client_data = {}
        self.client_data_map = {}

    def register_client(self, name, handler):
        with self.lock:
            #
            self.client_data[name] = handler
            self.client_data_map[handler] = name
        #

    def remove_client_index(self, handler):
        assert isinstance(handler, ThreadedTCPRequestHandler)
        with self.lock:
            if handler not in self.client_data_map:
                return
                #
            name = self.client_data_map.pop(handler)
            self.client_data.pop(name)
        #

    def get_handler(self, client_name):
        handler = self.client_data.get(client_name, None)
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
        #
    # --------------------------------------------------------------------------

    def authorize(self, handler) -> bool:
        assert isinstance(handler, ThreadedTCPRequestHandler)
        client_data: dict = self.transport.recv()
        client_name = client_data.get('client_name')
        #
        if self.app.get_handler(client_name) is not None:
            self.send_data({
                'status': 'error',
                'error': f'Имя {client_name} недоступно',
            })
            return False
        self.app.register_client(client_name, handler)
        self.send_data({
            'status':      'success',
            'client_name':  client_name,
        })
        return True
        #

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
            target_client_name = client_data.get('target_client_name')
            if self.app.get_handler(target_client_name) is None:
                self.send_data({
                    'status': 'error',
                    'error': f'Имя {target_client_name} недоступно',
                })
                continue
            #
            self.app.get_handler(target_client_name).send_data(client_data)
        #

    def send_data(self, data):
        self.transport.sender(data)
        #

    def finish(self):
        self.app.remove_client_index(self)

# ------------------------------------------------------------------------------


def main():
    HOST, PORT = '127.0.0.1', 7006
    #
    app = ServerApp()

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



