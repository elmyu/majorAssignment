<script setup>
import { ref, computed, onMounted } from 'vue';
import { getMySignals } from '@/services/api.js';
import { fmtDate } from '@/utils/format.js';
import { isNormal, rowAbnormal } from '@/utils/signals.js';

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

// ---- 最近一次测量概览 ----
const latest = computed(() => (records.value.length ? records.value[0] : null));
const abnormalCount = computed(() => records.value.filter(rowAbnormal).length);
const totalCount = computed(() => records.value.length);
const latestSummary = computed(() => {
  const r = latest.value;
  if (!r) return [];
  return [
    { key: '心率', val: `${r.heartRate} bpm`, ok: isNormal('heartRate', r.heartRate) },
    { key: '收缩压', val: `${r.sbp} mmHg`, ok: isNormal('sbp', r.sbp) },
    { key: '舒张压', val: `${r.dbp} mmHg`, ok: isNormal('dbp', r.dbp) },
    { key: '血氧', val: `${r.spo2}%`, ok: isNormal('spo2', r.spo2) },
    { key: '体温', val: `${r.temp}℃`, ok: isNormal('temp', r.temp) },
  ];
});
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

    <!-- 最近一次测量概览 -->
    <section v-if="latest" class="overview">
      <div class="ov-head">
        <h3>最近一次测量概览</h3>
        <span class="ov-time">{{ fmtDate(latest.recordTime) }}</span>
      </div>
      <div class="ov-grid">
        <div v-for="item in latestSummary" :key="item.key" class="ov-item">
          <span class="ov-label">{{ item.key }}</span>
          <b class="ov-val" :class="{ abn: !item.ok }">{{ item.val }}</b>
        </div>
      </div>
      <div class="ov-footer">
        <span
          >历史记录 <b>{{ totalCount }}</b> 条，其中异常记录
          <b :class="{ abn: abnormalCount > 0 }">{{ abnormalCount }}</b> 条</span
        >
      </div>
    </section>

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
.overview {
  background: #fff;
  border: 1px solid #eef2ee;
  padding: 14px 18px;
}
.ov-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.ov-head h3 {
  margin: 0;
  font-size: 0.95rem;
  color: #1f2937;
}
.ov-time {
  font-size: 0.8rem;
  color: #9ca3af;
}
.ov-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}
.ov-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px;
  background: #f8fbf8;
  border: 1px solid #e8f0e8;
  border-radius: 6px;
}
.ov-label {
  font-size: 0.76rem;
  color: #8aa08c;
}
.ov-val {
  font-size: 1rem;
  color: #1f2937;
}
.ov-val.abn {
  color: #c0392b;
}
.ov-footer {
  margin-top: 12px;
  font-size: 0.82rem;
  color: #6b7280;
}
.ov-footer b {
  color: #4a854d;
}
.ov-footer b.abn {
  color: #c0392b;
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
