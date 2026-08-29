from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "t_user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(128) NOT NULL,
    "password" VARCHAR(128) NOT NULL,
    "is_deleted" BOOL NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL,
    "updated_at" TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_t_user_email_6fe6a5" ON "t_user" ("email");
CREATE INDEX IF NOT EXISTS "idx_t_user_passwor_04bf8b" ON "t_user" ("password");
CREATE INDEX IF NOT EXISTS "idx_t_user_created_9700b0" ON "t_user" ("created_at");
COMMENT ON COLUMN "t_user"."email" IS '邮箱';
COMMENT ON COLUMN "t_user"."password" IS '密码';
COMMENT ON COLUMN "t_user"."is_deleted" IS '是否删除';
COMMENT ON TABLE "t_user" IS '用户表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "t_user";"""


MODELS_STATE = (
    "eJztlm1v2jAQx79KlFedtFWQQsj2DlqmMhWY2nSbuk6Wk5hg1bHT2BlFXb/7bEMISQijU9"
    "exqe+S/93Z59/54e7NiAWI8MNLjhLznXFvUhgh+VHQXxsmjONcVYKAHtGOAqSZj8dFAn0h"
    "1QkkHEkpQNxPcCwwo8r3Ou20Lec6ta2jznXqOLaj4gLmy0BMQ+lCU0KklFJ8myIgWIjEVG"
    "f29ZuUMQ3QHeLZb3wDJhiRoJA4DtSYWgdiHmttQMV77ahm84DPSBrR3DmeiymjK29MhVJD"
    "RFECBVLDiyRVy1HZLdedrXCRae6ySHEtJkATmBKRr00mkGsmAKOxCy76LgBmBVgWUQXkM6"
    "pgy1S5Xn2oUnhjNVudlnNktxzpotNcKZ2HxdQ5mEWgxjNyzQdthwIuPDTjHCqKICZVrsdT"
    "mGwGuwoosZVJl9lmJLfBzYQnpSu349sGRHJTel6zZiOWOUfwDhBEQzGVv03L2UL1U/f8+L"
    "R7fiC9XqnRmTwbiyMzWpqshU2hz1HHkPMZSzbs4nra6zH7Dbzt+bYE7jT2BzjmcgEEKTYV"
    "5D3GCIK05vIoBJa4ezLyacDnd2lGeaU8Cr1tWxNZgJYlC9C2rIbc/bbd2q0MW6j3xuMzNU"
    "jE+S3RwsAt0b8c9vqyLLoo0gkLtH7r5JXwE6RIASiqlTiRFoEjtLkUxchSKYJl6GH2sTcH"
    "Yvf7Xa4vGFMyX867pR7uYNi/cLvDj4WinHTdvrJYWp2X1AO7dGBWgxifB+6poX6Nq/Gor+"
    "kyLsJEz5j7uVemygmmggHKZgAGa4gyNcNYKHoaB79Z9GLk8xS9ehhfqr5r1VXLNrlZ6y+U"
    "4EH/ZgaTAFQszGJ1vlVTZEVlBVIY6popuCrNZUvbRQn2p+aGZndp2druwtznV+1ufZ1f2t"
    "v9am+/o4SrlB7Rcq2F/KmO63nvmkKjZbXbOzRa0qu20dK24vOuDtUjCC/d/0O6zUZjlza2"
    "0ahvY5Wt1DwxKhDd8Ih+uBiParqmPKT8emJfGD8MgnnlrvgHaG+Bq2AUnsiM6cGw+6WM+/"
    "hs3Cu/fWqAnkT/Vx+zh58r451H"
)
