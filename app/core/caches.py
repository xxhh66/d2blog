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
        # TTLCache 会在指定时间内自动清理过期项，避免无限增长。
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def get(self, key: str) -> T | None:
        # 读取缓存时返回键对应的值，如不存在则返回 None。
        return self.cache.get(key)

    def set(self, key: str, value: T):
        # 保存数据时使用字符串键，便于按业务字段查询。
        self.cache[key] = value

    def delete(self, key: str) -> bool:
        # 删除缓存项并返回是否实际删除成功。
        return self.cache.pop(key, None)


# 验证码缓存：最多保存 100 个验证码记录，3 分钟自动过期。
verify_code_cache = TTLCache(maxsize=100, ttl=60 * 3)