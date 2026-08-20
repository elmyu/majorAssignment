import '@/assets/main.css';

import { createApp } from 'vue';
import ElementPlus from 'element-plus';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import 'element-plus/dist/index.css';

import App from '@/App.vue';
import router from '@/router';

// 引入 Element Plus 组件库（全局注册，中文语言包）
createApp(App)
  .use(router)
  .use(ElementPlus, { locale: zhCn })
  .mount('#app');
