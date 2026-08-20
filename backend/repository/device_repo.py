# ==================== 设备数据访问层 (Repository/Mapper) ====================

from database import get_connection


class DeviceRepo:
    """设备表 devices 的数据访问对象。"""

    _COLS = ("id", "code", "name", "model", "department", "purchase_date",
             "price", "status", "run_status", "last_calibrated", "note")

    @staticmethod
    def list_all():
        conn = get_connection()
        try:
            return conn.execute("SELECT * FROM devices ORDER BY purchase_date DESC, id").fetchall()
        finally:
            conn.close()

    @staticmethod
    def find_by_id(device_id):
        conn = get_connection()
        try:
            return conn.execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
        finally:
            conn.close()

    @staticmethod
    def insert(device):
        conn = get_connection()
        try:
            conn.execute(
                """INSERT INTO devices
                   (id, code, name, model, department, purchase_date,
                    price, status, run_status, last_calibrated, note)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    device["id"], device.get("code", ""), device["name"],
                    device.get("model", ""), device["department"],
                    device.get("purchase_date", ""), device.get("price", 0),
                    device.get("status", "正常使用"),
                    device.get("run_status", "在线"),
                    device.get("last_calibrated"), device.get("note", ""),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def update(device_id, fields: dict):
        conn = get_connection()
        try:
            sets = ", ".join(f"{k} = ?" for k in fields.keys())
            values = [*fields.values(), device_id]
            conn.execute(f"UPDATE devices SET {sets} WHERE id = ?", values)
            conn.commit()
            return conn.execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
        finally:
            conn.close()

    @staticmethod
    def delete(device_id):
        conn = get_connection()
        try:
            conn.execute("DELETE FROM devices WHERE id = ?", (device_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def next_code_counter():
        """根据现有设备数量生成编号序号（简单策略）。"""
        conn = get_connection()
        try:
            row = conn.execute("SELECT COUNT(*) AS c FROM devices").fetchone()
            return row["c"] + 1
        finally:
            conn.close()
