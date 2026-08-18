<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { login, register, resetPassword } from '@/services/api.js';
import { ROLE_LABELS } from '@/utils/constants.js';

const router = useRouter();

// 当前展示的面板：login / register / forgot
const mode = ref('login');

// ---- 登录 ----
const role = ref('patient');
const account = ref('');
const password = ref('');
const errorMsg = ref('');
const successMsg = ref('');

// ---- 注册 ----
const regForm = ref({
  role: 'patient',
  account: '',
  name: '',
  gender: '男',
  age: '',
  dept: '',
  title: '',
  phone: '',
  password: '',
  confirm: '',
});
const regError = ref('');
const regSuccess = ref('');

// ---- 忘记密码 ----
const forgotForm = ref({
  account: '',
  name: '',
  phone: '',
  newPassword: '',
  confirm: '',
});
const forgotError = ref('');
const forgotSuccess = ref('');

// ---- 模拟验证码（纯前端演示，实际应服务端生成并短信下发）----
// 注册流程
const regCaptcha = ref('');
const regCaptchaInput = ref('');
const regCaptchaMsg = ref('');
// 忘记密码流程
const forgotCaptcha = ref('');
const forgotCaptchaInput = ref('');
const forgotCaptchaMsg = ref('');

/** 生成 4 位随机验证码并返回 */
function genCaptcha() {
  return String(Math.floor(1000 + Math.random() * 9000));
}

/**
 * 获取验证码（模拟短信下发）。
 * field: 用于区分当前所在的表单流程提示对象
 */
function sendCaptcha(field, msg) {
  const code = genCaptcha();
  field.value = code;
  msg.value = `验证码已发送：${code}（演示环境直接展示）`;
  // 3 秒后清除提示
  setTimeout(() => {
    if (msg.value) msg.value = '';
  }, 5000);
}

/** 校验验证码，错误时返回提示，通过返回空字符串 */
function checkCaptcha(field, input) {
  if (!field.value) return '请先获取验证码';
  if (!input.value.trim()) return '请填写验证码';
  if (input.value.trim() !== field.value) return '验证码错误';
  return '';
}

const roleOptions = [
  { value: 'patient', label: '患者' },
  { value: 'doctor', label: '医生' },
  { value: 'admin', label: '管理员' },
];

// 各角色演示账号（登录页选择身份后自动填入，便于测试）
const demoAccounts = {
  patient: { acc: 'patient01', pwd: 'p123456' },
  doctor: { acc: 'doctor01', pwd: 'd123456' },
  admin: { acc: 'admin01', pwd: 'a123456' },
};

const homeByRole = { patient: '/patient/health', doctor: '/doctor/records', admin: '/admin/users' };

// ---------- 面板切换 ----------
function openRegister() {
  mode.value = 'register';
  regError.value = '';
  regSuccess.value = '';
}
function openForgot() {
  mode.value = 'forgot';
  forgotError.value = '';
  forgotSuccess.value = '';
}
function backToLogin() {
  mode.value = 'login';
  errorMsg.value = '';
  successMsg.value = '';
}

// ---------- 登录 ----------
function selectRole(value) {
  role.value = value;
  const demo = demoAccounts[value];
  account.value = demo.acc;
  password.value = demo.pwd;
  errorMsg.value = '';
}

function doLogin() {
  errorMsg.value = '';
  successMsg.value = '';
  if (!account.value.trim() || !password.value) {
    errorMsg.value = '请输入账号与密码';
    return;
  }
  try {
    const user = login(account.value.trim(), password.value);
    if (user.role !== role.value) {
      errorMsg.value = `该账号为"${ROLE_LABELS[user.role]}"身份，与当前选择不符`;
      return;
    }
    router.push(homeByRole[user.role]);
  } catch (e) {
    errorMsg.value = e.message || '登录失败';
  }
}

// ---------- 注册 ----------
function doRegister() {
  regError.value = '';
  regSuccess.value = '';
  const f = regForm.value;
  if (f.password !== f.confirm) {
    regError.value = '两次输入的密码不一致';
    return;
  }
  try {
    register({
      role: f.role,
      account: f.account,
      password: f.password,
      name: f.name,
      dept: f.dept,
      title: f.title,
      gender: f.gender,
      age: f.age,
      phone: f.phone,
    });
    // 注册成功后自动登录并进入对应首页
    login(f.account.trim(), f.password);
    router.push(homeByRole[f.role]);
  } catch (e) {
    regError.value = e.message || '注册失败';
  }
}

// ---------- 忘记密码 ----------
function doResetPassword() {
  forgotError.value = '';
  forgotSuccess.value = '';
  const f = forgotForm.value;
  if (f.newPassword !== f.confirm) {
    forgotError.value = '两次输入的新密码不一致';
    return;
  }
  try {
    resetPassword({ account: f.account, name: f.name, phone: f.phone, newPassword: f.newPassword });
    forgotSuccess.value = '密码重置成功，请使用新密码登录';
  } catch (e) {
    forgotError.value = e.message || '重置失败';
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
        <h1>医疗机构信息管理系统</h1>
        <p class="brand-sub">三角色权限平台 · 安全认证</p>
      </div>

      <div class="form-box">
        <!-- ======== 登录 ======== -->
        <template v-if="mode === 'login'">
          <h2>登录</h2>
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
            <span>账号（{{ ROLE_LABELS[role] }}）</span>
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
          <p v-if="successMsg" class="success">{{ successMsg }}</p>

          <button class="login-btn" @click="doLogin">登录</button>

          <div class="auth-links">
            <a class="link" @click="openForgot">忘记密码？</a>
            <a class="link" @click="openRegister">没有账号？去注册</a>
          </div>

          <div class="quick-fill">
            <span>已按所选身份自动填入演示账号，您也可自行修改。</span>
          </div>
        </template>

        <!-- ======== 注册 ======== -->
        <template v-else-if="mode === 'register'">
          <h2>注册账号</h2>
          <div class="role-select small">
            <button
              v-for="r in ['patient', 'doctor']"
              :key="r"
              type="button"
              class="role-item"
              :class="{ active: regForm.role === r }"
              @click="regForm.role = r"
            >
              {{ ROLE_LABELS[r] }}
            </button>
          </div>

          <label class="field">
            <span>账号 <em class="req">*</em></span>
            <input v-model="regForm.account" type="text" placeholder="请输入登录账号" />
          </label>
          <label class="field">
            <span>姓名 <em class="req">*</em></span>
            <input v-model="regForm.name" type="text" placeholder="请输入真实姓名" />
          </label>

          <div class="row2">
            <label class="field">
              <span>性别</span>
              <select v-model="regForm.gender">
                <option value="男">男</option>
                <option value="女">女</option>
              </select>
            </label>
            <label class="field">
              <span>年龄</span>
              <input v-model="regForm.age" type="number" min="1" max="120" placeholder="如 30" />
            </label>
          </div>

          <template v-if="regForm.role === 'doctor'">
            <label class="field">
              <span>所在科室</span>
              <input v-model="regForm.dept" type="text" placeholder="如 心内科" />
            </label>
            <label class="field">
              <span>职称</span>
              <input v-model="regForm.title" type="text" placeholder="如 主治医师" />
            </label>
          </template>

          <label class="field">
            <span>手机号 <em class="req">*</em></span>
            <input
              v-model="regForm.phone"
              type="tel"
              maxlength="11"
              placeholder="请输入 11 位手机号"
            />
          </label>
          <label class="field">
            <span>密码 <em class="req">*</em>（至少 6 位）</span>
            <input v-model="regForm.password" type="password" placeholder="设置登录密码" />
          </label>
          <label class="field">
            <span>确认密码 <em class="req">*</em></span>
            <input v-model="regForm.confirm" type="password" placeholder="再次输入密码" />
          </label>

          <p v-if="regError" class="error">{{ regError }}</p>
          <p v-if="regSuccess" class="success">{{ regSuccess }}</p>

          <button class="login-btn" @click="doRegister">注册</button>
          <div class="auth-links">
            <a class="link" @click="backToLogin">← 返回登录</a>
          </div>
        </template>

        <!-- ======== 忘记密码 ======== -->
        <template v-else>
          <h2>重置密码</h2>
          <p class="desc">通过「账号 + 姓名 + 手机号」验证身份后设置新密码。</p>

          <label class="field">
            <span>账号 <em class="req">*</em></span>
            <input v-model="forgotForm.account" type="text" placeholder="请输入注册账号" />
          </label>
          <label class="field">
            <span>姓名 <em class="req">*</em></span>
            <input v-model="forgotForm.name" type="text" placeholder="请输入注册时填写的姓名" />
          </label>
          <label class="field">
            <span>手机号 <em class="req">*</em></span>
            <input
              v-model="forgotForm.phone"
              type="tel"
              maxlength="11"
              placeholder="请输入注册时填写的手机号"
            />
          </label>
          <label class="field">
            <span>新密码 <em class="req">*</em>（至少 6 位）</span>
            <input v-model="forgotForm.newPassword" type="password" placeholder="设置新密码" />
          </label>
          <label class="field">
            <span>确认新密码 <em class="req">*</em></span>
            <input v-model="forgotForm.confirm" type="password" placeholder="再次输入新密码" />
          </label>

          <p v-if="forgotError" class="error">{{ forgotError }}</p>
          <p v-if="forgotSuccess" class="success">{{ forgotSuccess }}</p>

          <button class="login-btn" @click="doResetPassword">重置密码</button>
          <div class="auth-links">
            <a class="link" @click="backToLogin">← 返回登录</a>
          </div>
        </template>
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
  margin: 0 0 8px;
  letter-spacing: 0.02em;
  position: relative;
  z-index: 1;
}
.login-brand .brand-sub {
  margin: 0;
  font-size: 0.86rem;
  opacity: 0.9;
  position: relative;
  z-index: 1;
}

.form-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 36px 40px;
}
.form-box h2 {
  margin: 0 0 16px;
  font-size: 1.3rem;
  color: #2c3e2f;
}
.form-box .desc {
  margin: 0 0 14px;
  font-size: 0.82rem;
  color: #6b7280;
  line-height: 1.6;
}
.role-select {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}
.role-select.small {
  grid-template-columns: repeat(2, 1fr);
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
.row2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 12px;
}
.field span {
  font-size: 0.84rem;
  font-weight: 600;
  color: #3f5242;
}
.req {
  color: #c0392b;
  font-style: normal;
}
.field input,
.field select {
  padding: 10px 12px;
  border: 1px solid #dde7dd;
  border-radius: 8px;
  font-size: 0.88rem;
  outline: none;
  font-family: inherit;
  background: #fbfdfb;
  transition:
    border-color 0.15s,
    background 0.15s;
}
.field input:focus,
.field select:focus {
  border-color: #4a9d50;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(74, 157, 80, 0.12);
}
.error {
  color: #c0392b;
  font-size: 0.82rem;
  margin: 0 0 10px;
}
.success {
  color: #2e8b57;
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
.auth-links {
  display: flex;
  justify-content: space-between;
  margin-top: 14px;
}
.link {
  font-size: 0.84rem;
  color: #3d7d5d;
  cursor: pointer;
  text-decoration: none;
}
.link:hover {
  color: #2c6e33;
  text-decoration: underline;
}
.quick-fill {
  font-size: 0.78rem;
  color: #93a293;
  margin-top: 14px;
}
@media (max-width: 720px) {
  .login-card {
    flex-direction: column;
  }
  .login-brand {
    padding: 28px;
  }
  .row2 {
    grid-template-columns: 1fr;
  }
}
</style>
