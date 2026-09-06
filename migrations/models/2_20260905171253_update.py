from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "t_category" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "is_deleted" BOOL NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL,
    "update_at" TIMESTAMPTZ NOT NULL,
    "name" VARCHAR(64) NOT NULL,
    "user_id" INT NOT NULL REFERENCES "t_user" ("id") ON DELETE NO ACTION
);
CREATE INDEX IF NOT EXISTS "idx_t_category_created_fd8005" ON "t_category" ("created_at");
COMMENT ON COLUMN "t_category"."is_deleted" IS '是否删除';
COMMENT ON COLUMN "t_category"."created_at" IS '创建时间';
COMMENT ON COLUMN "t_category"."update_at" IS '更新时间';
COMMENT ON COLUMN "t_category"."name" IS '分类名称';
COMMENT ON COLUMN "t_category"."user_id" IS '用户';
COMMENT ON TABLE "t_category" IS '分类表';
        CREATE TABLE IF NOT EXISTS "t_article" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "is_deleted" BOOL NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL,
    "update_at" TIMESTAMPTZ NOT NULL,
    "status" SMALLINT NOT NULL,
    "title" VARCHAR(256) NOT NULL,
    "intro" VARCHAR(256) NOT NULL,
    "content" TEXT NOT NULL,
    "view_count" INT NOT NULL,
    "seo_title" VARCHAR(256) NOT NULL,
    "seo_keywords" VARCHAR(256) NOT NULL,
    "seo_description" VARCHAR(256) NOT NULL,
    "category_id" INT NOT NULL REFERENCES "t_category" ("id") ON DELETE NO ACTION,
    "user_id" INT NOT NULL REFERENCES "t_user" ("id") ON DELETE NO ACTION
);
CREATE INDEX IF NOT EXISTS "idx_t_article_created_c6a57d" ON "t_article" ("created_at");
COMMENT ON COLUMN "t_article"."is_deleted" IS '是否删除';
COMMENT ON COLUMN "t_article"."created_at" IS '创建时间';
COMMENT ON COLUMN "t_article"."update_at" IS '更新时间';
COMMENT ON COLUMN "t_article"."status" IS '文章状态 0-未发布 1-已发布';
COMMENT ON COLUMN "t_article"."title" IS '文章标题';
COMMENT ON COLUMN "t_article"."intro" IS '文章摘要';
COMMENT ON COLUMN "t_article"."content" IS '文章内容';
COMMENT ON COLUMN "t_article"."view_count" IS '文章浏览次数';
COMMENT ON COLUMN "t_article"."seo_title" IS 'SEO标题';
COMMENT ON COLUMN "t_article"."seo_keywords" IS 'SEO关键词';
COMMENT ON COLUMN "t_article"."seo_description" IS 'SEO描述';
COMMENT ON COLUMN "t_article"."category_id" IS '分类';
COMMENT ON COLUMN "t_article"."user_id" IS '用户';
COMMENT ON TABLE "t_article" IS '文章表';
        CREATE TABLE IF NOT EXISTS "t_tag" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "is_deleted" BOOL NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL,
    "update_at" TIMESTAMPTZ NOT NULL,
    "name" VARCHAR(64) NOT NULL,
    "user_id" INT NOT NULL REFERENCES "t_user" ("id") ON DELETE NO ACTION
);
CREATE INDEX IF NOT EXISTS "idx_t_tag_created_719d35" ON "t_tag" ("created_at");
COMMENT ON COLUMN "t_tag"."is_deleted" IS '是否删除';
COMMENT ON COLUMN "t_tag"."created_at" IS '创建时间';
COMMENT ON COLUMN "t_tag"."update_at" IS '更新时间';
COMMENT ON COLUMN "t_tag"."name" IS '标签名称';
COMMENT ON COLUMN "t_tag"."user_id" IS '用户';
COMMENT ON TABLE "t_tag" IS '标签表';
        CREATE TABLE "t_article_tag" (
    "t_article_id" INT NOT NULL REFERENCES "t_article" ("id") ON DELETE CASCADE,
    "tag_id" INT NOT NULL REFERENCES "t_tag" ("id") ON DELETE NO ACTION
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "t_category";
        DROP TABLE IF EXISTS "t_article_tag";
        DROP TABLE IF EXISTS "t_tag";
        DROP TABLE IF EXISTS "t_article";"""


MODELS_STATE = (
    "eJztXG1zmzgQ/isePqUzbQdj8+L75rjuNdfEvknoXaeXG0aAbDPB4IJo6unlv5+W9/eC46"
    "S45YtjS1qQnt2V9tmFfGO2to5N9/XUIYZmYua3wTfGQlv4ku96OWDQbpd0QANBqi/EEAWl"
    "hqkucZBGaMcKmS6mTTp2NcfYEcO2YPitJ/CSeOuJCLO3niQJEsjptkYFDWtNh1ieadImzz"
    "I+e1gh9hqTDXZoxz//0mbD0vFX7EY/d3fKysCmnpm+ocM1/XaF7Hd+24VF3voD4W6qotmm"
    "t7WSwbs92dhWPNqwCLSusYUdRDBcnjgeLAdmFy49WmEw02RIMMWUjI5XyDNJsjY6gaSNUZ"
    "TFUlZu5rKiMAXAIokiQJptAdh0qq6/+jVM4RU3HItjaSSMJTrEn2bcIj4Et06ACQR9eBYy"
    "8+D3I4KCET7GKVBdOmcTAxgFcM9t28TIqgA4I5gDWqWSeaQjXOugjhoSrBN7i4CNW5qjDe"
    "YpcKtbjx9zAv3kOGqkE0EYVxhpTgc1AJ8vl5dwka3rfjb9hgsZftvUXQJHWny4Op9fnw1f"
    "QDMdZBCc1kyiCc3BgJSCSFETb2gPMba4XBVZyZwq9FD0dfTlOHo5gg8woImhSj+pAGwgK6"
    "qbCb9qqBWGrlpfWuY+nE2NluSLq/mNPL36M6OqN1N5Dj2c37rPtZ4JL7KKjC8y+PtCfjeA"
    "n4NPy8Xcx9x2ydrx75iMkz8xMCfkEVux7HsF6SngotYI3IwpeDtQ1gGWkBF8HkMoOuhBli"
    "AIqzHYgMr+MpYQIZcyhXD2iSW4BBHPLT335pa39a3ggoKBLA0XrCER/v45eCzls+01nwoc"
    "RE6lmhdYdjhgX9EvIkc3Bn6kD2GTYEeDIW3k9RWXbmxoI8E5OuJEIT5C4Ufd6XlzNb28LG"
    "7UxCBBWJRVyWyDnHKvjAVyaqDz65YPpjQhSCz9PpEmVYFcHt8t+qqY2FqTDQQnvFCD61/T"
    "69m76fUZHZXzrEXYxQV9WdzprRy7De6xwCnhPuYlGkBPpGFncKd3JNgqOYtk/LUi+k6JnB"
    "D2/FDi6aeqTh4dF8rzj3LmiIkQPruafnyROWYul4vfo+Epjcwul+c5RXwx8D0F2SvTRSUR"
    "ygqdykEg6OMVuIFGnUFQuSH0imyrrf6RlCl1BmNbab3nZ4Q67QM382Unt3tA8A7v721HLw"
    "mA6pFPy3UffH4ojiDe5TA1eVXTO6WC9IRbaiEn2n1FCCMNdp3VqulO8wyHL4VmbTt7pVX2"
    "Kyf1fLv+gVkAlkb9oiaqP2aD91zstMM3JdFxbEWegyOUG4nPhy1kcFd3pelGAK6I81vbwc"
    "baeo/3BUKbgzdMYX8IL3OyMD9EFhW1MnFmyEH3cfI7bWgUhSDh6u8Zy8F0Jl8sF0zpbnEE"
    "iGepS3UG5rY7RVOYc/tlFdRg2CrS7u6RoysZC4cem7NzLfHYYteW25Y6CEHrkmjnCll72Y"
    "bPhtqT0foQxf3QUkeNsvxVKbk6VrhGB5t+9jvqDetWAYq24+NP48EQ3FDDsWainqjcFfaT"
    "jWN76022iwQ3rLAO2qMU8PZNZosstPbbYOEPL4s+VlKlS/tfXZku7fJN6nSJC/V1ur5O19"
    "fp+jpdo3O3r9P1dbq+TldZp/P/FoygOj0Sje90TiQbLPBjVqffJ4clR4Rxg9yIMK5MjUBX"
    "z9p71v6zsPZqKpnAnmEy2YgvlHz7/hrYT3mCtfi4X2eAPxaPf3gk765lZ8AvS4hZSDvrOF"
    "lIFBs9NukXXkRVxD0d6+lYT8d6OtbTsZ6O9XSsp2PfCRZ6OtZdntDTsZ+Hjh2tslfN5lpX"
    "9x5B6U6qwpdaZ77KF9dJcxW+XB2vUOeLK4CNK3yz6c1s+sY/pZQ8Baov7/kOVsIgI8ero5"
    "CRjzfhkInf9BzyhDgk3iLDbBOlxAJPFaYch51MWIQhSlEPeoR9yEkNQhM6qjI28fuywckO"
    "uS48ENoG7bRMtwHnVQ2yaRLbHcD7/EifH/lBDtF8fz9N/ts8E3KI0rOSp5ML+VW1XqCJv3"
    "Zh6VgUsuypWuOxgHXykdonQaz8KdY2WB34AGv3YXrKiuUUO4a2Ycr+50vQ87KOdKJkzPdI"
    "Z/Vu25PMbpHML9hxW766lRLpcj68OcS5t7T4Rm9p8TVvafF5ugNO1QLhcPhPiO6QZZuQSZ"
    "atJpPQ1/AF9D9ulosK7lL5ArpuaGTw38A03A7VGNpmUMvABTAygWrhlfP82+W5CBQucF5W"
    "eXiy5HjJYfbwP4JYaxM="
)
