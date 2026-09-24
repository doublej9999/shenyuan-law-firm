import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// Tailwind 核心与全局律所品牌样式
import './styles/globals.css'

// vue-sonner Toast 样式（缺失会导致通知无样式并堆叠在页面最底部）
import 'vue-sonner/style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
