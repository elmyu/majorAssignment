# ==================== 数据库访问层（连接 + 建表） ====================
# 使用 Python 内置 sqlite3，避免引入 ORM，更清晰地体现"数据访问层"职责。

import sqlite3
from config import DB_PATH

# 打开数据库连接（row_factory 让访问列名像字典一样方便）
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# 数据库初始化建表语句
SCHEMA = """
-- ============ 1. 用户表 ============
CREATE TABLE IF NOT EXISTS users (
    id          TEXT PRIMARY KEY,              -- 用户ID
    account     TEXT NOT NULL UNIQUE,          -- 登录账号
    password    TEXT NOT NULL,                 -- 密码
    role        TEXT NOT NULL,                 -- 角色标签: admin/doctor/patient
    name        TEXT NOT NULL,                 -- 姓名
    dept        TEXT,                          -- 科室(医生)
    title       TEXT,                          -- 职称(医生)
    gender      TEXT,                          -- 性别(患者)
    age         INTEGER,                       -- 年龄(患者)
    blood_type  TEXT,                          -- 血型(患者)
    phone       TEXT,                          -- 联系电话
    medical_no  TEXT,                          -- 门诊号(患者)
    created_at  TEXT
);

-- ============ 2. 设备表 ============
CREATE TABLE IF NOT EXISTS devices (
    id               TEXT PRIMARY KEY,         -- 设备ID
    code             TEXT NOT NULL UNIQUE,     -- 设备编号
    name             TEXT NOT NULL,            -- 设备名称
    model            TEXT,                     -- 型号
    department       TEXT NOT NULL,            -- 所属科室
    purchase_date    TEXT,                     -- 购置日期
    price            REAL DEFAULT 0,           -- 价格
    status           TEXT,                     -- 当前状态(使用/维修/闲置/报废)
    run_status       TEXT,                     -- 运行状态(在线/故障等)
    last_calibrated  TEXT,                     -- 上次校准日期
    note             TEXT                      -- 备注
);

-- ============ 3. 生理信号记录表 ============
CREATE TABLE IF NOT EXISTS signals (
    id           TEXT PRIMARY KEY,             -- 记录ID
    patient_id   TEXT NOT NULL,                -- 患者ID(关联 users)
    signal_type  TEXT DEFAULT 'ECG',           -- 信号类型(ECG/SPO2/BP等)
    sample_rate  INTEGER DEFAULT 0,            -- 采样率(Hz)
    data         TEXT,                         -- 一段模拟信号数值(以JSON存储)
    heart_rate   REAL,                         -- 心率
    sbp          REAL,                         -- 收缩压
    dbp          REAL,                         -- 舒张压
    spo2         REAL,                         -- 血氧
    temp         REAL,                         -- 体温
    record_time  TEXT,                         -- 采集时间
    note         TEXT,
    FOREIGN KEY (patient_id) REFERENCES users(id)
);

-- ============ 4. 预约记录表(设备预约) ============
CREATE TABLE IF NOT EXISTS reservations (
    id          TEXT PRIMARY KEY,              -- 预约ID
    device_id   TEXT NOT NULL,                 -- 设备ID(关联 devices)
    doctor_id   TEXT NOT NULL,                 -- 医生ID(关联 users)
    patient_id  TEXT,                          -- 患者ID(可选)
    start_time  TEXT NOT NULL,                 -- 预约开始时间
    time_range  TEXT,                          -- 预约时间范围描述
    purpose     TEXT,                          -- 用途
    status      TEXT DEFAULT '待确认',          -- 预约状态
    created_at  TEXT,
    FOREIGN KEY (device_id) REFERENCES devices(id),
    FOREIGN KEY (doctor_id) REFERENCES users(id),
    FOREIGN KEY (patient_id) REFERENCES users(id)
);

-- ============ 5. 医生排班表(辅助业务: 预约挂号) ============
CREATE TABLE IF NOT EXISTS schedules (
    id          TEXT PRIMARY KEY,              -- 排班ID
    doctor_id   TEXT NOT NULL,                 -- 医生ID
    date        TEXT NOT NULL,                 -- 出诊日期
    weekday     TEXT,
    time_range  TEXT,                          -- 时间段
    status      TEXT DEFAULT '出诊',            -- 出诊/空闲/停诊
    location    TEXT,                          -- 诊室位置
    FOREIGN KEY (doctor_id) REFERENCES users(id)
);

-- ============ 6. 患者挂号记录表(辅助业务: 在线挂号) ============
CREATE TABLE IF NOT EXISTS appointments (
    id                TEXT PRIMARY KEY,        -- 挂号ID
    patient_id        TEXT NOT NULL,           -- 患者ID
    doctor_id         TEXT NOT NULL,           -- 医生ID
    schedule_id       TEXT,                    -- 关联排班
    appointment_date  TEXT,
    weekday           TEXT,
    time_range        TEXT,
    location          TEXT,
    reason            TEXT,
    status            TEXT DEFAULT '待就诊',    -- 待就诊/已完成/已取消
    created_at        TEXT,
    FOREIGN KEY (patient_id) REFERENCES users(id),
    FOREIGN KEY (doctor_id) REFERENCES users(id)
);
"""


def init_db():
    """初始化数据库：创建所有表。"""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def table_count(table):
    """返回指定表记录数，用于判断是否需要写入种子数据。"""
    conn = get_connection()
    try:
        row = conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()
        return row["c"]
    finally:
        conn.close()
