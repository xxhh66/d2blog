from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from app.core import config
myapp = FastAPI()

register_tortoise(myapp,config=config.TORTOISE_ORM,generate_schemas=False)

@myapp.get("/")
async def root():
    return {"hello": "world"}