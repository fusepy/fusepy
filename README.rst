fusepy
======

``fusepy`` is a Python module that provides a simple interface to FUSE_ and
MacFUSE_. It's just one file and is implemented using ctypes.

The official version of ``fusepy`` is hosted on `Google Code`_, but was split
into 3 seperate files: fuse24.py, fuse.py, and fuse3.py. These versions were
for <Python2.5, <Python3.x, and Python3.x respectively. Unfortunately they were
not all maintained, and installing the package in Python3 did not work.

This repo mereges bits from all 3 files and combines them into one file. The
file is written in 2x syntax, but trying to pay attention to bytes and other
changes 3x would care about. The only incompatible changes between 2x and 3x
are the change in syntax for number literals and exceptions. These issues are
fixed using the 2to3 tool when installing the package, or runnning::

    2to3 -f numliterals -f except -w fuse.py


examples
--------
See some examples of how you can use fusepy:

:memory_: A simple memory filesystem
:loopback_: A loopback filesystem
:context_: Sample usage of fuse_get_context()
:sftp_: A simple SFTP filesystem (requires paramiko)

To get started download_ fusepy or just browse the source_.

fusepy requires FUSE 2.6 (or later) and runs on:

- Linux (i386, x86_64, PPC)
- Mac OS X (Intel, PowerPC)
- FreeBSD (i386, amd64)


.. _FUSE: http://fuse.sourceforge.net/
.. _MacFUSE: http://code.google.com/p/macfuse/
.. _`Google Code`: http://code.google.com/p/fusepy/
.. _memory: http://github.com/terencehonles/fusepy/tree/master/examples/memory.py
.. _loopback: http://github.com/terencehonles/fusepy/tree/master/examples/loopback.py
.. _context: http://github.com/terencehonles/fusepy/tree/master/examples/context.py
.. _sftp: http://github.com/terencehonles/fusepy/tree/master/examples/sftp.py
.. _download: https://github.com/terencehonles/fusepy/zipball/master
.. _source: http://github.com/terencehonles/fusepy/tree/master/
