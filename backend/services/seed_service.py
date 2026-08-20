# ==================== 种子数据服务 ====================
# 首次启动时写入演示数据（用户、设备、信号、排班），保证系统开箱即用。

import json
import random
from datetime import datetime, timedelta
from datetime import date

from database import init_db, table_count, get_connection
from utils import now_str, gen_id


def _seed_users(conn):
    users = [
        # (id, account, password, role, name, dept/title 或 gender/age/blood,...)
        ("u_admin01", "admin01", "a123456", "admin", "系统管理员", None, None,
         None, None, None, "010-88880001", None),
        ("u_doc01", "doctor01", "d123456", "doctor", "张医生", "心内科", "主任医师",
         None, None, None, "13900000001", None),
        ("u_doc02", "doctor02", "d123456", "doctor", "李医生", "超声科", "主治医师",
         None, None, None, "13900000002", None),
        ("u_doc03", "doctor03", "d123456", "doctor", "王医生", "呼吸科", "副主任医师",
         None, None, None, "13900000003", None),
        ("u_doc04", "doctor04", "d123456", "doctor", "赵医生", "ICU重症监护室", "主治医师",
         None, None, None, "13900000004", None),
        ("u_pat01", "patient01", "p123456", "patient", "陈小明", None, None,
         "男", 45, "A", "13800000001", "MN-2023001"),
        ("u_pat02", "patient02", "p123456", "patient", "刘丽", None, None,
         "女", 32, "B", "13800000002", "MN-2023002"),
        ("u_pat03", "patient03", "p123456", "patient", "张伟", None, None,
         "男", 58, "O", "13800000003", "MN-2023003"),
        ("u_pat04", "patient04", "p123456", "patient", "王芳", None, None,
         "女", 27, "AB", "13800000004", "MN-2023004"),
        ("u_pat05", "patient05", "p123456", "patient", "李强", None, None,
         "男", 51, "A", "13800000005", "MN-2023005"),
    ]
    now = now_str()
    for u in users:
        conn.execute(
            """INSERT OR IGNORE INTO users
               (id, account, password, role, name, dept, title, gender,
                age, blood_type, phone, medical_no, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (u[0], u[1], u[2], u[3], u[4], u[5], u[6], u[7], u[8], u[9],
             u[10], u[11], now),
        )


def _seed_devices(conn):
    devices = [
        ("dev_pre_001", "MEQ-202603-0001", "心电图机", "ECG-1200", "心内科",
         "2026-03-15", 85000, "正常使用", "在线", "2026-08-01", "门诊大楼3楼心电检查室"),
        ("dev_pre_002", "MEQ-202604-0002", "彩色超声诊断仪", "US-5800Pro", "超声科",
         "2026-04-20", 1280000, "正常使用", "在线", "2026-08-05", "用于腹部及心脏超声检查"),
        ("dev_pre_003", "MEQ-202605-0003", "多参数监护仪", "PM-9000", "ICU重症监护室",
         "2026-05-10", 156000, "正常使用", "在线", "2026-07-20", "ICU病区3号床"),
        ("dev_pre_004", "MEQ-202605-0004", "有创呼吸机", "VNT-8200", "呼吸科",
         "2026-05-22", 320000, "正常使用", "运行中", "2026-08-03", "重症呼吸治疗专用"),
        ("dev_pre_005", "MEQ-202606-0005", "输液泵", "IP-660", "普外科",
         "2026-06-08", 28000, "维修中", "故障", "2026-06-10", "显示屏故障，已送修"),
        ("dev_pre_006", "MEQ-202606-0006", "血液透析机", "HD-4000S", "肾内科",
         "2026-06-15", 450000, "正常使用", "运行中", "2026-08-01", "透析中心A区"),
        ("dev_pre_007", "MEQ-202607-0007", "麻醉机", "AN-7100", "麻醉科",
         "2026-07-05", 520000, "闲置", "校准中", "2026-08-06", "备用设备，定期维护中"),
        ("dev_pre_008", "MEQ-202607-0008", "便携式超声仪", "PUS-200", "急诊科",
         "2026-07-12", 195000, "已报废", "离线", "2025-12-01", "使用年限到期，核心部件老化"),
        ("dev_pre_009", "MEQ-202607-0009", "除颤监护仪", "DF-5000", "心内科",
         "2026-07-18", 78000, "已报废", "离线", "2025-11-20", "电池无法蓄电，主板损坏"),
    ]
    for d in devices:
        conn.execute(
            """INSERT OR IGNORE INTO devices
               (id, code, name, model, department, purchase_date, price,
                status, run_status, last_calibrated, note)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", d,
        )


def _seed_signals(conn):
    base = [
        ("u_pat01", 72, 118, 78, 98, 36.5),
        ("u_pat02", 88, 132, 85, 96, 37.1),
        ("u_pat03", 66, 142, 90, 97, 36.8),
        ("u_pat04", 79, 121, 80, 98, 36.6),
        ("u_pat05", 95, 150, 95, 94, 37.4),
    ]
    random.seed(42)
    records = []
    for p, heart, sbp, dbp, spo2, temp in base:
        for i in range(20):
            d = datetime.now() - timedelta(days=i * 3 + i // 4 * 20 + 1)
            d = d.replace(hour=8 + (i % 11), minute=(i * 7) % 60, second=0)
            fl = lambda v: round(v + (random.random() - 0.5) * 8)
            data = {
                "type": "ECG",
                "sample_rate": 250,
                "points": [round(random.uniform(60, 140), 1) for _ in range(10)],
            }
            records.append((
                gen_id("sig"), p, "ECG", 250, json.dumps(data),
                fl(heart), fl(sbp), fl(dbp),
                round(max(90, min(100, spo2 + (random.random() - 0.5) * 4))),
                round(temp + (random.random() - 0.5) * 0.6, 1),
                d.strftime("%Y-%m-%d %H:%M:%S"), "",
            ))
    for r in records:
        conn.execute(
            """INSERT OR IGNORE INTO signals
               (id, patient_id, signal_type, sample_rate, data,
                heart_rate, sbp, dbp, spo2, temp, record_time, note)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", r,
        )


def _seed_schedules(conn):
    doctors = ["u_doc01", "u_doc02", "u_doc03", "u_doc04"]
    day_names = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
    today = date.today()
    rows = []
    for week in range(2):
        for did in doctors:
            for slot in range(3):
                off_day = (week * 3 + slot + (ord(did[-1]) % 5)) % 7
                d = today + timedelta(days=((off_day - today.weekday()) % 7) + week * 7)
                morning = slot % 2 == 0
                rows.append((
                    gen_id("sched"), did, d.isoformat(), day_names[d.weekday()],
                    "08:00-11:30" if morning else "14:00-17:00", "出诊",
                    ["门诊大楼3楼", "门诊大楼2楼", "医技楼1楼", "重症楼6楼"][slot % 4],
                ))
    for r in rows:
        conn.execute(
            """INSERT OR IGNORE INTO schedules
               (id, doctor_id, date, weekday, time_range, status, location)
               VALUES (?, ?, ?, ?, ?, ?, ?)""", r,
        )


def run_seed():
    """初始化数据库并写入种子数据（若用户表为空）。"""
    init_db()
    if table_count("users") == 0:
        conn = get_connection()
        try:
            _seed_users(conn)
            _seed_devices(conn)
            _seed_signals(conn)
            _seed_schedules(conn)
            conn.commit()
        finally:
            conn.close()


if __name__ == "__main__":
    run_seed()
    print("数据库初始化完成。")
