# -*- coding: utf-8 -*-
import pkgutil
import os
import sys
import time

def millitime():
    return int(round(time.time() * 1000))

def get_root_path(import_name):
    mod = sys.modules.get(import_name)
    if mod is None and hasattr(mod, '__file__'):
        return os.path.dirname(os.path.abspath(mod.__file__))

    loader = pkgutil.get_loader(import_name)

    if loader is None or import_name == '__main__':
        return os.getcwd()

    if hasattr(loader, 'get_filename'):
        filepath = loader.get_filename(import_name)
    else:
        __import__(import_name)
        filepath = sys.modules[import_name].__file__

    return os.path.dirname(os.path.abspath(filepath))
