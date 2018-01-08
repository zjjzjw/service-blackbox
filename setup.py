#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup (
    name='blackbox',
    version='2.2.5',
    author='ZhuangYuan, BaiJian, LiangShan',
    packages=['blackbox'],
    install_requires=[
         'aps==1.2.0.0.alpha1',
         'werkzeug==0.9.4',
         'pyzmq==14.0.0',
         'mysql-connector-python>=1.1.4',
         'msgpack-python>=0.4.0'
        ],

    entry_points = """

    [console_scripts]
    bbctl=blackbox.cli:main
    """,

    dependency_links = [
        'http://git.corp.anjuke.com/_aps/pyaps/archive/v1.2.0.0.alpha1.zip#egg=aps-1.2.0.0.alpha1'
    ]
)
