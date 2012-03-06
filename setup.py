#!/usr/bin/env python

from setuptools import setup

import fuse


setup(
    name='fusepy',
    version=fuse.__version__,
    description='Simple ctypes bindings for FUSE',
    author='Giorgos Verigakis',
    author_email='verigak@gmail.com',
    url='http://code.google.com/p/fusepy/',
    license='ISC',
    py_modules=['fuse']
)
