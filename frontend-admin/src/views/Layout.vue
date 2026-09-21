<template>
  <el-container style="height: 100vh;">
    <el-aside width="240px" class="admin-aside">
      <div class="aside-brand">
        <span class="brand-badge">深</span>
        <div class="brand-titles">
          <strong>Shenyuan Legal</strong>
          <small>咨询管理与业务中台</small>
        </div>
      </div>
      <el-menu
        router
        :default-active="$route.path"
        background-color="#084d50"
        text-color="#b4d5d4"
        active-text-color="#f1b68f"
        class="admin-menu"
      >
        <el-menu-item index="/crm">
          <el-icon><UserFilled /></el-icon>
          <span>线索管理 (CRM)</span>
        </el-menu-item>
        <el-menu-item index="/content">
          <el-icon><Document /></el-icon>
          <span>内容中心 (CMS)</span>
        </el-menu-item>
        <el-menu-item index="/research">
          <el-icon><Search /></el-icon>
          <span>案件法律研究</span>
        </el-menu-item>
        <el-menu-item index="/marketing">
          <el-icon><Promotion /></el-icon>
          <span>出海营销助手</span>
        </el-menu-item>
      </el-menu>
      <div class="aside-footer">
        <a href="https://shenyuan-web.vercel.app" target="_blank" class="preview-portal-link">
          🌐 访问官网门户 ↗
        </a>
      </div>
    </el-aside>
    <el-container>
      <el-header class="admin-header">
        <div class="header-title">{{ $route.meta.title || '深远涉外律所管理中台' }}</div>
        <div class="header-right">
          <span class="db-status-pill">
            <span class="status-dot"></span>
            Supabase Postgres 在线
          </span>
          <el-button size="small" class="logout-btn" @click="logout">退出登录</el-button>
        </div>
      </el-header>
      <el-main class="admin-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { UserFilled, Document, Search, Promotion } from '@element-plus/icons-vue'

const router = useRouter()
const logout = () => {
  localStorage.removeItem('shenyuan_admin_token')
  router.push('/login')
}
</script>

<style scoped>
.admin-aside {
  background-color: #084d50;
  color: #fff;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255,255,255,0.08);
}

.aside-brand {
  padding: 20px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.12);
}

.brand-badge {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  background: #f7f2e9;
  color: #084d50;
  border-radius: 6px;
  font-weight: 800;
  font-size: 17px;
  font-family: serif;
}

.brand-titles {
  display: flex;
  flex-direction: column;
}

.brand-titles strong {
  font-size: 14.5px;
  color: #fff;
}

.brand-titles small {
  font-size: 11px;
  color: rgba(255,255,255,0.65);
}

.admin-menu {
  border-right: none;
  margin-top: 10px;
  flex: 1;
}

.admin-menu :deep(.el-menu-item) {
  font-size: 13.5px;
  font-weight: 500;
}

.admin-menu :deep(.el-menu-item.is-active) {
  background-color: #06393b !important;
  font-weight: 700;
  border-left: 3px solid #f1b68f;
}

.aside-footer {
  padding: 16px;
  border-top: 1px solid rgba(255,255,255,0.12);
}

.preview-portal-link {
  display: block;
  text-align: center;
  color: #b4d5d4;
  font-size: 12.5px;
  text-decoration: none;
  padding: 6px;
  border: 1px dashed rgba(255,255,255,0.25);
  border-radius: 6px;
  transition: all 0.2s;
}

.preview-portal-link:hover {
  color: #fff;
  border-color: rgba(255,255,255,0.6);
}

.admin-header {
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #d9d9d2;
  background: #fffdf9;
  padding: 0 24px;
}

.header-title {
  font-weight: 700;
  font-size: 16px;
  color: #084d50;
  font-family: serif;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.db-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #deefea;
  color: #084d50;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid #b9d8d0;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #2e7d32;
}

.logout-btn {
  background: transparent;
  color: #627180;
  border-color: #d9d9d2;
}

.logout-btn:hover {
  color: #d76e39;
  border-color: #d76e39;
}

.admin-main {
  background-color: #f6f3ed;
  padding: 24px;
}
</style>
