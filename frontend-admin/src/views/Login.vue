<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-brand">
        <span class="brand-badge">深</span>
        <div class="brand-text">
          <h3>Shenyuan Legal</h3>
          <small>咨询管理后台</small>
        </div>
      </div>
      <h2>管理登录</h2>
      <p class="sub-text">输入部署时配置的 ADMIN_TOKEN 管理令牌。</p>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-item">
          <label>管理口令</label>
          <input
            v-model="token"
            type="password"
            placeholder="请输入 ADMIN_TOKEN"
            autocomplete="current-password"
            required
          />
        </div>
        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '进入中...' : '进入后台' }}
        </button>
      </form>
      <p class="login-hint">口令仅保存在本浏览器会话中，关闭标签页即失效。</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const token = ref('')
const loading = ref(false)

const handleLogin = () => {
  if (!token.value) {
    ElMessage.warning('请输入管理口令')
    return
  }
  localStorage.setItem('shenyuan_admin_token', token.value)
  ElMessage.success('登录成功')
  router.push('/crm')
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f6f3ed;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", sans-serif;
}

.login-box {
  width: 380px;
  background: #fffdf9;
  border: 1px solid #d9d9d2;
  border-radius: 10px;
  padding: 32px 28px;
  box-shadow: 0 10px 30px rgba(20, 33, 44, 0.08);
}

.login-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0ede6;
}

.brand-badge {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  background: #084d50;
  color: #fff;
  border-radius: 6px;
  font-weight: 800;
  font-size: 18px;
  font-family: serif;
}

.brand-text h3 {
  margin: 0;
  font-size: 16px;
  color: #084d50;
}

.brand-text small {
  color: #627180;
  font-size: 11.5px;
}

.login-box h2 {
  margin: 0 0 6px;
  font-size: 19px;
  color: #172433;
}

.sub-text {
  margin: 0 0 20px;
  color: #627180;
  font-size: 13px;
  line-height: 1.5;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-item label {
  display: block;
  font-size: 12px;
  font-weight: 700;
  color: #627180;
  margin-bottom: 6px;
}

.form-item input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d9d9d2;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  background: #fff;
  box-sizing: border-box;
}

.form-item input:focus {
  border-color: #0d6c6b;
  box-shadow: 0 0 0 3px rgba(13, 108, 107, 0.12);
}

.submit-btn {
  background: #d76e39;
  color: #fff;
  border: none;
  padding: 11px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  margin-top: 8px;
  transition: background 0.2s;
}

.submit-btn:hover {
  background: #c85d2e;
}

.login-hint {
  font-size: 12px;
  color: #627180;
  margin-top: 18px;
  text-align: center;
}
</style>
