<script setup>
import { ref, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getCurrentUser, logout } from '@/services/api.js';
import { ROLE_LABELS } from '@/utils/constants.js';

const route = useRoute();
const router = useRouter();

const user = ref(getCurrentUser());

// 侧边栏宽度：从 localStorage 读取用户自定义值，默认 200
const DEFAULT_WIDTH = 200;
const MIN_WIDTH = 140;
const MAX_WIDTH = 360;
const sidebarWidth = ref(Number(localStorage.getItem('sidebarWidth')) || DEFAULT_WIDTH);

// 各角色导航菜单
const menus = {
  patient: [
    { to: '/patient/health', label: '我的健康档案' },
    { to: '/patient/schedule', label: '医生时间查看' },
  ],
  doctor: [
    { to: '/doctor/records', label: '患者信息调阅' },
    { to: '/doctor/device', label: '设备台账看板' },
    { to: '/doctor/reserve', label: '设备预约' },
  ],
  admin: [
    { to: '/admin/users', label: '系统用户管理' },
    { to: '/admin/devices', label: '设备物资维护' },
  ],
};

const currentMenus = menus[user.value?.role] || [];
const currentRole = ROLE_LABELS[user.value?.role] || '';

function doLogout() {
  logout();
  router.push('/login');
}

// ---- 拖拽调整侧边栏宽度 ----
const resizing = ref(false);

function startResize(e) {
  e.preventDefault();
  resizing.value = true;
  document.body.classList.add('sidebar-resizing');
  document.addEventListener('mousemove', onResize);
  document.addEventListener('mouseup', stopResize);
}

function onResize(e) {
  if (!resizing.value) return;
  const w = e.clientX;
  if (w >= MIN_WIDTH && w <= MAX_WIDTH) {
    sidebarWidth.value = w;
  }
}

function stopResize() {
  resizing.value = false;
  document.body.classList.remove('sidebar-resizing');
  document.removeEventListener('mousemove', onResize);
  document.removeEventListener('mouseup', stopResize);
  // 记住用户拖拽后的宽度
  localStorage.setItem('sidebarWidth', String(sidebarWidth.value));
}

onBeforeUnmount(() => {
  document.body.classList.remove('sidebar-resizing');
  document.removeEventListener('mousemove', onResize);
  document.removeEventListener('mouseup', stopResize);
});
</script>

<template>
  <div class="layout">
    <!-- 顶栏 -->
    <header class="topbar">
      <div class="brand">
        <h1>医疗信息管理系统</h1>
        <span>三角色权限平台</span>
      </div>
      <div class="topbar-right">
        <div class="user-info">
          <span class="user-name">{{ user?.name }}（{{ currentRole }}）</span>
        </div>
        <button class="logout-btn" @click="doLogout">退出登录</button>
      </div>
    </header>

    <div class="body">
      <!-- 侧边导航 -->
      <aside class="sidebar" :style="{ width: sidebarWidth + 'px' }">
        <nav class="menu">
          <router-link
            v-for="m in currentMenus"
            :key="m.to"
            :to="m.to"
            class="menu-item"
            active-class="active"
          >
            {{ m.label }}
          </router-link>
        </nav>
      </aside>
      <!-- 拖拽手柄 -->
      <div class="resize-handle" title="拖拽调整导航宽度" @mousedown="startResize"></div>

      <!-- 内容区：无过渡动画，切换即时生效 -->
      <main class="content">
        <div class="page-title">{{ route.meta.title || '首页' }}</div>
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  padding: 12px 24px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}
.brand h1 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: #1f2937;
}
.brand span {
  font-size: 0.75rem;
  color: #9ca3af;
}
.topbar-right {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}
.user-name {
  font-weight: 500;
  color: #1f2937;
  font-size: 0.9rem;
}
.logout-btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid #e5e0e0;
  background: #fff;
  color: #b05656;
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 600;
  font-family: inherit;
}
.logout-btn:hover {
  background: #fdeeee;
}

.body {
  display: flex;
  flex: 1;
  min-height: 0;
}
.sidebar {
  width: 200px;
  flex-shrink: 0;
  padding: 18px 12px;
  background: #fff;
  border-right: 1px solid #eef2ee;
  overflow: hidden;
  box-sizing: border-box;
}
.menu {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.menu-item {
  display: block;
  padding: 10px 14px;
  border-radius: 6px;
  color: #4b5563;
  text-decoration: none;
  font-size: 0.9rem;
  white-space: nowrap;
}
.menu-item:hover {
  background: #f0f7f0;
}
.menu-item.active {
  background: #eaf5ea;
  color: #3d6b40;
  font-weight: 700;
}

/* 拖拽手柄 */
.resize-handle {
  width: 6px;
  flex-shrink: 0;
  cursor: col-resize;
  background: transparent;
  border-right: 1px dashed transparent;
  position: relative;
}
.resize-handle:hover {
  background: #e8f2e8;
  border-right-color: #9fc4a2;
}
.resize-handle::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 2px;
  transform: translateX(-50%);
  background: transparent;
}

.content {
  flex: 1;
  min-width: 0;
  padding: 20px 24px;
  overflow-y: auto;
}
.page-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 16px;
}

/* 拖拽时禁止选中文本 */
:global(body.sidebar-resizing) {
  user-select: none;
  cursor: col-resize;
}
</style>
