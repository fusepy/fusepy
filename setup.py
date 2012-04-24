#!/usr/bin/env python

from setuptools import setup, find_packages

from fuse import __version__

setup(
    name = 'fusepy',
    version = __version__,
    packages = find_packages(),

    description = 'Simple ctypes bindings for FUSE',
    author = 'Giorgos Verigakis',
    author_email = 'verigak@gmail.com',
    url = 'http://code.google.com/p/fusepy/',
    license = 'ISC',
)
