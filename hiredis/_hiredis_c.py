""" CFFI definitions for hiredis.
"""

import cffi

ffi = cffi.FFI()

ffi.cdef("""

  #define REDIS_OK ...
  #define REDIS_ERR ...

  #define REDIS_REPLY_ERROR ...

  typedef struct redisReadTask {
    int type;
    int elements;
    int idx;
    void *obj;
    struct redisReadTask *parent;
    void *privdata;
  } redisReadTask;

  typedef struct redisReplyObjectFunctions {
    void *(*createString)(const redisReadTask*, char*, size_t);
    void *(*createArray)(const redisReadTask*, int);
    void *(*createInteger)(const redisReadTask*, long long);
    void *(*createNil)(const redisReadTask*);
    void (*freeObject)(void*);
  } redisReplyObjectFunctions;

  typedef struct redisReader {
    int err;
    char errstr[...];
    redisReplyObjectFunctions *fn;
    void *privdata;
    ...;
  } redisReader;

  redisReader *redisReaderCreate(void);
  void redisReaderFree(redisReader *r);
  int redisReaderFeed(redisReader *r, const char *buf, size_t len);
  int redisReaderGetReply(redisReader *r, void **reply);

""")

hiredis_c = ffi.verify(
    libraries=['hiredis'],
    include_dirs=['/usr/include/hiredis', '/usr/local/include/hiredis'],
    source="""

  #include <hiredis.h>

""")
