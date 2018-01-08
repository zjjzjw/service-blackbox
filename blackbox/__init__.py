# -*- coding: utf-8
from threading import Lock

from blackbox.util.config import Config, ConfigAttribute
from blackbox.util.helpers import get_root_path
import sys


_logger_lock = Lock()

class BaseApplication(object):

    default_config = {
        'DEBUG': False,
        'LOGGER_NAME': None
    }

    debug_log_format = (
        '=== %(levelname)s in %(module)s [%(pathname)s:%(lineno)d] ===\n'
        '%(message)s\n'
    )

    log_format = (
        "[%(asctime)s %(levelname)s(%(process)d)] %(message)s"
    )

    debug = ConfigAttribute('DEBUG')
    def __init__(self, import_name):
        self.import_name = import_name
        self.root_path = get_root_path(import_name)
        self.logger_name = import_name
        self._logger = None
        self.config = self.make_config()
    def make_config(self):
        root_path = self.root_path
        return Config(root_path, self.default_config)

    @property
    def logger(self):
        if self._logger and self._logger.name == self.logger_name:
            return self._logger
        with _logger_lock:
            if self._logger and self._logger.name == self.logger_name:
                return self._logger
            from blackbox.util.logger import create_logger
            self._logger = rv = create_logger(self)
            return rv
