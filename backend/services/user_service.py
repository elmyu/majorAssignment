# ==================== 用户业务层 (Service) ====================
# 负责认证、注册、用户管理；校验、业务规则与数据组织均在此层。

from repository.user_repo import UserRepo
from utils import BizError, NotAuthorized, gen_id, now_str, row_to_dict

# 密码脱敏用到的字段（蛇形 -> 对外驼峰键）
_PUBLIC_FIELDS = {
    "id": "id", "account": "account", "role": "role", "name": "name",
    "dept": "dept", "title": "title", "gender": "gender", "age": "age",
    "blood_type": "bloodType", "phone": "phone", "medical_no": "medicalNo",
}


def _public(user: dict) -> dict:
    """去除密码字段，转为对外安全且前端可用的驼峰数据。"""
    result = {}
    for col, camel in _PUBLIC_FIELDS.items():
        if col in user:
            result[camel] = user[col]
    return result


class UserService:
    """用户相关业务逻辑。"""

    @staticmethod
    def login(account, password):
        user = UserRepo.find_by_account(account)
        if not user or user["password"] != password:
            raise BizError("账号或密码错误", 401)
        return _public(row_to_dict(user))

    @staticmethod
    def register(payload):
        role = payload.get("role")
        if role not in ("patient", "doctor"):
            raise BizError("该身份暂不支持自助注册")
        account = (payload.get("account") or "").strip()
        name = (payload.get("name") or "").strip()
        if not account or not name:
            raise BizError("请填写账号与姓名")
        if not payload.get("password") or len(payload["password"]) < 6:
            raise BizError("密码长度至少为 6 位")
        phone = (payload.get("phone") or "").strip()
        import re
        if not re.match(r"^1[3-9]\d{9}$", phone):
            raise BizError("请填写有效的 11 位手机号")
        if UserRepo.find_by_account(account):
            raise BizError("该账号已存在")

        new_user = {
            "id": gen_id("u"),
            "account": account,
            "password": payload["password"],
            "role": role,
            "name": name,
            "phone": phone,
            "created_at": now_str(),
        }
        if role == "doctor":
            new_user["dept"] = (payload.get("dept") or "").strip() or None
            new_user["title"] = (payload.get("title") or "").strip() or None
        else:
            new_user["gender"] = payload.get("gender")
            new_user["age"] = payload.get("age")
            new_user["medical_no"] = f"MN-{int(time_conflict()):06d}"

        UserRepo.insert(new_user)
        return _public(new_user)

    @staticmethod
    def reset_password(payload):
        account = (payload.get("account") or "").strip()
        name = (payload.get("name") or "").strip()
        phone = (payload.get("phone") or "").strip()
        new_password = payload.get("newPassword") or ""
        if not account or not name:
            raise BizError("请填写完整的账号、姓名与手机号")
        if len(new_password) < 6:
            raise BizError("新密码长度至少为 6 位")
        user = UserRepo.find_by_account(account)
        if not user:
            raise BizError("未找到该账号")
        if user["role"] == "admin":
            raise BizError("管理员账户不支持通过此方式重置密码")
        if user["name"] != name or (user["phone"] or "") != phone:
            raise BizError("身份信息校验失败，姓名或手机号不正确")
        UserRepo.update(user["id"], {"password": new_password})
        return True

    # ---------- 管理员：用户管理 ----------
    @staticmethod
    def list_users(role_filter=None):
        users = UserRepo.list_all()
        data = [_public(row_to_dict(u)) for u in users]
        if role_filter and role_filter != "all":
            data = [u for u in data if u["role"] == role_filter]
        return data

    @staticmethod
    def create_user(payload):
        account = (payload.get("account") or "").strip()
        password = payload.get("password") or ""
        name = (payload.get("name") or "").strip()
        role = payload.get("role")
        if not account or not password or not name:
            raise BizError("请填写完整账号、密码与姓名")
        if UserRepo.find_by_account(account):
            raise BizError("该账号已存在")
        new_user = {
            "id": gen_id("u"),
            "account": account,
            "password": password,
            "role": role,
            "name": name,
            "phone": payload.get("phone"),
            "created_at": now_str(),
        }
        if role == "doctor":
            new_user["dept"] = payload.get("dept")
            new_user["title"] = payload.get("title")
        elif role == "patient":
            new_user["gender"] = payload.get("gender")
            new_user["age"] = payload.get("age")
            new_user["blood_type"] = payload.get("bloodType")
            new_user["medical_no"] = payload.get("medicalNo")
        UserRepo.insert(new_user)
        return _public(new_user)

    @staticmethod
    def update_user(user_id, patch):
        target = row_to_dict(UserRepo.find_by_id(user_id))
        if not target:
            raise BizError("用户不存在")
        if target["role"] == "admin":
            raise BizError("管理员账户不允许修改")
        # 仅允许更新安全字段（支持前端驼峰键）
        _INPUT_MAP = {"bloodType": "blood_type", "medicalNo": "medical_no"}
        allowed = {
            "name", "phone", "password", "dept", "title",
            "gender", "age", "blood_type", "medical_no",
        }
        fields = {}
        for k, v in patch.items():
            col = _INPUT_MAP.get(k, k)
            if col in allowed and v is not None:
                fields[col] = v
        if fields:
            UserRepo.update(user_id, fields)
        return _public(row_to_dict(UserRepo.find_by_id(user_id)))

    @staticmethod
    def delete_user(user_id):
        target = row_to_dict(UserRepo.find_by_id(user_id))
        if not target:
            raise BizError("用户不存在")
        if target["role"] == "admin":
            raise BizError("管理员账户不允许删除")
        UserRepo.delete(user_id)
        return True


# 用于生成门诊号的小工具函数（避免与 now_str 耦合）
def time_conflict():
    import time
    return int(time.time() % 1000000)


class AuthContext:
    """从请求头解析出的当前登录用户信息，供 service 做角色校验。"""

    def __init__(self, role, user_id=None, name=None):
        self.role = role
        self.user_id = user_id
        self.name = name

    def require(self, roles):
        """要求当前用户角色属于给定集合，否则抛 403。"""
        if self.role not in roles:
            raise NotAuthorized("当前角色无权限执行该操作")
        return self
