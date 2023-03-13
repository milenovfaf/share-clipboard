import os
import sys
import time
import datetime
import io
import base64
from threading import Thread
from threading import Event
from functools import wraps
from pathlib import Path
from contextlib import contextmanager

import pyperclip
from PIL import Image
from PyQt5 import QtWidgets, QtCore, QtGui

import app_settings
import gui_qt
import handler
import client
import servise

import logging
from logging import handlers

log = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
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
            self.create_image_file,
            self.callback_show_image,
            # self.is_need_reconnect,
        )
        # ----------------------------------------------------------------------
        self.remote = client.Client(
            callback_server_data=self._callback_receive_clipboard_data,
            callback_server_msg=self._callback_receive_msg
        )
        # ----------------------------------------------------------------------
        self.settings = None
        self.received_sync_clipboard_data = None
        self.list_received_share_data = []
        # ------ Буфер ---------------------------------------------------------
        self.clipboard = QtWidgets.QApplication.clipboard()
        # Если содержимое буфера обмена изменилось
        self.clipboard.dataChanged.connect(
            lambda: self.hotkey_handler.synchronizer_clipboard(
                self.received_sync_clipboard_data
            ))
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
        self.settings = servise.load_settings(self.settings_file_path)
        if self.settings is None:
            self.settings = servise.create_settings(self.settings_file_path)
        assert isinstance(self.settings, app_settings.AppSettings)
        log.debug(f'App.start_app - settings: {self.settings.to_dict()}')
        #
        with servise.error_interceptor(
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
                self.gui.show_icon('red')
                time.sleep(1)
                continue
            # ----------------------------------- #
            log.info('RECONNECT')
            self.is_need_reconnect.clear()
            #
            with servise.error_interceptor(
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

    # ------ Apply settings ----------------------------------------------------

    @servise.callback_error_alert
    def callback_settings_update(self, new_settings: app_settings.AppSettings):
        """ Рестарт c новыми настройками """
        self.settings = new_settings
        with open(self.settings_file_path, 'w') as file:
            self.settings.save_to_file(file)
        #
        log.debug(
            f'App.callback_settings_update - new_settings {self.settings.to_dict()}')
        with servise.error_interceptor(
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

    @servise.callback_error_alert
    def _callback_on_synchronization(self, type_data, clipboard_data):
        """ Отправка данных на сервер для клиента синхронизации """
        log.debug(f'App._callback_on_synchronization')
        with servise.error_interceptor(
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

    @servise.callback_error_alert
    def _callback_on_share(self, type_data, clipboard_data):
        """ Отправка данных на сервер для клиента с которым делимся """
        log.debug(f'App._callback_on_share')
        with servise.error_interceptor(
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
        #

    # ------- Receive ----------------------------------------------------------

    @servise.callback_error_alert
    def _callback_receive_msg(self, msg, success=None, popup=None):
        """ Получение сообщений от клиента и сервера """
        log.debug(f'App._callback_receive_msg {msg}')
        self.gui.show_msg(msg, success, popup=True)

    #

    @servise.callback_error_alert
    def _callback_receive_clipboard_data(self, client_name, type_data,
                                         clipboard_data):
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
            msg = f'Получены данные от: {client_name}'
            log.debug(f'App._callback_receive_clipboard_data - {msg}')
            #
            self.gui.show_msg(msg, success=True, popup=True)
            self.gui.show_icon('green')
            return
        #
        self.apply_received_data(type_data, clipboard_data)
        #

    @servise.callback_error_alert
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
            self.apply_received_data(type_data, clipboard_data,
                                     show_window=True)
            #
            self.gui.show_icon('blue')
            #
        #
        # Тест
        # type_data = 'image/png'
        # data = 'iVBORw0KGgoAAAANSUhEUgAAAGwAAACJCAYAAADJ7938AAAABHNCSVQICAgIfAhkiAAAAvlJREFUeF7tndFKBEEQA13x/39ZXWFBln0QzOQm6boXOZF0WzUZ70D0+Px+vPGIIfAesymL/hBAWNhBQBjCwgiErUvDEBZGIGxdGoawMAJh69IwhIURCFuXhiEsjEDYujQMYWEEwtalYQgLIxC2Lg1DWBiBsHVpGMLCCIStS8MQFkYgbF0ahrAwAmHr0jCEhREIW5eGISyMQNi6NAxhYQTC1qVhCAsjELYuDUNYGIGwdWkYwsIIhK37Ebbv8nWP41g+4z8DRgvbXc6T2JHCEkVd8kYJSxY1SliDqEtY/cv6JlmntNorsU1UdcNaZZ3S6q7EZlmVwq6ro/VjVcPa21XVsAmyqoS1XoH376viSpzSLhp2P74Bz+MbNqldNCygUfcVoxs2rV007H58A55HNyyAr3xFhMmRrg1E2Fq+8vRYYRNfcJz2Y4XJj25IIMJCRF1rIgxhYQTC1o1t2NR/exYrLKwYsnURJkPpCUKYh7NsCsJkKD1B0cImvvCIFuY503tNiRc2rWXxwvY6/+u3qRA2qWUVwtaf630m1Aib0rIaYWcHJkirErbPxbVukzph7S2rE9Z+NVYKu6Q1tq1W2PVTpE1avbC2to0Q9rtt6Y0bJaxBXO1fwvnLO6Gntu3+G8WjhT1JfZL49HWv+tzIK/FVsBVzEaagaMxAmBG2YhTCFBSNGQgzwlaMQpiCojEDYUbYilEIU1A0ZiDMCFsxCmEKisYMhBlhK0YhTEHRmIEwI2zFKIQpKBozEGaErRiFMAVFYwbCjLAVoxCmoGjMQJgRtmIUwhQUjRkIM8JWjEKYgqIxA2FG2IpRCFNQNGYgzAhbMQphCorGDIQZYStGIUxB0ZiBMCNsxSiEKSgaMxBmhK0YhTAFRWMGwoywFaMQpqBozECYEbZiFMIUFI0ZCDPCVoxCmIKiMQNhRtiKUQhTUDRmIMwIWzEKYQqKxgyEGWErRiFMQdGYgTAjbMUohCkoGjMQZoStGIUwBUVjBsKMsBWjEKagaMz4ArtnPhXIRKmLAAAAAElFTkSuQmCC'
        # self.apply_received_data(type_data, data, show_window=True)

    # ------- handling ---------------------------------------------------------

    @servise.callback_error_alert
    def callback_show_image(self):
        log.debug(f'App.callback_show_image')
        if not isinstance(self.received_sync_clipboard_data, bytes):
            return
        image, _ = servise.create_image_object(
            self.received_sync_clipboard_data
        )
        self.gui.image_window.show_window(image)
    #

    def apply_received_data(self, type_data, clipboard_data, show_window=None):
        """ Применить полученные данные """
        log.debug(f'App.apply_received_data - '
                  f'type_data: {type_data}')
        #
        if type_data == 'text':
            if clipboard_data == self.clipboard.text():
                log.debug(f'App.apply_received_data - PASS')
                return
            #
            self.received_sync_clipboard_data = clipboard_data
            # ---- Вызовит синхронизацию ---- #
            pyperclip.copy(clipboard_data)
            log.debug(f'App.apply_received_data - '
                      f'Добавлены полученные данные в буфер обмена')
            return
            #
        #
        if type_data == 'image/png':
            # Декодирование данных изображения из строки в бинарный формат
            binary_image_data = base64.b64decode(clipboard_data.encode('utf-8'))
            #
            image, image_buffer = servise.create_image_object(binary_image_data)
            #
            received_mime_data = QtCore.QMimeData()
            received_mime_data.setData('image/png', image_buffer.data())
            # ------------------------------------------------------------------
            mime_data = self.clipboard.mimeData()
            binary_data = bytes(mime_data.data("image/png"))
            received_binary_data = bytes(received_mime_data.data("image/png"))
            #
            if received_binary_data == binary_data:
                log.debug(f'App.apply_received_data - PASS')
                return
            # ------------------------------------------------------------------
            self.received_sync_clipboard_data = received_binary_data
            # ---- Вызовит синхронизацию ---- #
            self.clipboard.setMimeData(received_mime_data)
            log.debug(f'App.apply_received_data - '
                      f'Добавлены полученные данные в буфер обмена')
            #
            if show_window:
                self.gui.image_window.show_window(image)
            return
        #
        #     ''' урлы нельзя сравнить, так как приходят не урлы а файлы,
        #     нужно где то хранить изначальные данные буфера и их сравнивать '''
        # if type_data == 'list_urls':
        #     if clipboard_data == self.clipboard.mimeData().urls():
        #         log.debug(f'App._callback_receive_clipboard_data - PASS')
        #         return

    def create_image_file(self, directory="images", file_name=None):
        if not os.path.exists(directory):
            # os.makedirs(directory)
            return
        #
        if not isinstance(self.received_sync_clipboard_data, bytes):
            return
        #
        image = Image.open(io.BytesIO(self.received_sync_clipboard_data))
        #
        if file_name:
            name, extension = os.path.splitext(file_name)
            if not extension:
                file_name = file_name + '.png'
                absolute_file_path = os.path.join(directory, file_name)
                image.save(absolute_file_path)
                log.debug(f'App.create_image_file - Файл создан')
                return
            #
            if extension != '.png':
                msg = 'Указано не верное расширение'
                self.gui.show_msg(msg, success=True, popup=True)
                return
            #
            file_path = os.path.join(directory, file_name)
            image.save(file_path)
            log.debug(f'App.create_image_file - Файл создан')
            return
            #
        now = datetime.datetime.now()
        file_name = now.strftime('%Y-%m-%d_%H-%M-%S.png')
        absolute_file_path = os.path.join(directory, file_name)
        image.save(absolute_file_path)
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


def init_logging(app):
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
    file_handler = logging.handlers.RotatingFileHandler('logs.log',
                                                        maxBytes=1024)
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
