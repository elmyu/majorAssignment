// ==================== 业务接口封装 ====================
// 前端所有数据操作均通过 Axios 调用 Flask 后端 REST API，
// 不再使用 localStorage 模拟数据库。各方法返回 Promise。

import http, { getCurrentUser, setCurrentUser } from './http.js';

// 重导出：当前登录用户（本地读取）
export { getCurrentUser };

// 兼容既有代码：路由守卫通过 currentUser.info 读取当前用户
export const currentUser = {
  get info() {
    return getCurrentUser();
  },
};

// ---------- 认证 ----------
// 登录成功后，将用户信息存入本地，供后续请求附加权限标识头
export async function login(account, password) {
  const user = await http.post('/users/login', { account, password });
  setCurrentUser(user);
  return user;
}

export function logout() {
  setCurrentUser(null);
}

export async function register(form) {
  const user = await http.post('/users/register', form);
  setCurrentUser(user);
  return user;
}

export async function resetPassword(form) {
  return http.post('/users/reset-password', form);
}

// ---------- 生理信号 ----------
// 患者查看本人的信号记录
export async function getMySignals() {
  return http.get('/signals/my');
}

// 医生查看指定患者信号记录
export async function getSignalsOfPatient(patientId) {
  return http.get(`/signals/patient/${patientId}`);
}

// ---------- 医生排班 ----------
export async function getSchedules() {
  return http.get('/booking/schedules');
}

// ---------- 患者挂号 ----------
export async function createAppointment({ scheduleId, reason }) {
  return http.post('/booking/appointments', { scheduleId, reason });
}

export async function getMyAppointments() {
  return http.get('/booking/appointments');
}

export async function cancelAppointment(id) {
  return http.post(`/booking/appointments/${id}/cancel`);
}

// 医生可调阅的患者列表
export async function getPatientsForDoctor() {
  return http.get('/booking/patients');
}

// ---------- 设备 ----------
export async function getDevices() {
  return http.get('/devices');
}

export async function createDevice(data) {
  return http.post('/devices', data);
}

export async function updateDevice(id, data) {
  return http.put(`/devices/${id}`, data);
}

export async function deleteDevice(id) {
  return http.delete(`/devices/${id}`);
}

// ---------- 设备预约 ----------
export async function createReservation({ deviceId, timeRange, purpose }) {
  return http.post('/booking/reservations', { deviceId, timeRange, purpose });
}

export async function getReservations() {
  return http.get('/booking/reservations');
}

export async function cancelReservation(id) {
  return http.post(`/booking/reservations/${id}/cancel`);
}

// ---------- 用户管理（管理员） ----------
export async function listUsers(roleFilter) {
  return http.get('/users', { params: { role: roleFilter || 'all' } });
}

export async function createUser(data) {
  return http.post('/users', data);
}

export async function updateUser(id, patch) {
  return http.put(`/users/${id}`, patch);
}

export async function deleteUser(id) {
  return http.delete(`/users/${id}`);
}
