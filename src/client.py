from socket import *
from threading import Thread, Event
import app_settings
from transport import JsonTransportProtocol
import logging
from socket import timeout as ReadTimeoutError

log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


class Client:
    def __init__(self,
                 callback_server_data,
                 callback_server_msg,
                 ):
        assert callable(callback_server_data)
        assert callable(callback_server_msg)
        self.callback_server_msg = callback_server_msg
        #
        self.sock = socket(AF_INET, SOCK_STREAM)
        self._is_connected = Event()
        #
        self.transport = JsonTransportProtocol(self.sock)
        #
        self._is_listening = Event()
        #
        self.settings = None
        # ----------------------------------------------------------------------

        def msg_server_handler():
            """ Получение данных от сервера """
            #
            self.transport.settimeout(0.5)
            #
            while self._is_listening.is_set() is True:
                try:
                    server_data = self.transport.recv()
                except ReadTimeoutError as e:
                    # log.exception(e)
                    continue
                #
                if not server_data:
                    break
                #
                if server_data.get('status') in ('error', 'notification'):
                    server_msg = server_data['msg']
                    callback_server_msg(
                        server_msg
                    )
                    continue
                #
                client_name = server_data.get('client_name')
                clipboard_content = server_data.get('client_data')
                #
                callback_server_data(
                    client_name, clipboard_content
                )
            #
            self._is_listening.clear()
        #
        self.listen_thread = Thread(
            target=msg_server_handler
        )
    # --------------------------------------------------------------------------

    @property
    def is_connected(self):
        return self._is_connected.is_set()

    @property
    def is_listening(self):
        return self._is_listening.is_set()

    # --------------------------------------------------------------------------

    def _start_listening(self) -> None:
        if not self.is_connected:
            raise RuntimeError('Сначала нужно подключиться к серверу')
        #
        self._is_listening.set()
        self.listen_thread.start()

    def _stop_listening(self, join=True):
        if join:
            print('_stop_listening ', join)
            print('self.listen_thread.is_alive()', self.listen_thread.is_alive())
            self.listen_thread.join()
        #
    # --------------------------------------------------------------------------

    def connect(self, settings: app_settings.AppSettings) -> None:
        self.settings = settings
        self.transport.sock.connect((settings.ip, int(settings.port)))
        log.info(f'Подключено к: {settings.ip}:{settings.port}')
        #
        self.transport.settimeout(30)
        # self.send_to_server({  # еще не установлен флаг _is_connected
        self.transport.sender({
            'client_version': settings.client_version,
            'client_name': settings.client_name,
        })
        server_data = self.transport.recv()
        #
        if not server_data:
            raise ConnectionError
        #
        if server_data.get('status') in ('error', 'notification'):
            server_msg = server_data['msg']
            self.callback_server_msg(
                server_msg
            )
        self._is_connected.set()
        #
        self._start_listening()

    def disconnect(self, join=True):
        if not self.is_connected:
            return
        #
        try:
            self.transport.settimeout(30)
            self.send_to_server({
                'status': 'disconnect',
            })
        finally:
            print('self.remote.disconnect()  0 _stop_listening')
            self._stop_listening(join)
            #
            print('self.remote.disconnect()  1 sock.close')
            self.transport.sock.close()
            print('self.remote.disconnect()  2 SUCCESS ')
        #
    # --------------------------------------------------------------------------

    def send_to_server(self, data):
        if not self.is_connected:
            raise ConnectionError
        #
        return self.transport.sender(data)

    def send_clipboard_content(
            self,
            client_name,
            target_client_name,
            clipboard_data,
    ):
        return self.send_to_server({
            'client_name':        client_name,
            'target_client_name': target_client_name,
            'client_data':        clipboard_data,
        })
# ------------------------------------------------------------------------------


