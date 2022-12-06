from pynput.keyboard import Controller, Key
from pynput import keyboard
import pyperclip


class HotkeysCopyPasteHandler(object):
    def __init__(
            self,
            callback_on_copy,
            callback_on_copy_share,
    ):
        assert callable(callback_on_copy)
        self.callback_on_copy = callback_on_copy
        self.callback_on_copy_share = callback_on_copy_share
        self.keyboard = Controller()
        self.kh = None
        self.connector = '\n'
        self.list_clipboard_content = ['', '']
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
            (app_settings.copy_keys,                self._copy),
            (app_settings.copy_join_keys,           self._copy_join),
            (app_settings.copy_share_keys,          self._copy_share),
            (app_settings.connector_space_bar_keys, self._connector_space_bar),
            (app_settings.connector_enter_keys,     self._connector_enter),
            (app_settings.connector_none_keys,      self._connector_none),
        ]:
            if hot_key_map is None:
                continue
            #
            callback_set[hot_key_map] = callback
        #
        self.kh = keyboard.GlobalHotKeys(callback_set)  # <<<<<<<<<<<<<<
    # --------------------------------------------------------------------------

    def _connector_enter(self) -> None:
        self.connector = '\n'
    #

    def _connector_space_bar(self) -> None:
        self.connector = ' '
    #

    def _connector_none(self) -> None:
        self.connector = ''
    #

    def _copy(self):
        """ Копирование и синхронизация буфера между клиентами """
        print('Обнаружена комбинация клавиш Ctrl+C')
        clipboard_content = pyperclip.paste()
        self.list_clipboard_content.append(clipboard_content)
        self.callback_on_copy(clipboard_content)

        print(self.list_clipboard_content)

        if len(self.list_clipboard_content) >= 50:
            del self.list_clipboard_content[:30]
    #

    def _copy_join(self):
        """ Копирование и соединение содержимого с содержимым предидущего
        копирования """
        print('Обнаружена комбинация клавиш copy join')
        with self.keyboard.pressed(Key.ctrl):
            self.keyboard.press('c')
            self.keyboard.release('c')
        #
        previous_content = self.list_clipboard_content[-2]
        new_content = self.list_clipboard_content[-1]
        content = previous_content, new_content
        joined_content = self.connector.join(content)
        #
        pyperclip.copy(joined_content)
        self.list_clipboard_content.append(joined_content)
        #
        self.callback_on_copy(joined_content)
        print(self.list_clipboard_content)
    #

    def _copy_share(self):
        """ Поделиться содержимым буфера обмена """
        print('Обнаружена комбинация клавиш copy share')
        clipboard_content = pyperclip.paste()
        #
        self.callback_on_copy_share(clipboard_content)
    # --------------------------------------------------------------------------
