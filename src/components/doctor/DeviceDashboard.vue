<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDevices } from '../../services/api.js'

const devices = ref([])
const loading = ref(true)
const errorMsg = ref('')
const statusFilter = ref('')
const runFilter = ref('')

onMounted(() => {
  try {
    devices.value = getDevices()
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
})

const runCount = computed(() => {
  const c = { '在线': 0, '运行中': 0, '故障': 0, '校准中': 0, '离线': 0 }
  devices.value.forEach((d) => { if (c[d.runStatus] !== undefined) c[d.runStatus]++ })
  return c
})

const filtered = computed(() => {
  return devices.value.filter((d) => {
    const okStatus = !statusFilter.value || d.status === statusFilter.value
    const okRun = !runFilter.value || d.runStatus === runFilter.value
    return okStatus && okRun
  })
})

const runClass = (rs) => {
  const map = { '在线': 'run-online', '运行中': 'run-running', '故障': 'run-fail', '校准中': 'run-calib', '离线': 'run-offline' }
  return map[rs] || 'run-offline'
}

const fmtPrice = (p) => Number(p || 0).toLocaleString('zh-CN')
</script>

<template>
  <div class="dashboard-page">
    <div class="head-desc">设备台账：查看实验室内所有医疗设备的运行状态。</div>

    <!-- 运行状态汇总 -->
    <section class="run-summary">
      <div class="run-item" :class="{ sum_active: runFilter === '在线' }" @click="runFilter = runFilter === '在线' ? '' : '在线'">
        在线 <b>{{ runCount['在线'] }}</b>
      </div>
      <div class="run-item" :class="{ sum_active: runFilter === '运行中' }" @click="runFilter = runFilter === '运行中' ? '' : '运行中'">
        运行中 <b>{{ runCount['运行中'] }}</b>
      </div>
      <div class="run-item" :class="{ sum_active: runFilter === '故障' }" @click="runFilter = runFilter === '故障' ? '' : '故障'">
        故障 <b>{{ runCount['故障'] }}</b>
      </div>
      <div class="run-item" :class="{ sum_active: runFilter === '校准中' }" @click="runFilter = runFilter === '校准中' ? '' : '校准中'">
        校准中 <b>{{ runCount['校准中'] }}</b>
      </div>
      <div class="run-item" :class="{ sum_active: runFilter === '离线' }" @click="runFilter = runFilter === '离线' ? '' : '离线'">
        离线 <b>{{ runCount['离线'] }}</b>
      </div>
    </section>

    <!-- 表格 -->
    <section class="table-card">
      <div class="toolbar">
        <label>使用状态：
          <select v-model="statusFilter">
            <option value="">全部</option>
            <option value="正常使用">正常使用</option>
            <option value="维修中">维修中</option>
            <option value="闲置">闲置</option>
            <option value="已报废">已报废</option>
          </select>
        </label>
        <span class="count">共 <b>{{ filtered.length }}</b> 台</span>
      </div>
      <div v-if="loading" class="empty">加载中...</div>
      <div v-else-if="errorMsg" class="empty error">{{ errorMsg }}</div>
      <div v-else-if="filtered.length" class="table-wrap">
        <table class="dev-table">
          <thead>
            <tr><th>编号</th><th>设备名称</th><th>型号</th><th>所属科室</th><th>价格(元)</th><th>使用状态</th><th>运行状态</th><th>备注</th></tr>
          </thead>
          <tbody>
            <tr v-for="d in filtered" :key="d.id">
              <td class="code">{{ d.code }}</td>
              <td class="name">{{ d.name }}</td>
              <td>{{ d.model || '-' }}</td>
              <td>{{ d.department }}</td>
              <td>{{ fmtPrice(d.price) }}</td>
              <td><span class="use-badge">{{ d.status }}</span></td>
              <td><span class="run-badge" :class="runClass(d.runStatus)">{{ d.runStatus }}</span></td>
              <td class="note">{{ d.note || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="empty">无符合条件的设备</div>
    </section>
  </div>
</template>

<style scoped>
.dashboard-page { display: flex; flex-direction: column; gap: 16px; }
.head-desc { padding: 10px 14px; background: #eef6ee; color: #3d6b40; border: 1px solid #d0e4d0; font-size: 0.85rem; }
.run-summary { display: flex; gap: 8px; flex-wrap: wrap; }
.run-item { padding: 8px 14px; background: #fff; border: 1px solid #eef2ee; cursor: pointer; font-size: 0.85rem; color: #4b5563; }
.run-item b { margin-left: 4px; }
.run-item.sum_active { border-color: #83b785; background: #f0faf0; }
.table-card { background: #fff; border: 1px solid #eef2ee; overflow: hidden; }
.toolbar { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; border-bottom: 1px solid #eef2ee; }
.toolbar label { font-size: 0.85rem; color: #4b5563; }
.toolbar select { padding: 6px 10px; border: 1px solid #e0e7e0; font-family: inherit; }
.count { font-size: 0.85rem; color: #4b5563; }
.count b { color: #4a854d; }
.table-wrap { overflow-x: auto; }
.dev-table { width: 100%; border-collapse: collapse; font-size: 0.84rem; min-width: 900px; }
.dev-table th { padding: 10px 12px; text-align: left; background: #f6faf6; color: #557457; border-bottom: 2px solid #dbe8db; }
.dev-table td { padding: 10px 12px; border-bottom: 1px solid #f3f4f6; color: #4b5563; }
.code { font-family: monospace; font-size: 0.78rem; color: #6b7280; }
.name { font-weight: 600; color: #1f2937; }
.use-badge { padding: 2px 10px; font-size: 0.76rem; font-weight: 600; }
.run-badge { padding: 2px 10px; font-size: 0.76rem; font-weight: 600; }
.run-badge.run-online { background: #e7faf1; color: #0b7d4f; }
.run-badge.run-running { background: #e7f1ff; color: #2563eb; }
.run-badge.run-fail { background: #fdecec; color: #dc2626; }
.run-badge.run-calib { background: #fdf5e0; color: #b45309; }
.run-badge.run-offline { background: #eef0f2; color: #6b7280; }
.note { max-width: 160px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #9ca3af; }
.empty { text-align: center; padding: 40px; color: #b0b0b0; }
.empty.error { color: #c0392b; }
</style>
