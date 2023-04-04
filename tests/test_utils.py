import os
import json
import subprocess
from unittest.mock import MagicMock, patch
import pytest

from app_settings import AppSettings
from utils import error_interceptor, load_settings, create_settings, \
    get_clipboard_data_on_linux
from tests.conftest import settings_file_path

# ------------------------------------------------------------------------------


def test_error_interceptor_with_success():
    gui = MagicMock()
    with error_interceptor(gui, success=True):
        pass
    gui.show_msg.assert_called_with('Подключено к серверу', True)
    gui.show_icon.assert_called_with('blue')


def test_error_interceptor_with_connection_error():
    gui = MagicMock()
    with error_interceptor(gui):
        raise ConnectionError()
    gui.show_msg.assert_called_with('Нет подключения к серверу')
    gui.show_icon.assert_called_with('red')


def test_error_interceptor_with_exception():
    gui = MagicMock()
    with error_interceptor(gui, msg='Ошибка'):
        raise ValueError('Test error')
    gui.show_msg.assert_called_with('Ошибка (Test error)')
    gui.show_icon.assert_called_with('red')


# ------------------------------------------------------------------------------

def temp_settings_file(tmp_path, test_data):
    file_path = os.path.join(tmp_path, 'settings.json')
    with open(file_path, 'w') as f:
        f.write(json.dumps(test_data))
        return file_path


# Тест, когда файл настроек существует и содержит данные
def test_load_settings_file_exists(tmp_path):
    # Создаем временный файл и записываем в него данные
    test_data = {
        "client_id": "0smbj9156kistydzkuzhkv3wdwbry9on",
        "client_name": "name",
        "client_name_for_sync": ["name"],
        "client_name_for_share": [],
        "ip": "45.141.77.236",
        "port": "7000",
        "copy_join_keys": None,
        "share_keys": "<shift>+<ctrl>+p",
        "connector_new_line_keys": "<ctrl>+1",
        "connector_space_bar_keys": "<ctrl>+2",
        "connector_none_keys": "<ctrl>+3"
    }
    file_path = temp_settings_file(tmp_path, test_data)
    settings = load_settings(file_path)
    assert settings.client_name == 'name'
    assert settings.client_name_for_sync == ['name']
    assert settings.copy_join_keys is None


def test_load_settings_file_not_exists(settings_file_path):
    assert load_settings(settings_file_path) is None


def test_create_settings(settings_file_path):
    create_settings(settings_file_path)
    assert os.path.exists(settings_file_path)

# ------------------------------------------------------------------------------

