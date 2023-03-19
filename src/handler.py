import binascii
import imghdr
import platform
import subprocess
import time
import pyperclip
import base64
from PyQt5 import QtWidgets, QtGui, QtCore
from pynput.keyboard import Controller, Key
import mimetypes

from pynput import keyboard
import logging

import service

log = logging.getLogger(__name__)


class HotkeysCopyPasteHandler(object):
    def __init__(
            self,
            _callback_on_synchronization,
            _callback_on_share,
    ):
        assert callable(_callback_on_synchronization)
        assert callable(_callback_on_share)
        self._callback_on_synchronization = _callback_on_synchronization
        self._callback_on_share = _callback_on_share
        # ----------------------------------------------------------------------
        self.clipboard = QtWidgets.QApplication.clipboard()
        # ----------------------------------------------------------------------
        self.keyboard = Controller()
        self.kh = None
        self.connector = '\n'
        self.list_clipboard_data = ['', '']
        # ----------------------------------------------------------------------
    #

    def start(self, app_settings) -> None:
        if self.kh is not None:
            raise RuntimeError('Нельзя запускать обработчик дважды!')
        #
        self._configure(app_settings)
        assert isinstance(self.kh, keyboard.GlobalHotKeys)
        self.kh.start()
    #

    def stop(self):
        assert isinstance(self.kh, keyboard.GlobalHotKeys)
        self.kh.stop()
    #

    # --------------------------------------------------------------------------

    def _configure(self, app_settings):
        callback_set = {}
        for hot_key_map, callback in [
            (app_settings.copy_join_keys,           self._copy_join),
            (app_settings.share_keys,               self._share_clipboard),
            (app_settings.connector_space_bar_keys, self._connector_space_bar),
            (app_settings.connector_new_line_keys,  self._connector_new_line),
            (app_settings.connector_none_keys,      self._connector_none),
        ]:
            if hot_key_map is None:
                continue
            #
            callback_set[hot_key_map] = callback
        #
        self.kh = keyboard.GlobalHotKeys(callback_set)  # <<<<<<<<<<<<<<
    # --------------------------------------------------------------------------

    def synchronizer_clipboard(self, received_data_for_comparison):
        """ Синхронизация буфера между клиентами """
        log.info(f'handler.synchronizer_clipboard --- '
                 f'Обнаружено изменение буфера обмена {"-" * 39}')
        # ----------------------------------------------------------------------

        with service.identify_os(
                service.get_clipboard_data_on_linux,
                service.get_clipboard_data_on_windows
        ) as get_clipboard_data:
            try:
                clipboard_data, type_data, binary_data = get_clipboard_data()
            except:
                return
        if not clipboard_data:
            log.info('handler.synchronizer_clipboard -- '
                     'Нет данных text/plain и image/png - RETURN')
            return
        # ----------------------------------------------------------------------
        if (clipboard_data or binary_data) == received_data_for_comparison:
            self.list_clipboard_data.append(clipboard_data)
            #
            log.info(f'{list(map(lambda x: x[:300], self.list_clipboard_data[-3:]))[::-1]}')
            return
        # ----------------------------------------------------------------------
        log.info('handler.synchronizer_clipboard - '
                     f'type_data - {type_data}, '
                     f'clipboard_data - {clipboard_data[:100]}, ')
        if binary_data:
            log.info(f'binary_data - {binary_data[:100]}')
        # ----------------------------------------------------------------------
        #
        if clipboard_data != self.list_clipboard_data[-1]:
            self.list_clipboard_data.append(clipboard_data)
        #

        if len(self.list_clipboard_data) >= 10:
            del self.list_clipboard_data[:1]  # удалить первые 30

        log.info(f'handler.synchronizer_clipboard - Сработала синхронизация: '
                 f'{list(map(lambda x: x[:500], self.list_clipboard_data[-3:]))[::-1]}')
        #
        self._callback_on_synchronization(type_data, clipboard_data, binary_data)

        # ----------------------------------------------------------------------

    def _copy_join(self):
        """ Копирование и соединение содержимого с содержимым предидущего
        копирования """
        log.info('Обнаружена комбинация клавиш COPY_JOIN')
        return
        # # pyautogui.hotkey('ctrl', 'c')
        # with self.keyboard.pressed(Key.ctrl):
        #     self.keyboard.press('c')
        #     self.keyboard.release('c')
        # #
        # # time.sleep(1)
        # previous_content = self.list_clipboard_data[-2]
        # new_content = self.list_clipboard_data[-1]
        # content = previous_content, new_content
        # joined_content = self.connector.join(content)
        # log.info(f'previous_content: {previous_content}'
        #          f'new_content: {new_content}'
        #          f'joined_content: {joined_content}')
        #
        # #
        # self.list_clipboard_data.append(joined_content)
        # # ---- Вызовит синхронизацию ---- #
        # pyperclip.copy(joined_content)
        # # self.clipboard.setText(joined_content, mode=self.clipboard.Clipboard)
        # # ------------------------------- #
        # self.callback_on_copy(joined_content, type_data='text')
        # log.info(f'Сработал copy join: '
        #          f'{list(reversed(self.list_clipboard_data))}')
    #

    def _share_clipboard(self):
        """ Поделиться содержимым буфера обмена """
        log.info('Обнаружена комбинация клавиш share_keys')
        #
        type_data = 'text'
        clipboard_data = self.clipboard.text()
        #
        self._callback_on_share(type_data, clipboard_data)

    def _connector_new_line(self) -> None:
        log.info('Обнаружена комбинация клавиш connector_new_line')
        self.connector = '\n'
    #

    def _connector_space_bar(self) -> None:
        log.info('Обнаружена комбинация клавиш connector_space_bar')
        self.connector = ' '
    #

    def _connector_none(self) -> None:
        log.info('Обнаружена комбинация клавиш connector_none')
        self.connector = ''
    #
    # --------------------------------------------------------------------------
