# ==================== Flask 应用入口 ====================
# 组装 Flask 应用：注册蓝图、全局异常处理、CORS、Swagger 文档，
# 启动时初始化数据库与演示数据。

from flask import Flask, jsonify
from flask_cors import CORS
from flask_smorest import Api

from config import active_config
from controllers.auth_utils import error_handler
from services.seed_service import run_seed

from controllers.user_controller import blp as user_blp
from controllers.device_controller import blp as device_blp
from controllers.booking_controller import blp as booking_blp
from controllers.signal_controller import blp as signal_blp

app = Flask(__name__)
app.config.from_object(active_config)

CORS(app, supports_credentials=True)

app.errorhandler(Exception)(error_handler)

api = Api(app)
api.register_blueprint(user_blp)
api.register_blueprint(device_blp)
api.register_blueprint(booking_blp)
api.register_blueprint(signal_blp)


@app.route("/")
def index():
    return {"message": "医疗机构信息管理系统后端服务运行中", "docs": "/api/docs/swagger-ui"}


run_seed()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.debug)
