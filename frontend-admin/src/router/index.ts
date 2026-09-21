import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import AdminLayout from '../layouts/AdminLayout.vue'
import Login from '../views/Login.vue'
import DashboardView from '../views/dashboard/DashboardView.vue'
import CrmListView from '../views/crm/ListView.vue'
import ArticleList from '../views/content/ArticleList.vue'
import ResearchStudio from '../views/research/ResearchStudio.vue'
import GeneratorView from '../views/marketing/GeneratorView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '管理登录' },
  },
  {
    path: '/',
    component: AdminLayout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: DashboardView,
        meta: { title: '经营概览大盘' },
      },
      {
        path: 'crm',
        name: 'CRM',
        component: CrmListView,
        meta: { title: '涉外商事线索中枢' },
      },
      {
        path: 'content',
        name: 'CMS',
        component: ArticleList,
        meta: { title: '多语言内容中心' },
      },
      {
        path: 'research',
        name: 'Research',
        component: ResearchStudio,
        meta: { title: '涉外法律智能调研' },
      },
      {
        path: 'marketing',
        name: 'Marketing',
        component: GeneratorView,
        meta: { title: '出海营销获客矩阵' },
      },
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
