<template>
  <div style="height: 100vh; display: flex; align-items: center; justify-content: center; background: #0f172a;">
    <el-card style="width: 400px; border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.3);">
      <template #header>
        <div style="text-align: center; font-weight: bold; font-size: 18px; color: #1e293b;">
          申远涉外律所业务中台
        </div>
      </template>
      <el-form :model="form" @submit.prevent="handleLogin">
        <el-form-item label="管理口令">
          <el-input
            v-model="form.token"
            type="password"
            placeholder="请输入 ADMIN_TOKEN"
            show-password
          />
        </el-form-item>
        <el-button type="primary" style="width: 100%; margin-top: 10px;" @click="handleLogin" :loading="loading">
          立即进入系统
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const form = ref({ token: '' })
const loading = ref(false)

const handleLogin = () => {
  if (!form.value.token) {
    ElMessage.warning('请输入管理口令')
    return
  }
  localStorage.setItem('shenyuan_admin_token', form.value.token)
  ElMessage.success('登录成功')
  router.push('/crm')
}
</script>
