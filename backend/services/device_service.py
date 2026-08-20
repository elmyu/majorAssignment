# ==================== 设备业务层 (Service) ====================

import datetime

from repository.device_repo import DeviceRepo
from utils import BizError, gen_id, row_to_dict

# 前端表单字段(驼峰) -> 数据表字段(蛇形) 映射
_INPUT_MAP = {
    "purchaseDate": "purchase_date",
    "runStatus": "run_status",
    "lastCalibrated": "last_calibrated",
}


def _serialize(d):
    """将设备记录转为前端使用的驼峰字段。"""
    return {
        "id": d["id"],
        "code": d["code"],
        "name": d["name"],
        "model": d["model"],
        "department": d["department"],
        "purchaseDate": d["purchase_date"],
        "price": d["price"],
        "status": d["status"],
        "runStatus": d["run_status"],
        "lastCalibrated": d["last_calibrated"],
        "note": d["note"],
    }


class DeviceService:
    """设备相关业务逻辑。"""

    @staticmethod
    def list_devices():
        return [_serialize(row_to_dict(d)) for d in DeviceRepo.list_all()]

    @staticmethod
    def create_device(payload, auth):
        auth.require(["admin"])
        name = (payload.get("name") or "").strip()
        department = (payload.get("department") or "").strip()
        purchase_date = payload.get("purchaseDate")
        if not name or not department or not purchase_date:
            raise BizError("请填写设备名称、科室与购置日期")

        counter = DeviceRepo.next_code_counter()
        now = datetime.datetime.now()
        ym = now.strftime("%Y%m")
        device = {
            "id": gen_id("dev"),
            "code": f"MEQ-{ym}-{counter:04d}",
            "name": name,
            "model": (payload.get("model") or "").strip(),
            "department": department,
            "purchase_date": purchase_date,
            "price": float(payload.get("price") or 0),
            "status": payload.get("status") or "正常使用",
            "run_status": payload.get("runStatus") or "在线",
            "last_calibrated": payload.get("lastCalibrated") or purchase_date,
            "note": (payload.get("note") or "").strip(),
        }
        DeviceRepo.insert(device)
        return _serialize(row_to_dict(DeviceRepo.find_by_id(device["id"])))

    @staticmethod
    def update_device(device_id, patch, auth):
        auth.require(["admin"])
        target = DeviceRepo.find_by_id(device_id)
        if not target:
            raise BizError("设备不存在")
        allowed = {
            "name", "model", "department", "purchase_date", "price",
            "status", "run_status", "last_calibrated", "note",
        }
        fields = {}
        for k, v in patch.items():
            col = _INPUT_MAP.get(k, k)
            if col in allowed and v is not None:
                fields[col] = v
        if fields:
            DeviceRepo.update(device_id, fields)
        return _serialize(row_to_dict(DeviceRepo.find_by_id(device_id)))

    @staticmethod
    def delete_device(device_id, auth):
        auth.require(["admin"])
        DeviceRepo.delete(device_id)
        return True
