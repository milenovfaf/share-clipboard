import select
import time
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
            log.debug(f'Client.msg_server_handler - while event')
            self.transport.settimeout(3)
            #
            while self._is_listening.is_set() is True:
                # --------------------------------------------#
                ready_to_read, _, _ = select.select([self.sock], [], [], 5)
                if not ready_to_read:
                    # Если прошло 5 секунд без готовых для чтения данных
                    self.send_to_server({
                        'status': 'ping',
                    })
                    try:
                        # Ждём ответ pong, если нет ответа то reconnect
                        server_data = self.transport.recv()
                        if server_data.get('status') == 'pong':
                            continue
                    except ReadTimeoutError as e:
                        log.debug(f'Client.msg_server_handler - Не получен ответ PONG - BREAK')
                        break
                #
                else:
                    server_data = self.transport.recv()
                    log.debug(f'Client.msg_server_handler - server_data: {server_data} ')
                # --------------------------------------------#
                #
                if not server_data:
                    log.debug(f'Client.msg_server_handler - not server_data - BREAK')
                    break
                #
                server_status = server_data.get('status')
                #
                if server_status in ('error', 'notification'):
                    server_msg = server_data['msg']
                    callback_server_msg(
                        server_msg
                    )
                    continue
                #
                client_name = server_data.get('client_name')
                type_data = server_data.get('type_data')
                clipboard_data = server_data.get('client_data')
                #
                if client_name:
                    callback_server_data(
                        client_name, type_data, clipboard_data
                    )
            #
            log.debug(f'Client.msg_server_handler - END thread')
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

    def _stop_listening(self, join=True):
        if join:
            print('_stop_listening ', join)
            print('self.listen_thread.is_alive()', self.listen_thread.is_alive())
            self.listen_thread.join()
            print('self.listen_thread.is_alive()', self.listen_thread.is_alive())
        #
    # --------------------------------------------------------------------------

    def connect(self, settings: app_settings.AppSettings) -> None:
        log.debug(f'Client.connect')
        self.settings = settings
        self.transport.sock.connect((settings.ip, int(settings.port)))
        log.info(f'Подключено к: {settings.ip}:{settings.port}')
        #
        self.transport.settimeout(30)
        # self.send_to_server({  # еще не установлен флаг _is_connected
        self.transport.sender({
            'client_version': settings.client_version,
            'client_name': settings.client_name,
            'client_id': settings.client_id,
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
        if not self.is_connected:
            raise RuntimeError('Сначала нужно подключиться к серверу')
        #
        log.debug(f'Client.connect - SUCCESS')
        self._is_listening.set()
        self.listen_thread.start()

    def disconnect(self, join=True):
        log.debug(f'Client.disconnect ')
        if not self.is_connected:
            return
        #
        try:
            #
            self._is_listening.clear()
            self._stop_listening(join)
            #
            self.transport.settimeout(5)
            self.send_to_server({
                'status': 'disconnect',
            })
            # ожидаем ответ от сервера - что бы освободить nickname клиента
            server_data = self.transport.recv()  # IMPORTANT
        except Exception as e:
            log.exception(e)
            pass
        finally:
            self.transport.sock.close()
            log.debug(f'Client.disconnect - END')
        #
    # --------------------------------------------------------------------------

    def send_to_server(self, data):
        if not self.is_connected:
            raise ConnectionError
        #
        if data.get('status') == 'active':
            data = data['client_name'] = self.settings.client_name
        return self.transport.sender(data)

    def send_clipboard_content(
            self,
            client_name,
            client_id,
            target_client_name,
            type_data,
            clipboard_data,
    ):
        return self.send_to_server({
            'client_name':        client_name,
            'client_id':          client_id,
            'target_client_name': target_client_name,
            'type_data':          type_data,
            'client_data':        clipboard_data,
        })
# ------------------------------------------------------------------------------


