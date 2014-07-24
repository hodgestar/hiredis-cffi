""" Python implementations for hiredis classes.
"""

from ._hiredis_c import hiredis_c, ffi


class HiredisError(Exception):
    pass


class ProtocolError(HiredisError):
    pass


class ReplyError(HiredisError):
    pass


class Reader(object):
    "Hiredis protocol reader"

    def __init__(self, protocolError=None, replyError=None, encoding=None):
        self._protocol_error = ProtocolError
        self._reply_error = ReplyError
        self._encoding = encoding or None

        if protocolError:
            if not callable(protocolError):
                raise TypeError("Expected a callable")
            self._protocol_error = protocolError

        if replyError:
            if not callable(replyError):
                raise TypeError("Expected a callable")
            self._reply_error = replyError

        self._reader = hiredis_c.redisReaderCreate()
        self._reader.privdata = ffi.new_handle(self)
        self._reader.fn.createString = self._create_string

    @ffi.callback("void * (const redisReadTask*, char*, size_t)")
    def _create_string(task, s, length):
        task = ffi.cast("redisReadTask*", task)
        if task.type == hiredis_c.REDIS_REPLY_ERROR:
            self = ffi.from_handle(task.privdata)
            raise self._reply_error(s)
        data = ffi.string(s, length)
        return ffi.new_handle(data)

    def feed(self, buf, offset=None, length=None):
        if offset is None:
            offset = 0
        if length is None:
            length = len(buf) - offset

        if offset < 0 or length < 0:
            raise ValueError("negative input")

        if offset + length > len(buf):
            raise ValueError("input is larger than buffer size")

        c_buf = ffi.new("char[]", buf[offset:offset + length])
        hiredis_c.redisReaderFeed(self._reader, c_buf, length)

    def gets(self):
        reply = ffi.new_handle("")
        result = hiredis_c.redisReaderGetReply(self._reader, reply)
        if result != hiredis_c.REDIS_OK:
            raise self._protocol_error(self._reader.errstr)
        return ffi.from_handle(reply)
