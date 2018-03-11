# Copyright (c) 2010 Giorgos Verigakis <verigak@gmail.com>
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
from __future__ import print_function, absolute_import, division

import contextlib
import ctypes
import errno
import os

from ctypes.util import find_library
from platform import machine, system
from signal import signal, SIGINT, SIG_DFL
from stat import S_IFDIR


_system = system()
_machine = machine()

_libfuse_path = os.environ.get('FUSE_LIBRARY_PATH')
if not _libfuse_path:
    if _system == 'Darwin':
        # libfuse dependency
        _libiconv = ctypes.CDLL(find_library('iconv'), ctypes.RTLD_GLOBAL)

        _libfuse_path = (find_library('fuse4x') or find_library('osxfuse') or
                         find_library('fuse'))
    else:
        _libfuse_path = find_library('fuse')

if not _libfuse_path:
    raise EnvironmentError('Unable to find libfuse')
else:
    _libfuse = ctypes.CDLL(_libfuse_path)

class LibFUSE(ctypes.CDLL):
    def __init__(self):
        if _system == 'Darwin':
            self.libiconv = _libiconv
        super(LibFUSE, self).__init__(_libfuse_path)

        self.fuse_mount.argtypes = (
            ctypes.c_char_p, ctypes.POINTER(fuse_args))

        self.fuse_mount.restype = ctypes.c_void_p

        self.fuse_lowlevel_new.argtypes = (
            ctypes.POINTER(fuse_args), ctypes.POINTER(fuse_lowlevel_ops),
            ctypes.c_size_t, ctypes.c_void_p)

        self.fuse_lowlevel_new.restype = ctypes.c_void_p
        self.fuse_set_signal_handlers.argtypes = (ctypes.c_void_p,)
        self.fuse_session_add_chan.argtypes = (
            ctypes.c_void_p, ctypes.c_void_p)
        self.fuse_session_loop.argtypes = (ctypes.c_void_p,)
        self.fuse_session_loop_mt.argtypes = (ctypes.c_void_p,)
        self.fuse_remove_signal_handlers.argtypes = (ctypes.c_void_p,)
        self.fuse_session_remove_chan.argtypes = (ctypes.c_void_p,)
        self.fuse_session_destroy.argtypes = (ctypes.c_void_p,)
        self.fuse_unmount.argtypes = (ctypes.c_char_p, ctypes.c_void_p)

        self.fuse_req_ctx.restype = ctypes.POINTER(fuse_ctx)
        self.fuse_req_ctx.argtypes = (fuse_req_t,)

        self.fuse_reply_err.argtypes = (fuse_req_t, ctypes.c_int)
        self.fuse_reply_attr.argtypes = (
            fuse_req_t, ctypes.c_void_p, ctypes.c_double)
        self.fuse_reply_entry.argtypes = (fuse_req_t, ctypes.c_void_p)
        self.fuse_reply_open.argtypes = (fuse_req_t, ctypes.c_void_p)
        self.fuse_reply_buf.argtypes = (
            fuse_req_t, ctypes.c_char_p, ctypes.c_size_t)
        self.fuse_reply_none.argtypes = (fuse_req_t,)
        self.fuse_reply_write.argtypes = (fuse_req_t, ctypes.c_size_t)
        self.fuse_reply_readlink.argtypes = (
            fuse_req_t, ctypes.c_char_p)
        self.fuse_reply_statfs.argtypes = (fuse_req_t, c_statvfs_p)
        self.fuse_reply_xattr.argtypes = (fuse_req_t, ctypes.c_size_t)
        self.fuse_reply_create.argtypes = (
            fuse_req_t, ctypes.c_void_p, ctypes.c_void_p)

        self.fuse_add_direntry.argtypes = (
            ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t,
            ctypes.c_char_p, c_stat_p, c_off_t)

class fuse_args(ctypes.Structure):
    _fields_ = [
        ('argc', ctypes.c_int),
        ('argv', ctypes.POINTER(ctypes.c_char_p)),
        ('allocated', ctypes.c_int),
    ]

class c_timespec(ctypes.Structure):
    _fields_ = [
        ('tv_sec', ctypes.c_long),
        ('tv_nsec', ctypes.c_long),
    ]

class c_stat(ctypes.Structure):
    pass    # Platform dependent

class c_statvfs(ctypes.Structure):
    pass    # Platform dependent

if _system == 'Darwin':
    ENOTSUP = 45

    c_dev_t = ctypes.c_int32
    c_fsblkcnt_t = ctypes.c_ulong
    c_fsfilcnt_t = ctypes.c_ulong
    c_gid_t = ctypes.c_uint32
    c_mode_t = ctypes.c_uint16
    c_off_t = ctypes.c_int64
    c_pid_t = ctypes.c_int32
    c_uid_t = ctypes.c_uint32
    c_stat._fields_ = [
        ('st_dev', c_dev_t),
        ('st_ino', ctypes.c_uint32),
        ('st_mode', c_mode_t),
        ('st_nlink', ctypes.c_uint16),
        ('st_uid', c_uid_t),
        ('st_gid', c_gid_t),
        ('st_rdev', c_dev_t),
        ('st_atimespec', c_timespec),
        ('st_mtimespec', c_timespec),
        ('st_ctimespec', c_timespec),
        ('st_size', c_off_t),
        ('st_blocks', ctypes.c_int64),
        ('st_blksize', ctypes.c_int32)]
elif _system == 'Linux':
    ENOTSUP = 95

    c_dev_t = ctypes.c_ulonglong
    c_fsblkcnt_t = ctypes.c_ulonglong
    c_fsfilcnt_t = ctypes.c_ulonglong
    c_gid_t = ctypes.c_uint
    c_mode_t = ctypes.c_uint
    c_off_t = ctypes.c_longlong
    c_pid_t = ctypes.c_int
    c_uid_t = ctypes.c_uint

    if _machine == 'x86_64':
        c_stat._fields_ = [
            ('st_dev', c_dev_t),
            ('st_ino', ctypes.c_ulong),
            ('st_nlink', ctypes.c_ulong),
            ('st_mode', c_mode_t),
            ('st_uid', c_uid_t),
            ('st_gid', c_gid_t),
            ('__pad0', ctypes.c_int),
            ('st_rdev', c_dev_t),
            ('st_size', c_off_t),
            ('st_blksize', ctypes.c_long),
            ('st_blocks', ctypes.c_long),
            ('st_atimespec', c_timespec),
            ('st_mtimespec', c_timespec),
            ('st_ctimespec', c_timespec)]
        c_statvfs._fields = [
            ('f_bsize', ctypes.c_ulong),
            ('f_frsize', ctypes.c_ulong),
            ('f_blocks', c_fsblkcnt_t),
            ('f_bfree', c_fsblkcnt_t),
            ('f_bavail', c_fsblkcnt_t),
            ('f_files', c_fsfilcnt_t),
            ('f_ffree', c_fsfilcnt_t),
            ('f_favail', c_fsfilcnt_t),
            ('f_fsid', ctypes.c_ulong),
            ('f_flag', ctypes.c_ulong),
            ('f_namemax', ctypes.c_ulong)]
    elif _machine == 'mips':
        c_stat._fields_ = [
            ('st_dev', c_dev_t),
            ('__pad1_1', ctypes.c_ulong),
            ('__pad1_2', ctypes.c_ulong),
            ('__pad1_3', ctypes.c_ulong),
            ('st_ino', ctypes.c_ulong),
            ('st_mode', c_mode_t),
            ('st_nlink', ctypes.c_ulong),
            ('st_uid', c_uid_t),
            ('st_gid', c_gid_t),
            ('st_rdev', c_dev_t),
            ('__pad2_1', ctypes.c_ulong),
            ('__pad2_2', ctypes.c_ulong),
            ('st_size', c_off_t),
            ('__pad3', ctypes.c_ulong),
            ('st_atimespec', c_timespec),
            ('__pad4', ctypes.c_ulong),
            ('st_mtimespec', c_timespec),
            ('__pad5', ctypes.c_ulong),
            ('st_ctimespec', c_timespec),
            ('__pad6', ctypes.c_ulong),
            ('st_blksize', ctypes.c_long),
            ('st_blocks', ctypes.c_long),
            ('__pad7_1', ctypes.c_ulong),
            ('__pad7_2', ctypes.c_ulong),
            ('__pad7_3', ctypes.c_ulong),
            ('__pad7_4', ctypes.c_ulong),
            ('__pad7_5', ctypes.c_ulong),
            ('__pad7_6', ctypes.c_ulong),
            ('__pad7_7', ctypes.c_ulong),
            ('__pad7_8', ctypes.c_ulong),
            ('__pad7_9', ctypes.c_ulong),
            ('__pad7_10', ctypes.c_ulong),
            ('__pad7_11', ctypes.c_ulong),
            ('__pad7_12', ctypes.c_ulong),
            ('__pad7_13', ctypes.c_ulong),
            ('__pad7_14', ctypes.c_ulong)]
    elif _machine == 'ppc':
        c_stat._fields_ = [
            ('st_dev', c_dev_t),
            ('st_ino', ctypes.c_ulonglong),
            ('st_mode', c_mode_t),
            ('st_nlink', ctypes.c_uint),
            ('st_uid', c_uid_t),
            ('st_gid', c_gid_t),
            ('st_rdev', c_dev_t),
            ('__pad2', ctypes.c_ushort),
            ('st_size', c_off_t),
            ('st_blksize', ctypes.c_long),
            ('st_blocks', ctypes.c_longlong),
            ('st_atimespec', c_timespec),
            ('st_mtimespec', c_timespec),
            ('st_ctimespec', c_timespec)]
    else:
        # i686, use as fallback for everything else
        c_stat._fields_ = [
            ('st_dev', c_dev_t),
            ('__pad1', ctypes.c_ushort),
            ('__st_ino', ctypes.c_ulong),
            ('st_mode', c_mode_t),
            ('st_nlink', ctypes.c_uint),
            ('st_uid', c_uid_t),
            ('st_gid', c_gid_t),
            ('st_rdev', c_dev_t),
            ('__pad2', ctypes.c_ushort),
            ('st_size', c_off_t),
            ('st_blksize', ctypes.c_long),
            ('st_blocks', ctypes.c_longlong),
            ('st_atimespec', c_timespec),
            ('st_mtimespec', c_timespec),
            ('st_ctimespec', c_timespec),
            ('st_ino', ctypes.c_ulonglong)]
        c_statvfs._fields = [
            ('f_bsize', ctypes.c_ulong),
            ('f_frsize', ctypes.c_ulong),
            ('f_blocks', c_fsblkcnt_t),
            ('f_bfree', c_fsblkcnt_t),
            ('f_bavail', c_fsblkcnt_t),
            ('f_files', c_fsfilcnt_t),
            ('f_ffree', c_fsfilcnt_t),
            ('f_favail', c_fsfilcnt_t),
            ('f_fsid', ctypes.c_ulong),
            ('__f_unused', ctypes.c_int),
            ('f_flag', ctypes.c_ulong),
            ('f_namemax', ctypes.c_ulong)]
else:
    raise NotImplementedError('%s is not supported.' % _system)

class fuse_file_info(ctypes.Structure):
    _fields_ = [
        ('flags', ctypes.c_int),
        ('fh_old', ctypes.c_ulong),
        ('writepage', ctypes.c_int),
        ('direct_io', ctypes.c_uint, 1),
        ('keep_cache', ctypes.c_uint, 1),
        ('flush', ctypes.c_uint, 1),
        ('nonseekable', ctypes.c_uint, 1),
        ('flock_release', ctypes.c_uint, 1),
        ('padding', ctypes.c_uint, 27),
        ('fh', ctypes.c_uint64),
        ('lock_owner', ctypes.c_uint64)]

class fuse_ctx(ctypes.Structure):
    _fields_ = [
        ('uid', c_uid_t),
        ('gid', c_gid_t),
        ('pid', c_pid_t),
    ]

class fuse_forget_data(ctypes.Structure):
    _fields_ = [
        ('ino', ctypes.c_uint64),  # fuse_ino_t on libfuse3
        ('nlookup', ctypes.c_uint64),
    ]

fuse_ino_t = ctypes.c_ulong
fuse_req_t = ctypes.c_void_p
c_stat_p = ctypes.POINTER(c_stat)
c_statvfs_p = ctypes.POINTER(c_statvfs)
c_bytes_p = ctypes.POINTER(ctypes.c_byte)
fuse_file_info_p = ctypes.POINTER(fuse_file_info)
fuse_forget_data_p = ctypes.POINTER(fuse_forget_data)

FUSE_SET_ATTR = ('st_mode', 'st_uid', 'st_gid', 'st_size', 'st_atime', 'st_mtime')

class fuse_entry_param(ctypes.Structure):
    _fields_ = [
        ('ino', fuse_ino_t),
        ('generation', ctypes.c_ulong),
        ('attr', c_stat),
        ('attr_timeout', ctypes.c_double),
        ('entry_timeout', ctypes.c_double),
    ]

class fuse_lowlevel_ops(ctypes.Structure):
    _fields_ = [
        ('init', ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)),
        ('destroy', ctypes.CFUNCTYPE(None, ctypes.c_void_p)),

        ('lookup', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_char_p)),

        ('forget', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_ulong)),  # nlookup is uint64_t in libfuse3

        ('getattr', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, fuse_file_info_p)),

        ('setattr', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, c_stat_p, ctypes.c_int,
            fuse_file_info_p)),

        ('readlink', ctypes.CFUNCTYPE(None, fuse_req_t, fuse_ino_t)),

        ('mknod', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_char_p, c_mode_t,
            c_dev_t)),

        ('mkdir', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_char_p, c_mode_t)),

        ('unlink', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_char_p)),

        ('rmdir', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_char_p)),

        ('symlink', ctypes.CFUNCTYPE(
            None, fuse_req_t, ctypes.c_char_p, fuse_ino_t, ctypes.c_char_p)),

        ('rename', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_char_p, fuse_ino_t,
            ctypes.c_char_p)),  # There is an extra argument `unsigned int flags` in libfuse3

        ('link', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, fuse_ino_t, ctypes.c_char_p)),

        ('open', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, fuse_file_info_p)),

        ('read', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_size_t, c_off_t,
            fuse_file_info_p)),

        ('write', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, c_bytes_p, ctypes.c_size_t,
            c_off_t, fuse_file_info_p)),

        ('flush', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, fuse_file_info_p)),

        ('release', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, fuse_file_info_p)),

        ('fsync', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_int, fuse_file_info_p)),

        ('opendir', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, fuse_file_info_p)),

        ('readdir', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_size_t, c_off_t,
            fuse_file_info_p)),

        ('releasedir', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, fuse_file_info_p)),

        ('fsyncdir', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_int, fuse_file_info_p)),

        ('statfs', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t)),

        ('setxattr', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_char_p, c_bytes_p, ctypes.c_size_t, ctypes.c_int)),

        ('getxattr', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_char_p, ctypes.c_size_t)),

        ('listxattr', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_size_t)),

        ('removexattr', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_char_p)),

        ('access', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_int)),

        ('create', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_char_p, c_mode_t, fuse_file_info_p)),

        ('getlk', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, fuse_file_info_p, ctypes.c_void_p)),

        ('setlk', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, fuse_file_info_p, ctypes.c_void_p, ctypes.c_int)),

        ('bmap', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_size_t, ctypes.c_uint64)),

        ('ioctl', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_int, ctypes.c_void_p, fuse_file_info_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t)),

        ('poll', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, fuse_file_info_p, ctypes.c_void_p)),

        ('write_buf', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_void_p, c_off_t, fuse_file_info_p)),

        ('retrieve_reply', ctypes.CFUNCTYPE(
            None, fuse_req_t, ctypes.c_void_p, fuse_ino_t, c_off_t, ctypes.c_void_p)),

        ('forget_multi', ctypes.CFUNCTYPE(
            None, fuse_req_t, ctypes.c_size_t, fuse_forget_data_p)),

        ('flock', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, fuse_file_info_p, ctypes.c_int)),

        ('fallocate', ctypes.CFUNCTYPE(
            None, fuse_req_t, fuse_ino_t, ctypes.c_int, c_off_t, c_off_t, fuse_file_info_p)),

        # readdirplus only exists in libfuse3
        #('readdirplus', ctypes.CFUNCTYPE(
            #None, fuse_req_t, fuse_ino_t, ctypes.c_size_t, c_off_t, fuse_file_info_p)),
    ]

def stat_to_dict(p):
    try:
        d = {}
        x = p.contents
        for key, type in x._fields_:
            if key in ('st_atimespec', 'st_mtimespec', 'st_ctimespec'):
                ts = getattr(x, key)
                key = key[:-4]      # Lose the "spec"
                d[key] = ts.tv_sec + ts.tv_nsec / 10 ** 9
            else:
                d[key] = getattr(x, key)
        return d
    except ValueError:
        return {}

def dict_to_stat(d):
    for key in ('st_atime', 'st_mtime', 'st_ctime'):
        if key in d:
            val = d[key]
            sec = int(val)
            nsec = int((val - sec) * 10 ** 9)
            d[key + 'spec'] = c_timespec(sec, nsec)
    return c_stat(**d)

def setattr_mask_to_list(mask):
    return [FUSE_SET_ATTR[i] for i in range(len(FUSE_SET_ATTR)) if mask & (1 << i)]

class FUSELL(object):
    def __init__(self, mountpoint, raw_fi=False, encoding='utf-8', encode=None,
                 decode=None, nothreads=False, debug=False, **kwargs):
        self.libfuse = LibFUSE()

        if encode is None:
            if hasattr(os, 'fsencode'):
                encode = os.fsencode
            else:
                encode = lambda s: s.encode(self.encoding)
        if decode is None:
            if hasattr(os, 'fsdecode'):
                decode = os.fsdecode
            else:
                decode = lambda s: s.decode(self.encoding)

        self.encoding = encoding
        self.encode = encode
        self.decode = decode
        self.raw_fi = raw_fi

        mountpoint = self.encode(mountpoint)
        fuse_ops = fuse_lowlevel_ops()

        for name, prototype in fuse_lowlevel_ops._fields_:
            method = getattr(self, 'fuse_' + name, None) or getattr(self, name, None)
            if method:
                setattr(fuse_ops, name, prototype(method))

        args = ['fuse']

        try:
            old_handler = signal(SIGINT, SIG_DFL)
        except ValueError:
            old_handler = SIG_DFL

        if debug:
            args.append('-d')

        kwargs.setdefault('fsname', self.__class__.__name__)
        args.append('-o')
        args.append(','.join(self._normalize_fuse_options(**kwargs)))

        args = [self.encode(arg) for arg in args]
        argv = fuse_args(len(args), (ctypes.c_char_p * len(args))(*args), 0)

        try:
            signal(SIGINT, old_handler)
        except ValueError:
            pass

        @contextlib.contextmanager
        def make_chan():
            chan = self.libfuse.fuse_mount(mountpoint, argv)
            assert chan
            try:
                yield chan
            finally:
                self.libfuse.fuse_unmount(mountpoint, chan)

        @contextlib.contextmanager
        def make_session():
            session = self.libfuse.fuse_lowlevel_new(
                argv, ctypes.byref(fuse_ops), ctypes.sizeof(fuse_ops), None)
            assert session
            try:
                yield session
            finally:
                self.libfuse.fuse_session_destroy(session)

        @contextlib.contextmanager
        def connect_chan_to_session(chan, session):
            self.libfuse.fuse_session_add_chan(session, chan)
            try:
                yield
            finally:
                self.libfuse.fuse_session_remove_chan(chan)

        @contextlib.contextmanager
        def use_fuse_signal_handlers(session):
            err = self.libfuse.fuse_set_signal_handlers(session)
            assert err == 0
            try:
                yield
            finally:
                err = self.libfuse.fuse_remove_signal_handlers(session)
                assert err == 0

        @contextlib.contextmanager
        def python_default_signals():
            try:
                old_handler = signal.signal(signal.SIGINT, signal.SIG_DFL)
            except ValueError:
                old_handler = signal.SIG_DFL
            try:
                yield
            finally:
                try:
                    signal.signal(signal.SIGINT, old_handler)
                except ValueError:
                    pass

        with make_chan() as chan:
            with make_session() as session:
                with connect_chan_to_session(chan, session):
                    with python_default_signals():
                        with use_fuse_signal_handlers(session):
                            if nothreads:
                                err = self.libfuse.fuse_session_loop(session)
                            else:
                                err = self.libfuse.fuse_session_loop_mt(
                                    session)
                            assert err == 0

    @staticmethod
    def _normalize_fuse_options(**kargs):
        for key, value in kargs.items():
            if isinstance(value, bool):
                if value is True: yield key
            else:
                yield '%s=%s' % (key, value)

    def reply_err(self, req, err):
        return self.libfuse.fuse_reply_err(req, err)

    def reply_none(self, req):
        self.libfuse.fuse_reply_none(req)

    def reply_entry(self, req, entry):
        entry['attr'] = c_stat(**entry['attr'])
        e = fuse_entry_param(**entry)
        self.libfuse.fuse_reply_entry(req, ctypes.byref(e))

    def reply_attr(self, req, attr, attr_timeout):
        st = dict_to_stat(attr)
        return self.libfuse.fuse_reply_attr(
            req, ctypes.byref(st), ctypes.c_double(attr_timeout))

    def reply_readlink(self, req, link):
        return self.libfuse.fuse_reply_readlink(
            req, link)

    def reply_open(self, req, fi=None):
        if fi:
            fi = fuse_file_info(**fi)
        else:
            fi = fuse_file_info()
        return self.libfuse.fuse_reply_open(req, ctypes.byref(fi))

    def reply_write(self, req, count):
        return self.libfuse.fuse_reply_write(req, count)

    def reply_buf(self, req, buf):
        return self.libfuse.fuse_reply_buf(req, buf, len(buf))

    def reply_statfs(self, req, d):
        s = c_statvfs(**d)
        return self.libfuse.fuse_reply_statfs(req, s)

    def reply_xattr(self, req, value, max_size):
        if max_size == 0:
            return self.libfuse.fuse_reply_xattr(req, len(value))
        if len(value) > max_size:
            return self.libfuse.fuse_reply_err(req, errno.ERANGE)
        return self.reply_buf(req, value)

    def reply_listxattr(self, req, names, size):
        buf = b"".join(self.encode(name) + b"\0" for name in names)
        return self.reply_xattr(req, buf, size)

    def reply_create(self, req, entry, fi=None):
        entry['attr'] = c_stat(**entry['attr'])
        e = fuse_entry_param(**entry)
        if fi:
            fi = fuse_file_info(**fi)
        else:
            fi = fuse_file_info()
        self.libfuse.fuse_reply_create(req, ctypes.byref(e), ctypes.byref(fi))

    def reply_readdir(self, req, size, off, entries):
        bufsize = 0
        sized_entries = []
        for name, attr in entries:
            name = self.encode(name)
            entsize = self.libfuse.fuse_add_direntry(req, None, 0, name, None, 0)
            sized_entries.append((name, attr, entsize))
            bufsize += entsize

        next = 0
        buf = ctypes.create_string_buffer(bufsize)
        for name, attr, entsize in sized_entries:
            entbuf = ctypes.cast(
                ctypes.addressof(buf) + next, ctypes.c_char_p)
            st = c_stat(**attr)
            next += entsize
            self.libfuse.fuse_add_direntry(
                req, entbuf, entsize, name, ctypes.byref(st), next)

        if off < bufsize:
            buf = ctypes.cast(
                ctypes.addressof(buf) + off, ctypes.c_char_p) if off else buf
            return self.libfuse.fuse_reply_buf(req, buf, min(bufsize - off, size))
        else:
            return self.libfuse.fuse_reply_buf(req, None, 0)


    # If you override the following methods you should reply directly
    # with the self.libfuse.fuse_reply_* methods.

    def get_fi(self, fip):
        if not fip:
            return None
        if self.raw_fi:
            return fip.contents
        return fip.contents.fh

    def fuse_lookup(self, req, parent, name):
        self.lookup(req, parent, self.decode(name))

    def fuse_getattr(self, req, ino, fip):
        self.getattr(req, ino, self.get_fi(fip))

    def fuse_setattr(self, req, ino, attr, to_set, fip):
        attr_dict = stat_to_dict(attr)
        to_set_list = setattr_mask_to_list(to_set)
        self.setattr(req, ino, attr_dict, to_set_list, self.get_fi(fip))

    def fuse_mknod(self, req, parent, name, mode, rdev):
        self.mknod(req, parent, self.decode(name), mode, rdev)

    def fuse_mkdir(self, req, parent, name, mode):
        self.mkdir(req, parent, self.decode(name), mode)

    def fuse_unlink(self, req, parent, name):
        self.unlink(req, parent, self.decode(name))

    def fuse_rmdir(self, req, parent, name):
        self.rmdir(req, parent, self.decode(name))

    def fuse_symlink(self, req, link, parent, name):
        self.symlink(req, link, parent, self.decode(name))

    def fuse_rename(self, req, parent, name, newparent, newname):
        self.rename(
            req, parent, self.decode(name), newparent, self.decode(newname))

    def fuse_link(self, req, ino, newparent, newname):
        self.link(req, ino, newparent, self.decode(newname))

    def fuse_open(self, req, ino, fip):
        self.open(req, ino, fip.contents)

    def fuse_read(self, req, ino, size, off, fip):
        self.read(req, ino, size, off, self.get_fi(fip))

    def fuse_write(self, req, ino, buf, size, off, fip):
        buf_str = ctypes.string_at(buf, size)
        self.write(req, ino, buf_str, off, self.get_fi(fip))

    def fuse_flush(self, req, ino, fip):
        self.flush(req, ino, self.get_fi(fip))

    def fuse_release(self, req, ino, fip):
        self.release(req, ino, self.get_fi(fip))

    def fuse_fsync(self, req, ino, datasync, fip):
        self.fsyncdir(req, ino, datasync, self.get_fi(fip))

    def fuse_opendir(self, req, ino, fip):
        self.opendir(req, ino)

    def fuse_readdir(self, req, ino, size, off, fip):
        self.readdir(req, ino, size, off, self.get_fi(fip))

    def fuse_releasedir(self, req, ino, fip):
        self.releasedir(req, ino, self.get_fi(fip))

    def fuse_fsyncdir(self, req, ino, datasync, fip):
        self.fsyncdir(req, ino, datasync, self.get_fi(fip))

    def fuse_setxattr(self, req, ino, name, value_buf, value_size, flags):
        value = ctypes.string_at(value_buf, value_size)
        self.setxattr(req, ino, self.decode(name), value, flags)

    def fuse_getxattr(self, req, ino, name, size):
        self.getxattr(req, ino, self.decode(name), size)

    def fuse_removexattr(self, req, ino, name):
        self.removexattr(self, req, ino, self.decode(name))

    def fuse_create(self, req, parent, name, mode, fip):
        self.create(req, parent, self.decode(name), mode, fip.contents)

    # Utility methods

    def req_ctx(self, req):
        ctx = self.libfuse.fuse_req_ctx(req)
        return ctx.contents


    # Methods to be overridden in subclasses.
    # Reply with the self.reply_* methods.

    def init(self, userdata, conn):
        """Initialize filesystem

        There's no reply to this method
        """
        pass

    def destroy(self, userdata):
        """Clean up filesystem

        There's no reply to this method
        """
        pass

    def lookup(self, req, parent, name):
        """Look up a directory entry by name and get its attributes.

        Valid replies:
            reply_entry
            reply_err
        """
        self.reply_err(req, errno.ENOENT)

    def forget(self, req, ino, nlookup):
        """Forget about an inode

        Valid replies:
            reply_none
        """
        self.reply_none(req)

    def getattr(self, req, ino, fi):
        """Get file attributes

        Valid replies:
            reply_attr
            reply_err
        """
        if ino == 1:
            attr = {'st_ino': 1, 'st_mode': S_IFDIR | 0o755, 'st_nlink': 2}
            self.reply_attr(req, attr, 1.0)
        else:
            self.reply_err(req, errno.ENOENT)

    def setattr(self, req, ino, attr, to_set, fi):
        """Set file attributes

        Valid replies:
            reply_attr
            reply_err
        """
        self.reply_err(req, errno.EROFS)

    def readlink(self, req, ino):
        """Read symbolic link

        Valid replies:
            reply_readlink
            reply_err
        """
        self.reply_err(req, errno.ENOENT)

    def mknod(self, req, parent, name, mode, rdev):
        """Create file node

        Valid replies:
            reply_entry
            reply_err
        """
        self.reply_err(req, errno.EROFS)

    def mkdir(self, req, parent, name, mode):
        """Create a directory

        Valid replies:
            reply_entry
            reply_err
        """
        self.reply_err(req, errno.EROFS)

    def unlink(self, req, parent, name):
        """Remove a file

        Valid replies:
            reply_err
        """
        self.reply_err(req, errno.EROFS)

    def rmdir(self, req, parent, name):
        """Remove a directory

        Valid replies:
            reply_err
        """
        self.reply_err(req, errno.EROFS)

    def symlink(self, req, link, parent, name):
        """Create a symbolic link

        Valid replies:
            reply_entry
            reply_err
        """
        self.reply_err(req, errno.EROFS)

    def rename(self, req, parent, name, newparent, newname):
        """Rename a file

        Valid replies:
            reply_err
        """
        self.reply_err(req, errno.EROFS)

    def link(self, req, ino, newparent, newname):
        """Create a hard link

        Valid replies:
            reply_entry
            reply_err
        """
        self.reply_err(req, errno.EROFS)

    def open(self, req, ino, fi):
        """Open a file

        Valid replies:
            reply_open
            reply_err
        """
        self.reply_open(req)

    def read(self, req, ino, size, off, fi):
        """Read data

        Valid replies:
            reply_buf
            reply_err
        """
        self.reply_err(req, errno.EIO)

    def write(self, req, ino, buf, off, fi):
        """Write data

        Valid replies:
            reply_write
            reply_err
        """
        self.reply_err(req, errno.EROFS)

    def flush(self, req, ino, fi):
        """Flush method

        Valid replies:
            reply_err
        """
        self.reply_err(req, errno.ENOSYS)

    def release(self, req, ino, fi):
        """Release an open file

        Valid replies:
            reply_err
        """
        self.reply_err(req, 0)

    def fsync(self, req, ino, datasync, fi):
        """Synchronize file contents

        Valid replies:
            reply_err
        """
        self.reply_err(req, errno.ENOSYS)

    def opendir(self, req, ino):
        """Open a directory

        Valid replies:
            reply_open
            reply_err
        """
        self.reply_open(req)

    def readdir(self, req, ino, size, off, fi):
        """Read directory

        Valid replies:
            reply_readdir
            reply_err
        """
        if ino == 1:
            attr = {'st_ino': 1, 'st_mode': S_IFDIR}
            entries = [('.', attr), ('..', attr)]
            self.reply_readdir(req, size, off, entries)
        else:
            self.reply_err(req, errno.ENOENT)

    def releasedir(self, req, ino, fi):
        """Release an open directory

        Valid replies:
            reply_err
        """
        self.reply_err(req, 0)

    def fsyncdir(self, req, ino, datasync, fi):
        """Synchronize directory contents

        Valid replies:
            reply_err
        """
        self.reply_err(req, errno.ENOSYS)

    def statfs(self, req, ino):
        """Get filesystem information.

        Valid replies:
            reply_statfs
            reply_err
        """
        self.reply_err(req, 0)

    def setxattr(self, req, ino, name, value, flags):
        """Set extended attribute.

        Valid replies:
            reply_err
        """
        self.reply_err(req, errno.ENOSYS)

    def getxattr(self, req, ino, name, size):
        """Get extended attribute.

        Valid replies:
            reply_buf
            reply_xattr
            reply_err
        """
        self.reply_err(req, errno.ENOSYS)

    def listxattr(self, req, ino, size):
        """List extended attributes.

        Valid replies:
            reply_listxattr
            reply_err
        """
        self.reply_err(req, errno.ENOSYS)

    def removexattr(self, req, ino, name):
        """Remove extended attribute.

        Valid replies:
            reply_err
        """
        self.reply_err(req, errno.ENOSYS)

    def access(self, req, ino, mask):
        """Return access permissions.

        Valid replies:
            reply_err
        """
        self.reply_err(req, errno.ENOSYS)

    def create(self, req, parent, name, mode, fi):
        """Create a file.

        Valid replies:
            reply_create
            reply_err
        """
        self.reply_err(req, errno.ENOSYS)
