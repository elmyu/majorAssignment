// ==================== 模拟后端 API 服务层 ====================
// 本文件模拟真实后端 API。每个业务接口内部都做"角色权限校验"，
// 权限不足抛出 403。前端组件通过这些接口访问数据，实现后端条件判断隔离。
//
// 生产环境接入真实后端时，仅需将此文件内的每个函数替换为对应的
// http 请求（如 axios/fetch），并携带 token，服务端做同样的权限判断即可。
import { initDB, tables } from './db.js'

// 会话状态（模拟服务端 session / 前端登录 token 的解码结果）
const CURRENT_USER_KEY = 'hms_current_user'
export const currentUser = {
  get info() {
    try {
      const raw = localStorage.getItem(CURRENT_USER_KEY)
      return raw ? JSON.parse(raw) : null
    } catch {
      return null
    }
  },
  set info(v) {
    if (v === null) {
      localStorage.removeItem(CURRENT_USER_KEY)
    } else {
      localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(v))
    }
  },
}

// 确保数据库已初始化
initDB()

// 权限异常
class PermissionError extends Error {
  constructor(message = '无权限执行该操作') {
    super(message)
    this.name = 'PermissionError'
    this.code = 403
  }
}

// 业务异常
class BizError extends Error {
  constructor(message, code = 400) {
    super(message)
    this.name = 'BizError'
    this.code = code
  }
}

// 内建权限校验：role 需属于 allowed
function assertRole(allowed) {
  const u = currentUser.info
  if (!u) throw new PermissionError('请先登录')
  if (!allowed.includes(u.role)) throw new PermissionError('当前角色无权限执行该操作')
  return u
}

// 统一返回「当前登录用户」（含角色），供前端条件渲染使用
export function getCurrentUser() {
  return currentUser.info
}

// ==================== 认证 ====================
export function login(account, password) {
  const users = tables.users()
  const u = users.find((x) => x.account === account && x.password === password)
  if (!u) throw new BizError('账号或密码错误', 401)
  const { password: _pwd, ...safe } = u
  currentUser.info = safe
  return safe
}

export function logout() {
  currentUser.info = null
}

// ==================== 患者视角接口 ====================
// 我的健康档案：只能查阅属于当前患者本人的生理信号历史记录
export function getMySignals() {
  const u = assertRole(['patient'])
  return {
    patient: u,
    records: tables.signals()
      .filter((s) => s.patientId === u.id)
      .sort((a, b) => new Date(b.recordTime) - new Date(a.recordTime)),
  }
}

// 医生时间查看：能查看所有医生的出诊/空闲时间表
export function getSchedules() {
  const u = assertRole(['patient', 'doctor', 'admin'])
  const users = tables.users()
  const doctors = users.filter((x) => x.role === 'doctor')
  const schedules = tables.schedules()
    .map((s) => {
      const doc = doctors.find((d) => d.id === s.doctorId)
      return { ...s, doctorName: doc ? doc.name : '未知', doctorDept: doc ? doc.dept : '', doctorTitle: doc ? doc.title : '' }
    })
    .sort((a, b) => (a.date + a.timeRange).localeCompare(b.date + b.timeRange))
  return schedules
}

// ==================== 医生视角接口 ====================
// 患者信息调阅：医生有权限查看所有患者的生理信号记录与基本信息
export function getPatientsForDoctor() {
  assertRole(['doctor'])
  const users = tables.users()
  const patients = users
    .filter((x) => x.role === 'patient')
    .map(({ password, ...safe }) => safe)
  return patients
}

export function getSignalsOfPatient(patientId) {
  assertRole(['doctor'])
  const users = tables.users()
  const patient = users.find((x) => x.id === patientId && x.role === 'patient')
  if (!patient) throw new BizError('未找到该患者')
  return {
    patient: (() => { const { password, ...safe } = patient; return safe })(),
    records: tables.signals()
      .filter((s) => s.patientId === patientId)
      .sort((a, b) => new Date(b.recordTime) - new Date(a.recordTime)),
  }
}

// 设备台账看板：实时查看所有设备运行状态
export function getDevices() {
  assertRole(['doctor', 'admin'])
  return tables.devices()
}

// 设备预约：选中空闲设备填写预约时间，提交生成预约日志
export function createReservation({ deviceId, timeRange, purpose }) {
  const u = assertRole(['doctor'])
  const devices = tables.devices()
  const device = devices.find((d) => d.id === deviceId)
  if (!device) throw new BizError('设备不存在')
  if (device.status === '已报废') throw new BizError('该设备已报废，不可预约')
  if (device.runStatus === '故障') throw new BizError('该设备处于故障状态，不可预约')
  if (!timeRange) throw new BizError('请填写预约时间')
  const reservations = tables.reservations()
  const newRes = {
    id: 'res_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8),
    deviceId: deviceId,
    deviceName: device.name,
    deviceCode: device.code,
    doctorId: u.id,
    doctorName: u.name,
    timeRange,
    purpose: purpose || '',
    createdAt: new Date().toISOString(),
  }
  reservations.unshift(newRes)
  tables.saveReservations(reservations)
  return newRes
}

// 医生查看自己/所有预约日志
export function getReservations() {
  const u = assertRole(['doctor', 'admin'])
  const reservations = tables.reservations()
  return reservations
}

// ==================== 管理员视角接口 ====================
// 系统用户管理：增删改查医生和患者账户
export function listUsers(roleFilter) {
  assertRole(['admin'])
  const users = tables.users()
  let list = users.map(({ password, ...safe }) => safe)
  if (roleFilter && roleFilter !== 'all') {
    list = list.filter((u) => u.role === roleFilter)
  }
  return list
}

export function createUser({ role, account, password, name, dept, title, gender, age, bloodType, phone, medicalNo }) {
  assertRole(['admin'])
  const users = tables.users()
  if (users.some((x) => x.account === account)) throw new BizError('该账号已存在')
  if (!account || !password || !name) throw new BizError('请填写完整账号、密码与姓名')
  const newUser = {
    id: 'u_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8),
    account,
    password,
    role,
    name,
    dept: role === 'doctor' ? dept : undefined,
    title: role === 'doctor' ? title : undefined,
    gender: role === 'patient' ? gender : undefined,
    age: role === 'patient' ? age : undefined,
    bloodType: role === 'patient' ? bloodType : undefined,
    phone,
    medicalNo: role === 'patient' ? medicalNo : undefined,
  }
  users.push(newUser)
  tables.saveUsers(users)
  const { password: _p, ...safe } = newUser
  return safe
}

export function updateUser(id, patch) {
  assertRole(['admin'])
  const users = tables.users()
  const idx = users.findIndex((x) => x.id === id)
  if (idx === -1) throw new BizError('用户不存在')
  const target = users[idx]
  if (target.role === 'admin') throw new BizError('管理员账户不允许修改')
  const next = { ...target }
  Object.keys(patch).forEach((k) => {
    if (patch[k] !== undefined && patch[k] !== null && k !== 'id' && k !== 'role') {
      next[k] = patch[k]
    }
  })
  users[idx] = next
  tables.saveUsers(users)
  const { password, ...safe } = next
  return safe
}

export function deleteUser(id) {
  assertRole(['admin'])
  const users = tables.users()
  const target = users.find((x) => x.id === id)
  if (!target) throw new BizError('用户不存在')
  if (target.role === 'admin') throw new BizError('管理员账户不允许删除')
  tables.saveUsers(users.filter((x) => x.id !== id))
  return true
}

// 设备物资维护：新增/修改/删除设备
export function createDevice(data) {
  assertRole(['admin'])
  if (!data.name || !data.department || !data.purchaseDate) throw new BizError('请填写设备名称、科室与购置日期')
  const devices = tables.devices()
  const counter = devices.length + 1
  const now = new Date()
  const ym = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}`
  const newDevice = {
    id: 'dev_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8),
    code: `MEQ-${ym}-${String(counter).padStart(4, '0')}`,
    name: data.name,
    model: data.model || '',
    department: data.department,
    purchaseDate: data.purchaseDate,
    price: Number(data.price) || 0,
    status: data.status || '正常使用',
    runStatus: data.runStatus || '在线',
    note: data.note || '',
  }
  devices.unshift(newDevice)
  tables.saveDevices(devices)
  return newDevice
}

export function updateDevice(id, data) {
  assertRole(['admin'])
  const devices = tables.devices()
  const idx = devices.findIndex((d) => d.id === id)
  if (idx === -1) throw new BizError('设备不存在')
  devices[idx] = { ...devices[idx], ...data, id }
  tables.saveDevices(devices)
  return devices[idx]
}

export function deleteDevice(id) {
  assertRole(['admin'])
  const devices = tables.devices()
  tables.saveDevices(devices.filter((d) => d.id !== id))
  return true
}
