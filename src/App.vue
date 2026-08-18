<script setup>
import { onMounted } from 'vue';
import { initDB } from '@/services/db.js';

// 应用启动时初始化模拟数据库（若无数据则写入种子数据）
onMounted(() => {
  initDB();
});
</script>

<template>
  <router-view />
</template>
