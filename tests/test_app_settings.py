import tempfile
import pytest
import json
import os
from app_settings import str_validator, string_to_list, AppSettings, \
    get_default_app_settings


@pytest.mark.parametrize('value, expected_result', [
    (' ', None), ('\n', None), ('\t', None), ('a', 'a'), (' a \t', 'a'),
    (' a b', 'ab'), (' a\nb', 'ab'), (' a\nb', 'ab'), ('a ,b', 'a,b'),
    ('<ctrl>+c', '<ctrl>+c'), (['name'], ['name'])
])
def test_str_validator(value, expected_result):
    assert str_validator(value) == expected_result


@pytest.mark.parametrize('value, expected_result', [
    ('a', ['a']), ('a,b', ['a', 'b']), (['name'], ['name'])
])
def test_string_to_list(value, expected_result):
    assert string_to_list(value) == expected_result


def test_get_default_app_settings():
    assert isinstance(
        get_default_app_settings(),
        AppSettings,
    )

# ------------------------------------------------------------------------------


def expected_data():
    expected_result = {
        'client_id': 'test_id',
        'client_name': 'test_name',
        'client_name_for_sync': ['test_name_sync'],
        'client_name_for_share': ['test_name_share'],
        'ip': '127.0.0.1',
        'port': '8080',
        'copy_join_keys': 'test_keys_join',
        'share_keys': 'test_keys_share',
        'connector_new_line_keys': 'test_keys_new_line',
        'connector_space_bar_keys': 'test_keys_space_bar',
        'connector_none_keys': None,
    }
    return expected_result


def temp_json_file():
    return tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')


def test_save_to_file():
    with temp_json_file() as temp_file:
        AppSettings(**expected_data()).save_to_file(temp_file)
        temp_file.flush()
        temp_file.close()

        with open(temp_file.name, 'r') as f:
            data = json.load(f)

        assert data == expected_data()
        os.unlink(temp_file.name)  # Удаляем временный файл


def test_load_from_file():

    with temp_json_file() as temp_file:
        dump = json.dumps(AppSettings(**expected_data()).to_dict())
        temp_file.write(dump)
        temp_file.flush()
        temp_file.close()
        with open(temp_file.name, 'r') as f:
            data = AppSettings.load_from_file(f)

    assert data.to_dict() == expected_data()
    os.unlink(temp_file.name)  # Удаляем временный файл


# ------------------------------------------------------------------------------
