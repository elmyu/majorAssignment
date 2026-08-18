<script setup>
import { ref, computed, onMounted } from 'vue';
import {
  getCurrentUser,
  getDevices,
  createReservation,
  getReservations,
  cancelReservation,
} from '@/services/api.js';

const devices = ref([]);
const reservations = ref([]);
const loading = ref(true);
const errorMsg = ref('');

const toast = ref('');
const toastTimer = ref(null);
function showToast(msg, type = 'success') {
  toast.value = { msg, type };
  clearTimeout(toastTimer.value);
  toastTimer.value = setTimeout(() => (toast.value = null), 2600);
}

// 预约表单
const reserveDeviceId = ref('');
const reserveDate = ref('');
const reserveSlot = ref('上午');
const reserveTimeRange = ref('');
const purpose = ref('');

// 设备搜索
const deviceKeyword = ref('');
const deviceDept = ref('all');

const slotOptions = [
  { value: '上午', range: '08:00-11:30' },
  { value: '下午', range: '14:00-17:00' },
  { value: '晚上', range: '19:00-21:00' },
  { value: '全天', range: '08:00-17:00' },
  { value: '自定义', range: '' },
];

// 预约部门列表（从设备数据动态生成）
const deptList = computed(() => {
  const s = new Set(devices.value.map((d) => d.department).filter(Boolean));
  return [...s];
});

onMounted(loadAll);
function loadAll() {
  try {
    devices.value = getDevices();
    reservations.value = getReservations();
  } catch (e) {
    errorMsg.value = e.message;
  } finally {
    loading.value = false;
  }
}

const bookable = computed(() =>
  devices.value.filter((d) => d.status !== '已报废' && d.runStatus !== '故障')
);

const filteredDevices = computed(() => {
  let r = bookable.value;
  if (deviceDept.value !== 'all') r = r.filter((d) => d.department === deviceDept.value);
  const k = deviceKeyword.value.trim().toLowerCase();
  if (k)
    r = r.filter(
      (d) => d.name.toLowerCase().includes(k) || (d.code || '').toLowerCase().includes(k)
    );
  return r;
});

const selectedDevice = computed(() => bookable.value.find((d) => d.id === reserveDeviceId.value));

// 计算时间段字符串
const computedTimeRange = computed(() => {
  if (reserveSlot.value === '自定义') return reserveTimeRange.value.trim();
  if (!reserveDate.value) return '';
  const slot = slotOptions.find((s) => s.value === reserveSlot.value);
  return `${reserveDate.value} ${reserveSlot.value} ${slot ? slot.range : ''}`.trim();
});

// 冲突校验：同一设备同一天同一时段
const isConflict = computed(() => {
  if (!reserveDeviceId.value || !reserveDate.value) return false;
  const target = computedTimeRange.value;
  if (!target) return false;
  return reservations.value.some((r) => {
    if (r.deviceId !== reserveDeviceId.value) return false;
    if (reserveSlot.value === '自定义') {
      return r.timeRange.includes(reserveDate.value) && r.timeRange.split(' ')[1] === '自定义';
    }
    return r.timeRange.includes(reserveDate.value) && r.timeRange.includes(reserveSlot.value);
  });
});

function selectDevice(id) {
  reserveDeviceId.value = id;
  // 选中后给个反馈
  if (selectedDevice.value) showToast(`已选择：${selectedDevice.value.name}`, 'info');
}

function doReserve() {
  if (!reserveDeviceId.value) {
    showToast('请先选择要预约的设备', 'warning');
    return;
  }
  if (!reserveDate.value) {
    showToast('请选择预约日期', 'warning');
    return;
  }
  const timeStr = computedTimeRange.value;
  if (!timeStr) {
    showToast('请设置预约时间段', 'warning');
    return;
  }
  try {
    createReservation({
      deviceId: reserveDeviceId.value,
      timeRange: timeStr,
      purpose: purpose.value.trim(),
    });
    showToast('预约成功');
    // 重置
    reserveDeviceId.value = '';
    reserveDate.value = '';
    reserveSlot.value = '上午';
    reserveTimeRange.value = '';
    purpose.value = '';
    loadAll();
  } catch (e) {
    showToast(e.message, 'warning');
  }
}

const fmtTime = (iso) => new Date(iso).toLocaleString('zh-CN');

// ---- 取消预约 ----
const currentUserName = ref(getCurrentUser()?.name || '');

function doCancel(res) {
  if (!confirm(`确定取消「${res.deviceName}」的预约吗？`)) return;
  try {
    cancelReservation(res.id);
    showToast('预约已取消');
    loadAll();
  } catch (e) {
    showToast(e.message, 'warning');
  }
}

// 医生仅可取消自己的预约（管理员日志中也可由管理员取消）
const canCancel = (r) => r.doctorName === currentUserName.value;
</script>

<template>
  <div class="reserve-page">
    <div class="head-desc">
      设备预约：选择可用设备，设置预约日期与时间段，提交生成预约记录（同一时段不可重复预约）。
    </div>

    <!-- 预约表单 -->
    <section class="card form-card">
      <h3>新建设备预约</h3>
      <div class="reserve-layout">
        <!-- 表单 -->
        <div class="form-left">
          <div class="form-row">
            <label class="field full">
              <span>选择设备 <em class="req">*</em></span>
              <select v-model="reserveDeviceId" @change="selectDevice(reserveDeviceId)">
                <option value="">-- 请选择可用设备 --</option>
                <option v-for="d in bookable" :key="d.id" :value="d.id">
                  {{ d.name }}（{{ d.code }} · {{ d.runStatus }}）
                </option>
              </select>
            </label>
          </div>
          <div class="form-row">
            <label class="field">
              <span>预约日期 <em class="req">*</em></span>
              <input type="date" v-model="reserveDate" />
            </label>
            <label class="field">
              <span>时间段 <em class="req">*</em></span>
              <select v-model="reserveSlot">
                <option v-for="s in slotOptions" :key="s.value" :value="s.value">
                  {{ s.value }}（{{ s.range || '手动填写' }}）
                </option>
              </select>
            </label>
          </div>
          <div v-if="reserveSlot === '自定义'" class="form-row">
            <label class="field full">
              <span>自定义时间</span>
              <input v-model="reserveTimeRange" placeholder="例如 09:00-10:30" />
            </label>
          </div>
          <div class="form-row">
            <label class="field full">
              <span>用途说明</span>
              <input v-model="purpose" placeholder="选填，例如：超声心动检查" />
            </label>
          </div>

          <!-- 提交确认条 -->
          <div class="confirm-bar">
            <div class="confirm-info">
              <template v-if="selectedDevice">
                <b>{{ selectedDevice.name }}</b>
                <span class="sep">|</span>
                <span class="code">{{ selectedDevice.code }}</span>
                <span class="sep">|</span>
                <span>{{ selectedDevice.department }}</span>
                <span class="sep">|</span>
                <span class="run-ok">{{ selectedDevice.runStatus }}</span>
              </template>
              <span v-else class="hint">未选择设备</span>
            </div>
            <div v-if="computedTimeRange" class="confirm-time">{{ computedTimeRange }}</div>
          </div>

          <p v-if="isConflict" class="conflict-msg">
            ⚠ 该设备在所选日期与时间段已有预约，请更换时间。
          </p>

          <button type="button" class="submit-btn" @click="doReserve" :disabled="isConflict">
            提交预约
          </button>
        </div>

        <!-- 设备筛选与清单 -->
        <div class="form-right">
          <h4>设备快速筛选与搜索</h4>
          <div class="filter-row">
            <input v-model="deviceKeyword" placeholder="搜索设备名称 / 编号" class="filter-input" />
            <select v-model="deviceDept" class="filter-select">
              <option value="all">全部科室</option>
              <option v-for="d in deptList" :key="d" :value="d">{{ d }}</option>
            </select>
          </div>
          <div class="avail-grid">
            <div
              v-for="d in filteredDevices"
              :key="d.id"
              class="avail-item"
              :class="{ picked: reserveDeviceId === d.id }"
              @click="selectDevice(d.id)"
            >
              <div class="avail-name">{{ d.name }}</div>
              <div class="avail-meta">
                {{ d.department }} · <span class="run-ok">{{ d.runStatus }}</span>
              </div>
            </div>
            <div v-if="!filteredDevices.length" class="avail-empty">无匹配设备</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 预约日志 -->
    <section class="card log-card">
      <h3>预约日志</h3>
      <div v-if="reservations.length" class="table-wrap">
        <table class="log-table">
          <thead>
            <tr>
              <th>#</th>
              <th>设备</th>
              <th>预约医生</th>
                            <th>预约时间</th>
              <th>用途</th>
              <th>提交时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in reservations" :key="r.id">
              <td>{{ i + 1 }}</td>
              <td>
                {{ r.deviceName }} <span class="code">{{ r.deviceCode }}</span>
              </td>
              <td>{{ r.doctorName }}</td>
              <td>{{ r.timeRange }}</td>
              <td>{{ r.purpose || '-' }}</td>
              <td>{{ fmtTime(r.createdAt) }}</td>
              <td>
                <button
                  v-if="canCancel(r)"
                  class="cancel-btn"
                  @click="doCancel(r)"
                >
                  取消预约
                </button>
                <span v-else class="op-disabled">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="empty">暂无预约记录</div>
    </section>

    <div v-if="toast" class="toast" :class="'toast-' + toast.type">{{ toast.msg }}</div>
  </div>
</template>

<style scoped>
.reserve-page {
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
}
.card h3 {
  margin: 0 0 14px;
  font-size: 1rem;
  color: #1f2937;
}

.reserve-layout {
  display: flex;
  gap: 20px;
}
.form-left {
  flex: 1.3;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.form-right {
  flex: 1;
  border-left: 1px solid #eef2ee;
  padding-left: 18px;
}
.form-right h4 {
  margin: 0 0 10px;
  font-size: 0.92rem;
  color: #1f2937;
}

.form-row {
  display: flex;
  gap: 12px;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
}
.field.full {
  width: 100%;
}
.field span {
  font-size: 0.82rem;
  font-weight: 600;
  color: #4b5563;
}
.req {
  color: #c0392b;
  font-style: normal;
}
.field select,
.field input {
  padding: 9px 10px;
  border: 1px solid #e0e7e0;
  font-size: 0.85rem;
  font-family: inherit;
  background: #fff;
}

.filter-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.filter-input {
  flex: 1;
  min-width: 0;
  padding: 8px 10px;
  border: 1px solid #e0e7e0;
  font-size: 0.85rem;
  font-family: inherit;
}
.filter-select {
  padding: 8px 6px;
  border: 1px solid #e0e7e0;
  font-size: 0.85rem;
  font-family: inherit;
  background: #fff;
}

.avail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}
.avail-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px 10px;
  border: 1px solid #eef2ee;
  cursor: pointer;
  background: #fbfdfb;
}
.avail-item:hover {
  border-color: #9cc39f;
  background: #f0f8f0;
}
.avail-item.picked {
  border-color: #4a854d;
  background: #e7f5e7;
}
.avail-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.85rem;
}
.avail-meta {
  font-size: 0.72rem;
  color: #9ca3af;
}
.avail-empty {
  grid-column: 1 / -1;
  text-align: center;
  padding: 24px;
  color: #b0b0b0;
}
.run-ok {
  color: #2d7d4f;
  font-weight: 600;
}

.confirm-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  background: #f6faf6;
  border: 1px solid #dbe8db;
  padding: 9px 12px;
  font-size: 0.84rem;
}
.confirm-info {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  color: #2c6e33;
}
.confirm-info .sep {
  color: #b9cfba;
}
.confirm-info .code {
  font-family: monospace;
  color: #6b7280;
  font-size: 0.76rem;
}
.confirm-info .hint {
  color: #9ca3af;
}
.confirm-time {
  font-weight: 700;
  color: #2c6e33;
}
.conflict-msg {
  color: #c0392b;
  font-size: 0.85rem;
  margin: 0;
}
.submit-btn {
  padding: 11px 24px;
  border: none;
  color: #fff;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  background: #4a854d;
  font-family: inherit;
  align-self: flex-start;
}
.submit-btn:hover {
  background: #3d6b40;
}
.submit-btn:disabled {
  background: #b7c9b7;
  cursor: not-allowed;
}

.log-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.84rem;
}
.log-table th {
  padding: 9px 10px;
  text-align: left;
  background: #f6faf6;
  color: #557457;
  border-bottom: 2px solid #dbe8db;
}
.log-table td {
  padding: 9px 10px;
  border-bottom: 1px solid #f3f4f6;
  color: #4b5563;
}
.code {
  font-family: monospace;
  font-size: 0.76rem;
  color: #9ca3af;
}
.cancel-btn {
  padding: 4px 12px;
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
  padding: 20px;
  color: #b0b0b0;
}
.toast {
  position: fixed;
  top: 84px;
  right: 24px;
  padding: 10px 16px;
  color: #fff;
  font-size: 0.85rem;
  font-weight: 600;
  z-index: 3000;
}
.toast-success {
  background: #2f9e5f;
}
.toast-warning {
  background: #df8c1a;
}
.toast-info {
  background: #3d7fc4;
}
@media (max-width: 900px) {
  .reserve-layout {
    flex-direction: column;
  }
  .form-right {
    border-left: none;
    padding-left: 0;
    border-top: 1px solid #eef2ee;
    padding-top: 14px;
  }
}
</style>
