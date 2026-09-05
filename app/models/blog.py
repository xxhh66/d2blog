from email.policy import default

from tortoise import Model,fields

from app.core.enums import ArticleStatusEnum
from app.models.common import BaseModel

class Category(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="categories", null=False, description="用户",
                                  on_delete=fields.NO_ACTION)
    name = fields.CharField(max_length=64, null=False, description="分类名称")

    class Meta:
        table = "t_category"
        table_description="分类表"

class Article(BaseModel):
    user = fields.ForeignKeyField("models.User",
                                  related_name="articles",
                                  null=False,
                                  description="用户",
                                  on_delete=fields.NO_ACTION)
    category = fields.ForeignKeyField("models.Category",
                                      related_name="articles",
                                      null=False,
                                      description="分类",
                                      on_delete=fields.NO_ACTION)
    tags = fields.ManyToManyField("models.Tag",
                                  related_name="articles",
                                  through="t_article_tag",
                                  on_delete=fields.NO_ACTION)
    status = fields.IntEnumField(
        enum_type=ArticleStatusEnum,
        default=ArticleStatusEnum.UB_PUBLISHED,
        null=False,
        description="文章状态 0-未发布 1-已发布"
    )
    title = fields.CharField(max_length=256,null=False,description="文章标题")
    intro = fields.CharField(max_length=256,null=False,description="文章摘要")
    content = fields.TextField(null=False,description="文章内容")
    view_count = fields.IntField(default=0,null=False,description="文章浏览次数")

    seo_title = fields.CharField(max_length=256,null=False,description="SEO标题")
    seo_keywords = fields.CharField(max_length=256,null=False,description="SEO关键词")
    seo_description =fields.CharField(max_length=256,null=False,description="SEO描述")


    class Meta:
        table = "t_article"
        table_description="文章表"
class Tag(BaseModel):
    user = fields.ForeignKeyField("models.User",related_name="tags",null=False, description="用户", on_delete=fields.NO_ACTION)
    name = fields.CharField(max_length=64,null=False,description="标签名称")
    articles = fields.ReverseRelation['Article']

    class Meta:
        table = "t_tag"
        table_description="标签表"