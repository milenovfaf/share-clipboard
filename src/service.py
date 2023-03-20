import io
import os
import sys
import base64
import pkgutil
import datetime
import platform
import subprocess
import time
import chardet

from functools import wraps
from pathlib import Path
from contextlib import contextmanager

from PIL import Image
try:
    import win32clipboard
except:
    pass

import app_settings

import logging
log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


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


def get_base_path():
    """ Определение базовой дерикторию в зависимости от режима запуска """
    if getattr(sys, 'frozen', False):
        # Если приложение запущено в режиме "упакованном" с помощью PyInstaller
        base_path = sys._MEIPASS
    else:
        # Если приложение запущено в режиме "обычном" (не упакованном)
        base_path = os.path.abspath(".")
    return base_path


def get_desktop_path():
    """ Получение пути рабочего стола """
    if platform.system() == 'Windows':
        desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        return desktop_path
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    return desktop_path  # Unix


def open_file_with_os(file_path):
    """ Открыть файл средствами операционной системы """
    if platform.system() == 'Windows':
        os.startfile(file_path)  # Windows
    subprocess.run(['xdg-open', file_path])  # Linux


@contextmanager
def identify_os(func_linux, func_windows):
    system = platform.system()
    if system == 'Windows':
        yield func_windows
    elif system == 'Linux':
        yield func_linux

# ------------------------------------------------------------------------------


def get_decoded_data(str_data):
    log.info('service.get_decoded_data')
    data = str_data.encode('utf-8')
    decoded_data = base64.b64decode(data)
    return decoded_data


def get_encoded_data(binary_data):
    log.info('service.get_encoded_data')
    encoded_data = base64.b64encode(binary_data)
    encoded_data = encoded_data.decode('utf-8')
    return encoded_data
# ------------------------------------------------------------------------------


def get_clipboard_data_on_linux():
    """ Получение данных из буфера обмена на Linux """
    log.info('service.get_clipboard_data_on_linux')

    # ----------------------------------------- #
    def _get_data(arg):
        process = subprocess.Popen(
            ['xclip', '-o', '-selection', 'clipboard', '-t', arg],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        try:
            stdout, _ = process.communicate(timeout=4)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, _ = process.communicate()
            log.exception('service.get_clipboard_data_on_linux - '
                          'Превышено время ожидания ответа от процесса.')
            return None
        return stdout
    # ----------------------------------------- #

    data = _get_data('TARGETS')
    list_types = data.decode('utf-8').splitlines()
    #
    if 'text/plain' in list_types:
        data = _get_data('text/plain')
        #
        encoding = chardet.detect(data)['encoding']
        log.info(f'service.get_clipboard_data_on_linux -- ЭТО ТЕКСТ {encoding}')
        if encoding == 'utf-8':
            data = data.decode('utf-8')
        if encoding == 'ascii':
            data = data.decode('unicode_escape')
        #
        binary_data = None
        type_data = 'text/plain'
        return data, type_data, binary_data
    #
    if 'image/png' in list_types:
        log.info('service.get_clipboard_data_on_linux -- ЭТО ИЗОБРАЖЕНИЕ')
        binary_data = _get_data('image/png')
        if not binary_data:
            return
        data = get_encoded_data(binary_data)
        type_data = 'image/png'
        return data, type_data, binary_data
    #


def get_clipboard_data_on_windows():
    """ Получение данных из буфера обмена на Windows """
    log.info('service.get_clipboard_data_on_windows')
    win32clipboard.OpenClipboard()

    if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
        log.info('service.get_clipboard_data_on_windows -- ЭТО ТЕКСТ')
        data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        binary_data = None
        type_data = 'text/plain'
        win32clipboard.CloseClipboard()
        return data, type_data, binary_data
    #
    if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
        log.info('service.get_clipboard_data_on_windows -- ЭТО ИЗОБРАЖЕНИЕ')
        binary_data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
        data = get_encoded_data(binary_data)
        type_data = 'image/png'
        win32clipboard.CloseClipboard()
        return data, type_data, binary_data
    #
    win32clipboard.CloseClipboard()


def paste_data_in_clipboard_on_linux(data, type_data):
    if type_data == 'text/plain':
        process = subprocess.Popen(
            ['xclip', '-selection', 'clipboard'],
            stdin=subprocess.PIPE)
        process.communicate(input=data.encode('utf-8'))
    #
    if type_data == 'image/png':
        process = subprocess.Popen(
            ['xclip', '-selection', 'clipboard', '-t', 'image/png'],
            stdin=subprocess.PIPE)
        process.communicate(input=data)
    #


def paste_data_in_clipboard_on_windows(data, type_data):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()

    if type_data == 'text/plain':
        win32clipboard.SetClipboardText(data, win32clipboard.CF_UNICODETEXT)

    if type_data == 'image/png':
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)

    win32clipboard.CloseClipboard()

# ------------------------------------------------------------------------------


def delete_cash_file(directory):
    files = os.listdir(directory)
    files = sorted(
        files, key=lambda f: os.path.getctime(
            os.path.join(directory, f)
        ))
    if len(files) > 10:
        os.remove(os.path.join(directory, files[-1]))


def create_image_file(image_bytes, format_img, directory=None):
    log.debug(f'App.create_image_file')
    #
    image = io.BytesIO(image_bytes)
    image = Image.open(image)
    #
    now = datetime.datetime.now()
    file_name = now.strftime('%Y-%m-%d_%H-%M-%S.')
    #
    file_name = file_name + format_img
    #
    if directory:
        absolute_file_path = os.path.join(directory, file_name)
        image.save(absolute_file_path)
        return absolute_file_path
    #
    directory = 'images'
    current_directory = os.getcwd()  # Текущая дерриктория
    absolute_directory = os.path.join(current_directory, directory)
    if not os.path.exists(absolute_directory):
        os.makedirs(absolute_directory)
    #
    absolute_file_path = os.path.join(absolute_directory, file_name)
    image.save(absolute_file_path)
    delete_cash_file(absolute_directory)
    return absolute_file_path

# ------------------------------------------------------------------------------



