#!/usr/bin/env python

from setuptools import setup

try:
    from lib2to3 import refactor
    fixers = set(refactor.get_fixers_from_package('lib2to3.fixes'))
except ImportError:
    fixers = set()

setup(
    name = 'fusepy',
    version = '1.2',

    description = 'Simple ctypes bindings for FUSE',
    author = 'Giorgos Verigakis',
    author_email = 'verigak@gmail.com',
    license = 'ISC',
    py_modules=['fuse'],

    use_2to3 = True,
    # only use the following fixers (everything else is already compatible)
    use_2to3_exclude_fixers = fixers - set([
        'lib2to3.fixes.fix_except',
        'lib2to3.fixes.fix_future',
        'lib2to3.fixes.fix_numliterals',
    ]),
)
