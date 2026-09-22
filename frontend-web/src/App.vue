<template>
  <div class="site-shell">
    <header class="site-header" :class="{ 'is-scrolled': isScrolled || !isHomePage }">
      <div class="wrap nav">
        <router-link :to="isEn ? '/en' : '/'" class="brand" aria-label="Shenyuan International 首页">
          <span class="brand-mark">深</span>
          <span class="brand-text">
            <span>Shenyuan International</span>
            <small>{{ isEn ? 'Shenyuan International Law' : '深远(国际)律师事务所' }}</small>
          </span>
        </router-link>

        <nav class="nav-links" :class="{ 'mobile-open': mobileMenuOpen }">
          <a @click.prevent="navigateSection('services')" href="#services">
            {{ isEn ? 'Services' : '服务范围' }}
          </a>
          <a @click.prevent="navigateSection('cases')" href="#cases">
            {{ isEn ? 'Results' : '成果与案例' }}
          </a>
          <a @click.prevent="navigateSection('global')" href="#global">
            {{ isEn ? 'Global reach' : '全球网络' }}
          </a>
          <a @click.prevent="navigateSection('team')" href="#team">
            {{ isEn ? 'Team' : '团队' }}
          </a>
          <a @click.prevent="navigateSection('faq')" href="#faq">
            {{ isEn ? 'FAQ' : '常见问题' }}
          </a>
          <router-link :to="isEn ? '/en/articles' : '/articles'">
            {{ isEn ? 'Insights' : '法律专栏' }}
          </router-link>
        </nav>

        <div class="nav-actions">
          <button class="lang-switch" type="button" @click="toggleLang" aria-label="切换语言">
            {{ isEn ? '中文' : 'EN / 中' }}
          </button>
          <a class="nav-cta" @click.prevent="navigateSection('intake')" href="#intake">
            {{ isEn ? 'Start consultation →' : '开始咨询 →' }}
          </a>
          <button class="menu-button" type="button" @click="mobileMenuOpen = !mobileMenuOpen" aria-label="打开菜单">
            {{ mobileMenuOpen ? '✕' : '☰' }}
          </button>
        </div>
      </div>
    </header>

    <main class="main-body">
      <router-view />
    </main>

    <!-- 浮动咨询快捷按钮 -->
    <div class="consult-float-pill" @click="openQuickConsult" title="免费咨询">
      <span class="pill-icon">💬</span>
      <span class="pill-text">{{ isEn ? 'Free Consultation' : '免费法律咨询' }}</span>
    </div>

    <!-- 浮动侧边/弹窗咨询抽屉 (在非主页或点击悬浮按钮时使用) -->
    <div v-if="drawerOpen" class="consult-drawer-backdrop" @click.self="drawerOpen = false">
      <div class="consult-drawer">
        <div class="drawer-head">
          <div>
            <h3>{{ isEn ? 'Initial Legal Consultation' : '跨境法律咨询与评估' }}</h3>
            <p>{{ isEn ? '24h response from licensed cross-border lawyers.' : '涉外执业团队 24 小时内首响，先评估再行动。' }}</p>
          </div>
          <button class="close-x" @click="drawerOpen = false">×</button>
        </div>

        <div class="wechat-mini-card">
          <img src="/wechat-qrcode.png" alt="WeChat QR" class="drawer-qr" />
          <div>
            <strong>{{ isEn ? 'WeChat Direct' : '微信快速咨询' }}</strong>
            <p>{{ isEn ? 'Add ShenyuanLegal for instant contact' : '微信号：ShenyuanLegal' }}</p>
          </div>
        </div>

        <form @submit.prevent="submitDrawerForm" class="drawer-fields">
          <div class="field-item">
            <label>{{ isEn ? 'Your Name *' : '您的称呼 *' }}</label>
            <input v-model="drawerForm.name" required :placeholder="isEn ? 'e.g. Mr. Zhang' : '例如：王女士 / 陈先生'" />
          </div>
          <div class="field-item">
            <label>{{ isEn ? 'Phone / WhatsApp *' : '联系电话 *' }}</label>
            <input v-model="drawerForm.phone" type="tel" required :placeholder="isEn ? '+86 / +1 ...' : '手机号码，用于及时回访'" />
          </div>
          <div class="field-item">
            <label>{{ isEn ? 'Email (Optional)' : '电子邮箱（选填）' }}</label>
            <input v-model="drawerForm.email" type="email" :placeholder="isEn ? 'For document checklist' : '用于接收材料清单与备忘录'" />
          </div>
          <div class="field-item">
            <label>{{ isEn ? 'Matter Type *' : '事项类型 *' }}</label>
            <select v-model="drawerForm.matter" required>
              <option value="国际贸易争议">{{ isEn ? 'International Trade Dispute' : '国际贸易争议' }}</option>
              <option value="诉讼与债务追收">{{ isEn ? 'Litigation & Debt Recovery' : '诉讼与债务追收' }}</option>
              <option value="继承与家族资产纠纷">{{ isEn ? 'Inheritance & Family Assets' : '继承与家族资产纠纷' }}</option>
              <option value="不确定，希望先沟通">{{ isEn ? 'Not Sure / Needs Consultation' : '不确定，希望先沟通' }}</option>
            </select>
          </div>
          <div class="field-item">
            <label>{{ isEn ? 'Brief Description *' : '一句话描述问题 *' }}</label>
            <textarea v-model="drawerForm.summary" rows="3" required :placeholder="isEn ? 'Briefly describe your situation...' : '简要说明涉案金额、对方所在地与当前诉求...'"></textarea>
          </div>
          <label class="drawer-consent">
            <input type="checkbox" v-model="drawerForm.consent" required />
            <span>{{ isEn ? 'I agree to the privacy statement and authorize consultation.' : '我已阅读并同意《隐私说明》，同意提交以上信息用于初步咨询评估。' }}</span>
          </label>
          <button type="submit" class="drawer-submit-btn" :disabled="drawerSubmitting">
            {{ drawerSubmitting ? (isEn ? 'Submitting...' : '提交中...') : (isEn ? 'Submit for Guidance →' : '提交，获取下一步建议 →') }}
          </button>
        </form>
      </div>
    </div>

    <!-- 全局提示 Toast -->
    <div class="page-toast" :class="{ 'is-visible': toastVisible }" role="status">
      {{ toastMessage }}
    </div>

    <footer class="site-footer">
      <div class="wrap">
        <div class="footer-grid">
          <div class="footer-brand">
            Shenyuan International
            <small>{{ isEn 
              ? 'Shenyuan International Law Firm · Cross-border dispute resolution & family asset protection' 
              : '深远(国际)律师事务所 · 跨境争议解决与家族资产保护' }}</small>
          </div>
          <div class="footer-col">
            <h4>{{ isEn ? 'Practice Areas' : '服务范围' }}</h4>
            <a @click.prevent="navigateSection('services')" href="#services">{{ isEn ? 'International Trade Disputes' : '国际贸易争议' }}</a>
            <a @click.prevent="navigateSection('services')" href="#services">{{ isEn ? 'Litigation & Debt Recovery' : '诉讼与债务追收' }}</a>
            <a @click.prevent="navigateSection('services')" href="#services">{{ isEn ? 'Inheritance & Family Assets' : '继承与家族资产纠纷' }}</a>
          </div>
          <div class="footer-col">
            <h4>{{ isEn ? 'Quick Links' : '快速入口' }}</h4>
            <a @click.prevent="navigateSection('intake')" href="#intake">{{ isEn ? 'Free Consultation' : '免费法律咨询' }}</a>
            <router-link :to="isEn ? '/en/articles' : '/articles'">{{ isEn ? 'Legal Insights' : '法律专栏' }}</router-link>
            <a @click.prevent="navigateSection('global')" href="#global">{{ isEn ? 'Global Network' : '全球网络' }}</a>
            <a @click.prevent="navigateSection('team')" href="#team">{{ isEn ? 'Legal Team' : '律师团队' }}</a>
            <a @click.prevent="navigateSection('faq')" href="#faq">{{ isEn ? 'FAQ' : '常见问题' }}</a>
          </div>
        </div>
        <div class="footer-meta">
          © 2026 Shenyuan International · 深远(国际)律师事务所<br>
          <span>{{ isEn 
            ? 'This website provides general information only and does not constitute formal legal advice. Foreign legal proceedings are conducted through locally licensed counsel.' 
            : '本网站内容仅供一般信息参考，不构成正式法律意见。境外法律程序通过与当地执业律所合作提供。' }}</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiClient, parseApiError } from '@/api/client'

const route = useRoute()
const router = useRouter()
const isEn = computed(() => route.path.startsWith('/en'))
const isHomePage = computed(() => route.path === '/' || route.path === '/en')

const isScrolled = ref(false)
const mobileMenuOpen = ref(false)
const drawerOpen = ref(false)
const drawerSubmitting = ref(false)
const toastVisible = ref(false)
const toastMessage = ref('')

const drawerForm = ref({
  name: '',
  phone: '',
  email: '',
  matter: '国际贸易争议',
  summary: '',
  consent: true
})

const handleScroll = () => {
  isScrolled.value = window.scrollY > 40
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

const toggleLang = () => {
  if (isEn.value) {
    const nextPath = route.path.replace(/^\/en/, '') || '/'
    router.push(nextPath)
  } else {
    const nextPath = `/en${route.path === '/' ? '' : route.path}`
    router.push(nextPath)
  }
}

const showToast = (msg: string) => {
  toastMessage.value = msg
  toastVisible.value = true
  setTimeout(() => {
    toastVisible.value = false
  }, 4000)
}

const navigateSection = (sectionId: string) => {
  mobileMenuOpen.value = false
  if (isHomePage.value) {
    const el = document.getElementById(sectionId)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' })
    }
  } else {
    router.push(isEn.value ? `/en#${sectionId}` : `/#${sectionId}`).then(() => {
      setTimeout(() => {
        const el = document.getElementById(sectionId)
        if (el) el.scrollIntoView({ behavior: 'smooth' })
      }, 200)
    })
  }
}

const openQuickConsult = () => {
  if (isHomePage.value) {
    const intakeEl = document.getElementById('intake')
    if (intakeEl) {
      intakeEl.scrollIntoView({ behavior: 'smooth' })
      return
    }
  }
  drawerOpen.value = true
}

const submitDrawerForm = async () => {
  if (!drawerForm.value.name || !drawerForm.value.phone || !drawerForm.value.summary) {
    alert(isEn.value ? 'Please fill in the required fields (Name, Phone, Description).' : '请填写必要字段（称呼、电话、问题描述）。')
    return
  }
  if (!drawerForm.value.consent) {
    alert(isEn.value ? 'Please agree to the privacy statement.' : '请勾选同意隐私说明。')
    return
  }

  drawerSubmitting.value = true
  try {
    await apiClient.post('/api/intakes', {
      name: drawerForm.value.name,
      phone: drawerForm.value.phone,
      email: drawerForm.value.email || undefined,
      matter: drawerForm.value.matter,
      summary: drawerForm.value.summary,
      consent: drawerForm.value.consent,
      language: isEn.value ? 'en' : 'zh'
    })
    drawerOpen.value = false
    drawerForm.value = {
      name: '',
      phone: '',
      email: '',
      matter: '国际贸易争议',
      summary: '',
      consent: true
    }
    showToast(isEn.value 
      ? 'Thank you! Your inquiry has been received. Our team will contact you within 24 hours.' 
      : '感谢您的信任！案件评估信息已收到，涉外律师将在 24 小时内与您联系。')
  } catch (err: any) {
    const errorDetail = parseApiError(err, isEn.value)
    alert(errorDetail)
  } finally {
    drawerSubmitting.value = false
  }
}
</script>

<style>
:root {
  --ink: #172433;
  --muted: #627180;
  --paper: #f6f3ed;
  --paper-card: #fbf9f4;
  --surface: #fffdf9;
  --line: #d9d9d2;
  --teal: #0d6c6b;
  --teal-deep: #084d50;
  --teal-soft: #deefea;
  --orange: #d76e39;
  --orange-soft: #f2dfd1;
  --cream: #ede8de;
  --gold: #b08d57;
  --shadow: 0 20px 50px rgba(20, 33, 44, .11);
  --radius: 10px;
  --max: 1180px;
  --serif: "Playfair Display", "Noto Serif SC", Georgia, "Songti SC", "SimSun", serif;
  --sans: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  padding: 0;
  color: var(--ink);
  background: var(--paper);
  font-family: var(--sans);
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
}
a { color: inherit; text-decoration: none; }
button, input, select, textarea { font: inherit; }
button { cursor: pointer; }

.site-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.wrap {
  width: min(calc(100% - 40px), var(--max));
  margin: 0 auto;
}

/* 顶部导航 Header */
.site-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  color: #f8f5ef;
  transition: background 0.25s ease, box-shadow 0.25s ease;
  background: rgba(8, 77, 80, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.site-header.is-scrolled {
  background: rgba(7, 49, 51, 0.98);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  min-height: 80px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: .05em;
  color: #fff;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  color: var(--teal-deep);
  background: #f7f2e9;
  border-radius: 8px;
  font-family: var(--serif);
  font-size: 19px;
  font-weight: 700;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}

.brand-text { display: grid; gap: 1px; }
.brand-text span { font-weight: 700; font-size: 15px; }
.brand-text small { color: rgba(255,255,255,.72); font-size: 11px; font-weight: 500; }

.nav-links {
  display: flex;
  align-items: center;
  gap: 24px;
  font-size: 14px;
  color: rgba(255,255,255,.82);
}

.nav-links a {
  cursor: pointer;
  transition: color 0.2s ease;
}

.nav-links a:hover,
.nav-links a.router-link-active {
  color: #fff;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.lang-switch {
  padding: 7px 12px;
  color: rgba(255,255,255,.9);
  background: transparent;
  border: 1px solid rgba(255,255,255,.3);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.2s;
}

.lang-switch:hover {
  background: rgba(255,255,255,.1);
  color: #fff;
  border-color: rgba(255,255,255,.6);
}

.nav-cta {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 18px;
  color: #fff;
  background: var(--orange);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 700;
  transition: background 0.2s, transform 0.2s;
}

.nav-cta:hover {
  background: #c85d2e;
  transform: translateY(-1px);
}

.menu-button {
  display: none;
  padding: 8px;
  color: #fff;
  background: transparent;
  border: 0;
  font-size: 20px;
}

.main-body {
  flex: 1;
}

/* 浮动咨询悬浮丸 */
.consult-float-pill {
  position: fixed;
  right: 24px;
  bottom: 28px;
  z-index: 95;
  background: var(--orange);
  color: #fff;
  padding: 12px 20px;
  border-radius: 30px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  box-shadow: 0 10px 25px rgba(215, 110, 57, 0.4);
  font-weight: 700;
  font-size: 14px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.consult-float-pill:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 30px rgba(215, 110, 57, 0.5);
}

/* 咨询弹窗抽屉 */
.consult-drawer-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(7, 31, 38, 0.7);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
  animation: fadeIn 0.2s ease-out;
}

.consult-drawer {
  background: var(--surface);
  width: min(100%, 460px);
  height: 100%;
  padding: 28px 24px;
  overflow-y: auto;
  box-shadow: -10px 0 40px rgba(0,0,0,0.3);
  display: flex;
  flex-direction: column;
  animation: slideIn 0.25s ease-out;
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.drawer-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--line);
  padding-bottom: 16px;
}

.drawer-head h3 {
  font-family: var(--serif);
  font-size: 20px;
  color: var(--teal-deep);
  margin: 0;
}

.drawer-head p {
  color: var(--muted);
  font-size: 13px;
  margin-top: 4px;
}

.close-x {
  background: transparent;
  border: 1px solid var(--line);
  border-radius: 6px;
  width: 32px;
  height: 32px;
  font-size: 20px;
  color: var(--muted);
}

.close-x:hover {
  color: var(--ink);
  background: #f4eee4;
}

.wechat-mini-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px;
  background: #f4eee4;
  border: 1px solid #e1d8c9;
  border-radius: 8px;
  margin-bottom: 20px;
}

.drawer-qr {
  width: 60px;
  height: 60px;
  border-radius: 6px;
  background: #fff;
  padding: 4px;
  border: 1px solid var(--line);
}

.wechat-mini-card strong {
  display: block;
  font-size: 14px;
  color: var(--teal-deep);
}

.wechat-mini-card p {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--muted);
}

.drawer-fields {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.field-item label {
  display: block;
  font-size: 12px;
  font-weight: 700;
  color: var(--muted);
  margin-bottom: 5px;
}

.field-item input,
.field-item select,
.field-item textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 6px;
  font-size: 14px;
  color: var(--ink);
  background: #fff;
  outline: none;
}

.field-item input:focus,
.field-item select:focus,
.field-item textarea:focus {
  border-color: var(--teal);
  box-shadow: 0 0 0 3px rgba(13, 108, 107, 0.12);
}

.drawer-consent {
  display: flex;
  gap: 8px;
  font-size: 12px;
  color: var(--muted);
  line-height: 1.5;
  margin-top: 6px;
}

.drawer-consent input {
  margin-top: 2px;
}

.drawer-submit-btn {
  background: var(--orange);
  color: #fff;
  border: none;
  padding: 12px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 14px;
  margin-top: 10px;
  transition: background 0.2s;
}

.drawer-submit-btn:hover {
  background: #c85d2e;
}

/* 全局 Toast */
.page-toast {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 1100;
  width: min(calc(100% - 48px), 420px);
  padding: 14px 18px;
  color: var(--teal-deep);
  background: #deefea;
  border: 1px solid #b9d8d0;
  border-radius: 8px;
  box-shadow: 0 14px 34px rgba(20, 33, 44, .16);
  font-size: 13px;
  opacity: 0;
  pointer-events: none;
  transform: translateY(12px);
  transition: opacity .25s ease, transform .25s ease;
}

.page-toast.is-visible {
  opacity: 1;
  transform: translateY(0);
}

/* 页脚 Footer */
.site-footer {
  padding: 50px 0 30px;
  color: rgba(255, 255, 255, 0.72);
  background: #15232d;
  margin-top: auto;
}

.footer-grid {
  display: grid;
  grid-template-columns: 1.3fr 1fr 1fr;
  gap: 40px;
}

.footer-brand {
  color: #fff;
  font-weight: 700;
  font-size: 17px;
  font-family: var(--serif);
}

.footer-brand small {
  display: block;
  margin-top: 10px;
  color: rgba(255, 255, 255, 0.55);
  font-size: 12px;
  font-weight: 400;
  line-height: 1.6;
  font-family: var(--sans);
}

.footer-col h4 {
  margin: 0 0 14px;
  color: #fff;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.footer-col a {
  display: block;
  margin-top: 9px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
  transition: color 0.2s;
  cursor: pointer;
}

.footer-col a:hover {
  color: #fff;
}

.footer-meta {
  margin-top: 36px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  font-size: 12px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.5);
}

@media (max-width: 880px) {
  .nav-links {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #084d50;
    flex-direction: column;
    padding: 20px;
    border-bottom: 1px solid rgba(255,255,255,0.15);
  }
  .nav-links.mobile-open {
    display: flex;
  }
  .menu-button {
    display: inline-flex;
  }
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 28px;
  }
}
</style>
