# ==================== 控制器通用工具 ====================
# 从请求头解析当前登录用户，构造 AuthContext 供 service 做权限校验。

from flask import request
from services.user_service import AuthContext
from utils import BizError


def get_auth():
    """从请求头 X-User-Role / X-User-Id 解析当前用户上下文。"""
    role = request.headers.get("X-User-Role")
    user_id = request.headers.get("X-User-Id")
    name = request.headers.get("X-User-Name", "")
    if not role:
        raise BizError("请先登录", 401)
    return AuthContext(role, user_id=user_id, name=name)


def error_handler(e):
    """统一异常处理器，将 BizError/NotAuthorized 映射为 JSON 响应。"""
    from utils import NotAuthorized

    if isinstance(e, BizError):
        return {"message": e.message}, e.status
    if isinstance(e, NotAuthorized):
        return {"message": e.message}, 403
    return {"message": "服务器内部错误: %s" % e}, 500
