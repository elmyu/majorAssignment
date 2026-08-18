// ==================== 模拟后端数据库层 (localStorage) ====================
// 本项目为纯前端演示，使用 localStorage 充当持久化数据库。
// 说明：若生产环境接入真实后端，仅需替换 api.js 中的网络请求实现，
// 组件层无需改动。

import { genId } from '@/utils/format.js'

const DB_KEYS = {
  users: 'hms_users',
  signals: 'hms_signals',
  schedules: 'hms_schedules',
  devices: 'hms_devices',
  reservations: 'hms_reservations',
}

// ---------- 通用读写 ----------
function read(key) {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) : null
  } catch (e) {
    console.warn(`读取数据库[${key}]失败:`, e)
    return null
  }
}

function write(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
    return true
  } catch (e) {
    console.warn(`写入数据库[${key}]失败:`, e)
    return false
  }
}

// ---------- 种子数据 ----------
function seedUsers() {
  return [
    // 管理员
    { id: 'u_admin01', account: 'admin01', password: 'a123456', role: 'admin', name: '系统管理员', phone: '010-88880001' },
    // 医生
    { id: 'u_doc01', account: 'doctor01', password: 'd123456', role: 'doctor', name: '张医生', dept: '心内科', title: '主任医师', phone: '13900000001' },
    { id: 'u_doc02', account: 'doctor02', password: 'd123456', role: 'doctor', name: '李医生', dept: '超声科', title: '主治医师', phone: '13900000002' },
    { id: 'u_doc03', account: 'doctor03', password: 'd123456', role: 'doctor', name: '王医生', dept: '呼吸科', title: '副主任医师', phone: '13900000003' },
    { id: 'u_doc04', account: 'doctor04', password: 'd123456', role: 'doctor', name: '赵医生', dept: 'ICU重症监护室', title: '主治医师', phone: '13900000004' },
    // 患者
    { id: 'u_pat01', account: 'patient01', password: 'p123456', role: 'patient', name: '陈小明', gender: '男', age: 45, bloodType: 'A', phone: '13800000001', medicalNo: 'MN-2023001' },
    { id: 'u_pat02', account: 'patient02', password: 'p123456', role: 'patient', name: '刘丽', gender: '女', age: 32, bloodType: 'B', phone: '13800000002', medicalNo: 'MN-2023002' },
    { id: 'u_pat03', account: 'patient03', password: 'p123456', role: 'patient', name: '张伟', gender: '男', age: 58, bloodType: 'O', phone: '13800000003', medicalNo: 'MN-2023003' },
    { id: 'u_pat04', account: 'patient04', password: 'p123456', role: 'patient', name: '王芳', gender: '女', age: 27, bloodType: 'AB', phone: '13800000004', medicalNo: 'MN-2023004' },
    { id: 'u_pat05', account: 'patient05', password: 'p123456', role: 'patient', name: '李强', gender: '男', age: 51, bloodType: 'A', phone: '13800000005', medicalNo: 'MN-2023005' },
  ]
}

function seedSignals() {
  const records = []
  const base = [
    { p: 'u_pat01', heart: 72, sbp: 118, dbp: 78, spo2: 98, temp: 36.5 },
    { p: 'u_pat02', heart: 88, sbp: 132, dbp: 85, spo2: 96, temp: 37.1 },
    { p: 'u_pat03', heart: 66, sbp: 142, dbp: 90, spo2: 97, temp: 36.8 },
    { p: 'u_pat04', heart: 79, sbp: 121, dbp: 80, spo2: 98, temp: 36.6 },
    { p: 'u_pat05', heart: 95, sbp: 150, dbp: 95, spo2: 94, temp: 37.4 },
  ]
  // 为每位患者生成约 20 条历史记录（模拟随时间波动）
  for (const row of base) {
    for (let i = 0; i < 20; i++) {
      const d = new Date()
      d.setMonth(d.getMonth() - Math.floor(i / 4))
      d.setDate(d.getDate() - ((i * 3) % 26) - 1)
      d.setHours(8 + (i % 11), (i * 7) % 60, 0, 0)
      const fluctuation = (v) => Math.round(v + (Math.random() - 0.5) * 8)
      records.push({
        id: genId('sig'),
        patientId: row.p,
        recordTime: d.toISOString(),
        heartRate: fluctuation(row.heart),
        sbp: fluctuation(row.sbp),
        dbp: fluctuation(row.dbp),
        spo2: Math.max(90, Math.min(100, row.spo2 + (Math.random() - 0.5) * 4)),
        temp: Math.round((row.temp + (Math.random() - 0.5) * 0.6) * 10) / 10,
        note: '',
      })
    }
  }
  // 时间倒序排列
  return records.sort((a, b) => new Date(b.recordTime) - new Date(a.recordTime))
}

function seedSchedules() {
  const doctors = [
    'u_doc01', 'u_doc02', 'u_doc03', 'u_doc04',
  ]
  const rows = []
  const today = new Date()
  const dayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  for (let week = 0; week < 2; week++) {
    for (const did of doctors) {
      // 每医生每周 3 个出诊日
      for (let slot = 0; slot < 3; slot++) {
        const offDay = (week * 3 + slot + (did.charCodeAt(did.length - 1) % 5)) % 7
        const date = new Date(today)
        date.setDate(date.getDate() + (offDay - today.getDay() + 7) % 7 + week * 7)
        const morning = slot % 2 === 0
        rows.push({
          id: genId('sched'),
          doctorId: did,
          date: date.toISOString().split('T')[0],
          weekday: dayNames[date.getDay()],
          timeRange: morning ? '08:00-11:30' : '14:00-17:00',
          status: '出诊', // 出诊 / 空闲 / 停诊
          location: ['门诊大楼3楼', '门诊大楼2楼', '医技楼1楼', '重症楼6楼'][slot % 4],
        })
      }
    }
  }
  return rows
}

function seedDevices() {
  return [
    { id: 'dev_pre_001', code: 'MEQ-202603-0001', name: '心电图机', model: 'ECG-1200', department: '心内科', purchaseDate: '2026-03-15', price: 85000, status: '正常使用', runStatus: '在线', note: '门诊大楼3楼心电检查室' },
    { id: 'dev_pre_002', code: 'MEQ-202604-0002', name: '彩色超声诊断仪', model: 'US-5800Pro', department: '超声科', purchaseDate: '2026-04-20', price: 1280000, status: '正常使用', runStatus: '在线', note: '用于腹部及心脏超声检查' },
    { id: 'dev_pre_003', code: 'MEQ-202605-0003', name: '多参数监护仪', model: 'PM-9000', department: 'ICU重症监护室', purchaseDate: '2026-05-10', price: 156000, status: '正常使用', runStatus: '在线', note: 'ICU病区3号床' },
    { id: 'dev_pre_004', code: 'MEQ-202605-0004', name: '有创呼吸机', model: 'VNT-8200', department: '呼吸科', purchaseDate: '2026-05-22', price: 320000, status: '正常使用', runStatus: '运行中', note: '重症呼吸治疗专用' },
    { id: 'dev_pre_005', code: 'MEQ-202606-0005', name: '输液泵', model: 'IP-660', department: '普外科', purchaseDate: '2026-06-08', price: 28000, status: '维修中', runStatus: '故障', note: '显示屏故障，已送修' },
    { id: 'dev_pre_006', code: 'MEQ-202606-0006', name: '血液透析机', model: 'HD-4000S', department: '肾内科', purchaseDate: '2026-06-15', price: 450000, status: '正常使用', runStatus: '运行中', note: '透析中心A区' },
    { id: 'dev_pre_007', code: 'MEQ-202607-0007', name: '麻醉机', model: 'AN-7100', department: '麻醉科', purchaseDate: '2026-07-05', price: 520000, status: '闲置', runStatus: '校准中', note: '备用设备，定期维护中' },
    { id: 'dev_pre_008', code: 'MEQ-202607-0008', name: '便携式超声仪', model: 'PUS-200', department: '急诊科', purchaseDate: '2026-07-12', price: 195000, status: '已报废', runStatus: '离线', note: '使用年限到期，核心部件老化' },
    { id: 'dev_pre_009', code: 'MEQ-202607-0009', name: '除颤监护仪', model: 'DF-5000', department: '心内科', purchaseDate: '2026-07-18', price: 78000, status: '已报废', runStatus: '离线', note: '电池无法蓄电，主板损坏' },
  ]
}

function seedReservations() {
  return [
    { id: 'res_1', deviceId: 'dev_pre_002', doctorId: 'u_doc02', patientName: '', timeRange: '2026-08-18 09:00 - 10:00', purpose: '超声心动检查', createdAt: new Date().toISOString() },
  ]
}

// ---------- 初始化 ----------
function isSeeded() {
  return read(DB_KEYS.users) !== null
}

export function initDB() {
  if (isSeeded()) return
  write(DB_KEYS.users, seedUsers())
  write(DB_KEYS.signals, seedSignals())
  write(DB_KEYS.schedules, seedSchedules())
  write(DB_KEYS.devices, seedDevices())
  write(DB_KEYS.reservations, seedReservations())
}

export function resetDB() {
  Object.values(DB_KEYS).forEach((k) => localStorage.removeItem(k))
  initDB()
}

// ---------- 暴露集合访问 ----------
export const tables = {
  users: () => read(DB_KEYS.users) || [],
  signals: () => read(DB_KEYS.signals) || [],
  schedules: () => read(DB_KEYS.schedules) || [],
  devices: () => read(DB_KEYS.devices) || [],
  reservations: () => read(DB_KEYS.reservations) || [],
  saveUsers: (v) => write(DB_KEYS.users, v),
  saveSignals: (v) => write(DB_KEYS.signals, v),
  saveSchedules: (v) => write(DB_KEYS.schedules, v),
  saveDevices: (v) => write(DB_KEYS.devices, v),
  saveReservations: (v) => write(DB_KEYS.reservations, v),
}
