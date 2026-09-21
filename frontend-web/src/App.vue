<template>
  <div class="site-wrapper">
    <header class="navbar">
      <div class="nav-container">
        <router-link :to="isEn ? '/en' : '/'" class="brand">
          <span class="logo-icon">⚖️</span>
          <span class="logo-text">{{ isEn ? 'Shenyuan Law Firm' : '申远律师事务所' }}</span>
        </router-link>
        <nav class="nav-links">
          <router-link :to="isEn ? '/en' : '/'">{{ isEn ? 'Home' : '首页' }}</router-link>
          <router-link :to="isEn ? '/en/services' : '/services'">{{ isEn ? 'Practice Areas' : '业务领域' }}</router-link>
          <router-link :to="isEn ? '/en/articles' : '/articles'">{{ isEn ? 'Insights' : '专业文章' }}</router-link>
          <button class="lang-btn" @click="toggleLang">
            {{ isEn ? '中文' : 'English' }}
          </button>
        </nav>
      </div>
    </header>

    <main class="main-content">
      <router-view />
    </main>

    <!-- 在线咨询悬浮按钮与抽屉 -->
    <div class="consult-float-btn" @click="showDrawer = true">
      💬 {{ isEn ? 'Free Consultation' : '涉外法律咨询' }}
    </div>

    <!-- 咨询弹窗抽屉 -->
    <div v-if="showDrawer" class="drawer-mask" @click.self="showDrawer = false">
      <div class="drawer-box">
        <div class="drawer-header">
          <h3>{{ isEn ? 'Legal Inquiry' : '在线涉外法律咨询' }}</h3>
          <span class="close-btn" @click="showDrawer = false">&times;</span>
        </div>
        <form @submit.prevent="submitIntake" class="drawer-form">
          <div class="form-group">
            <label>{{ isEn ? 'Your Name *' : '您的姓名 *' }}</label>
            <input v-model="form.name" required />
          </div>
          <div class="form-group">
            <label>{{ isEn ? 'Phone Number *' : '联系电话 *' }}</label>
            <input v-model="form.phone" required />
          </div>
          <div class="form-group">
            <label>{{ isEn ? 'Email' : '电子邮箱' }}</label>
            <input v-model="form.email" type="email" />
          </div>
          <div class="form-group">
            <label>{{ isEn ? 'Matter Category *' : '咨询业务类型 *' }}</label>
            <select v-model="form.matter" required>
              <option value="cross-border-contract">{{ isEn ? 'Cross-border Commercial Dispute' : '涉外商事与合同争议' }}</option>
              <option value="inheritance">{{ isEn ? 'Cross-border Inheritance & Probate' : '涉外继承与遗嘱检验' }}</option>
              <option value="fdi-compliance">{{ isEn ? 'Foreign Investment & Outbound Compliance' : '企业出海与合规' }}</option>
              <option value="enforcement">{{ isEn ? 'Judgment & Arbitration Enforcement' : '跨境判决与仲裁执行' }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>{{ isEn ? 'Case Summary *' : '案情简述 *' }}</label>
            <textarea v-model="form.summary" rows="4" required></textarea>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="consent" v-model="form.consent" required />
            <label for="consent" style="font-size: 12px; color: #64748b;">
              {{ isEn ? 'I consent to the collection of my information under PIPL.' : '我已阅读并同意个人信息保护政策，授权律师评估案情。' }}
            </label>
          </div>
          <button type="submit" class="submit-btn" :disabled="submitting">
            {{ submitting ? (isEn ? 'Submitting...' : '提交中...') : (isEn ? 'Submit Inquiry' : '立即提交评估') }}
          </button>
        </form>
      </div>
    </div>

    <footer class="footer">
      <div class="footer-inner">
        <p>© 2025 {{ isEn ? 'Shenyuan Law Firm. All rights reserved.' : '申远律师事务所 版权所有。涉外商事合规与争议解决团队' }}</p>
        <p style="font-size: 12px; color: #94a3b8;">
          {{ isEn ? 'Guangzhou · Shenzhen · Shanghai · Hong Kong Liaison' : '广州 · 深圳 · 上海 · 香港联络处' }}
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

axios.defaults.baseURL = import.meta.env.VITE_API_URL || ''

const route = useRoute()
const router = useRouter()
const isEn = computed(() => route.path.startsWith('/en'))

const showDrawer = ref(false)
const submitting = ref(false)
const form = ref({
  name: '',
  phone: '',
  email: '',
  matter: 'cross-border-contract',
  summary: '',
  consent: true,
})

const toggleLang = () => {
  if (isEn.value) {
    router.push(route.path.replace(/^\/en/, '') || '/')
  } else {
    router.push(`/en${route.path === '/' ? '' : route.path}`)
  }
}

const submitIntake = async () => {
  submitting.value = true
  try {
    await axios.post('/api/intakes', {
      ...form.value,
      language: isEn.value ? 'en' : 'zh',
    })
    alert(isEn.value ? 'Consultation submitted! Our lawyers will contact you within 24 hours.' : '咨询提交成功！涉外合伙人律师将在 24 小时内与您联系。')
    showDrawer.value = false
    form.value = { name: '', phone: '', email: '', matter: 'cross-border-contract', summary: '', consent: true }
  } catch (err: any) {
    alert(err.response?.data?.detail || '提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style>
* { box-sizing: border-box; }
.site-wrapper { min-height: 100vh; display: flex; flex-direction: column; }
.navbar { background: #0f172a; color: #fff; padding: 16px 24px; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
.brand { color: #fff; text-decoration: none; font-size: 20px; font-weight: bold; display: flex; align-items: center; gap: 8px; }
.nav-links { display: flex; align-items: center; gap: 24px; }
.nav-links a { color: #cbd5e1; text-decoration: none; font-size: 15px; font-weight: 500; transition: color 0.2s; }
.nav-links a:hover, .nav-links a.router-link-active { color: #38bdf8; }
.lang-btn { background: #1e293b; color: #38bdf8; border: 1px solid #38bdf8; border-radius: 4px; padding: 4px 12px; cursor: pointer; font-size: 13px; }
.main-content { flex: 1; max-width: 1200px; margin: 0 auto; width: 100%; padding: 32px 24px; }
.consult-float-btn { position: fixed; right: 24px; bottom: 32px; background: #0284c7; color: #fff; padding: 14px 22px; border-radius: 30px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4); z-index: 99; transition: transform 0.2s; }
.consult-float-btn:hover { transform: translateY(-2px); }
.drawer-mask { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; justify-content: flex-end; }
.drawer-box { background: #fff; width: 440px; height: 100%; padding: 24px; overflow-y: auto; box-shadow: -4px 0 20px rgba(0,0,0,0.2); }
.drawer-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 20px; }
.close-btn { font-size: 24px; cursor: pointer; color: #64748b; }
.drawer-form .form-group { margin-bottom: 16px; }
.drawer-form label { display: block; font-size: 13px; font-weight: 600; color: #334155; margin-bottom: 6px; }
.drawer-form input, .drawer-form select, .drawer-form textarea { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; }
.checkbox-group { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
.submit-btn { width: 100%; padding: 12px; background: #0284c7; color: #fff; border: none; border-radius: 6px; font-size: 15px; font-weight: bold; cursor: pointer; }
.footer { background: #0f172a; color: #64748b; padding: 32px 24px; text-align: center; margin-top: auto; border-top: 1px solid #1e293b; }
</style>
