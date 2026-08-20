# ==================== 用户资源控制器 (Controller) ====================
# 认证（登录/注册/重置密码）+ 管理员用户管理。

from flask import request
from flask_smorest import Blueprint as SmorestBlueprint
from flask.views import MethodView

from services.user_service import UserService
from controllers.auth_utils import get_auth
from schemas import (
    LoginSchema, RegisterSchema, ResetPasswordSchema,
    UserCreateSchema, UserUpdateSchema,
)

# 使用 flask-smorest Blueprint 自动生成 OpenAPI/Swagger 文档
blp = SmorestBlueprint("users", __name__, url_prefix="/api/users",
                       description="认证与用户管理接口")


@blp.route("/login")
class UserLogin(MethodView):
    @blp.response(200)
    @blp.arguments(LoginSchema)
    def post(self, payload):
        """用户登录"""
        return UserService.login(payload.get("account"), payload.get("password"))


@blp.route("/register")
class UserRegister(MethodView):
    @blp.response(201)
    @blp.arguments(RegisterSchema)
    def post(self, payload):
        """开放注册（患者/医生）"""
        return UserService.register(payload)


@blp.route("/reset-password")
class UserReset(MethodView):
    @blp.response(200)
    @blp.arguments(ResetPasswordSchema)
    def post(self, payload):
        """重置密码"""
        return UserService.reset_password(payload)


@blp.route("")
class UserList(MethodView):
    @blp.response(200)
    def get(self):
        """管理员：用户列表"""
        get_auth().require(["admin"])
        role_filter = request.args.get("role") or "all"
        return UserService.list_users(role_filter)

    @blp.response(201)
    @blp.arguments(UserCreateSchema)
    def post(self, payload):
        """管理员：创建用户"""
        get_auth().require(["admin"])
        return UserService.create_user(payload)


@blp.route("/<user_id>")
class UserItem(MethodView):
    @blp.response(200)
    @blp.arguments(UserUpdateSchema)
    def put(self, patch, user_id):
        """管理员：修改用户"""
        get_auth().require(["admin"])
        return UserService.update_user(user_id, patch)

    @blp.response(200)
    def delete(self, user_id):
        """管理员：删除用户"""
        get_auth().require(["admin"])
        return UserService.delete_user(user_id)
