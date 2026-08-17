<script setup>
import { ref, computed, onMounted } from 'vue'
import { getSchedules } from '../../services/api.js'

const schedules = ref([])
const loading = ref(true)
const errorMsg = ref('')
const deptFilter = ref('all')
const doctorFilter = ref('all')
const dateStart = ref('')
const dateEnd = ref('')

onMounted(() => {
  try {
    schedules.value = getSchedules()
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
})

const deptOptions = computed(() => [...new Set(schedules.value.map((s) => s.doctorDept))])
const doctorOptions = computed(() => {
  const map = {}
  schedules.value.forEach((s) => { map[s.doctorId] = s.doctorName })
  return Object.entries(map).map(([id, name]) => ({ id, name }))
})

const filtered = computed(() => {
  return schedules.value.filter((s) => {
    const okDept = deptFilter.value === 'all' || s.doctorDept === deptFilter.value
    const okDoc = doctorFilter.value === 'all' || s.doctorId === doctorFilter.value
    const okDate =
      (!dateStart.value || s.date >= dateStart.value) &&
      (!dateEnd.value || s.date <= dateEnd.value)
    return okDept && okDoc && okDate
  })
})

const clearDate = () => { dateStart.value = ''; dateEnd.value = '' }

const fmtDate = (d) => {
  const [y, m, day] = d.split('-')
  return `${y}年${Number(m)}月${Number(day)}日`
}
</script>

<template>
  <div class="schedule-page">
    <div class="head-desc">您可在此查询各科室医生的出诊 / 空闲时间安排。</div>

    <section class="toolbar">
      <label>
        <span>科室</span>
        <select v-model="deptFilter">
          <option value="all">全部科室</option>
          <option v-for="d in deptOptions" :key="d" :value="d">{{ d }}</option>
        </select>
      </label>
      <label>
        <span>医生</span>
        <select v-model="doctorFilter">
          <option value="all">全部医生</option>
          <option v-for="d in doctorOptions" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
      </label>
      <label>
        <span>开始日期</span>
        <input type="date" v-model="dateStart" class="date-input" />
      </label>
      <label>
        <span>结束日期</span>
        <input type="date" v-model="dateEnd" class="date-input" />
      </label>
      <button class="clear-btn" @click="clearDate">清除日期</button>
      <span class="count">共 <b>{{ filtered.length }}</b> 条安排</span>
    </section>

    <div v-if="loading" class="empty">加载中...</div>
    <div v-else-if="errorMsg" class="empty error">{{ errorMsg }}</div>
    <section v-else class="table-card">
      <table class="schedule-table">
        <thead>
          <tr>
            <th>医生</th><th>职称</th><th>所属科室</th><th>出诊日期</th><th>时间段</th><th>状态</th><th>诊室位置</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in filtered" :key="s.id">
            <td class="doc-name">{{ s.doctorName }}</td>
            <td>{{ s.doctorTitle }}</td>
            <td>{{ s.doctorDept }}</td>
            <td>{{ fmtDate(s.date) }} <span class="week">{{ s.weekday }}</span></td>
            <td>{{ s.timeRange }}</td>
            <td><span class="status" :class="s.status === '出诊' ? 'out' : 'sched'">{{ s.status }}</span></td>
            <td>{{ s.location }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<style scoped>
.schedule-page { display: flex; flex-direction: column; gap: 16px; }
.head-desc { padding: 10px 14px; background: #eef6ee; color: #3d6b40; border: 1px solid #d0e4d0; font-size: 0.85rem; }
.toolbar { display: flex; align-items: flex-end; gap: 16px; flex-wrap: wrap; background: #fff; padding: 14px 18px; border: 1px solid #eef2ee; }
.toolbar label { display: flex; flex-direction: column; gap: 5px; }
.toolbar label span { font-size: 0.8rem; color: #4b5563; font-weight: 600; }
.toolbar select, .toolbar .date-input { padding: 8px 10px; border: 1px solid #e0e7e0; font-size: 0.85rem; font-family: inherit; background: #fff; }
.clear-btn {
  padding: 8px 14px; font-size: 0.82rem; background: #fff; color: #b05656;
  border: 1px solid #f0c8c8; cursor: pointer; font-family: inherit; align-self: flex-end;
}
.clear-btn:hover { background: #fdeeee; }
.count { margin-left: auto; font-size: 0.85rem; color: #4b5563; }
.count b { color: #4a854d; }

.table-card { background: #fff; border: 1px solid #eef2ee; overflow-x: auto; }
.schedule-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; min-width: 760px; }
.schedule-table th { padding: 10px 12px; text-align: left; background: #f6faf6; color: #557457; border-bottom: 2px solid #dbe8db; }
.schedule-table td { padding: 10px 12px; border-bottom: 1px solid #f3f4f6; color: #4b5563; }
.doc-name { font-weight: 600; color: #1f2937; }
.week { color: #9ca3af; font-size: 0.78rem; }
.status { padding: 2px 10px; font-size: 0.78rem; font-weight: 600; }
.status.out { background: #e6f7ef; color: #2d7d4f; }
.status.sched { background: #e8f0f8; color: #3d5f80; }
.empty { text-align: center; padding: 40px; color: #b0b0b0; }
.empty.error { color: #c0392b; }
</style>
