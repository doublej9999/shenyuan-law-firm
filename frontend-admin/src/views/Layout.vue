<template>
  <el-container style="height: 100vh;">
    <el-aside width="240px" style="background-color: #1a2234; color: #fff;">
      <div style="padding: 24px 20px; font-weight: bold; font-size: 18px; border-bottom: 1px solid #2d3748;">
        ⚖️ 申远涉外律所中台
      </div>
      <el-menu
        router
        :default-active="$route.path"
        background-color="#1a2234"
        text-color="#a0aec0"
        active-text-color="#409eff"
        style="border-right: none; margin-top: 10px;"
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
          <span>涉外法律调研</span>
        </el-menu-item>
        <el-menu-item index="/marketing">
          <el-icon><Promotion /></el-icon>
          <span>出海营销助手</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="height: 60px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; background: #fff;">
        <div style="font-weight: 600; font-size: 16px; color: #2d3748;">{{ $route.meta.title }}</div>
        <div>
          <el-tag type="success" style="margin-right: 15px;">Supabase Postgres 在线</el-tag>
          <el-button size="small" type="danger" plain @click="logout">退出登录</el-button>
        </div>
      </el-header>
      <el-main style="background-color: #f7fafc; padding: 20px;">
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
