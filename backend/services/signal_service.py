# ==================== 生理信号业务层 (Service) ====================

from repository.signal_repo import SignalRepo
from repository.user_repo import UserRepo
from utils import BizError, row_to_dict


def _serialize_signal(s):
    """将信号记录转为前端使用的驼峰字段。"""
    return {
        "id": s["id"],
        "signalType": s["signal_type"],
        "sampleRate": s["sample_rate"],
        "data": s["data"],
        "heartRate": s["heart_rate"],
        "sbp": s["sbp"],
        "dbp": s["dbp"],
        "spo2": s["spo2"],
        "temp": s["temp"],
        "recordTime": s["record_time"].replace(" ", "T"),
        "note": s["note"] or "",
    }


def _serialize_patient(p):
    """将患者用户记录转为前端使用的驼峰字段（剥离敏感字段）。"""
    return {
        "id": p["id"],
        "account": p.get("account", ""),
        "name": p.get("name", ""),
        "role": p.get("role", ""),
        "gender": p.get("gender", ""),
        "age": p.get("age", ""),
        "bloodType": p.get("blood_type", ""),
        "phone": p.get("phone", ""),
        "medicalNo": p.get("medical_no", ""),
    }


class SignalService:
    """生理信号记录业务逻辑。"""

    @staticmethod
    def my_signals(auth):
        """患者仅可查看自己的信号记录。"""
        auth.require(["patient"])
        patient = _serialize_patient(row_to_dict(UserRepo.find_by_id(auth.user_id)))
        records = [
            _serialize_signal(row_to_dict(s)) for s in SignalRepo.list_by_patient(auth.user_id)
        ]
        return {"patient": patient, "records": records}

    @staticmethod
    def signals_of_patient(patient_id, auth):
        """医生查看指定患者的信号记录。"""
        auth.require(["doctor"])
        patient_row = UserRepo.find_by_id(patient_id)
        if not patient_row or patient_row["role"] != "patient":
            raise BizError("未找到该患者")
        patient = _serialize_patient(row_to_dict(patient_row))
        records = [
            _serialize_signal(row_to_dict(s)) for s in SignalRepo.list_by_patient(patient_id)
        ]
        return {"patient": patient, "records": records}
