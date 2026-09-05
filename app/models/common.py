from tortoise import Model,fields
class BaseModel(Model):
    is_deleted = fields.BooleanField(default=False,null=False,description="是否删除")
    created_at = fields.DatetimeField(auto_now_add=True,null=False,db_index=True,description="创建时间")
    update_at = fields.DatetimeField(auto_now=True,null=False,description="更新时间")

    class Meta:
        abstract = True