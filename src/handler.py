import time
# import pyautogui
import pyperclip
from PyQt5 import QtWidgets, Qt, QtCore
from pynput.keyboard import Controller, Key
from pynput import keyboard
import logging

log = logging.getLogger(__name__)


class HotkeysCopyPasteHandler(object):
    def __init__(
            self,
            callback_on_copy,
            callback_on_copy_share,
    ):
        assert callable(callback_on_copy)
        self.callback_on_copy = callback_on_copy
        self.callback_on_copy_share = callback_on_copy_share
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

    def synchronizer_clipboard(self, received_clipboard_data):
        """ Синхронизация буфера между клиентами """
        log.info('Обнаружено изменение буфера обмена')
        clipboard_data = self.clipboard.text()  # Взять с буфера
        #
        if clipboard_data == received_clipboard_data:
            self.list_clipboard_data.append(clipboard_data)
            log.info(f'{list(reversed(self.list_clipboard_data))}')
            return
        #
        if clipboard_data == self.list_clipboard_data[-1]:
            return
        #
        self.list_clipboard_data.append(clipboard_data)
        self.callback_on_copy(clipboard_data)

        log.info(f'Сработала синхронизация: '
                 f'{list((self.list_clipboard_data[-3:]))}')

        if len(self.list_clipboard_data) >= 50:
            del self.list_clipboard_data[:30]
        #

    def _copy_join(self):
        """ Копирование и соединение содержимого с содержимым предидущего
        копирования """
        log.info('Обнаружена комбинация клавиш COPY_JOIN')
        # pyautogui.hotkey('ctrl', 'c')
        with self.keyboard.pressed(Key.ctrl):
            self.keyboard.press('c')
            self.keyboard.release('c')
        #
        # time.sleep(1)
        previous_content = self.list_clipboard_data[-2]
        new_content = self.list_clipboard_data[-1]
        content = previous_content, new_content
        joined_content = self.connector.join(content)
        log.info(f'previous_content: {previous_content}'
                 f'new_content: {new_content}'
                 f'joined_content: {joined_content}')

        #
        self.list_clipboard_data.append(joined_content)
        # ---- Вызовит синхронизацию ---- #
        pyperclip.copy(joined_content)
        # self.clipboard.setText(joined_content, mode=self.clipboard.Clipboard)
        # ------------------------------- #
        self.callback_on_copy(joined_content)
        log.info(f'Сработал copy join: '
                 f'{list(reversed(self.list_clipboard_data))}')
    #

    def _share_clipboard(self):
        """ Поделиться содержимым буфера обмена """
        log.info('Обнаружена комбинация клавиш share_keys')
        clipboard_data = self.clipboard.text()
        #
        self.callback_on_copy_share(clipboard_data)

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
