import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Articles from '../views/Articles.vue'
import ArticleDetail from '../views/ArticleDetail.vue'
import Services from '../views/Services.vue'

const routes = [
  { path: '/', component: Home, meta: { lang: 'zh' } },
  { path: '/en', component: Home, meta: { lang: 'en' } },
  { path: '/services', component: Services, meta: { lang: 'zh' } },
  { path: '/en/services', component: Services, meta: { lang: 'en' } },
  { path: '/articles', component: Articles, meta: { lang: 'zh' } },
  { path: '/en/articles', component: Articles, meta: { lang: 'en' } },
  { path: '/articles/:slug', component: ArticleDetail, meta: { lang: 'zh' } },
  { path: '/en/articles/:slug', component: ArticleDetail, meta: { lang: 'en' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
