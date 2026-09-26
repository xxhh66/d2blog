"""缓存模块。

该模块集中管理应用中使用到的内存缓存，包括通用缓存包装器和验证码缓存。
缓存使用 cachetools.TTLCache，可在固定生命周期内存储临时数据，并自动过期。
"""
import asyncio
from unittest import result

from cachetools import TTLCache,LRUCache
from typing import Generic, TypeVar

T = TypeVar("T")


class CommonCache(Generic[T]):
    """对 TTLCache 的简单包装，提供统一的 get/set/delete 接口。

    适用于需要按键值存储的临时数据，例如验证码、会话状态或分布式任务状态。
    """
    def __init__(self, maxsize: int, ttl: int):
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def get(self, key: str) -> T | None:
        return self.cache.get(key)

    def set(self, key: str, value: T):
        self.cache[key] = value

    def delete(self, key: str):
        self.cache.pop(key, None)

class CommonLRUCache(Generic[T]):
    def __init__(self, maxsize: int):
        self.cache = LRUCache(maxsize=maxsize)

    def get(self, key: str) -> T | None:
        return self.cache.get(key)

    def set(self, key: str, value: T):
        self.cache[key] = value

    def delete(self, key: str):
        self.cache.pop(key, None)

async def cache_with_lock(cache_key:str, cache_obj:CommonCache, lock_obj: asyncio.Lock,func:callable):
    result = cache_obj.get(cache_key)
    if result:
        return result

    async with lock_obj:
        result = cache_obj.get(cache_key)
        if result:
            return result

        result = await func()
        cache_obj.set(cache_key, result)
        return result

NONE_OBJ = object()
async def load_cache_with_lock(cache_key:str, cache_obj:CommonCache, lock_obj: asyncio.Lock,func:callable):
    result = cache_obj.get(cache_key)

    if result is not None:
        if result is NONE_OBJ:
            return None
    async with lock_obj:
        result = cache_obj.get(cache_key)
        if result is not None:
            if result is NONE_OBJ:
                return None
            return result
        result = await func()
        if result is None:
            cache_obj.set(cache_key,NONE_OBJ)
        else:
            cache_obj.set(cache_key,result)
        return result

# 取消锁的缓存
async def load_cache(cache_key: str, cache_obj: CommonCache, func: callable):
    # 首先从缓存中加载
    result = cache_obj.get(cache_key)
    if result is not None:
        if result is NONE_OBJ:
            return None
        return result
    # 根据func获取结果
    result = await func()
    # 将结果放入缓存
    if result is None:
        cache_obj.set(cache_key, NONE_OBJ)
    else:
        cache_obj.set(cache_key, result)
    # 返回结果
    return result


# 验证码缓存：最多保存 100 个验证码记录，3 分钟自动过期。
verify_code_cache = CommonCache(maxsize=1024, ttl=60 * 3)
latest_articles_cache = CommonCache(maxsize=100, ttl=60 * 30)
category_stat_cache = CommonCache(maxsize=1, ttl=60 * 5)
stat_cache = CommonCache(maxsize=10, ttl=60 * 5)
article_cache = CommonCache(maxsize=1000, ttl=60 * 5)

# 文章详情锁缓存
article_lock_cache = CommonLRUCache(maxsize=1000)
article_page_cache = CommonCache(maxsize=1000, ttl=60 * 5)
article_view_count_cache = CommonLRUCache(maxsize=1000)