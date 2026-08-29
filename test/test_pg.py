# test_pg.py
import asyncpg
import asyncio


async def test_connection():
    # 使用你的 .env 中的连接字符串
    DATABASE_URL = "postgres://postgres:123456@127.0.0.1:5432/d2blog"

    try:
        # 解析连接字符串
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ 数据库连接成功！")

        # 测试查询
        result = await conn.fetchval("SELECT 1")
        print(f"✅ 查询测试成功: {result}")

        await conn.close()
        return True
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("\n请检查：")
        print("1. PostgreSQL 服务是否正在运行")
        print("2. 密码是否正确（当前密码: 123456）")
        print("3. 数据库 'd2blog' 是否存在")
        return False


if __name__ == "__main__":
    asyncio.run(test_connection())