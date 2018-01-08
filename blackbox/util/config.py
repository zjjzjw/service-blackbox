# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import errno
import imp
import os

from werkzeug.utils import import_string
import sys

"""
steal from flask.config
"""

class ConfigAttribute(object):

    def __init__(self, name, get_converter=None):
        self.__name__ = name
        self.get_converter = get_converter

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        ret = obj.config[self.__name__]
        if self.get_converter is not None:
            ret = self.get_converter[ret]
        return ret

class Config(dict):

    def __init__(self, root_path, defaults=None):
        dict.__init__(self, defaults or {})
        self.root_path = root_path

    def from_object(self, obj):
        if isinstance(obj, basestring):
            obj = import_string(obj)
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def from_pyfile(self, filename, silent=False):
        filename = os.path.join(self.root_path, filename)
        d = imp.new_module('config')
        d.__file__ = filename
        try:
            execfile(filename, d.__dict__)
        except IOError, e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        self.from_object(d)
        return True
