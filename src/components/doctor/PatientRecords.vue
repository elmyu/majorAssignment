<script setup>
import { ref, onMounted } from 'vue';
import { getPatientsForDoctor, getSignalsOfPatient } from '@/services/api.js';
import { fmtDate } from '@/utils/format.js';

const patients = ref([]);
const loading = ref(true);
const errorMsg = ref('');
const search = ref('');

const selected = ref(null);
const signalLoading = ref(false);
const signalError = ref('');
const signals = ref([]);

onMounted(() => {
  try {
    patients.value = getPatientsForDoctor();
  } catch (e) {
    errorMsg.value = e.message;
  } finally {
    loading.value = false;
  }
});

function viewSignals(patient) {
  selected.value = patient;
  signalLoading.value = true;
  signalError.value = '';
  signals.value = [];
  try {
    const res = getSignalsOfPatient(patient.id);
    signals.value = res.records;
  } catch (e) {
    signalError.value = e.message;
  } finally {
    signalLoading.value = false;
  }
}
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
                  <td>{{ r.spo2 }}%</td>
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
