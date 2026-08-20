# ==================== 预约/排班资源控制器 (Controller) ====================

from flask import request
from flask_smorest import Blueprint as SmorestBlueprint
from flask.views import MethodView

from services.booking_service import ScheduleService, BookingService
from controllers.auth_utils import get_auth
from schemas import AppointmentCreateSchema, ReservationCreateSchema

blp = SmorestBlueprint("booking", __name__, url_prefix="/api/booking",
                       description="排班与预约接口")


# ---------- 医生排班 ----------
@blp.route("/schedules")
class ScheduleList(MethodView):
    @blp.response(200)
    def get(self):
        """医生出诊排班列表"""
        get_auth()  # 任意登录角色
        return ScheduleService.get_schedules()


# ---------- 患者挂号 ----------
@blp.route("/appointments")
class AppointmentList(MethodView):
    @blp.response(200)
    def get(self):
        """患者：我的挂号记录"""
        return BookingService.my_appointments(get_auth())

    @blp.response(201)
    @blp.arguments(AppointmentCreateSchema)
    def post(self, payload):
        """患者：在线挂号"""
        return BookingService.create_appointment(payload, get_auth())


@blp.route("/appointments/<appt_id>/cancel")
class AppointmentCancel(MethodView):
    @blp.response(200)
    def post(self, appt_id):
        """患者：取消挂号"""
        return BookingService.cancel_appointment(appt_id, get_auth())


# ---------- 医生：患者调阅 ----------
@blp.route("/patients")
class PatientList(MethodView):
    @blp.response(200)
    def get(self):
        """医生：可调阅的患者列表"""
        return BookingService.patients_for_doctor(get_auth())


# ---------- 设备预约 ----------
@blp.route("/reservations")
class ReservationList(MethodView):
    @blp.response(200)
    def get(self):
        """设备预约日志（医生/管理员）"""
        return BookingService.list_reservations(get_auth())

    @blp.response(201)
    @blp.arguments(ReservationCreateSchema)
    def post(self, payload):
        """医生：预约设备"""
        return BookingService.create_reservation(payload, get_auth())


@blp.route("/reservations/<res_id>/cancel")
class ReservationCancel(MethodView):
    @blp.response(200)
    def post(self, res_id):
        """取消设备预约（本人或管理员）"""
        return BookingService.cancel_reservation(res_id, get_auth())
