import os
from functools import wraps
from pathlib import Path
from contextlib import contextmanager
from PyQt5 import QtGui, QtCore

import app_settings
import logging

log = logging.getLogger(__name__)


@contextmanager
def error_interceptor(gui, msg=None, success=False):
    """ Обработка ошибок """
    try:
        gui.show_msg(msg='')
        if success:
            gui.show_msg('Подключено к серверу', success)
            gui.show_icon('blue')
        yield None
    except (ConnectionError, ConnectionRefusedError) as e:
        log.exception(e)
        gui.show_msg('Нет подключения к серверу')
        gui.show_icon('red')
    except Exception as e:
        log.exception(e)
        gui.show_msg(f'{msg} ({e})')
        gui.show_icon('red')
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


def get_desktop_path():
    """ Получение пути рабочего стола """
    if os.name == 'nt':  # Windows
        desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        return desktop_path
    if os.name == 'posix':  # Unix
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        return desktop_path
    #


# ------------------------------------------------------------------------------


def load_settings(settings_file_path):
    """ Чтение файла настроек """
    log.debug(f'_load_settings - {settings_file_path}')
    if not Path(settings_file_path).exists():
        return
    #
    try:
        with open(settings_file_path, 'r') as file:
            old_settings = app_settings.AppSettings.load_from_file(file)
            return old_settings
        #
    except app_settings.EmtpyFileSettingsError as e:
        log.exception(e)
    #


def create_settings(settings_file_path):
    """ Создание файла настроек """
    log.debug(f'_create_settings - {settings_file_path}')
    #
    old_settings = app_settings.get_default_app_settings()
    with open(settings_file_path, 'w+') as file:
        old_settings.save_to_file(file)
    #
    return old_settings

# ------------------------------------------------------------------------------


def create_image_object(binary_image_data):
    """ Создание объекта изображения """
    image = QtGui.QImage.fromData(binary_image_data)
    image_buffer = QtCore.QBuffer()
    image_buffer.open(QtCore.QBuffer.ReadWrite)
    image.save(image_buffer, 'PNG')
    return image, image_buffer
