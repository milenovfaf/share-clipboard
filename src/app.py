import time
from threading import Thread

from PyQt5 import QtWidgets
import sys

from PyQt5.QtWidgets import QSystemTrayIcon

import app_settings
import gui_qt
import handler
from functools import wraps
from pathlib import Path
from contextlib import contextmanager
import client
import logging
from logging import handlers

log = logging.getLogger(__name__)


# ------------------------------------------------------------------------------


def show_msg(gui, msg, success=False, popup=False):
    if popup:
        gui.tray_icon.showMessage(
            "Share Clipboard",
            msg,
            QSystemTrayIcon.Information,
            2000
        )
    if success:
        gui.ui.label_error.setStyleSheet('color: #00CC00')  # Green
        gui.ui.label_error.setText(msg)
        gui.ui.label_error.update()
        return
    gui.ui.label_error.setStyleSheet('color: #FF0000')  # Red
    gui.ui.label_error.setText(msg)
    gui.ui.label_error.update()


@contextmanager
def error_interceptor(gui, msg=None, success=False):
    """ Обработка ошибок """
    try:
        show_msg(gui, msg='')
        if success:
            show_msg(gui, 'Подключено к серверу', success)
        yield None
    except (ConnectionError, ConnectionRefusedError) as e:
        log.exception(e)
        show_msg(gui, 'Нет подключения к серверу')
    except Exception as e:
        log.exception(e)
        show_msg(gui, f' {msg} ({e})')
    finally:
        pass


def callback_error_alert(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            log.exception(e)
            print(e)
            raise
        #

    return wrapper


# ------------------------------------------------------------------------------


def _load_settings(settings_file_path) -> app_settings.AppSettings:
    """ Чтение файла настроек """
    if Path(settings_file_path).exists():
        try:
            with open(settings_file_path, 'r') as file:
                old_settings = app_settings.AppSettings.load_from_file(file)
                return old_settings
            #
        except app_settings.EmtpyFileSettingsError as e:
            log.exception(e)
            pass
        #
    #


def _create_settings(settings_file_path):
    """ Создание файла настроек """
    old_settings = app_settings.get_default_app_settings()
    with open(settings_file_path, 'w+') as file:
        old_settings.save_to_file(file)
    #
    return old_settings


# ------------------------------------------------------------------------------


class App:
    def __init__(self, settings_file_path='settings.json'):
        self.settings_file_path = settings_file_path
        #
        self.hotkey_handler = handler.HotkeysCopyPasteHandler(
            self._callback_on_synchronization, self._callback_on_share,
        )
        # ----------------------------------------------------------------------
        self.gui = gui_qt.ShowUiMainWindow(
            self.callback_settings_update
        )
        # ----------------------------------------------------------------------
        self.remote = client.Client(
            callback_server_data=self._callback_receive_clipboard_data,
            callback_server_msg=self._callback_receive_msg
        )
        # ----------------------------------------------------------------------
        self.settings = None
        self.received_clipboard_data = None
        # ------ Буфер ---------------------------------------------------------
        self.clipboard = QtWidgets.QApplication.clipboard()
        # Если содержимое буфера обмена изменилось
        self.clipboard.dataChanged.connect(
            lambda: self.hotkey_handler.synchronizer_clipboard(
                self.received_clipboard_data
            ))
        # ----------------------------------------------------------------------
        self.reconnection = Thread(
            target=self.reconnect
        )
        # ----------------------------------------------------------------------

    def start_app(self):
        """ Старт """
        self.settings = _load_settings(self.settings_file_path)
        if self.settings is None:
            self.settings = _create_settings(self.settings_file_path)
        assert isinstance(self.settings, app_settings.AppSettings)
        #
        with error_interceptor(
                self.gui, 'Ошибка синтаксиса'
        ):
            self.hotkey_handler.start(self.settings)
        #
        self.gui.show_gui(self.settings)
        #
        if self.settings.client_name and self.settings.ip and self.settings.port:
            with error_interceptor(
                    self.gui, success=True
            ):
                self.remote.connect(self.settings)
        self.reconnection.start()

    def close_app(self):
        self.remote.disconnect()
        #

    # ------ Reconnect ---------------------------------------------------------

    def reconnect(self):
        """ Переподключение """
        while True:
            time.sleep(5)
            if self.remote.listen_thread.is_alive():
                continue
            log.info('Reconnect')
            with error_interceptor(
                    self.gui, success=True
            ):
                self.remote.disconnect()
                # ------------------------------- #
                self.remote = client.Client(
                    callback_server_data=self._callback_receive_clipboard_data,
                    callback_server_msg=self._callback_receive_msg
                )  # ---------------------------- #
                self.remote.connect(self.settings)

            time.sleep(5)

    # ------ Apply -------------------------------------------------------------

    @callback_error_alert
    def callback_settings_update(self, new_settings: app_settings.AppSettings):
        """ Рестарт c новыми настройками """
        self.settings = new_settings
        with open(self.settings_file_path, 'w') as file:
            self.settings.save_to_file(file)
        #
        with error_interceptor(
                self.gui, 'Ошибка синтаксиса'
        ):
            self.hotkey_handler.stop()
            # ------------------------------- #
            self.hotkey_handler = handler.HotkeysCopyPasteHandler(
                self._callback_on_synchronization, self._callback_on_share
            )  # ---------------------------- #
            self.hotkey_handler.start(self.settings)
        #
        if not self.settings.client_name and self.settings.ip and self.settings.port:
            show_msg(self.gui, 'Не заданы обязательные поля')
            return
        #
        with error_interceptor(
                self.gui, success=True
        ):
            self.remote.disconnect()
            # ------------------------------- #
            self.remote = client.Client(
                callback_server_data=self._callback_receive_clipboard_data,
                callback_server_msg=self._callback_receive_msg,
            )  # ---------------------------- #
            self.remote.connect(self.settings)
            #
        #
    # ------ Send --------------------------------------------------------------

    @callback_error_alert
    def _callback_on_synchronization(self, clipboard_data):
        """ Отправка данных на сервер для клиента синхронизации """
        with error_interceptor(
                self.gui, success=True
        ):
            self.remote.send_clipboard_content(
                self.settings.client_name,
                self.settings.client_name_for_sync,
                # ----------- ^^^^^^ -------- ^^^^
                clipboard_data,
            )

    @callback_error_alert
    def _callback_on_share(self, clipboard_data):
        """ Отправка данных на сервер для клиента с которым делимся """
        with error_interceptor(
                self.gui, success=True
        ):
            self.remote.send_clipboard_content(
                self.settings.client_name,
                self.settings.client_name_for_share,
                # ----------- ^^^^^ --------- ^^^^
                clipboard_data,
            )
        #

    # ------- Receive ----------------------------------------------------------

    @callback_error_alert
    def _callback_receive_clipboard_data(self, client_name, clipboard_data):
        """ Получение данных буфера обмена от сервера и синхронизация """
        self.received_clipboard_data = clipboard_data
        # ---- Вызовит синхронизацию ---- #
        self.clipboard.setText(clipboard_data, mode=self.clipboard.Clipboard)
        # ------------------------------- #
        if client_name != self.settings.client_name_for_sync:
            with error_interceptor(
                    self.gui, success=True
            ):
                self.remote.send_clipboard_content(
                    self.settings.client_name,
                    self.settings.client_name_for_sync,
                    clipboard_data,
                )
            #
        #

    @callback_error_alert
    def _callback_receive_msg(self, msg, success=None, popup=None):
        """ Получение сообщений от клиента и сервера """
        show_msg(self.gui, msg, success, popup=True)
    #


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


def main(file='settings.json'):
    window = QtWidgets.QApplication(sys.argv)
    app = App(file)
    # ------------------------------------------------- #
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # ------------------------------------------------- #
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # ------------------------------------------------- #
    window_handler = LogHandler(app.gui.log_window)
    window_handler.setLevel(logging.DEBUG)
    window_handler.setFormatter(formatter)
    # ------------------------------------------------- #
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    # ------------------------------------------------- #
    file_handler = logging.handlers.RotatingFileHandler('logs.log', maxBytes=1024)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    # ------------------------------------------------- #
    logger.addHandler(window_handler)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    # ------------------------------------------------- #
    try:
        app.start_app()
        return_code = window.exec()
        app.close_app()
        sys.exit(return_code)
    except Exception as e:
        log.exception(e)
        raise


if __name__ == '__main__':
    print('BEGIN')
    main()
    print('END')
#
