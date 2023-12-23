#!/usr/bin/env python3
# Based on https://github.com/libfuse/libfuse/blob/master/example/poll.c

import dataclasses
import errno
import logging
import queue
import stat
import threading
from select import POLLIN
from time import time, sleep
from typing import Optional

import fuse
from fuse import FUSE, Operations, LoggingMixIn, _libfuse, FuseOSError
from fusell import LibFUSE, fuse_pollhandle_p

DATA_STR = "This is some great data :)\n"


class ProducerThread(threading.Thread):
    def __init__(self, context):
        super().__init__()
        self._stop_flag = threading.Event()
        self._context = context

    def run(self):
        while not self._stop_flag.is_set():
            self._context.push_to_queue()
            sleep(5)

    def stop(self):
        self._stop_flag.set()


@dataclasses.dataclass
class FileHandleData:
    # Poll handle or None
    poll_handle: Optional[fuse_pollhandle_p]
    # The available data
    queue: queue.Queue
    # Read calls alternate between returning items in the queue and return nothing (aka EOF)
    force_eof: bool


class Context(LoggingMixIn, Operations):
    _file_handle_data: dict[int, FileHandleData]

    def __init__(self):
        self._file_handle_data = {}
        self._next_fh = 0
        # TODO: The .c example says this is required (it's called |fsel_fuse| there) but it isn't actually used.
        #   So why is it necessary?
        self._fuse_pointer = None
        # We need this to be able to call a few low-level functions related to polling
        self._lowlevel = LibFUSE()
        # The thread that will actually be writing data
        self._producer = ProducerThread(self)

    def init(self, path):
        self._producer.start()

    def destroy(self, path):
        self._producer.stop()
        self._producer.join()

    def open(self, path, fip):
        fip.direct_io = 1
        # Don't bother handling offset reads
        fip.nonseekable = 1
        fip.fh = self._next_fh
        assert fip.fh not in self._file_handle_data
        self._file_handle_data[fip.fh] = FileHandleData(poll_handle=None, force_eof=False, queue=queue.Queue())
        self._next_fh += 1
        return 0

    def release(self, path, fh):
        print(f"release: {fh.fh}")
        data = self._file_handle_data.pop(fh.fh, None)
        if data is not None and data.poll_handle is not None:
            self._lowlevel.fuse_pollhandle_destroy(data.poll_handle)
            data.poll_handle = None

    def poll(self, path, fh, ph, reventsp):
        idx = fh.fh

        # TODO: why is this necessary?
        if self._fuse_pointer is None:
            self._fuse_pointer = _libfuse.fuse_get_context().contents.fuse

        data = self._file_handle_data.get(idx)
        if data is not None:
            # Free the previous poll handle
            if data.poll_handle is not None:
                self._lowlevel.fuse_pollhandle_destroy(data.poll_handle)
            # Record this poll handle for later usage
            data.poll_handle = ph
            # If data is already available, notify the kernel
            if data.queue.qsize() != 0:
                reventsp.contents.value |= POLLIN

        return 0

    def read(self, path, size, offset, fh):
        data = self._file_handle_data.get(fh.fh)
        if data is not None:
            if data.force_eof:
                data.force_eof = False
                return "".encode("utf-8")
            ret = data.queue.get().encode("utf-8")
            data.force_eof = True

            # TODO: Proper handling for partial message reads. Ideally we would check whether |size| covers the entire
            #  message. If so, call 'get()' on the queue like above and return the entire message. If not, peek at the
            #  message in the queue and just return the requested substring. Would need to keep track of offset.
            # As it stands, we only slice on |size| below to keep FUSE and the kernel from complaining. We assume that
            # clients will call read() with a buffer size of at least message size.
            return ret[0:size]

        raise FuseOSError(errno.EBADF)

    def readdir(self, path, fh):
        return [".", "..", "data"]

    def getattr(self, path, fh=None):
        if path == '/':
            st = dict(st_mode=(stat.S_IFDIR | 0o755), st_nlink=2)
        elif path == "/data":
            st = dict(st_mode=(stat.S_IFREG | 0o444), st_size=0)
        else:
            raise fuse.FuseOSError(errno.ENOENT)
        st['st_ctime'] = st['st_mtime'] = st['st_atime'] = time()
        return st

    def push_to_queue(self):
        """
        Called by the producer thread to write data to the queues and notify poll handles.
        """
        for fh, data in self._file_handle_data.items():
            # Write data to the queue
            data.queue.put(DATA_STR)

            # TODO: Again, why do we need this?
            if not self._fuse_pointer:
                continue

            if data.poll_handle is not None:
                # Notify the caller of poll() that data is ready to read!
                self._lowlevel.fuse_notify_poll(data.poll_handle)
                self._lowlevel.fuse_pollhandle_destroy(data.poll_handle)
                data.poll_handle = None


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('mount')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    fuse = FUSE(
        Context(), args.mount, foreground=True, ro=True, raw_fi=True, direct_io=True)
