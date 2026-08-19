<script setup>
import { ref, computed, onMounted } from 'vue';
import {
  getSchedules,
  createAppointment,
  getMyAppointments,
  cancelAppointment,
} from '@/services/api.js';

const schedules = ref([]);
const myAppointments = ref([]);
const loading = ref(true);
const errorMsg = ref('');
const toast = ref('');
const toastTimer = ref(null);

// 排班筛选
const deptFilter = ref('all');
const doctorFilter = ref('all');
const dateStart = ref('');
const dateEnd = ref('');

// 预约弹层
const showModal = ref(false);
const selectedSchedule = ref(null);
const reason = ref('');
const submitting = ref(false);

function showToast(msg, type = 'success') {
  toast.value = { msg, type };
  clearTimeout(toastTimer.value);
  toastTimer.value = setTimeout(() => (toast.value = null), 2600);
}

onMounted(loadAll);
function loadAll() {
  try {
    schedules.value = getSchedules();
    myAppointments.value = getMyAppointments();
  } catch (e) {
    errorMsg.value = e.message;
  } finally {
    loading.value = false;
  }
}

// 筛选去重（科室 / 医生选项）
const deptOptions = computed(() => [...new Set(schedules.value.map((s) => s.doctorDept))]);
const doctorOptions = computed(() => {
  const map = {};
  schedules.value.forEach((s) => {
    if (!map[s.doctorId]) map[s.doctorId] = { id: s.doctorId, name: s.doctorName, dept: s.doctorDept };
  });
  return Object.values(map);
});

// 可预约的时段：仅出诊/空闲，且排除已过期日期
const bookableSchedules = computed(() =>
  schedules.value.filter((s) => s.status === '出诊' || s.status === '空闲')
);

// 已预约的「医生+日期+时段」组合，用于标记不可重复预约
const takenKeys = computed(
  () => new Set(myAppointments.value.filter((a) => a.status !== '已取消')
    .map((a) => `${a.doctorId}_${a.appointmentDate}_${a.timeRange}`))
);

const filtered = computed(() => {
  const todayStr = new Date().toISOString().slice(0, 10);
  return bookableSchedules.value.filter((s) => {
    if (deptFilter.value !== 'all' && s.doctorDept !== deptFilter.value) return false;
    if (doctorFilter.value !== 'all' && s.doctorId !== doctorFilter.value) return false;
    if (dateStart.value && s.date < dateStart.value) return false;
    if (dateEnd.value && s.date > dateEnd.value) return false;
    if (s.date < todayStr) return false; // 过期时段不展示
    return true;
  });
});

// 判断某个时段是否已被当前患者预约
const isTaken = (s) =>
  takenKeys.value.has(`${s.doctorId}_${s.date}_${s.timeRange}`);

const clearDate = () => {
  dateStart.value = '';
  dateEnd.value = '';
};

function openAppoint(s) {
  if (isTaken(s)) {
    showToast('您已预约该时段的号，请勿重复预约', 'warning');
    return;
  }
  selectedSchedule.value = s;
  reason.value = '';
  showModal.value = true;
}

function doCreate() {
  if (!selectedSchedule.value) return;
  submitting.value = true;
  try {
    createAppointment({ scheduleId: selectedSchedule.value.id, reason: reason.value.trim() });
    showToast('预约挂号成功');
    showModal.value = false;
    loadAll();
  } catch (e) {
    showToast(e.message, 'warning');
  } finally {
    submitting.value = false;
  }
}

const fmtDate = (d) => {
  const [y, m, day] = d.split('-');
  return `${y}年${Number(m)}月${Number(day)}日`;
};

function doCancel(a) {
  if (!confirm(`确定取消「${fmtDate(a.appointmentDate)} ${a.timeRange}」的${a.doctorName}挂号吗？`)) {
    return;
  }
  try {
    cancelAppointment(a.id);
    showToast('已取消挂号');
    loadAll();
  } catch (e) {
    showToast(e.message, 'warning');
  }
}

const statusClass = (s) =>
  ({ 待就诊: 'waiting', 已完成: 'done', 已取消: 'cancelled' })[s] || '';
</script>

<template>
  <div class="appt-page">
    <div class="head-desc">
      预约挂号：选择医生出诊时段在线挂号，同一时段不可重复预约；预约后可在下方「我的挂号」中查看或取消。
    </div>

    <!-- 排班筛选 + 预约列表 -->
    <section class="card book-card">
      <div class="toolbar">
        <h3>可预约时段</h3>
        <div class="toolbar-right">
          <select v-model="deptFilter">
            <option value="all">全部科室</option>
            <option v-for="d in deptOptions" :key="d" :value="d">{{ d }}</option>
          </select>
          <select v-model="doctorFilter">
            <option value="all">全部医生</option>
            <option v-for="doc in doctorOptions" :key="doc.id" :value="doc.id">
              {{ doc.name }}
            </option>
          </select>
          <label class="date-label"
            >起<input type="date" v-model="dateStart" class="date-input"
          /></label>
          <label class="date-label"
            >止<input type="date" v-model="dateEnd" class="date-input"
          /></label>
          <button class="clear-btn" @click="clearDate">清除日期</button>
        </div>
      </div>

      <div v-if="loading" class="empty">加载中...</div>
      <div v-else-if="errorMsg" class="empty error">{{ errorMsg }}</div>
      <div v-else-if="filtered.length" class="table-wrap">
        <table class="appt-table">
          <thead>
            <tr>
              <th>医生</th>
              <th>职称 / 科室</th>
              <th>出诊日期</th>
              <th>时间段</th>
              <th>诊室位置</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in filtered" :key="s.id">
              <td class="doc-name">{{ s.doctorName }}</td>
              <td>{{ s.doctorTitle }} · {{ s.doctorDept }}</td>
              <td>
                {{ fmtDate(s.date) }} <span class="week">{{ s.weekday }}</span>
              </td>
              <td>{{ s.timeRange }}</td>
              <td>{{ s.location }}</td>
              <td>
                <button
                  class="appoint-btn"
                  :class="{ taken: isTaken(s) }"
                  :disabled="isTaken(s)"
                  @click="openAppoint(s)"
                >
                  {{ isTaken(s) ? '已预约' : '预约' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="empty">当前筛选下无可用预约时段</div>
    </section>

    <!-- 我的挂号 -->
    <section class="card my-card">
      <h3>我的挂号（{{ myAppointments.length }}）</h3>
      <div v-if="myAppointments.length" class="table-wrap">
        <table class="appt-table">
          <thead>
            <tr>
              <th>#</th>
              <th>医生</th>
              <th>科室</th>
              <th>预约时段</th>
              <th>就诊备注</th>
              <th>状态</th>
              <th>提交时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(a, i) in myAppointments" :key="a.id">
              <td>{{ i + 1 }}</td>
              <td class="doc-name">{{ a.doctorName }}</td>
              <td>{{ a.doctorDept }}</td>
              <td>
                {{ fmtDate(a.appointmentDate) }} {{ a.weekday }}<br />
                <span class="time">{{ a.timeRange }}</span>
              </td>
              <td>{{ a.reason || '-' }}</td>
              <td><span class="status" :class="statusClass(a.status)">{{ a.status }}</span></td>
              <td>{{ new Date(a.createdAt).toLocaleString('zh-CN') }}</td>
              <td>
                <button
                  v-if="a.status === '待就诊'"
                  class="cancel-btn"
                  @click="doCancel(a)"
                >
                  取消
                </button>
                <span v-else class="op-disabled">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="empty">暂无挂号记录</div>
    </section>

    <!-- 预约确认弹层 -->
    <div v-if="showModal && selectedSchedule" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-head">
          <h3>确认预约挂号</h3>
          <button class="modal-x" @click="showModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="infos">
            <div class="info-row">
              <span>医生</span><b>{{ selectedSchedule.doctorName }}</b>
            </div>
            <div class="info-row">
              <span>科室 / 职称</span
              ><b>{{ selectedSchedule.doctorDept }} · {{ selectedSchedule.doctorTitle }}</b>
            </div>
            <div class="info-row">
              <span>预约时段</span
              ><b>{{ fmtDate(selectedSchedule.date) }}（{{ selectedSchedule.weekday }}）{{
                selectedSchedule.timeRange
              }}</b>
            </div>
            <div class="info-row">
              <span>诊室位置</span><b>{{ selectedSchedule.location }}</b>
            </div>
          </div>
          <label class="reason-field">
            <span>就诊备注（选填）</span>
            <textarea v-model="reason" rows="3" maxlength="100" placeholder="例如：近期胸闷，复查血压"></textarea>
          </label>
        </div>
        <div class="modal-foot">
          <button class="btn cancel" @click="showModal = false">取消</button>
          <button class="btn save" :disabled="submitting" @click="doCreate">
            {{ submitting ? '提交中...' : '确认挂号' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="toast" class="toast" :class="'toast-' + toast.type">{{ toast.msg }}</div>
  </div>
</template>

<style scoped>
.appt-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
}
.head-desc {
  padding: 10px 14px;
  background: #eef6ee;
  color: #3d6b40;
  border: 1px solid #d0e4d0;
  font-size: 0.85rem;
}
.card {
  background: #fff;
  border: 1px solid #eef2ee;
  padding: 16px 18px;
  min-width: 0;
}
.card h3 {
  margin: 0 0 14px;
  font-size: 1rem;
  color: #1f2937;
}
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px 16px;
  margin-bottom: 14px;
}
.toolbar h3 {
  margin: 0;
}
.toolbar-right {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}
.toolbar select {
  padding: 7px 10px;
  border: 1px solid #e0e7e0;
  font-size: 0.85rem;
  font-family: inherit;
  background: #fff;
}
.date-label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.72rem;
  color: #6b7280;
  font-weight: 600;
}
.date-input {
  padding: 5px 8px;
  border: 1px solid #e0e7e0;
  font-size: 0.82rem;
  font-family: inherit;
  background: #fff;
  width: 140px;
  max-width: 140px;
  box-sizing: border-box;
}
.clear-btn {
  padding: 6px 12px;
  border: 1px solid #f0c8c8;
  background: #fff;
  color: #b05656;
  font-size: 0.78rem;
  cursor: pointer;
  font-family: inherit;
}
.clear-btn:hover {
  background: #fdeeee;
}
.table-wrap {
  overflow-x: auto;
}
.appt-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  min-width: 720px;
  white-space: nowrap;
}
.appt-table th {
  padding: 10px 12px;
  text-align: left;
  background: #f6faf6;
  color: #557457;
  border-bottom: 2px solid #dbe8db;
}
.appt-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #f3f4f6;
  color: #4b5563;
}
.doc-name {
  font-weight: 600;
  color: #1f2937;
}
.week {
  color: #9ca3af;
  font-size: 0.78rem;
}
.time {
  color: #6b7280;
  font-size: 0.8rem;
}
.appoint-btn {
  padding: 5px 16px;
  border: none;
  background: #4a854d;
  color: #fff;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
}
.appoint-btn:hover {
  background: #3d6b40;
}
.appoint-btn.taken,
.appoint-btn:disabled {
  background: #c6d2c6;
  cursor: not-allowed;
}
.status {
  padding: 2px 10px;
  font-size: 0.76rem;
  font-weight: 600;
}
.status.waiting {
  background: #e7f1ff;
  color: #2563eb;
}
.status.done {
  background: #e6f7ef;
  color: #2d7d4f;
}
.status.cancelled {
  background: #eef0f2;
  color: #6b7280;
}
.cancel-btn {
  padding: 4px 14px;
  border: 1px solid #f0c8c8;
  background: #fff;
  color: #c0392b;
  font-size: 0.76rem;
  cursor: pointer;
  font-family: inherit;
}
.cancel-btn:hover {
  background: #fdeeee;
}
.op-disabled {
  color: #c6cdc6;
  font-size: 0.78rem;
}
.empty {
  text-align: center;
  padding: 30px;
  color: #b0b0b0;
}
.empty.error {
  color: #c0392b;
}
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}
.modal {
  background: #fff;
  width: 100%;
  max-width: 460px;
  max-height: 85vh;
  overflow-y: auto;
}
.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  border-bottom: 1px solid #eef2ee;
}
.modal-head h3 {
  margin: 0;
  font-size: 1.05rem;
}
.modal-x {
  border: none;
  background: #f3f4f6;
  width: 28px;
  height: 28px;
  cursor: pointer;
}
.modal-body {
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.infos {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.info-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 0.85rem;
}
.info-row span {
  color: #6b7280;
}
.info-row b {
  color: #1f2937;
  text-align: right;
}
.reason-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #4b5563;
}
.reason-field textarea {
  padding: 8px 10px;
  border: 1px solid #e0e7e0;
  font-family: inherit;
  font-size: 0.85rem;
  resize: vertical;
}
.modal-foot {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 12px 18px;
  border-top: 1px solid #eef2ee;
}
.btn {
  padding: 9px 20px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
}
.btn.cancel {
  background: #f3f4f6;
  color: #6b7280;
}
.btn.save {
  background: #4a854d;
  color: #fff;
}
.btn.save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.toast {
  position: fixed;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  padding: 12px 24px;
  color: #fff;
  font-size: 0.9rem;
  font-weight: 600;
  z-index: 3000;
  border-radius: 6px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  white-space: nowrap;
}
.toast-success {
  background: #2f9e5f;
}
.toast-warning {
  background: #df8c1a;
}
</style>
