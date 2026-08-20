# ==================== 设备资源控制器 (Controller) ====================

from flask_smorest import Blueprint as SmorestBlueprint
from flask.views import MethodView

from services.device_service import DeviceService
from controllers.auth_utils import get_auth
from schemas import DeviceCreateSchema, DeviceUpdateSchema

blp = SmorestBlueprint("devices", __name__, url_prefix="/api/devices",
                       description="设备管理接口")


@blp.route("")
class DeviceList(MethodView):
    @blp.response(200)
    def get(self):
        """设备列表（医生/管理员可查看）"""
        get_auth().require(["doctor", "admin"])
        return DeviceService.list_devices()

    @blp.response(201)
    @blp.arguments(DeviceCreateSchema)
    def post(self, payload):
        """管理员：新增设备"""
        return DeviceService.create_device(payload, get_auth())


@blp.route("/<device_id>")
class DeviceItem(MethodView):
    @blp.response(200)
    @blp.arguments(DeviceUpdateSchema)
    def put(self, patch, device_id):
        """管理员：修改设备"""
        return DeviceService.update_device(device_id, patch, get_auth())

    @blp.response(200)
    def delete(self, device_id):
        """管理员：删除设备"""
        return DeviceService.delete_device(device_id, get_auth())
