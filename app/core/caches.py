"""缓存模块。

该模块集中管理应用中使用到的内存缓存，包括通用缓存包装器和验证码缓存。
缓存使用 cachetools.TTLCache，可在固定生命周期内存储临时数据，并自动过期。
"""

from cachetools import TTLCache
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


# 验证码缓存：最多保存 100 个验证码记录，3 分钟自动过期。
verify_code_cache = CommonCache(maxsize=100, ttl=60 * 3)