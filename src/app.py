from PyQt5 import QtWidgets
import sys
import app_settings
import gui_qt
import handler
from functools import wraps
from pathlib import Path
from contextlib import contextmanager
import client
import pyperclip
import logging

log = logging.getLogger(__name__)


# ------------------------------------------------------------------------------


@contextmanager
def display_error(label_error, msg=None):
    """ Отображение ошибки в интерфэйсе """
    try:
        label_error.setText('')
        label_error.update()
        yield None
    except ConnectionError as e:
        log.exception(e)
        label_error.setText('Нет подключения к серверу')
        label_error.update()
    except Exception as e:
        log.exception(e)
        label_error.setText(f' {msg} ({e})')
        label_error.update()
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
            self._callback_on_copy, self._callback_on_copy_share
        )
        self.gui = gui_qt.ShowUiMainWindow(
            self.callback_settings_update
        )
        self.remote = client.Client(
            callback_server_msg=self._callback_receive_clipboard_content,
            callback_server_error_msg=self._callback_receive_error_msg,
        )
        self.settings = None

    def start_app(self):
        """ Старт """
        self.settings = _load_settings(self.settings_file_path)
        if self.settings is None:
            self.settings = _create_settings(self.settings_file_path)
        assert isinstance(self.settings, app_settings.AppSettings)
        #
        with display_error(
                self.gui.ui.label_error, 'Ошибка синтаксиса'
        ):
            self.hotkey_handler.start(self.settings)
        #
        self.gui.show_gui(self.settings)
        #
        if self.settings.client_name and self.settings.ip and self.settings.port:
            with display_error(
                    self.gui.ui.label_error
            ):
                self.remote.connect(self.settings)
            #
        #
    #

    def close_app(self):
        self.remote.disconnect(self.settings)

    # --------------------------------------------------------------------------

    @callback_error_alert
    def callback_settings_update(self, new_settings: app_settings.AppSettings):
        """ Рестарт c новыми настройками """
        self.settings = new_settings
        with open(self.settings_file_path, 'w') as file:
            self.settings.save_to_file(file)
        #
        with display_error(
                self.gui.ui.label_error, 'Ошибка синтаксиса'
        ):
            self.hotkey_handler.stop()
            self.hotkey_handler = handler.HotkeysCopyPasteHandler(
                self._callback_on_copy, self._callback_on_copy_share
            )
            self.hotkey_handler.start(self.settings)
            #
        #
        if self.settings.client_name and self.settings.ip and self.settings.port:
            with display_error(
                    self.gui.ui.label_error
            ):
                self.remote.disconnect(self.settings)
                self.remote = client.Client(
                    callback_server_msg=self._callback_receive_clipboard_content,
                    callback_server_error_msg=self._callback_receive_error_msg,
                )
                self.remote.connect(self.settings)
                #
            #
        #
    #

    @callback_error_alert
    def _callback_on_copy(self, clipboard_content):
        """ Отправка данных на сервер для клиента синхронизации """
        self.remote.send_clipboard_content(
            self.settings.client_name,
            self.settings.client_name_for_sync,
            # ----------- ^^^^^^ -------- ^^^^
            clipboard_content,
        )

    @callback_error_alert
    def _callback_on_copy_share(self, clipboard_content):
        """ Отправка данных на сервер для клиента с которым делимся """
        self.remote.send_clipboard_content(
            self.settings.client_name,
            self.settings.client_name_for_share,
            # ----------- ^^^^^ --------- ^^^^
            clipboard_content,
        )

    @callback_error_alert
    def _callback_receive_clipboard_content(self, client_name, clipboard_content):
        """ Получение данных буфера обмена от сервера и синхронизация """
        pyperclip.copy(clipboard_content)
        if client_name != self.settings.client_name_for_sync:
            self.remote.send_clipboard_content(
                self.settings.client_name,
                self.settings.client_name_for_sync,
                clipboard_content,
            )

    @callback_error_alert
    def _callback_receive_error_msg(self, error_msg):
        """ Получение сообщений об ошибке от сервера """
        self.gui.ui.label_error.setText(error_msg)
        self.gui.ui.label_error.update()

# ------------------------------------------------------------------------------


def main(file='settings.json'):
    window = QtWidgets.QApplication(sys.argv)
    app = App(file)
    app.start_app()
    return_code = window.exec()
    app.close_app()
    sys.exit(return_code)


if __name__ == '__main__':
    print('BEGIN')
    main()
    print('END')
#

