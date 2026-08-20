# ==================== 后端公共工具 ====================
# ID 生成、时间格式化、Row 转 dict 等通用函数。

import time
import uuid
from datetime import datetime

# 业务异常：供 service 层抛出，由 controller 捕获并映射为 HTTP 状态码
class BizError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


class NotAuthorized(Exception):
    def __init__(self, message="无权限执行该操作"):
        super().__init__(message)
        self.message = message


def gen_id(prefix):
    """生成带前缀的唯一 ID，如 u_1700000_abc123。"""
    return f"{prefix}_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"


def now_str():
    """当前 UTC 时间 ISO 字符串。"""
    return datetime.utcnow().isoformat()


def local_now_str():
    """当前本地时间字符串。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def row_to_dict(row):
    """sqlite3.Row 转普通 dict（递归处理可空字段）。"""
    if row is None:
        return None
    return dict(row)
