import sys
import time
from threading import Thread
from threading import Event
from PyQt5 import QtWidgets

import app_settings
import gui_qt
import handler
import client
import service

import logging
from logging import handlers

log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


class App:
    def __init__(self, settings_file_path='app_settings.json'):
        self.settings_file_path = settings_file_path
        # ----------------------------------------------------------------------
        self.hotkey_handler = handler.HotkeysCopyPasteHandler(
            self._callback_on_synchronization,
            self._callback_on_share,
        )
        # ----------------------------------------------------------------------
        self.gui = gui_qt.ShowUiMainWindow(
            self.callback_settings_update,
            self.callback_apply_received_share_data,
            self.callback_create_image_file,
            self.callback_show_image,
            self.callback_is_need_reconnect,
        )
        # ----------------------------------------------------------------------
        self.remote = client.Client(
            callback_server_data=self._callback_receive_clipboard_data,
            callback_server_msg=self._callback_receive_msg
        )
        # ----------------------------------------------------------------------
        self.settings = None
        self.data_for_create_file = ['', '']
        self.received_data_for_comparison = None
        self.list_received_share_data = []
        self.type_data = ''
        # ------ Буфер ---------------------------------------------------------
        self.clipboard = QtWidgets.QApplication.clipboard()
        # Если содержимое буфера обмена изменилось
        self.clipboard.dataChanged.connect(
            lambda: self.hotkey_handler.synchronizer_clipboard()
        )
        # ----------------------------------------------------------------------
        self.reconnection = Thread(
            target=self.reconnect
        )
        # ----------------------------------------------------------------------
        self.is_need_reconnect = Event()
        # ----------------------------------------------------------------------

    def start_app(self):
        """ Старт """
        log.debug(f'App.start_app - START')
        self.settings = service.load_settings(self.settings_file_path)
        if self.settings is None:
            self.settings = service.create_settings(self.settings_file_path)
        assert isinstance(self.settings, app_settings.AppSettings)
        log.debug(f'App.start_app - settings: {self.settings.to_dict()}')
        #
        with service.error_interceptor(
                self.gui, 'Ошибка синтаксиса'
        ):
            self.hotkey_handler.start(self.settings)
        #
        self.gui.show_gui(self.settings)
        #
        self.reconnection.start()
        #

    def close_app(self):
        self.remote.disconnect()
        #

    # ------ Reconnect ---------------------------------------------------------

    def reconnect(self):
        """ Переподключение """
        log.debug('App.reconnect - thread BEGIN')
        _reconnect_id = 0
        _reconnect_sleep_map = [1, 10, 30, 60]
        while True:
            if self.remote.listen_thread.is_alive():
                if self.is_need_reconnect.is_set() is False:
                    time.sleep(0.2)
                    _reconnect_id = 1
                    continue
                #
            #
            if not self.settings.client_name and self.settings.ip and self.settings.port:
                self.gui.show_msg('Не заданы обязательные поля')
                time.sleep(1)
                continue
            # ----------------------------------- #
            log.info('RECONNECT')
            self.is_need_reconnect.clear()
            self.gui.show_icon('red')
            #
            with service.error_interceptor(
                    self.gui, success=True
            ):
                if self.remote.is_connected:
                    self.remote.disconnect()
                #
                # ------------------------------- #
                self.remote = client.Client(
                    callback_server_data=self._callback_receive_clipboard_data,
                    callback_server_msg=self._callback_receive_msg
                )  # ---------------------------- #
                self.remote.connect(self.settings)
                log.debug('App.reconnect - try reconnect - SUCCESS')
            #
            _sleep_value = _reconnect_sleep_map[-1]
            if _reconnect_id < len(_reconnect_sleep_map):
                _sleep_value = _reconnect_sleep_map[_reconnect_id]
            #
            for i in range(_sleep_value):
                if self.is_need_reconnect.is_set():
                    break
                #
                time.sleep(1)
            #
            _reconnect_id += 1
        #
        log.debug(f'App.reconnect - thread END')

    # --------------------------------------------------------------------------
    @service.callback_error_alert
    def callback_is_need_reconnect(self):
        self.is_need_reconnect.set()

    # ------ Apply settings ----------------------------------------------------

    @service.callback_error_alert
    def callback_settings_update(self, new_settings: app_settings.AppSettings):
        """ Рестарт c новыми настройками """
        self.settings = new_settings
        with open(self.settings_file_path, 'w') as file:
            self.settings.save_to_file(file)
        #
        log.debug(
            f'App.callback_settings_update - new_settings {self.settings.to_dict()}')
        with service.error_interceptor(
                self.gui, 'Ошибка синтаксиса'
        ):
            self.hotkey_handler.stop()
            # ------------------------------- #
            self.hotkey_handler = handler.HotkeysCopyPasteHandler(
                self._callback_on_synchronization, self._callback_on_share
            )  # ---------------------------- #
            self.hotkey_handler.start(self.settings)
        #
        log.debug(f'App.callback_settings_update - APPLY SUCCESS')
        self.is_need_reconnect.set()

    # ------ Send --------------------------------------------------------------

    @service.callback_error_alert
    def _callback_on_synchronization(
            self, type_data, clipboard_data, binary_data
    ):
        """ Отправка данных на сервер для клиента синхронизации """
        log.debug(f'App._callback_on_synchronization')
        #
        self.data_for_create_file = [type_data, binary_data]
        #
        with service.error_interceptor(
                self.gui, success=True
        ):
            self.remote.send_clipboard_content(
                self.settings.client_name,
                self.settings.client_id,
                self.settings.client_name_for_sync,
                # ----------- ^^^^^^ -------- ^^^^
                type_data,
                clipboard_data,
            )

    @service.callback_error_alert
    def _callback_on_share(self, type_data, clipboard_data):
        """ Отправка данных на сервер для клиента с которым делимся """
        log.debug(f'App._callback_on_share')
        with service.error_interceptor(
                self.gui, success=True
        ):
            self.remote.send_clipboard_content(
                self.settings.client_name,
                self.settings.client_id,
                self.settings.client_name_for_share,
                # ----------- ^^^^^ --------- ^^^^
                type_data,
                clipboard_data,
            )

    # ------- Receive ----------------------------------------------------------

    @service.callback_error_alert
    def _callback_receive_msg(self, msg, success=None, popup=None):
        """ Получение сообщений от клиента и сервера """
        log.debug(f'App._callback_receive_msg {msg}')
        self.gui.show_msg(msg, success, popup=True)
    #

    @service.callback_error_alert
    def _callback_receive_clipboard_data(
            self, client_name, type_data, clipboard_data
    ):
        """ Получение данных буфера обмена от сервера и синхронизация """
        log.debug(f'App._callback_receive_clipboard_data - '
                  f'client_name: {client_name}, '
                  f'type_data: {type_data}, '
                  f'clipboard_data: {clipboard_data[:60]}')

        # Если имя отправителя нет в списке синхронизации
        if client_name not in self.settings.client_name_for_sync:
            self.list_received_share_data.append({
                'client_name': client_name,
                'type_data': type_data,
                'data': clipboard_data,
            }, )
            #
            if len(self.list_received_share_data) >= 10:
                del self.list_received_share_data[:1]
            #
            msg = None
            if type_data == 'text/plain':
                msg = f'Получен текст от: {client_name}'
            if type_data == 'image/png':
                msg = f'Получено изображение от: {client_name}'
            #
            log.debug(f'App._callback_receive_clipboard_data - {msg}')
            #
            self.gui.show_msg(msg, success=True, popup=True)
            self.gui.show_icon('green')
            return
        #
        self.type_data = type_data
        self.apply_received_data(type_data, clipboard_data)
        #

    # ------- Apply data -------------------------------------------------------

    @service.callback_error_alert
    def callback_apply_received_share_data(self):
        """ Применить полученные данные """
        log.debug(f'App.callback_apply_received_data')
        if self.list_received_share_data:
            received_share_data = self.list_received_share_data[-1]
            #
            type_data = received_share_data.get('type_data')
            clipboard_data = received_share_data.get('data')
            #
            log.debug(f'App.callback_apply_received_share_data - '
                      f'type_data: {type_data}, '
                      f'clipboard_data: {clipboard_data[:60]}')
            #
            self.apply_received_data(
                type_data, clipboard_data, show_window=True
            )
            #
            self.gui.show_icon('blue')
            #
        #

    def apply_received_data(self, type_data, received_data, show_window=None):
        """ Применить полученные данные """
        log.debug(f'App.apply_received_data - '
                  f'type_data: {type_data}')

        # ------- TEXT ---------------------------------------------------------
        if type_data == 'text/plain':
            # ---------------------------------------------- #
            with service.identify_os(
                    service.paste_data_in_clipboard_on_linux,
                    service.paste_data_in_clipboard_on_windows
            ) as paste_data_in_clipboard:
                # ---- Вызовит синхронизацию ---- #
                self.hotkey_handler.is_need_synchronization.clear()
                paste_data_in_clipboard(received_data, type_data)
            # ---------------------------------------------- #
            log.debug(f'App.apply_received_data --- '
                      f'Добавлены полученные данные в буфер обмена')
            return

        # ------- IMAGE --------------------------------------------------------
        if type_data == 'image/png':
            # ---------------------------------------------- #
            received_binary_data = service.get_decoded_data(received_data)
            #
            self.data_for_create_file = [type_data, received_binary_data]
            # ---------------------------------------------- #
            with service.identify_os(
                    service.paste_data_in_clipboard_on_linux,
                    service.paste_data_in_clipboard_on_windows
            ) as paste_data_in_clipboard:
                # ---- Вызовит синхронизацию ---- #
                self.hotkey_handler.is_need_synchronization.clear()
                paste_data_in_clipboard(received_binary_data, type_data)
            # ---------------------------------------------- #
            log.debug(f'App.apply_received_data --- '
                      f'Добавлены полученные данные в буфер обмена')
            #
            if show_window:
                self.callback_show_image()
            #
    # --------------------------------------------------------------------------

    @service.callback_error_alert
    def callback_create_image_file(self, directory=None):
        log.debug(f'App.callback_create_image_file')
        if self.data_for_create_file:
            type_data, data = self.data_for_create_file

            if not isinstance(data, bytes):
                log.debug(f'App.callback_show_image - Данные не бинарные')
                return

            service.create_image_file(
                data,
                'png',
                directory,
            )
            return
        log.debug(f'App.callback_create_image_file - Нет изображения')

    @service.callback_error_alert
    def callback_show_image(self):
        log.debug(f'App.callback_show_image')
        if self.data_for_create_file:
            type_data, data = self.data_for_create_file

            if not isinstance(data, bytes):
                log.debug(f'App.callback_show_image - Данные не бинарные')
                return

            absolute_file_path = service.create_image_file(
                data,
                'png',
                directory=None
            )
            try:
                service.open_file_with_os(absolute_file_path)
            except:
                pass
            return
        log.debug(f'App.callback_show_image - Нет изображения')

# ------------------------------------------------------------------------------


class LogHandler(logging.Handler):
    def __init__(self, log_window: gui_qt.LogWindow):
        super(LogHandler, self).__init__()
        self.log_window = log_window

    def emit(self, record):
        message = self.format(record)
        level = record.levelno
        # self.log_window.log(message, level)
        self.log_window.newMessage.emit(message, level)


def init_logging(app):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # ------------------------------------------------- #
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    # ------------------------------------------------- #
    window_handler = LogHandler(app.gui.log_window)
    window_handler.setLevel(logging.DEBUG)
    window_handler.setFormatter(formatter)
    # ------------------------------------------------- #
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    # ------------------------------------------------- #
    file_handler = logging.handlers.RotatingFileHandler(
        'logs.log', maxBytes=1024
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    # ------------------------------------------------- #
    logger.addHandler(window_handler)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def main(file='app_settings.json'):
    window = QtWidgets.QApplication(sys.argv)
    app = App(file)
    # ------------------------------------------------- #
    init_logging(app)
    # ------------------------------------------------- #
    log.debug('main - BEGIN')
    try:
        log.debug(f'main - start_app')
        app.start_app()
        return_code = window.exec()
        app.close_app()
        sys.exit(return_code)
    except Exception as e:
        log.exception(e)
        raise
    finally:
        log.debug(f'main - END')
    #


if __name__ == '__main__':
    main()
#

