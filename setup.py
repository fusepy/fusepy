#!/usr/bin/env python

from __future__ import with_statement

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
    version = '2.0.2',

    description = 'Simple ctypes bindings for FUSE',
    long_description = documentation,
    author = 'Giorgos Verigakis',
    author_email = 'verigak@gmail.com',
    maintainer = 'Terence Honles',
    maintainer_email = 'terence@honles.com',
    license = 'ISC',
    py_modules=['fuse'],
    url = 'http://github.com/terencehonles/fusepy',

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
