# coding: utf-8
import time
import threading

from copy import deepcopy


def NewCacheHandler(expire=60, maxCache=30):
    cache = dict()
    lock = threading.Lock()

    def cacheHandler(ctx):
        cache_key = f"{ctx.method}{ctx.path}{ctx.version}{ctx.content_length}"
        if cache_key in cache:
            with lock:
                code, headers, body, stamp = cache[cache_key]
                cache_enable = stamp + expire > int(time.time())
                if not cache_enable:
                    cache.clear()
            if cache_enable:
                ctx.response_status_code = code
                ctx.response_headers = deepcopy(headers)
                ctx.response_body = deepcopy(body)
                ctx.log.info("hit cache")
                return
        ctx.next()
        if ctx._flush_header or ctx.response_status_code >= 400:
            return
        try:
            with lock:
                if len(cache) > maxCache:
                    cache.clear()
                cache[cache_key] = (
                    ctx.response_status_code,
                    deepcopy(ctx.response_headers),
                    deepcopy(ctx.response_body),
                    int(time.time()),
                )
            ctx.log.info("cache success")
        except:
            pass

    return cacheHandler
