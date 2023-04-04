import os
import pytest


@pytest.fixture(scope='function')
def settings_file_path(tmp_path):
    return os.path.join(tmp_path, 'settings.json')


