// ==================== 全局常量 ====================
// 集中管理各组件中重复出现的业务常量，便于统一维护。

// 角色中文映射
export const ROLE_LABELS = {
  patient: '患者',
  doctor: '医生',
  admin: '管理员',
};

// 各角色登录后的默认落地页
export const HOME_BY_ROLE = {
  patient: '/patient/health',
  doctor: '/doctor/records',
  admin: '/admin/users',
};

// 各角色侧边导航菜单
export const MENUS = {
  patient: [
    { to: '/patient/health', label: '我的健康档案' },
    { to: '/patient/appointment', label: '预约挂号' },
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

// 设备运行状态
export const RUN_STATUSES = ['在线', '运行中', '故障', '校准中', '离线'];

// 设备运行状态样式映射（用于表格徽标）
export const RUN_STATUS_CLASS = {
  在线: 'run-online',
  运行中: 'run-running',
  故障: 'run-fail',
  校准中: 'run-calib',
  离线: 'run-offline',
};

// 设备使用状态
export const USE_STATUSES = ['正常使用', '维修中', '闲置', '已报废'];

// 常用科室（管理员 / 设备录入 / 医生注册与维护时选填）
export const DEPARTMENTS = [
  '心内科',
  '心血管外科',
  '呼吸科',
  '消化内科',
  '内分泌科',
  '肾内科',
  '血液科',
  '神经内科',
  '神经外科',
  '普外科',
  '骨科',
  '泌尿外科',
  '胸外科',
  '妇产科',
  '儿科',
  '眼科',
  '耳鼻喉科',
  '口腔科',
  '皮肤科',
  '感染科',
  '肿瘤科',
  '康复科',
  '老年医学科',
  '中医科',
  '急诊科',
  '麻醉科',
  'ICU重症监护室',
  '放射科',
  '超声科',
  '检验科',
  '病理科',
  '放疗科',
  '疼痛科',
  '营养科',
  '健康管理中心',
  '日间手术中心',
];

