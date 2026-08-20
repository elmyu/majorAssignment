# ==================== 预约/排班业务层 (Service) ====================
# 管理：医生排班查询、患者挂号、设备预约日志。

from repository.booking_repo import ReservationRepo, ScheduleRepo, AppointmentRepo
from repository.device_repo import DeviceRepo
from repository.user_repo import UserRepo
from utils import BizError, gen_id, now_str, row_to_dict


class ScheduleService:
    """医生排班业务逻辑。"""

    @staticmethod
    def get_schedules(user_repo=UserRepo, schedule_repo=ScheduleRepo):
        """返回含医生信息的排班列表（驼峰字段）。"""
        users = {u["id"]: row_to_dict(u) for u in user_repo.list_all()}
        rows = []
        for s in schedule_repo.list_all():
            item = row_to_dict(s)
            doc = users.get(item["doctor_id"], {})
            rows.append(
                {
                    "id": item["id"],
                    "doctorId": item["doctor_id"],
                    "doctorName": doc.get("name", "未知"),
                    "doctorDept": doc.get("dept", ""),
                    "doctorTitle": doc.get("title", ""),
                    "date": item["date"],
                    "weekday": item.get("weekday", ""),
                    "timeRange": item.get("time_range", ""),
                    "status": item.get("status", "出诊"),
                    "location": item.get("location", ""),
                }
            )
        rows.sort(key=lambda r: r["date"] + r["timeRange"])
        return rows


class BookingService:
    """患者挂号与设备预约业务逻辑。"""

    # ---------- 患者挂号 ----------
    @staticmethod
    def create_appointment(payload, auth):
        auth.require(["patient"])
        schedule_id = payload.get("scheduleId")
        schedule = ScheduleRepo.find_by_id(schedule_id)
        if not schedule:
            raise BizError("该排班时段不存在或已失效")
        schedule = row_to_dict(schedule)
        if schedule["status"] not in ("出诊", "空闲"):
            raise BizError("该时段不支持预约")
        doctor = UserRepo.find_by_id(schedule["doctor_id"])
        if not doctor:
            raise BizError("医生信息不存在")
        doctor = row_to_dict(doctor)

        patient = row_to_dict(UserRepo.find_by_id(auth.user_id))
        # 校验是否重复预约
        existing = AppointmentRepo.list_by_patient(auth.user_id)
        for a in existing:
            if (
                a["doctor_id"] == schedule["doctor_id"]
                and a["appointment_date"] == schedule["date"]
                and a["time_range"] == schedule["time_range"]
                and a["status"] != "已取消"
            ):
                raise BizError("您已预约该时段的号，请勿重复预约")

        new_appt = {
            "id": gen_id("appt"),
            "patientId": auth.user_id,
            "patientName": patient.get("name", ""),
            "doctorId": schedule["doctor_id"],
            "doctorName": doctor.get("name", ""),
            "doctorDept": doctor.get("dept", ""),
            "doctorTitle": doctor.get("title", ""),
            "scheduleId": schedule["id"],
            "appointmentDate": schedule["date"],
            "weekday": schedule.get("weekday", ""),
            "timeRange": schedule.get("time_range", ""),
            "location": schedule.get("location", ""),
            "reason": (payload.get("reason") or "").strip(),
            "status": "待就诊",
            "createdAt": now_str(),
        }
        AppointmentRepo.insert({
            "id": new_appt["id"],
            "patient_id": auth.user_id,
            "doctor_id": schedule["doctor_id"],
            "schedule_id": schedule["id"],
            "appointment_date": schedule["date"],
            "weekday": schedule.get("weekday", ""),
            "time_range": schedule.get("time_range", ""),
            "location": schedule.get("location", ""),
            "reason": new_appt["reason"],
            "status": "待就诊",
            "created_at": now_str(),
        })
        return new_appt

    @staticmethod
    def my_appointments(auth):
        auth.require(["patient"])
        users = {u["id"]: row_to_dict(u) for u in UserRepo.list_all()}
        result = []
        for a in AppointmentRepo.list_by_patient(auth.user_id):
            doc = users.get(a["doctor_id"], {})
            result.append(
                {
                    "id": a["id"],
                    "patientId": a["patient_id"],
                    "doctorId": a["doctor_id"],
                    "doctorName": doc.get("name", ""),
                    "doctorDept": doc.get("dept", ""),
                    "doctorTitle": doc.get("title", ""),
                    "appointmentDate": a["appointment_date"],
                    "weekday": a["weekday"],
                    "timeRange": a["time_range"],
                    "location": a["location"],
                    "reason": a["reason"],
                    "status": a["status"],
                    "createdAt": a["created_at"],
                }
            )
        return result

    @staticmethod
    def cancel_appointment(appt_id, auth):
        auth.require(["patient"])
        target = row_to_dict(AppointmentRepo.find_by_id(appt_id))
        if not target:
            raise BizError("该挂号记录不存在")
        if target["patient_id"] != auth.user_id:
            raise BizError("您只能取消本人的挂号")
        if target["status"] != "待就诊":
            raise BizError("当前状态不支持取消")
        AppointmentRepo.update(appt_id, {"status": "已取消"})
        return True

    # ---------- 医生：患者调阅 ----------
    @staticmethod
    def patients_for_doctor(auth):
        auth.require(["doctor"])
        users = [row_to_dict(u) for u in UserRepo.list_all()]
        patients = []
        for u in users:
            if u["role"] == "patient":
                u.pop("password", None)
                patients.append(u)
        return patients

    # ---------- 设备预约 ----------
    @staticmethod
    def create_reservation(payload, auth):
        auth.require(["doctor"])
        device_id = payload.get("deviceId")
        device = DeviceRepo.find_by_id(device_id)
        if not device:
            raise BizError("设备不存在")
        device = row_to_dict(device)
        if device["status"] == "已报废":
            raise BizError("该设备已报废，不可预约")
        if device["run_status"] == "故障":
            raise BizError("该设备处于故障状态，不可预约")
        time_range = (payload.get("timeRange") or "").strip()
        if not time_range:
            raise BizError("请填写预约时间")

        doctor = row_to_dict(UserRepo.find_by_id(auth.user_id))
        new_res = {
            "id": gen_id("res"),
            "deviceId": device_id,
            "deviceName": device["name"],
            "deviceCode": device["code"],
            "doctorId": auth.user_id,
            "doctorName": doctor.get("name", ""),
            "startTime": time_range.split(" ")[0],
            "timeRange": time_range,
            "purpose": (payload.get("purpose") or "").strip(),
            "createdAt": now_str(),
        }
        ReservationRepo.insert({
            "id": new_res["id"],
            "device_id": device_id,
            "doctor_id": auth.user_id,
            "start_time": new_res["startTime"],
            "time_range": time_range,
            "purpose": new_res["purpose"],
            "created_at": now_str(),
        })
        return new_res

    @staticmethod
    def list_reservations(auth):
        auth.require(["doctor", "admin"])
        rows = []
        for r in ReservationRepo.list_all():
            item = row_to_dict(r)
            dev = row_to_dict(DeviceRepo.find_by_id(item["device_id"]))
            doc = row_to_dict(UserRepo.find_by_id(item["doctor_id"]))
            rows.append(
                {
                    "id": item["id"],
                    "deviceId": item["device_id"],
                    "deviceName": (dev or {}).get("name", ""),
                    "deviceCode": (dev or {}).get("code", ""),
                    "doctorId": item["doctor_id"],
                    "doctorName": (doc or {}).get("name", ""),
                    "startTime": item["start_time"],
                    "timeRange": item["time_range"],
                    "purpose": item["purpose"],
                    "createdAt": item["created_at"],
                }
            )
        rows.sort(key=lambda r: r["createdAt"], reverse=True)
        return rows

    @staticmethod
    def cancel_reservation(res_id, auth):
        auth.require(["doctor", "admin"])
        target = ReservationRepo.find_by_id(res_id)
        if not target:
            raise BizError("该预约记录不存在")
        if auth.role != "admin" and target["doctor_id"] != auth.user_id:
            raise BizError("您只能取消本人创建的预约")
        ReservationRepo.delete(res_id)
        return True
