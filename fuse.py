# Copyright (c) 2008 Giorgos Verigakis <verigak@gmail.com>
# 
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from ctypes import *
from ctypes.util import find_library
from errno import EFAULT
from platform import machine, system
from traceback import print_exc


c_blkcnt_t = c_int64
c_blksize_t = c_long
c_fsblkcnt_t = c_ulong
c_fsfilcnt_t = c_ulong
c_gid_t = c_uint
c_ino_t = c_ulong
c_off_t = c_int64
c_time_t = c_long
c_uid_t = c_uint


class c_timespec(Structure):
    _fields_ = [('tv_sec', c_time_t), ('tv_nsec', c_long)]


class c_utimbuf(Structure):
    _fields_ = [('actime', c_time_t), ('modtime', c_time_t)]


_system = system()

if _system == 'Darwin':
    c_dev_t = c_int32
    c_mode_t = c_uint16
    c_nlink_t = c_uint16
    
    class c_stat(Structure):
        _fields_ = [
                ('st_dev', c_dev_t),
                ('st_ino', c_ino_t),
                ('st_mode', c_mode_t),
                ('st_nlink', c_nlink_t),
                ('st_uid', c_uid_t),
                ('st_gid', c_gid_t),
                ('st_rdev', c_dev_t),
                ('st_atimespec', c_timespec),
                ('st_mtimespec', c_timespec),
                ('st_ctimespec', c_timespec),
                ('st_size', c_off_t),
                ('st_blocks', c_blkcnt_t),
                ('st_blksize', c_blksize_t),
        ]
elif _system == 'Linux':
    c_dev_t = c_ulonglong
    c_mode_t = c_uint
    c_nlink_t = c_ulong
    
    if machine() == 'x86_64':
        class c_stat(Structure):
            _fields_ = [
                    ('st_dev', c_dev_t),
                    ('st_ino', c_ino_t),
                    ('st_nlink', c_nlink_t),
                    ('st_mode', c_mode_t),
                    ('st_uid', c_uid_t),
                    ('st_gid', c_gid_t),
                    ('__pad0', c_int),
                    ('st_rdev', c_dev_t),
                    ('st_size', c_off_t),
                    ('st_blksize', c_blksize_t),
                    ('st_blocks', c_blkcnt_t),
                    ('st_atimespec', c_timespec),
                    ('st_mtimespec', c_timespec),
                    ('st_ctimespec', c_timespec),
            ]
    else:
        class c_stat(Structure):
            _fields_ = [
                    ('st_dev', c_dev_t),
                    ('__pad1', c_short),
                    ('st_ino', c_ino_t),
                    ('st_mode', c_mode_t),
                    ('st_nlink', c_nlink_t),
                    ('st_uid', c_uid_t),
                    ('st_gid', c_gid_t),
                    ('st_rdev', c_dev_t),
                    ('__pad2', c_short),
                    ('st_size', c_off_t),
                    ('st_blksize', c_blksize_t),
                    ('st_blocks', c_blkcnt_t),
                    ('st_atimespec', c_timespec),
                    ('st_mtimespec', c_timespec),
                    ('st_ctimespec', c_timespec),
            ]
else:
    raise NotImplementedError('%s is not supported.' % _system)


class c_statvfs(Structure):
    _fields_ = [
            ('f_bsize', c_ulong),
            ('f_frsize', c_ulong),
            ('f_blocks', c_fsblkcnt_t),
            ('f_bfree', c_fsblkcnt_t),
            ('f_bavail', c_fsblkcnt_t),
            ('f_files', c_fsfilcnt_t),
            ('f_ffree', c_fsfilcnt_t),
            ('f_favail', c_fsfilcnt_t),
            ('f_fsid', c_ulong),
            ('f_flag', c_ulong),
            ('f_namemax', c_ulong)
    ]


class fuse_file_info(Structure):
    _fields_ = [
            ('flags', c_int),
            ('fh_old', c_ulong),
            ('writepage', c_int),
            ('direct_io', c_uint, 1),
            ('keep_cache', c_uint, 1),
            ('flush', c_uint, 1),
            ('padding', c_uint, 29),
            ('fh', c_uint64),
            ('lock_owner', c_uint64)
    ]

fuse_fill_dir_t = CFUNCTYPE(c_int, c_voidp, c_char_p, POINTER(c_stat), c_off_t)
getattr_t = CFUNCTYPE(c_int, c_char_p, POINTER(c_stat))
readlink_t = CFUNCTYPE(c_int, c_char_p, POINTER(c_byte), c_size_t)
mknod_t = CFUNCTYPE(c_int, c_char_p, c_mode_t, c_dev_t)
mkdir_t = CFUNCTYPE(c_int, c_char_p, c_mode_t)
unlink_t = CFUNCTYPE(c_int, c_char_p)
rmdir_t = CFUNCTYPE(c_int, c_char_p)
symlink_t = CFUNCTYPE(c_int, c_char_p, c_char_p)
rename_t = CFUNCTYPE(c_int, c_char_p, c_char_p)
link_t = CFUNCTYPE(c_int, c_char_p, c_char_p)
chmod_t = CFUNCTYPE(c_int, c_char_p, c_mode_t)
chown_t = CFUNCTYPE(c_int, c_char_p, c_uid_t, c_gid_t)
truncate_t = CFUNCTYPE(c_int, c_char_p, c_off_t)
open_t = CFUNCTYPE(c_int, c_char_p, POINTER(fuse_file_info))
read_t = CFUNCTYPE(c_int, c_char_p, POINTER(c_byte), c_size_t, c_off_t, POINTER(fuse_file_info))
write_t = CFUNCTYPE(c_int, c_char_p, POINTER(c_byte), c_size_t, c_off_t, POINTER(fuse_file_info))
statfs_t = CFUNCTYPE(c_int, c_char_p, POINTER(c_statvfs))
flush_t = CFUNCTYPE(c_int, c_char_p, POINTER(fuse_file_info))
release_t = CFUNCTYPE(c_int, c_char_p, POINTER(fuse_file_info))
fsync_t = CFUNCTYPE(c_int, c_char_p, c_int, POINTER(fuse_file_info))
if _system == 'Darwin':
    setxattr_t = CFUNCTYPE(c_int, c_char_p, c_char_p, POINTER(c_byte), c_size_t, c_int, c_uint32)
    getxattr_t = CFUNCTYPE(c_int, c_char_p, c_char_p, POINTER(c_byte), c_size_t, c_uint32)
else:
    setxattr_t = CFUNCTYPE(c_int, c_char_p, c_char_p, POINTER(c_byte), c_size_t, c_int)
    getxattr_t = CFUNCTYPE(c_int, c_char_p, c_char_p, POINTER(c_byte), c_size_t)
listxattr_t = CFUNCTYPE(c_int, c_char_p, POINTER(c_byte), c_size_t)
removexattr_t = CFUNCTYPE(c_int, c_char_p, c_char_p)
opendir_t = CFUNCTYPE(c_int, c_char_p, POINTER(fuse_file_info))
readdir_t = CFUNCTYPE(c_int, c_char_p, c_voidp, fuse_fill_dir_t, c_off_t, POINTER(fuse_file_info))
releasedir_t = CFUNCTYPE(c_int, c_char_p, POINTER(fuse_file_info))
fsyncdir_t = CFUNCTYPE(c_int, c_char_p, c_int, POINTER(fuse_file_info))
init_t = CFUNCTYPE(c_voidp, c_voidp)
destroy_t = CFUNCTYPE(c_voidp)
access_t = CFUNCTYPE(c_int, c_char_p, c_int)
create_t = CFUNCTYPE(c_int, c_char_p, c_mode_t, POINTER(fuse_file_info))
ftruncate_t = CFUNCTYPE(c_int, c_char_p, c_off_t, POINTER(fuse_file_info))
fgetattr_t = CFUNCTYPE(c_int, c_char_p, POINTER(c_stat), POINTER(fuse_file_info))
lock_t = CFUNCTYPE(c_int, c_char_p, POINTER(fuse_file_info), c_int, c_voidp)
utimens_t = CFUNCTYPE(c_int, c_char_p, POINTER(c_utimbuf))
bmap_t = CFUNCTYPE(c_int, c_char_p, c_size_t, POINTER(c_ulonglong))


class fuse_operations(Structure):
    _fields_ = [
            ('getattr', getattr_t),
            ('readlink', readlink_t),
            ('getdir', c_voidp),    # Deprecated, use readdir
            ('mknod', mknod_t),
            ('mkdir', mkdir_t),
            ('unlink', unlink_t),
            ('rmdir', rmdir_t),
            ('symlink', symlink_t),
            ('rename', rename_t),
            ('link', link_t),
            ('chmod', chmod_t),
            ('chown', chown_t),
            ('truncate', truncate_t),
            ('utime', c_voidp),     # Deprecated, use utimens
            ('open', open_t),
            ('read', read_t),
            ('write', write_t),
            ('statfs', statfs_t),
            ('flush', flush_t),
            ('release', release_t),
            ('fsync', fsync_t),
            ('setxattr', setxattr_t),
            ('getxattr', getxattr_t),
            ('listxattr', listxattr_t),
            ('removexattr', removexattr_t),
            ('opendir', opendir_t),
            ('readdir', readdir_t),
            ('releasedir', releasedir_t),
            ('fsyncdir', fsyncdir_t),
            ('init', init_t),
            ('destroy', destroy_t),
            ('access', access_t),
            ('create', create_t),
            ('ftruncate', ftruncate_t),
            ('fgetattr', fgetattr_t),
            ('lock', lock_t),
            ('utimens', utimens_t),
            ('bmap', bmap_t)
    ]


class FuseError(BaseException):
    pass


def safe(func):
    def wrapper(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            return ret if ret is not None else -EFAULT
        except FuseError, e:
            return -e.message if e.message else -EFAULT
        except:
            print_exc()
            return -EFAULT
    return wrapper


class FUSE(object):
    """Low level FUSE operations. Assumes API version 2.6 or later.
       Shouldn't be subclassed under normal use."""
    
    def __init__(self, operations, mountpoint="/mnt", **kwargs):
        self.operations = operations
        
        if _system == 'Darwin':
            libiconv = CDLL(find_library("iconv"), RTLD_GLOBAL)
        libfuse = CDLL(find_library("fuse"))
        
        args = ['fuse']
        if kwargs.pop('foreground', False):
            args.append('-f')
        if kwargs.pop('debug', False):
            args.append('-d')
        if kwargs:
            args.append('-o')
            args.append(','.join(key if val == True else '%s=%s' % (key, val)
                    for key, val in kwargs.items()))
        args.append(mountpoint)
        argv = (c_char_p * len(args))(*args)
        
        fuse_ops = fuse_operations()
        for name, prototype in fuse_operations._fields_:
            method = getattr(self, name, None)
            if method:
                setattr(fuse_ops, name, prototype(method))
        
        libfuse.fuse_main_real(len(args), argv, pointer(fuse_ops), sizeof(fuse_ops), None)
        
    @safe
    def getattr(self, path, buf):
        return self.fgetattr(path, buf, None)
    
    @safe
    def readlink(self, path, buf, bufsize):
        ret = self.operations('readlink', path)
        memmove(buf, create_string_buffer(ret), bufsize)
        return 0
    
    @safe
    def mknod(self, path, mode, dev):
        return self.operations('mknod', path, mode, dev)
    
    @safe
    def mkdir(self, path, mode):
        return self.operations('mkdir', path, mode)
    
    @safe
    def unlink(self, path):
        return self.operations('unlink', path)
    
    @safe
    def rmdir(self, path):
        return self.operations('rmdir', path)
    
    @safe
    def symlink(self, source, target):
        return self.operations('symlink', source, target)
    
    @safe
    def rename(self, old, new):
        return self.operations('rename', old, new)
    
    @safe
    def link(self, source, target):
        return self.operations('link', source, target)
    
    @safe
    def chmod(self, path, mode):
        return self.operations('chmod', path, mode)
    
    @safe
    def chown(self, path, uid, gid):
        return self.operations('chown', path, uid, gid)
    
    @safe
    def truncate(self, path, length):
        return self.operations('truncate', path, length)
    
    @safe
    def open(self, path, fi):
        fi.contents.fh = self.operations('open', path, fi.contents.flags)
        return 0
    
    @safe
    def read(self, path, buf, size, offset, fi):
        ret = self.operations('read', path, size, offset, fi.contents.fh)
        memmove(buf, create_string_buffer(ret), size)
        return size
    
    @safe
    def write(self, path, buf, size, offset, fi):
        data = string_at(buf, size)
        return self.operations('write', path, data, offset, fi.contents.fh)
    
    @safe
    def statfs(self, path, buf):
        stv = buf.contents
        attrs = self.operations('statvfs', path)
        for key, val in attrs.items():
            if hasattr(stv, key):
                setattr(stv, key, val)
        return 0
    
    @safe
    def flush(self, path, fi):
        return self.operations('flush', path, fi.contents.fh)
    
    @safe
    def release(self, path, fi):
        return self.operations('release', path, fi.contents.fh)
    
    @safe
    def fsync(self, path, datasync, fi):
        return self.operations('fsync', path, datasync, fi.contents.fh)
    
    @safe
    def setxattr(self, path, name, value, size, options, *args):
        s = string_at(value, size)
        return self.operations('setxattr', path, name, s, options, *args)
    
    @safe
    def getxattr(self, path, name, value, size, *args):
        ret = self.operations('getxattr', path, name, *args)
        buf = create_string_buffer(ret)
        if bool(value):
            memmove(value, buf, size)
        return len(ret)
    
    @safe
    def listxattr(self, path, namebuf, size):
        ret = self.operations('listxattr', path)
        if not ret:
            return 0
        buf = create_string_buffer('\x00'.join(ret))
        if bool(namebuf):
            memmove(namebuf, buf, size)
        return len(buf)
    
    @safe
    def removexattr(self, path, name):
        return self.operations('removexattr', path, name)
    
    @safe
    def opendir(self, path, fi):
        fi.contents.fh = self.operations('opendir', path)
        return 0
    
    @safe
    def readdir(self, path, buf, filler, offset, fi):
        for name in self.operations('readdir', path, fi.contents.fh):
            filler(buf, name, None, 0)
        return 0
    
    @safe
    def releasedir(self, path, fi):
        return self.operations('releasedir', path, fi.contents.fh)
    
    @safe
    def fsyncdir(self, path, datasync, fi):
        return self.operations('fsyncdir', path, datasync, fi.contents.fh)
    
    @safe
    def init(self, conn):
        return self.operations('init')
    
    @safe
    def destroy(self):
        self.operations('destroy')
        return
    
    @safe
    def access(self, path, amode):
        return self.operations('access', path, amode)
    
    @safe
    def create(self, path, mode, fi):
        fi.contents.fh = self.operations('create', path, mode)
        return 0
    
    @safe
    def ftruncate(self, path, length, fi):
        return self.operations('truncate', path, length, fi.contents.fh)
    
    @safe
    def fgetattr(self, path, buf, fi):
        memset(buf, 0, sizeof(c_stat))
        st = buf.contents
        fh = fi.contents.fh if fi else None
        attrs = self.operations('getattr', path, fh)
        for key, val in attrs.items():
            if key in ('st_atime', 'st_mtime', 'st_ctime'):
                timespec = getattr(st, key + 'spec')
                timespec.tv_sec = int(val)
                timespec.tv_nsec = int((val - timespec.tv_sec) * 10 ** 9)
            elif hasattr(st, key):
                setattr(st, key, val)
        return 0
    
    @safe
    def lock(self, path, fi, cmd, lock):
        return self.operations('lock', path, fi.contents.fh, cmd, lock)
    
    @safe
    def utimens(self, path, buf):
        if buf:
            atime = buf.contents.actime
            mtime = buf.contents.modtime
        else:
            atime = mtime = 0
        return self.operations('utimens', path, atime, mtime)
    
    @safe
    def bmap(self, path, blocksize, idx):
        return self.operations('bmap', path, blocksize, idx)
        

from errno import EACCES, ENODATA, ENOENT
from stat import S_IFDIR

import logging


class FuseOperations(object):
    """This class should be subclassed and passed as an argument to the
       FUSE class on initialization. All operations should raise a
       FuseError exception on error.
       
       When in doubt of what an operation should do, check the FUSE header
       file or the corresponding system call man page."""
    
    def __call__(self, op, *args, **kwargs):
        logging.debug('%s: %s', op, args[:1])
        if not hasattr(self, op):
            return -EFAULT
        return getattr(self, op)(*args, **kwargs)
    
    def access(self, path, amode):
        return 0
    
    def chmod(self, path, mode):
        raise FuseError(EACCES)
    
    def chown(self, path, uid, gid):
        raise FuseError(EACCES)
    
    def create(self, path, mode):
        """Returns a numerical file handle."""
        raise FuseError(EACCES)
    
    def destroy(self):
        """Called on filesystem destruction."""
        return
    
    def flush(self, path, fh):
        return 0
    
    def fsync(self, path, datasync, fh):
        return 0
    
    def fsyncdir(self, path, datasync, fh):
        return 0
    
    def getattr(self, path, fh=None):
        """Returns a dictionary with keys identical to the `struct stat`
        C structure. `st_atime`, `st_mtime` and `st_ctime` should be floats."""
        if path != '/':
            raise FuseError(ENOENT)
        return dict(st_mode=(S_IFDIR | 0755), st_nlink=2)
    
    def getxattr(self, path, name, position=0):
        raise FuseError(ENODATA)
    
    def init(self):
        """Called on filesystem initialization."""
        return None
    
    def link(self, source, target):
        raise FuseError(EACCES)
    
    def listxattr(self, path):
        return []
    
    def mkdir(self, path, mode):
        raise FuseError(EACCES)
    
    def mknod(self, path, mode, dev):
        raise FuseError(EACCES)
    
    def open(self, path, flags):
        """Returns a numerical file handle."""
        raise FuseError(EACCES)
    
    def opendir(self, path):
        """Returns a numerical file handle."""
        return 0
    
    def read(self, path, size, offset, fh):
        """Returns a string containing the data requested."""
        raise FuseError(EACCES)
    
    def readdir(self, path, fh):
        return ['.', '..']
    
    def readlink(self, path):
        raise FuseError(EACCES)
    
    def release(self, path, fh):
        return 0
    
    def releasedir(self, path, fh):
        return 0
    
    def removexattr(self, path, name):
        raise FuseError(ENODATA)
    
    def rename(self, old, new):
        raise FuseError(EACCES)
    
    def rmdir(self, path):
        raise FuseError(EACCES)
    
    def setxattr(self, path, name, value, options, position=0):
        raise FuseError(ENODATA)
    
    def statvfs(self, path):
        return {}
    
    def symlink(self, source, target):
        raise FuseError(EACCES)
    
    def truncate(self, path, length, fh=None):
        raise FuseError(EACCES)
    
    def unlink(self, path):
        raise FuseError(EACCES)
    
    def utimens(self, path, atime, mtime):
        """If `atime`, `mtime` are zero, use current time."""
        return 0
    
    def write(self, path, data, offset, fh):
        raise FuseError(EACCES)
