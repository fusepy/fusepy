#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

import logging
import paramiko

from errno import ENOENT

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn


class SFTP(LoggingMixIn, Operations):
    '''
    A simple SFTP filesystem. Requires paramiko: http://www.lag.net/paramiko/

    You need to be able to login to remote host without entering a password.
    '''

    def __init__(self, host, username=None, port=22):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.load_system_host_keys()
        self.client.connect(host, port=port, username=username)
        self.sftp = self.client.open_sftp()

    def chmod(self, path, mode):
        return self.sftp.chmod(path, mode)

    def chown(self, path, uid, gid):
        return self.sftp.chown(path, uid, gid)

    def create(self, path, mode):
        f = self.sftp.open(path, 'w')
        f.chmod(mode)
        f.close()
        return 0

    def destroy(self, path):
        self.sftp.close()
        self.client.close()

    def getattr(self, path, fh=None):
        try:
            st = self.sftp.lstat(path)
        except IOError:
            raise FuseOSError(ENOENT)

        return dict((key, getattr(st, key)) for key in (
            'st_atime', 'st_gid', 'st_mode', 'st_mtime', 'st_size', 'st_uid'))

    def mkdir(self, path, mode):
        return self.sftp.mkdir(path, mode)

    def read(self, path, size, offset, fh):
        f = self.sftp.open(path)
        f.seek(offset, 0)
        buf = f.read(size)
        f.close()
        return buf

    def readdir(self, path, fh):
        return ['.', '..'] + [name.encode('utf-8')
                              for name in self.sftp.listdir(path)]

    def readlink(self, path):
        return self.sftp.readlink(path)

    def rename(self, old, new):
        return self.sftp.rename(old, new)

    def rmdir(self, path):
        return self.sftp.rmdir(path)

    def symlink(self, target, source):
        return self.sftp.symlink(source, target)

    def truncate(self, path, length, fh=None):
        return self.sftp.truncate(path, length)

    def unlink(self, path):
        return self.sftp.unlink(path)

    def utimens(self, path, times=None):
        return self.sftp.utime(path, times)

    def write(self, path, data, offset, fh):
        f = self.sftp.open(path, 'r+')
        f.seek(offset, 0)
        f.write(data)
        f.close()
        return len(data)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', dest='login')
    parser.add_argument('host')
    parser.add_argument('mount')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    if not args.login:
        if '@' in args.host:
            args.login, _, args.host = args.host.partition('@')

    fuse = FUSE(
        SFTP(args.host, username=args.login),
        args.mount,
        foreground=True,
        nothreads=True,
        allow_other=True)
