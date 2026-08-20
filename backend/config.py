# ==================== 后端配置文件 ====================
# 集中管理应用配置、数据库路径、跨域与 Swagger 常量。

import os

# 项目根目录（backend 目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据库文件存放路径（backend/data/hms.db）
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "hms.db")

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)


class Config:
    """Flask 应用基础配置"""

    # SQLite 数据库连接串
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # JSON 中文不转义，保证接口返回可读的中文字段
    JSON_AS_ASCII = False
    # 密钥（生产环境应从环境变量读取）
    SECRET_KEY = os.environ.get("HMS_SECRET_KEY", "hms-dev-secret-key-change-me")

    # Swagger 文档配置（flask-smorest）
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_JSON_PATH = "api-spec.json"
    OPENAPI_URL_PREFIX = "/api/docs"
    OPENAPI_REDOC_PATH = "/redoc"
    OPENAPI_REDOC_URL = (
        "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    )
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )
    API_TITLE = "医疗机构信息管理系统 REST API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = (
        "医疗信息管理系统后端接口。包含用户、设备、生理信号记录、预约记录等核心业务。"
    )


class DevelopmentConfig(Config):
    """开发环境：开启调试"""

    DEBUG = True


class ProductionConfig(Config):
    """生产环境：关闭调试"""

    DEBUG = False


# 默认使用开发配置
active_config = DevelopmentConfig
