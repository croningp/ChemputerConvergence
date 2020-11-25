#!/usr/bin/python

from setuptools import setup, find_packages
import os.path
from glob import iglob

VERSION = '1.1'
NAME = 'SerialLabware'

setup(
    name=NAME,
    version=VERSION,
    install_requires=['pyserial>=3.3',],
    package_data={'':['docs/*'],},
    packages=find_packages(),
    zip_safe=True,
    author='Cronin Group',
    license='See LICENSE.txt',
    description='Universal module to control laboratory hardware through serial port or TCP/IP connection',
    long_description='',
    platforms='any',
)
