<script setup>
import { ref, computed, onMounted } from 'vue';
import { getPatientsForDoctor, getSignalsOfPatient } from '@/services/api.js';
import { fmtDate } from '@/utils/format.js';
import { SIGNAL_KEYS, SIGNAL_LABELS, SIGNAL_UNITS, isNormal } from '@/utils/signals.js';

const patients = ref([]);
const loading = ref(true);
const errorMsg = ref('');
const search = ref('');

const selected = ref(null);
const signalLoading = ref(false);
const signalError = ref('');
const signals = ref([]);

onMounted(async () => {
  try {
    patients.value = await getPatientsForDoctor();
  } catch (e) {
    errorMsg.value = e.message;
  } finally {
    loading.value = false;
  }
});

async function viewSignals(patient) {
  selected.value = patient;
  signalLoading.value = true;
  signalError.value = '';
  signals.value = [];
  try {
    const res = await getSignalsOfPatient(patient.id);
    signals.value = res.records;
  } catch (e) {
    signalError.value = e.message;
  } finally {
    signalLoading.value = false;
  }
}

// ---- 信号统计（平均值 & 异常判断）----
const avg = (key) => {
  if (!signals.value.length) return '-';
  const sum = signals.value.reduce((acc, s) => acc + Number(s[key]), 0);
  return (sum / signals.value.length).toFixed(1);
};
const summaryItems = computed(() => {
  if (!signals.value.length) return [];
  return SIGNAL_KEYS.map((key) => ({
    key,
    label: SIGNAL_LABELS[key],
    avg: signals.value.length ? avg(key) : '-',
    unit: SIGNAL_UNITS[key],
    abnormal: signals.value.filter((s) => !isNormal(key, s[key])).length,
  }));
});
</script>

<template>
  <div class="records-page">
    <div class="head-desc">医生权限：可调阅所有患者的基本信息与生理信号记录。</div>

    <div class="records-layout">
      <!-- 患者列表 -->
      <section class="patient-list-card">
        <div class="search-box">
          <input v-model="search" placeholder="搜索姓名 / 门诊号 / 手机" />
        </div>
        <div v-if="loading" class="empty">加载中...</div>
        <div v-else-if="errorMsg" class="empty error">{{ errorMsg }}</div>
        <ul v-else class="patient-list">
          <li
            v-for="p in patients.filter(
              (p) =>
                !search ||
                p.name.includes(search) ||
                (p.medicalNo || '').includes(search) ||
                (p.phone || '').includes(search)
            )"
            :key="p.id"
            class="patient-item"
            :class="{ on: selected && selected.id === p.id }"
            @click="viewSignals(p)"
          >
            <div class="p-info">
              <span class="p-name">{{ p.name }}</span>
              <span class="p-meta"
                >{{ p.gender }} · {{ p.age }}岁 · {{ p.bloodType }}型 · {{ p.medicalNo }}</span
              >
            </div>
          </li>
        </ul>
      </section>

            <!-- 信号记录 -->
      <section class="detail-card">
        <template v-if="selected">
          <div class="detail-head">
            <h3>{{ selected.name }} 的生理信号记录</h3>
            <span class="badge">{{ signals.length }} 条</span>
          </div>

          <!-- 患者基本信息 -->
          <div class="base-info">
            <span>门诊号：{{ selected.medicalNo }}</span>
            <span>性别：{{ selected.gender }}</span>
            <span>年龄：{{ selected.age }}岁</span>
            <span>血型：{{ selected.bloodType }}</span>
            <span>手机号：{{ selected.phone || '-' }}</span>
          </div>

          <!-- 信号统计摘要 -->
          <div v-if="signals.length" class="sum-grid">
            <div v-for="item in summaryItems" :key="item.key" class="sum-item">
              <span class="sum-label">{{ item.label }}</span>
              <b class="sum-avg">{{ item.avg }} <small>{{ item.unit }}</small></b>
              <span class="sum-abn" :class="{ warn: item.abnormal > 0 }">
                异常 {{ item.abnormal }} 条
              </span>
            </div>
          </div>

          <div v-if="signalLoading" class="empty">加载中...</div>
          <div v-else-if="signalError" class="empty error">{{ signalError }}</div>
          <div v-else-if="signals.length" class="table-wrap">
            <table class="sig-table">
              <thead>
                <tr>
                  <th>时间</th>
                  <th>心率</th>
                  <th>收缩压</th>
                  <th>舒张压</th>
                  <th>血氧</th>
                  <th>体温</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in signals.slice(0, 15)" :key="r.id">
                  <td>{{ fmtDate(r.recordTime) }}</td>
                  <td>{{ r.heartRate }} bpm</td>
                  <td>{{ r.sbp }} mmHg</td>
                  <td>{{ r.dbp }} mmHg</td>
                  <td>{{ Math.round(r.spo2) }}%</td>
                  <td>{{ r.temp }}℃</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="empty">该患者暂无信号记录</div>
        </template>
        <div v-else class="empty-placeholder">请从左侧选择一名患者查看其生理信号记录</div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.records-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.head-desc {
  padding: 10px 14px;
  background: #eef6ee;
  color: #3d6b40;
  border: 1px solid #d0e4d0;
  font-size: 0.85rem;
}
.records-layout {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}
.patient-list-card {
  width: 280px;
  flex-shrink: 0;
  background: #fff;
  border: 1px solid #eef2ee;
}
.search-box {
  padding: 12px;
  border-bottom: 1px solid #eef2ee;
}
.search-box input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #e0e7e0;
  font-size: 0.85rem;
  font-family: inherit;
  box-sizing: border-box;
}
.patient-list {
  list-style: none;
  margin: 0;
  padding: 6px;
  max-height: 560px;
  overflow-y: auto;
}
.patient-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
}
.patient-item:hover {
  background: #f0f7f0;
}
.patient-item.on {
  background: #eaf5ea;
}
.p-info {
  display: flex;
  flex-direction: column;
  line-height: 1.4;
  min-width: 0;
}
.p-name {
  font-weight: 600;
  color: #1f2937;
}
.p-meta {
  font-size: 0.75rem;
  color: #9ca3af;
}
.detail-card {
  flex: 1;
  min-width: 0;
  background: #fff;
  border: 1px solid #eef2ee;
  padding: 18px;
  min-height: 380px;
}
.detail-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.detail-head h3 {
  margin: 0;
  font-size: 1rem;
  color: #1f2937;
}
.badge {
  background: #eaf5ea;
  color: #3d6b40;
  padding: 2px 10px;
  font-size: 0.8rem;
  font-weight: 600;
}
.base-info {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 18px;
  font-size: 0.82rem;
  color: #4b5563;
  background: #f8fbf8;
  border: 1px solid #e8f0e8;
  padding: 10px 14px;
  margin-bottom: 12px;
}
.sum-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
  margin-bottom: 14px;
}
.sum-item {
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 8px 12px;
  background: #fff;
  border: 1px solid #eef2ee;
  border-radius: 6px;
}
.sum-label {
  font-size: 0.74rem;
  color: #8aa08c;
}
.sum-avg {
  font-size: 1rem;
  color: #1f2937;
}
.sum-avg small {
  font-weight: 400;
  font-size: 0.7rem;
  color: #9ca3af;
}
.sum-abn {
  font-size: 0.7rem;
  color: #2d7d4f;
}
.sum-abn.warn {
  color: #c0392b;
}
.table-wrap {
  overflow-x: auto;
}
.sig-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.84rem;
}
.sig-table th {
  padding: 9px 10px;
  text-align: left;
  background: #f6faf6;
  color: #557457;
  border-bottom: 2px solid #dbe8db;
}
.sig-table td {
  padding: 9px 10px;
  border-bottom: 1px solid #f3f4f6;
  color: #4b5563;
}
.empty-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b0b0b0;
}
.empty {
  text-align: center;
  padding: 30px;
  color: #b0b0b0;
}
.empty.error {
  color: #c0392b;
}
@media (max-width: 760px) {
  .records-layout {
    flex-direction: column;
  }
  .patient-list-card {
    width: 100%;
  }
}
</style>
