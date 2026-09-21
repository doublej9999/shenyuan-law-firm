import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../views/Layout.vue'
import Login from '../views/Login.vue'
import CrmIntakes from '../views/CrmIntakes.vue'
import ContentList from '../views/ContentList.vue'
import LegalResearch from '../views/LegalResearch.vue'
import MarketingAssistant from '../views/MarketingAssistant.vue'

const routes = [
  {
    path: '/login',
    component: Login,
  },
  {
    path: '/',
    component: Layout,
    redirect: '/crm',
    children: [
      { path: 'crm', component: CrmIntakes, meta: { title: '线索管理 (CRM)' } },
      { path: 'content', component: ContentList, meta: { title: '内容中心 (CMS)' } },
      { path: 'research', component: LegalResearch, meta: { title: '法律智能调研' } },
      { path: 'marketing', component: MarketingAssistant, meta: { title: '出海营销助手' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('shenyuan_admin_token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
