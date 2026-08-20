# ==================== 生理信号记录资源控制器 (Controller) ====================

from flask_smorest import Blueprint as SmorestBlueprint
from flask.views import MethodView

from services.signal_service import SignalService
from controllers.auth_utils import get_auth

blp = SmorestBlueprint("signals", __name__, url_prefix="/api/signals",
                       description="生理信号记录接口")


@blp.route("/my")
class MySignals(MethodView):
    @blp.response(200)
    def get(self):
        """患者：查看本人的生理信号记录"""
        return SignalService.my_signals(get_auth())


@blp.route("/patient/<patient_id>")
class PatientSignals(MethodView):
    @blp.response(200)
    def get(self, patient_id):
        """医生：查看指定患者的生理信号记录"""
        return SignalService.signals_of_patient(patient_id, get_auth())
