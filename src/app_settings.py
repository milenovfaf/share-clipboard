import json
import re


class SettingsError(Exception):
    """ """


class EmtpyFileSettingsError(SettingsError):
    """ """


def get_default_app_settings():
    return AppSettings(
        ip='127.0.0.1',
        port='7006',
        copy_join_keys='<shift>+<ctrl>+c',
        connector_new_line_keys='<ctrl>+1',
        connector_space_bar_keys='<ctrl>+2',
        connector_none_keys='<ctrl>+3',
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
            copy_join_keys:             str = None,
            share_keys:                 str = None,
            connector_new_line_keys:    str = None,
            connector_space_bar_keys:   str = None,
            connector_none_keys:        str = None,
    ):
        self.client_name = str_validator(client_name)
        self.client_name_for_sync = str_validator(client_name_for_sync)
        self.client_name_for_share = str_validator(client_name_for_share)
        self.ip = str_validator(ip)
        self.port = str_validator(port)
        self.copy_join_keys = str_validator(copy_join_keys)
        self.share_keys = str_validator(share_keys)
        self.connector_new_line_keys = str_validator(connector_new_line_keys)
        self.connector_space_bar_keys = str_validator(connector_space_bar_keys)
        self.connector_none_keys = str_validator(connector_none_keys)

    def to_dict(self):
        return {
            'client_name':              self.client_name,
            'client_name_for_sync':     self.client_name_for_sync,
            'client_name_for_share':    self.client_name_for_share,
            'ip':                       self.ip,
            'port':                     self.port,
            'copy_join_keys':           self.copy_join_keys,
            'share_keys':               self.share_keys,
            'connector_new_line_keys':  self.connector_new_line_keys,
            'connector_space_bar_keys': self.connector_space_bar_keys,
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

