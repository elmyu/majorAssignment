<script setup>
import { ref, computed, onMounted } from 'vue'
import { getSchedules } from '@/services/api.js'

const schedules = ref([])
const loading = ref(true)
const errorMsg = ref('')
const deptKeyword = ref('')
const doctorKeyword = ref('')
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

// 科室输入联想建议
const deptSuggest = computed(() => {
  const k = deptKeyword.value.trim()
  if (!k) return []
  return deptOptions.value.filter((d) => d.includes(k))
})
// 医生输入联想建议
const doctorSuggest = computed(() => {
  const k = doctorKeyword.value.trim()
  if (!k) return []
  return doctorOptions.value.filter((d) => d.name.includes(k) || d.id.includes(k))
})

const filtered = computed(() => {
  const dk = deptKeyword.value.trim()
  const dok = doctorKeyword.value.trim()
  return schedules.value.filter((s) => {
    const okDept = !dk || s.doctorDept.includes(dk)
    const okDoc = !dok || s.doctorName.includes(dok) || s.doctorId.includes(dok)
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
      <label class="search-field">
        <span>科室（可输入搜索）</span>
        <div class="suggest-wrap">
          <input v-model="deptKeyword" placeholder="输入科室名称..." class="suggest-input" />
          <div v-if="deptSuggest.length" class="suggest-list">
            <div v-for="d in deptSuggest" :key="d" class="suggest-item" @click="deptKeyword = d">{{ d }}</div>
          </div>
        </div>
      </label>
      <label class="search-field">
        <span>医生（可输入搜索）</span>
        <div class="suggest-wrap">
          <input v-model="doctorKeyword" placeholder="输入医生姓名..." class="suggest-input" />
          <div v-if="doctorSuggest.length" class="suggest-list">
            <div v-for="d in doctorSuggest" :key="d.id" class="suggest-item" @click="doctorKeyword = d.name">{{ d.name }}</div>
          </div>
        </div>
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
.toolbar select, .toolbar .date-input, .toolbar .suggest-input { padding: 8px 10px; border: 1px solid #e0e7e0; font-size: 0.85rem; font-family: inherit; background: #fff; }

/* 联想搜索 */
.search-field { position: relative; min-width: 170px; }
.suggest-wrap { position: relative; }
.suggest-input { width: 100%; box-sizing: border-box; }
.suggest-list {
  position: absolute; top: 100%; left: 0; right: 0; z-index: 20; margin-top: 2px;
  background: #fff; border: 1px solid #e0e7e0; max-height: 180px; overflow-y: auto;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}
.suggest-item { padding: 8px 12px; cursor: pointer; font-size: 0.85rem; color: #3f5242; }
.suggest-item:hover { background: #eaf5ea; color: #2c6e33; }
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
