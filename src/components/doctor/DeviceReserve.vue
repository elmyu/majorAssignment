<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDevices, createReservation, getReservations } from '../../services/api.js'

const devices = ref([])
const reservations = ref([])
const loading = ref(true)
const errorMsg = ref('')
const toast = ref('')

const reserveDeviceId = ref('')
const timeRange = ref('')
const purpose = ref('')

const toastTimer = ref(null)
function showToast(msg, type = 'success') {
  toast.value = { msg, type }
  clearTimeout(toastTimer.value)
  toastTimer.value = setTimeout(() => (toast.value = null), 2600)
}

onMounted(loadAll)
function loadAll() {
  try {
    devices.value = getDevices()
    reservations.value = getReservations()
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
}

const bookable = computed(() => devices.value.filter((d) => d.status !== '已报废' && d.runStatus !== '故障'))

function doReserve() {
  if (!reserveDeviceId.value) { showToast('请选择要预约的设备', 'warning'); return }
  if (!timeRange.value.trim()) { showToast('请填写预约使用时间', 'warning'); return }
  try {
    createReservation({ deviceId: reserveDeviceId.value, timeRange: timeRange.value.trim(), purpose: purpose.value.trim() })
    showToast('预约成功')
    timeRange.value = ''
    purpose.value = ''
    reserveDeviceId.value = ''
    loadAll()
  } catch (e) {
    showToast(e.message, 'warning')
  }
}

const fmtTime = (iso) => new Date(iso).toLocaleString('zh-CN')
</script>

<template>
  <div class="reserve-page">
    <div class="head-desc">设备预约：选择可用设备，填写预约使用时间并提交。</div>

    <!-- 预约表单 -->
    <section class="form-card">
      <h3>新建设备预约</h3>
      <form @submit.prevent="doReserve" class="reserve-form">
        <div class="field">
          <label>选择设备 <span class="req">*</span></label>
          <select v-model="reserveDeviceId" required>
            <option value="">-- 请选择设备（共 {{ bookable.length }} 台可用）--</option>
            <option v-for="d in bookable" :key="d.id" :value="d.id">
              {{ d.name }}（{{ d.code }} · {{ d.runStatus }}）
            </option>
          </select>
        </div>
        <div class="field">
          <label>预约使用时间 <span class="req">*</span></label>
          <input v-model="timeRange" type="text" placeholder="例如：2026-08-20 09:00 - 12:00" />
        </div>
        <div class="field">
          <label>用途说明</label>
          <input v-model="purpose" type="text" placeholder="选填" />
        </div>
        <button type="submit" class="submit-btn">提交预约</button>
      </form>
    </section>

    <!-- 可用设备清单 -->
    <section class="avail-card">
      <h3>当前可用设备</h3>
      <div class="avail-grid">
        <div v-for="d in bookable" :key="d.id" class="avail-item">
          <div class="avail-name">{{ d.name }}</div>
          <div class="avail-meta">{{ d.department }} · {{ d.runStatus }}</div>
        </div>
      </div>
    </section>

    <!-- 预约日志 -->
    <section class="log-card">
      <h3>预约日志</h3>
      <div v-if="reservations.length" class="table-wrap">
        <table class="log-table">
          <thead>
            <tr><th>#</th><th>设备</th><th>预约医生</th><th>预约时间</th><th>用途</th><th>提交时间</th></tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in reservations" :key="r.id">
              <td>{{ i + 1 }}</td>
              <td>{{ r.deviceName }} <span class="code">{{ r.deviceCode }}</span></td>
              <td>{{ r.doctorName }}</td>
              <td>{{ r.timeRange }}</td>
              <td>{{ r.purpose || '-' }}</td>
              <td>{{ fmtTime(r.createdAt) }}</td>
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
.reserve-page { display: flex; flex-direction: column; gap: 16px; position: relative; }
.head-desc { padding: 10px 14px; background: #eef6ee; color: #3d6b40; border: 1px solid #d0e4d0; font-size: 0.85rem; }
.form-card, .avail-card, .log-card { background: #fff; border: 1px solid #eef2ee; padding: 16px 18px; }
.form-card h3, .avail-card h3, .log-card h3 { margin: 0 0 12px; font-size: 1rem; color: #1f2937; }
.reserve-form { display: flex; flex-wrap: wrap; gap: 14px; align-items: flex-end; }
.field { display: flex; flex-direction: column; gap: 5px; flex: 1; min-width: 200px; }
.field label { font-size: 0.82rem; font-weight: 600; color: #4b5563; }
.req { color: #c0392b; }
.field input, .field select { padding: 9px 10px; border: 1px solid #e0e7e0; font-size: 0.85rem; font-family: inherit; }
.submit-btn { padding: 9px 20px; border: none; color: #fff; font-weight: 700; font-size: 0.88rem; cursor: pointer; background: #4a854d; font-family: inherit; }
.submit-btn:hover { background: #3d6b40; }
.avail-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; }
.avail-item { display: flex; flex-direction: column; gap: 2px; padding: 10px 12px; border: 1px solid #eef2ee; }
.avail-name { font-weight: 600; color: #1f2937; }
.avail-meta { font-size: 0.76rem; color: #9ca3af; }
.log-table { width: 100%; border-collapse: collapse; font-size: 0.84rem; }
.log-table th { padding: 9px 10px; text-align: left; background: #f6faf6; color: #557457; border-bottom: 2px solid #dbe8db; }
.log-table td { padding: 9px 10px; border-bottom: 1px solid #f3f4f6; color: #4b5563; }
.code { font-family: monospace; font-size: 0.76rem; color: #9ca3af; }
.empty { text-align: center; padding: 20px; color: #b0b0b0; }
.toast { position: fixed; top: 84px; right: 24px; padding: 10px 16px; color: #fff; font-size: 0.85rem; font-weight: 600; }
.toast-success { background: #2f9e5f; }
.toast-warning { background: #df8c1a; }
</style>
