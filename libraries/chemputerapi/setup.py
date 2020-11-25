#!/usr/bin/python

from setuptools import setup
import os.path
from glob import iglob

VERSION = '2.0.dev0'
NAME = 'ChemputerAPI'

setup(
    name=NAME,
    version=VERSION,
    package_data={'':['docs/*'],},
    packages=['ChemputerAPI'],
    zip_safe=True,
    author='Cronin Group',
    license='See LICENSE.txt',
    description='API to control Chemputer pumps and valves.',
    platforms='any',
)
