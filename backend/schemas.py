# ==================== Marshmallow 请求/响应 Schema 定义 ====================
# 用于 flask-smorest：校验请求体并生成 Swagger 参数文档。
# 说明：marshmallow 4.x 字段仅支持 metadata 传描述。

from marshmallow import Schema, fields


def _m(desc):
    return {"description": desc}


# ---------- 认证 ----------
class LoginSchema(Schema):
    account = fields.Str(required=True, metadata=_m("登录账号"))
    password = fields.Str(required=True, metadata=_m("登录密码"))


class RegisterSchema(Schema):
    role = fields.Str(required=True, metadata=_m("角色: patient/doctor"))
    account = fields.Str(required=True)
    password = fields.Str(required=True)
    name = fields.Str(required=True)
    phone = fields.Str(required=True)
    dept = fields.Str(metadata=_m("科室(医生)"))
    title = fields.Str(metadata=_m("职称(医生)"))
    gender = fields.Str(metadata=_m("性别(患者)"))
    age = fields.Int(metadata=_m("年龄(患者)"))


class ResetPasswordSchema(Schema):
    account = fields.Str(required=True)
    name = fields.Str(required=True)
    phone = fields.Str(metadata=_m("手机号"))
    newPassword = fields.Str(required=True)


# ---------- 用户管理 ----------
class UserCreateSchema(Schema):
    role = fields.Str(required=True)
    account = fields.Str(required=True)
    password = fields.Str(required=True)
    name = fields.Str(required=True)
    dept = fields.Str()
    title = fields.Str()
    gender = fields.Str()
    age = fields.Int()
    bloodType = fields.Str()
    phone = fields.Str()
    medicalNo = fields.Str()


class UserUpdateSchema(Schema):
    name = fields.Str()
    phone = fields.Str()
    password = fields.Str()
    dept = fields.Str()
    title = fields.Str()
    gender = fields.Str()
    age = fields.Int()
    bloodType = fields.Str()
    medicalNo = fields.Str()


# ---------- 设备 ----------
class DeviceCreateSchema(Schema):
    name = fields.Str(required=True)
    model = fields.Str()
    department = fields.Str(required=True)
    purchaseDate = fields.Str(required=True)
    price = fields.Float()
    status = fields.Str()
    runStatus = fields.Str()
    lastCalibrated = fields.Str()
    note = fields.Str()


class DeviceUpdateSchema(Schema):
    name = fields.Str()
    model = fields.Str()
    department = fields.Str()
    purchaseDate = fields.Str()
    price = fields.Float()
    status = fields.Str()
    runStatus = fields.Str()
    lastCalibrated = fields.Str()
    note = fields.Str()


# ---------- 预约 ----------
class AppointmentCreateSchema(Schema):
    scheduleId = fields.Str(required=True)
    reason = fields.Str()


class ReservationCreateSchema(Schema):
    deviceId = fields.Str(required=True)
    timeRange = fields.Str(required=True)
    purpose = fields.Str()
