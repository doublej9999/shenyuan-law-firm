import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// Tailwind 核心与全局律所品牌样式
import './styles/globals.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
