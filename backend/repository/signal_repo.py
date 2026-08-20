# ==================== 生理信号记录数据访问层 (Repository/Mapper) ====================

from database import get_connection


class SignalRepo:
    """生理信号记录表 signals 的数据访问对象。"""

    @staticmethod
    def list_by_patient(patient_id):
        conn = get_connection()
        try:
            return conn.execute(
                "SELECT * FROM signals WHERE patient_id = ? "
                "ORDER BY record_time DESC",
                (patient_id,),
            ).fetchall()
        finally:
            conn.close()

    @staticmethod
    def find_by_id(signal_id):
        conn = get_connection()
        try:
            return conn.execute(
                "SELECT * FROM signals WHERE id = ?", (signal_id,)
            ).fetchone()
        finally:
            conn.close()

    @staticmethod
    def insert(rec):
        conn = get_connection()
        try:
            conn.execute(
                """INSERT INTO signals
                   (id, patient_id, signal_type, sample_rate, data,
                    heart_rate, sbp, dbp, spo2, temp, record_time, note)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    rec["id"], rec["patient_id"], rec.get("signal_type", "ECG"),
                    rec.get("sample_rate", 0), rec.get("data", "[]"),
                    rec.get("heart_rate"), rec.get("sbp"), rec.get("dbp"),
                    rec.get("spo2"), rec.get("temp"), rec["record_time"],
                    rec.get("note", ""),
                ),
            )
            conn.commit()
        finally:
            conn.close()
