// ==================== Axios 请求封装 ====================
// 统一管理 baseURL、登录用户标识请求头、异常处理。

import axios from 'axios';
import { ref } from 'vue';

// 后端服务地址（开发环境）— 见后端 run_dev.py
const BASE_URL = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000';

// 本地存储键
const STORAGE_KEY = 'hms_current_user';

const http = axios.create({
  baseURL: BASE_URL + '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// ---- 当前登录用户（响应式，供路由守卫与组件读取） ----
const currentUser = ref(null);

function readStored() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}
currentUser.value = readStored();

export function getCurrentUser() {
  return currentUser.value;
}

export function setCurrentUser(user) {
  currentUser.value = user || null;
  if (user) localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  else localStorage.removeItem(STORAGE_KEY);
}

export { currentUser };

// ---- 请求拦截器：为已登录用户附加权限标识请求头 ----
http.interceptors.request.use((config) => {
  const user = getCurrentUser();
  if (user) {
    config.headers['X-User-Role'] = user.role;
    config.headers['X-User-Id'] = user.id;
    config.headers['X-User-Name'] = user.name;
  }
  return config;
});

// ---- 响应拦截器：统一下发错误信息 ----
http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    // 从后端统一异常 JSON 中提取 message
    const data = err.response && err.response.data;
    const message = (data && data.message) || err.message || '请求失败，请稍后重试';
    return Promise.reject(new Error(message));
  }
);

export default http;
