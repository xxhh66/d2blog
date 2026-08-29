"""启动脚本。

用于直接运行 FastAPI 应用，便于本地开发时快速预览并调试接口。
"""

if __name__ == "__main__":
    import uvicorn

    # 使用 uvicorn 以开发模式启动服务，自动监听代码变更并重载。
    uvicorn.run("app.main:myapp", host="0.0.0.0", port=8000, reload=True)