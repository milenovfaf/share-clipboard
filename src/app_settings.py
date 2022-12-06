import json
import re


class SettingsError(Exception):
    """ """


class EmtpyFileSettingsError(SettingsError):
    """ """


def get_default_app_settings():
    return AppSettings(
        copy_keys='<ctrl>+c',
    )


def str_validator(value):
    if value is None:
        return None
    #
    assert isinstance(value, str)
    value = re.sub(r'\s+', ' ', value)
    value = value.strip()
    if value == '':
        return None
    #
    return value


class AppSettings:
    def __init__(
            self,
            client_name:                str = None,
            client_name_for_sync:       str = None,
            client_name_for_share:      str = None,
            ip:                         str = None,
            port:                       str = None,
            copy_keys:                  str = '<ctrl>+c',
            copy_join_keys:             str = None,
            copy_share_keys:            str = None,
            connector_space_bar_keys:   str = None,
            connector_enter_keys:       str = None,
            connector_none_keys:        str = None,
    ):
        self.client_name = str_validator(client_name)
        self.client_name_for_sync = str_validator(client_name_for_sync)
        self.client_name_for_share = str_validator(client_name_for_share)
        self.ip = str_validator(ip)
        self.port = str_validator(port)
        self.copy_keys = str_validator(copy_keys)
        self.copy_join_keys = str_validator(copy_join_keys)
        self.copy_share_keys = str_validator(copy_share_keys)
        self.connector_space_bar_keys = str_validator(connector_space_bar_keys)
        self.connector_enter_keys = str_validator(connector_enter_keys)
        self.connector_none_keys = str_validator(connector_none_keys)

    def to_dict(self):
        return {
            'client_name':              self.client_name,
            'client_name_for_sync':     self.client_name_for_sync,
            'client_name_for_share':    self.client_name_for_share,
            'ip':                       self.ip,
            'port':                     self.port,
            'copy_keys':                self.copy_keys,
            'copy_join_keys':           self.copy_join_keys,
            'copy_share_keys':          self.copy_share_keys,
            'connector_space_bar_keys': self.connector_space_bar_keys,
            'connector_enter_keys':     self.connector_enter_keys,
            'connector_none_keys':      self.connector_none_keys,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    def save_to_file(self, file, flush=True):  # для сокета False
        dump = json.dumps(
            self.to_dict(),
            indent=2
        )
        file.write(
            dump,
        )
        if flush:
            file.flush()
        #

    @classmethod
    def load_from_file(cls, file):
        dump = file.read()
        if not dump:
            raise EmtpyFileSettingsError
        #
        data = json.loads(dump)
        return cls.from_dict(data)

