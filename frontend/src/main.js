import { createApp } from 'vue'
// import { pinia } from './stores'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import 'v-calendar/dist/style.css';
import { createPinia } from 'pinia'
import VCalendar from 'v-calendar';

// Vuetify
import 'vuetify/styles'
import {createVuetify} from "vuetify";
import * as components from "vuetify/components";
import * as directives from 'vuetify/directives'
const vuetify = createVuetify({
  components,
  directives,
})

const pinia = createPinia() /* axios interceptors needs Pinia already */

// auth: axios interceptors
import './api/axios';

createApp(App).use(pinia).use(router).use(vuetify).use(VCalendar).mount('#app')
