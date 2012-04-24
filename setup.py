#!/usr/bin/env python

from setuptools import setup

try:
    from lib2to3 import refactor
    fixers = set(refactor.get_fixers_from_package('lib2to3.fixes'))
except ImportError:
    fixers = set()

with open('README') as readme:
    documentation = readme.read()

setup(
    name = 'fusepy',
    version = '1.2',

    description = 'Simple ctypes bindings for FUSE',
    long_description = documentation,
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

    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Filesystems',
    ]
)
