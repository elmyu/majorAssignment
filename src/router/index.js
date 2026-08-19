import { createRouter, createWebHashHistory } from 'vue-router';
import { currentUser } from '@/services/api.js';
import { HOME_BY_ROLE } from '@/utils/constants.js';

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/components/auth/LoginPage.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    redirect: () => {
      const u = currentUser.info;

      return u ? HOME_BY_ROLE[u.role] || '/login' : '/login';
    },
  },
  {
    path: '/patient',
    component: () => import('@/components/layout/MainLayout.vue'),
    meta: { role: 'patient' },
    children: [
      {
        path: 'health',
        name: 'patientHealth',
        component: () => import('@/components/patient/MyHealthRecord.vue'),
        meta: { title: '我的健康档案' },
      },
            {
        path: 'schedule',
        name: 'patientSchedule',
        component: () => import('@/components/patient/DoctorScheduleView.vue'),
        meta: { title: '医生时间查看' },
      },
      {
        path: 'appointment',
        name: 'patientAppointment',
        component: () => import('@/components/patient/PatientAppointment.vue'),
        meta: { title: '预约挂号' },
      },
      { path: '', redirect: '/patient/health' },
    ],
  },
  {
    path: '/doctor',
    component: () => import('@/components/layout/MainLayout.vue'),
    meta: { role: 'doctor' },
    children: [
      {
        path: 'records',
        name: 'doctorRecords',
        component: () => import('@/components/doctor/PatientRecords.vue'),
        meta: { title: '患者信息调阅' },
      },
      {
        path: 'device',
        name: 'doctorDevice',
        component: () => import('@/components/doctor/DeviceDashboard.vue'),
        meta: { title: '设备台账看板' },
      },
      {
        path: 'reserve',
        name: 'doctorReserve',
        component: () => import('@/components/doctor/DeviceReserve.vue'),
        meta: { title: '设备预约' },
      },
      { path: '', redirect: '/doctor/records' },
    ],
  },
  {
    path: '/admin',
    component: () => import('@/components/layout/MainLayout.vue'),
    meta: { role: 'admin' },
    children: [
      {
        path: 'users',
        name: 'adminUsers',
        component: () => import('@/components/admin/UserManage.vue'),
        meta: { title: '系统用户管理' },
      },
      {
        path: 'devices',
        name: 'adminDevices',
        component: () => import('@/components/admin/DeviceManage.vue'),
        meta: { title: '设备物资维护' },
      },
      { path: '', redirect: '/admin/users' },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/login' },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

// 全局路由守卫：登录校验 + 角色权限隔离（前端条件判断）
router.beforeEach((to) => {
  const u = currentUser.info;
  if (to.meta.public) {
    return true;
  }
  if (!u) {
    return { name: 'login', query: { redirect: to.fullPath } };
  }
    // 角色校验
  if (to.meta.role && to.meta.role !== u.role) {
    return HOME_BY_ROLE[u.role] || '/login';
  }
  return true;
});

export default router;
