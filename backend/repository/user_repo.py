# ==================== 用户数据访问层 (Repository/Mapper) ====================
# 专注 SQL 读写，不包含业务逻辑；业务规则统一放在 services 层。

from database import get_connection


class UserRepo:
    """用户表 users 的数据访问对象。"""

    @staticmethod
    def find_by_account(account):
        conn = get_connection()
        try:
            return conn.execute(
                "SELECT * FROM users WHERE account = ?", (account,)
            ).fetchone()
        finally:
            conn.close()

    @staticmethod
    def find_by_id(user_id):
        conn = get_connection()
        try:
            return conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        finally:
            conn.close()

    @staticmethod
    def list_all():
        conn = get_connection()
        try:
            return conn.execute(
                "SELECT * FROM users ORDER BY created_at ASC"
            ).fetchall()
        finally:
            conn.close()

    @staticmethod
    def insert(user):
        conn = get_connection()
        try:
            conn.execute(
                """INSERT INTO users
                   (id, account, password, role, name, dept, title, gender,
                    age, blood_type, phone, medical_no, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user["id"], user["account"], user["password"], user["role"],
                    user["name"], user.get("dept"), user.get("title"),
                    user.get("gender"), user.get("age"), user.get("blood_type"),
                    user.get("phone"), user.get("medical_no"), user["created_at"],
                ),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def update(user_id, fields: dict):
        """按字段字典更新用户，fields 中 key 必须为合法列名。"""
        conn = get_connection()
        try:
            sets = ", ".join(f"{k} = ?" for k in fields.keys())
            values = [*fields.values(), user_id]
            conn.execute(f"UPDATE users SET {sets} WHERE id = ?", values)
            conn.commit()
            return conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        finally:
            conn.close()

    @staticmethod
    def delete(user_id):
        conn = get_connection()
        try:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
        finally:
            conn.close()
