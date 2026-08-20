# ==================== 预约/排班数据访问层 (Repository/Mapper) ====================
# 管理：设备预约记录 reservations、医生排班 schedules、患者挂号 appointments

from database import get_connection


class ReservationRepo:
    """设备预约记录表 reservations 的数据访问对象。"""

    @staticmethod
    def list_all():
        conn = get_connection()
        try:
            return conn.execute(
                "SELECT * FROM reservations ORDER BY created_at DESC"
            ).fetchall()
        finally:
            conn.close()

    @staticmethod
    def find_by_id(res_id):
        conn = get_connection()
        try:
            return conn.execute(
                "SELECT * FROM reservations WHERE id = ?", (res_id,)
            ).fetchone()
        finally:
            conn.close()

    @staticmethod
    def insert(rec):
        conn = get_connection()
        try:
            conn.execute(
                """INSERT INTO reservations
                   (id, device_id, doctor_id, patient_id, start_time,
                    time_range, purpose, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    rec["id"], rec["device_id"], rec["doctor_id"],
                    rec.get("patient_id"), rec.get("start_time", ""),
                    rec.get("time_range", ""), rec.get("purpose", ""),
                    rec.get("status", "待确认"), rec["created_at"],
                ),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def delete(res_id):
        conn = get_connection()
        try:
            conn.execute("DELETE FROM reservations WHERE id = ?", (res_id,))
            conn.commit()
        finally:
            conn.close()


class ScheduleRepo:
    """医生排班表 schedules 的数据访问对象。"""

    @staticmethod
    def list_all():
        conn = get_connection()
        try:
            return conn.execute(
                "SELECT * FROM schedules ORDER BY date ASC, time_range ASC"
            ).fetchall()
        finally:
            conn.close()

    @staticmethod
    def find_by_id(sched_id):
        conn = get_connection()
        try:
            return conn.execute(
                "SELECT * FROM schedules WHERE id = ?", (sched_id,)
            ).fetchone()
        finally:
            conn.close()

    @staticmethod
    def insert(rec):
        conn = get_connection()
        try:
            conn.execute(
                """INSERT INTO schedules
                   (id, doctor_id, date, weekday, time_range, status, location)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    rec["id"], rec["doctor_id"], rec["date"], rec.get("weekday", ""),
                    rec.get("time_range", ""), rec.get("status", "出诊"),
                    rec.get("location", ""),
                ),
            )
            conn.commit()
        finally:
            conn.close()


class AppointmentRepo:
    """患者挂号记录表 appointments 的数据访问对象。"""

    @staticmethod
    def list_by_patient(patient_id):
        conn = get_connection()
        try:
            return conn.execute(
                "SELECT * FROM appointments WHERE patient_id = ? "
                "ORDER BY created_at DESC",
                (patient_id,),
            ).fetchall()
        finally:
            conn.close()

    @staticmethod
    def list_all():
        conn = get_connection()
        try:
            return conn.execute(
                "SELECT * FROM appointments ORDER BY created_at DESC"
            ).fetchall()
        finally:
            conn.close()

    @staticmethod
    def find_by_id(appt_id):
        conn = get_connection()
        try:
            return conn.execute(
                "SELECT * FROM appointments WHERE id = ?", (appt_id,)
            ).fetchone()
        finally:
            conn.close()

    @staticmethod
    def insert(rec):
        conn = get_connection()
        try:
            conn.execute(
                """INSERT INTO appointments
                   (id, patient_id, doctor_id, schedule_id, appointment_date,
                    weekday, time_range, location, reason, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    rec["id"], rec["patient_id"], rec["doctor_id"],
                    rec.get("schedule_id"), rec.get("appointment_date", ""),
                    rec.get("weekday", ""), rec.get("time_range", ""),
                    rec.get("location", ""), rec.get("reason", ""),
                    rec.get("status", "待就诊"), rec["created_at"],
                ),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def update(appt_id, fields: dict):
        conn = get_connection()
        try:
            sets = ", ".join(f"{k} = ?" for k in fields.keys())
            values = [*fields.values(), appt_id]
            conn.execute(f"UPDATE appointments SET {sets} WHERE id = ?", values)
            conn.commit()
            return conn.execute(
                "SELECT * FROM appointments WHERE id = ?", (appt_id,)
            ).fetchone()
        finally:
            conn.close()
