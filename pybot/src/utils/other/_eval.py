import time
from nonebot import logger
def timeit(func):
    def timed(*args, **kw):
        ts = time.time()
        result = func(*args, **kw)
        te = time.time()
        logger.debug(f"{func.__name__} took: {te-ts} sec")
        return result
    return timed