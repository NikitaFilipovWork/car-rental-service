import Vue from 'vue';
import VCalendar from 'v-calendar';

import App from './App.vue';
import api from './api.js';
import notify from './notify.js';
import router from './router.js';

import './assets/main.css';

Vue.use(VCalendar);

Vue.prototype.$api = api;
Vue.prototype.$notify = notify;
Vue.prototype.$route = router.route;
Vue.prototype.$go = router.go;

new Vue({
  render: (h) => h(App)
}).$mount('#app');
