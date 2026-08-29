from tortoise import Model,fields


class User(Model):
    email= fields.CharField(max_length=128, null=False,db_index=True,description="邮箱")
    password  =fields.CharField(max_length=128,null=False,db_index=True,description="密码")

    is_deleted = fields.BooleanField(default=False,null=False,description="是否删除")
    created_at = fields.DatetimeField(auto_now_add=True,null=False,db_index=True,descriptions="创建时间")
    updated_at = fields.DatetimeField(auto_now_add=True,null=False,descriptions="更新时间")

    class Meta:
        table = 't_user'
        table_description = '用户表'

