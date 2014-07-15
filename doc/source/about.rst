About
======

``fusepy`` is a Python module that provides a simple interface to FUSE_ and
MacFUSE_. It's just one file and is implemented using ctypes.

The original version of ``fusepy`` was hosted on `Google Code`_, but is now
`officially hosted on GitHub`_.

``fusepy`` is written in 2x syntax, but trying to pay attention to bytes and
other changes 3x would care about. The only incompatible changes between 2x and
3x are the change in syntax for number literals and exceptions. These issues
are fixed using the 2to3 tool when installing the package, or runnning::

    2to3 -f numliterals -f except -w fuse.py
