#!/usr/bin/env python

from __future__ import with_statement

from errno import EACCES, EPERM
from os.path import realpath
from sys import argv, exit
from threading import Lock

import os

from fuse import FUSE, FuseOSError, Operations


class Factors(Operations):
    def __init__(self, root):
        self.root = realpath(root)
        self.rwlock = Lock()

    def __call__(self, op, path, *args):
        return super(Factors, self).__call__(op, self.root + path, *args)

    def __path_to_int(self, path):
        return int(os.path.basename(path))

    def __factors(self, n):
        # cf. http://stackoverflow.com/questions/6800193/
        return list(set(reduce(list.__add__,
            ([str(i), str(n//i)] for i in range(1, int(n**0.5) + 1) if n % i == 0))))

    def access(self, path, mode):
        if not os.access(path, mode):
            raise FuseOSError(EACCES)

    def create(self, path, mode):
        return os.open(path, os.O_WRONLY | os.O_CREAT, mode)

    def flush(self, path, fh):
        return os.fsync(fh)

    def fsync(self, path, datasync, fh):
        return os.fsync(fh)

    def getattr(self, path, fh=None):
        st = os.lstat(path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
            'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def mkdir(self, path, mode):
        try:
            n = self.__path_to_int(path)
        except ValueError:
            raise FuseOSError(EPERM)
        retcode = os.mkdir(path, mode)
	if retcode:
	    return retcode
	for factor in self.__factors(n):
	    factor_path = os.path.join(path, factor)
	    self.create(factor_path, mode)

    def readdir(self, path, fh):
        return ['.', '..'] + os.listdir(path)

    rmdir = os.rmdir

    def statfs(self, path):
        stv = os.statvfs(path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))


if __name__ == '__main__':
    if len(argv) != 3:
        print('usage: %s <root> <mountpoint>' % argv[0])
        exit(1)

    fuse = FUSE(Factors(argv[1]), argv[2], foreground=True)
