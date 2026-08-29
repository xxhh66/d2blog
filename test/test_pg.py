"""PostgreSQL 连接测试脚本。

该脚本用于在开发环境中验证数据库是否能够正常连接并执行查询。
"""

import asyncio

import asyncpg


async def test_connection():
    """尝试连接 PostgreSQL，并执行一个简单查询确保可用性。"""
    # 读取配置中的数据库地址；实际项目中建议从 .env 中读取，避免硬编码敏感信息。
    DATABASE_URL = "postgres://postgres:123456@127.0.0.1:5432/d2blog"

    try:
        # 建立数据库连接。
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ 数据库连接成功！")

        # 执行简单查询，确认连接和 SQL 执行都正常。
        result = await conn.fetchval("SELECT 1")
        print(f"✅ 查询测试成功: {result}")

        await conn.close()
        return True
    except Exception as e:
        # 捕获异常并输出常见问题提示，帮助快速定位配置错误。
        print(f"❌ 连接失败: {e}")
        print("\n请检查：")
        print("1. PostgreSQL 服务是否正在运行")
        print("2. 密码是否正确（当前密码: 123456）")
        print("3. 数据库 'd2blog' 是否存在")
        return False


if __name__ == "__main__":
    asyncio.run(test_connection())