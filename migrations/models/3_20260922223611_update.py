from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "t_article" RENAME COLUMN "update_at" TO "updated_at";
        ALTER TABLE "t_category" RENAME COLUMN "update_at" TO "updated_at";
        ALTER TABLE "t_tag" RENAME COLUMN "update_at" TO "updated_at";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "t_tag" RENAME COLUMN "updated_at" TO "update_at";
        ALTER TABLE "t_article" RENAME COLUMN "updated_at" TO "update_at";
        ALTER TABLE "t_category" RENAME COLUMN "updated_at" TO "update_at";"""


MODELS_STATE = (
    "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"
    "8YrD7OF/wNVtaw=="
)
