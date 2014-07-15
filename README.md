fusepy
======

`fusepy` is a Python module that provides a simple interface to [FUSE][] and [MacFUSE][]. It’s just one file and is implemented using ctypes.

The original version of `fusepy` was hosted on [Google Code][], but is now [officially hosted on GitHub][].

`fusepy` is written in 2x syntax, but trying to pay attention to bytes and other changes 3x would care about. The only incompatible changes between 2x and 3x are the change in syntax for number literals and exceptions. These issues are fixed using the 2to3 tool when installing the package, or runnning:

    2to3 -f numliterals -f except -w fuse.py

examples
--------

See some examples of how you can use fusepy:

memory\_
A simple memory filesystem

loopback\_
A loopback filesystem

context\_
Sample usage of fuse\_get\_context()

sftp\_
A simple SFTP filesystem (requires paramiko)

To get started [download][] fusepy or just browse the [source][].

fusepy requires FUSE 2.6 (or later) and runs on:

-   Linux (i386, x86\_64, PPC)
-   Mac OS X (Intel, PowerPC)
-   FreeBSD (i386, amd64)

  [FUSE]: http://fuse.sourceforge.net/
  [MacFUSE]: http://code.google.com/p/macfuse/
  [Google Code]: http://code.google.com/p/fusepy/
  [officially hosted on GitHub]: source_
  [download]: https://github.com/terencehonles/fusepy/zipball/master
  [source]: http://github.com/terencehonles/fusepy

### TODO
  * Cleanup           DONE
  * Restructure       DONE
  * Add minimal docs
  * Build on rtd      DONE
  * Tests
  * Add travis
