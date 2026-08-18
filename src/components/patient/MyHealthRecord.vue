<script setup>
import { ref, computed, onMounted } from 'vue';
import { getMySignals } from '../../services/api.js';

const patient = ref(null);
const records = ref([]);
const loading = ref(true);
const errorMsg = ref('');
const timeRange = ref('all');

onMounted(() => {
  try {
    const res = getMySignals();
    patient.value = res.patient;
    records.value = res.records;
  } catch (e) {
    errorMsg.value = e.message;
  } finally {
    loading.value = false;
  }
});

const filtered = computed(() => {
  const now = Date.now();
  let days = 99999;
  if (timeRange.value === '7') days = 7;
  else if (timeRange.value === '30') days = 30;
  else if (timeRange.value === '90') days = 90;
  return records.value.filter((r) => now - new Date(r.recordTime).getTime() <= days * 86400000);
});

// 正常参考范围
const refRange = {
  heartRate: [60, 100],
  sbp: [90, 140],
  dbp: [60, 90],
  spo2: [95, 100],
  temp: [36.0, 37.4],
};
const isNormal = (key, v) => {
  const [lo, hi] = refRange[key];
  return v >= lo && v <= hi;
};
const rowAbnormal = (r) =>
  !isNormal('heartRate', r.heartRate) ||
  !isNormal('sbp', r.sbp) ||
  !isNormal('dbp', r.dbp) ||
  !isNormal('spo2', r.spo2) ||
  !isNormal('temp', r.temp);

const fmtDate = (iso) => {
  const d = new Date(iso);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
};
</script>

<template>
  <div class="health-page">
    <section class="patient-card" v-if="patient">
      <div class="base">
        <h3>{{ patient.name }}</h3>
        <p>
          门诊号：{{ patient.medicalNo }} &nbsp; 性别：{{ patient.gender }} &nbsp; 年龄：{{
            patient.age
          }}岁 &nbsp; 血型：{{ patient.bloodType }}
        </p>
      </div>
      <div class="record-count">
        记录 <b>{{ records.length }}</b> 条
      </div>
    </section>

    <div class="privacy-banner">隐私提示：您仅可查看本人的生理信号历史记录。</div>

    <section class="table-card">
      <div class="toolbar">
        <h3>生理信号历史记录</h3>
        <select v-model="timeRange" class="range-select">
          <option value="all">全部</option>
          <option value="90">近 90 天</option>
          <option value="30">近 30 天</option>
          <option value="7">近 7 天</option>
        </select>
      </div>
      <div v-if="loading" class="empty">加载中...</div>
      <div v-else-if="errorMsg" class="empty error">{{ errorMsg }}</div>
      <table v-else-if="filtered.length" class="sig-table">
        <thead>
          <tr>
            <th>#</th>
            <th>采集时间</th>
            <th>心率</th>
            <th>收缩压</th>
            <th>舒张压</th>
            <th>血氧</th>
            <th>体温</th>
            <th>备注</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(r, i) in filtered" :key="r.id" :class="{ abn: rowAbnormal(r) }">
            <td>{{ i + 1 }}</td>
            <td>{{ fmtDate(r.recordTime) }}</td>
            <td>{{ r.heartRate }} bpm</td>
            <td>{{ r.sbp }} mmHg</td>
            <td>{{ r.dbp }} mmHg</td>
            <td>{{ r.spo2 }}%</td>
            <td>{{ r.temp }}℃</td>
            <td>{{ r.note || '-' }}</td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty">当前筛选范围内暂无记录</div>
    </section>
  </div>
</template>

<style scoped>
.health-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.patient-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #fff;
  border: 1px solid #eef2ee;
}
.base h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #1f2937;
}
.base p {
  margin: 6px 0 0;
  color: #6b7280;
  font-size: 0.85rem;
}
.record-count {
  font-size: 0.85rem;
  color: #4b5563;
}
.record-count b {
  color: #4a854d;
}
.privacy-banner {
  padding: 10px 14px;
  background: #eef6ee;
  color: #3d6b40;
  border: 1px solid #d0e4d0;
  font-size: 0.85rem;
}
.table-card {
  background: #fff;
  border: 1px solid #eef2ee;
  overflow: hidden;
}
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid #eef2ee;
}
.toolbar h3 {
  margin: 0;
  font-size: 1rem;
  color: #1f2937;
}
.range-select {
  padding: 6px 10px;
  border: 1px solid #e0e7e0;
  font-size: 0.84rem;
  font-family: inherit;
}
.sig-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}
.sig-table th {
  padding: 10px 12px;
  text-align: left;
  background: #f6faf6;
  color: #557457;
  border-bottom: 2px solid #dbe8db;
}
.sig-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #f3f4f6;
  color: #4b5563;
}
.sig-table tbody tr.abn td {
  background: #fdf6f1;
}
.empty {
  text-align: center;
  padding: 40px;
  color: #b0b0b0;
}
.empty.error {
  color: #c0392b;
}
</style>
