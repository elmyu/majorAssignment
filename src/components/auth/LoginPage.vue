<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { login } from '../../services/api.js';

const router = useRouter();
const role = ref('patient');
const account = ref('');
const password = ref('');
const errorMsg = ref('');

const roleOptions = [
  { value: 'patient', label: '患者' },
  { value: 'doctor', label: '医生' },
  { value: 'admin', label: '管理员' },
];

// 各角色演示账号（选择身份后自动填入，便于测试）
const demoAccounts = {
  patient: { acc: 'patient01', pwd: 'p123456' },
  doctor: { acc: 'doctor01', pwd: 'd123456' },
  admin: { acc: 'admin01', pwd: 'a123456' },
};

const homeByRole = { patient: '/patient/health', doctor: '/doctor/records', admin: '/admin/users' };

function selectRole(value) {
  role.value = value;
  // 切换身份时自动填入对应演示账号
  const demo = demoAccounts[value];
  account.value = demo.acc;
  password.value = demo.pwd;
  errorMsg.value = '';
}

function doLogin() {
  errorMsg.value = '';
  if (!account.value.trim() || !password.value) {
    errorMsg.value = '请输入账号与密码';
    return;
  }
  try {
    const user = login(account.value.trim(), password.value);
    // 校验身份是否匹配
    if (user.role !== role.value) {
      errorMsg.value = `该账号为"${roleLabel(user.role)}"身份，与当前选择不符`;
      return;
    }
    router.push(homeByRole[user.role]);
  } catch (e) {
    errorMsg.value = e.message || '登录失败';
  }
}

function roleLabel(r) {
  const map = { patient: '患者', doctor: '医生', admin: '管理员' };
  return map[r] || r;
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
        <h1>医疗机构信息管理系统</h1>
      </div>
      <div class="form-box">
        <h2>登录</h2>

        <!-- 身份选择 -->
        <div class="role-select">
          <button
            v-for="opt in roleOptions"
            :key="opt.value"
            type="button"
            class="role-item"
            :class="{ active: role === opt.value }"
            @click="selectRole(opt.value)"
          >
            {{ opt.label }}
          </button>
        </div>

        <label class="field">
          <span>账号（{{ roleLabel(role) }}）</span>
          <input v-model="account" type="text" placeholder="请输入账号" @keyup.enter="doLogin" />
        </label>
        <label class="field">
          <span>密码</span>
          <input
            v-model="password"
            type="password"
            placeholder="请输入密码"
            @keyup.enter="doLogin"
          />
        </label>

        <p v-if="errorMsg" class="error">{{ errorMsg }}</p>

        <button class="login-btn" @click="doLogin">登录</button>
        <div class="quick-fill">
          <span>已按所选身份自动填入演示账号，您也可自行修改。</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(135deg, #e8f3e8 0%, #f5faf5 50%, #e7f1e7 100%);
}
.login-card {
  display: flex;
  max-width: 840px;
  width: 100%;
  overflow: hidden;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 16px 40px rgba(45, 90, 50, 0.16);
  border: 1px solid #e6f0e6;
}
.login-brand {
  flex: 1;
  padding: 48px 36px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: linear-gradient(160deg, #4a9d50 0%, #35833c 55%, #2c6e33 100%);
  color: #fff;
  position: relative;
  overflow: hidden;
}
.login-brand::after {
  content: '';
  position: absolute;
  right: -50px;
  top: -50px;
  width: 190px;
  height: 190px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 50%;
}
.login-brand::before {
  content: '';
  position: absolute;
  left: -40px;
  bottom: -60px;
  width: 170px;
  height: 170px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 50%;
}
.login-brand h1 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 12px;
  letter-spacing: 0.02em;
  position: relative;
  z-index: 1;
}

.form-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 44px 40px;
}
.form-box h2 {
  margin: 0 0 20px;
  font-size: 1.3rem;
  color: #2c3e2f;
}
.role-select {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 18px;
}
.role-item {
  padding: 10px 0;
  border: 1px solid #dde7dd;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  color: #5a6d5d;
  background: #fbfdfb;
  font-family: inherit;
  text-align: center;
  transition: all 0.15s;
}
.role-item:hover {
  border-color: #9cc39f;
  background: #f0f8f0;
}
.role-item.active {
  background: linear-gradient(135deg, #4a9d50, #35833c);
  color: #fff;
  border-color: #35833c;
  box-shadow: 0 3px 10px rgba(46, 110, 52, 0.25);
}
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
}
.field span {
  font-size: 0.84rem;
  font-weight: 600;
  color: #3f5242;
}
.field input {
  padding: 11px 13px;
  border: 1px solid #dde7dd;
  border-radius: 8px;
  font-size: 0.9rem;
  outline: none;
  font-family: inherit;
  background: #fbfdfb;
  transition:
    border-color 0.15s,
    background 0.15s;
}
.field input:focus {
  border-color: #4a9d50;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(74, 157, 80, 0.12);
}
.error {
  color: #c0392b;
  font-size: 0.82rem;
  margin: 0 0 10px;
}
.login-btn {
  padding: 12px;
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  background: linear-gradient(90deg, #4a9d50, #35833c);
  font-family: inherit;
  box-shadow: 0 4px 12px rgba(46, 110, 52, 0.28);
}
.login-btn:hover {
  background: linear-gradient(90deg, #3d8c43, #2c6e33);
}
.quick-fill {
  font-size: 0.8rem;
  color: #93a293;
  margin-top: 16px;
}
@media (max-width: 720px) {
  .login-card {
    flex-direction: column;
  }
  .login-brand {
    padding: 28px;
  }
}
</style>
