"""全局配置中心（教程第 02 章）。

为什么用 pydantic-settings 而不是直接 os.getenv？
1. 环境变量会自动做类型转换：字符串 "10080" → int，"false" → bool；
2. 缺少环境变量时用这里声明的默认值，本地开发开箱即用；
3. .env 文件自动加载，生产环境用环境变量覆盖，两者互不干扰。

用法：任何模块里 `from app.core.config import settings` 即可拿到单例配置。
"""
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ---- 应用基础信息 ----
    APP_NAME: str = "MathTeam API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # ---- 跨域（Vue 3 前端默认跑在 5173 端口）----
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # ---- 认证（教程第 04 章）----
    # 生产环境务必通过环境变量 SECRET_KEY 覆盖，且不要提交到 Git
    SECRET_KEY: str = "dev-only-change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 天，学习项目图方便

    # ---- 数据库 ----
    # 默认连接本机 PostgreSQL；其他环境通过 DATABASE_URL 覆盖。
    DATABASE_URL: str = "postgresql+psycopg://zhengrui@localhost:5432/mathteam"
    # 开发环境自动建表；生产环境建议关掉并改用 Alembic 迁移
    AUTO_CREATE_TABLES: bool = True
    # 生产环境必须关闭演示账号和演示业务数据写入
    SEED_DEMO_DATA: bool = True

    # SettingsConfigDict 是 pydantic-settings v2 的写法
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # SECRET_KEY 与 secret_key 都能读进来
        extra="ignore",        # 忽略无关的 .env 条目，避免启动报错
    )

    @property
    def origins_list(self) -> list[str]:
        """把逗号分隔的字符串切成 CORSMiddleware 需要的列表。"""
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @model_validator(mode="after")
    def validate_production_security(self):
        """生产环境拒绝默认密钥和演示数据，避免误部署。"""
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY == "dev-only-change-me-in-production":
                raise ValueError("生产环境必须设置独立的 SECRET_KEY")
            if self.SEED_DEMO_DATA:
                raise ValueError("生产环境必须设置 SEED_DEMO_DATA=false")
        return self


# 模块级单例：全项目共享同一份配置，不要在各处重复实例化 Settings()
settings = Settings()
