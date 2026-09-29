<template>
  <div class="site-shell" :class="{ 'is-rtl': currentLangCode === 'ar' }">
    <!-- 智能地理位置与多语言导流横幅（非侵入式，爬虫自动忽略） -->
    <GeoSmartBanner />

    <header class="site-header" :class="{ 'is-scrolled': isScrolled || !isHomePage }">
      <div class="wrap nav">
        <NuxtLink :to="homePath" class="brand" aria-label="Shenyuan International 首页">
          <span class="brand-mark">深</span>
          <span class="brand-text">
            <span>Shenyuan International</span>
            <small>{{ i18n.brandSub }}</small>
          </span>
        </NuxtLink>

        <nav class="nav-links" :class="{ 'mobile-open': mobileMenuOpen }">
          <a @click.prevent="navigateSection('services')" href="#services">
            {{ i18n.services }}
          </a>
          <a @click.prevent="navigateSection('cases')" href="#cases">
            {{ i18n.cases }}
          </a>
          <a @click.prevent="navigateSection('global')" href="#global">
            {{ i18n.global }}
          </a>
          <a @click.prevent="navigateSection('team')" href="#team">
            {{ i18n.team }}
          </a>
          <a @click.prevent="navigateSection('faq')" href="#faq">
            {{ i18n.faq }}
          </a>
          <NuxtLink :to="articlesPath">
            {{ i18n.articles }}
          </NuxtLink>
        </nav>

        <div class="nav-actions">
          <!-- 升级为多语言下拉菜单 (中 / EN / AR / ES) -->
          <div class="header-lang-dropdown" ref="langDropdownRef">
            <button
              class="lang-switch-btn"
              type="button"
              @click="langMenuOpen = !langMenuOpen"
              :aria-expanded="langMenuOpen"
              aria-label="选择语言"
            >
              <span class="lang-globe-icon">🌐</span>
              <span class="current-lang-text">{{ currentLangLabel }}</span>
              <svg class="dropdown-caret" viewBox="0 0 20 20" fill="currentColor" width="10" height="10">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>

            <div v-if="langMenuOpen" class="lang-dropdown-menu">
              <button
                type="button"
                class="lang-option"
                :class="{ 'is-active': currentLangCode === 'zh' }"
                @click="switchLanguage('zh')"
              >
                <span class="opt-flag">🇨🇳</span>
                <span class="opt-label">简体中文</span>
              </button>
              <button
                type="button"
                class="lang-option"
                :class="{ 'is-active': currentLangCode === 'en' }"
                @click="switchLanguage('en')"
              >
                <span class="opt-flag">🇺🇸</span>
                <span class="opt-label">English</span>
              </button>
              <button
                type="button"
                class="lang-option"
                :class="{ 'is-active': currentLangCode === 'ar' }"
                @click="switchLanguage('ar')"
              >
                <span class="opt-flag">🇦🇪</span>
                <span class="opt-label">العربية (RTL)</span>
              </button>
              <button
                type="button"
                class="lang-option"
                :class="{ 'is-active': currentLangCode === 'es' }"
                @click="switchLanguage('es')"
              >
                <span class="opt-flag">🇪🇸</span>
                <span class="opt-label">Español</span>
              </button>
            </div>
          </div>

          <a class="nav-cta" @click.prevent="navigateSection('intake')" href="#intake">
            {{ i18n.cta }}
          </a>
          <button class="menu-button" type="button" @click="mobileMenuOpen = !mobileMenuOpen" aria-label="打开菜单">
            {{ mobileMenuOpen ? '✕' : '☰' }}
          </button>
        </div>
      </div>
    </header>

    <main class="main-body">
      <NuxtPage />
    </main>

    <!-- 浮动咨询快捷按钮 -->
    <div class="consult-float-pill" @click="openQuickConsult" title="免费咨询">
      <span class="pill-icon">💬</span>
      <span class="pill-text">{{ i18n.quickConsult }}</span>
    </div>

    <!-- 浮动侧边/弹窗咨询抽屉 (在非主页或点击悬浮按钮时使用) -->
    <div v-if="drawerOpen" class="consult-drawer-backdrop" @click.self="drawerOpen = false">
      <div class="consult-drawer" :class="{ 'is-rtl': currentLangCode === 'ar' }">
        <div class="drawer-head">
          <div>
            <h3>{{ i18n.drawerTitle }}</h3>
            <p>{{ i18n.drawerSub }}</p>
          </div>
          <button class="close-x" @click="drawerOpen = false">×</button>
        </div>

        <div class="wechat-mini-card">
          <img src="/wechat-qrcode.png" alt="WeChat QR" class="drawer-qr" />
          <div>
            <strong>{{ i18n.wechatTitle }}</strong>
            <p>{{ i18n.wechatDesc }}</p>
          </div>
        </div>

        <form @submit.prevent="submitDrawerForm" class="drawer-fields">
          <div class="field-item">
            <label>{{ i18n.formName }}</label>
            <input v-model="drawerForm.name" required :placeholder="i18n.formNamePlaceholder" />
          </div>
          <div class="field-item">
            <label>{{ i18n.formPhone }}</label>
            <div class="phone-input-row">
              <CountryDialSelect
                v-model="drawerCountryDial"
                :is-en="currentLangCode !== 'zh'"
              />
              <input
                v-model="drawerForm.phone"
                type="tel"
                required
                :placeholder="i18n.formPhonePlaceholder"
              />
            </div>
          </div>
          <div class="field-item">
            <label>{{ i18n.formEmail }}</label>
            <input v-model="drawerForm.email" type="email" :placeholder="i18n.formEmailPlaceholder" />
          </div>
          <div class="field-item">
            <label>{{ i18n.formMatter }}</label>
            <select v-model="drawerForm.matter" required>
              <option value="国际贸易争议">{{ currentLangCode === 'en' ? 'International Trade Dispute' : (currentLangCode === 'ar' ? 'نزاع التجارة الدولية' : (currentLangCode === 'es' ? 'Disputa de Comercio Internacional' : '国际贸易争议')) }}</option>
              <option value="诉讼与债务追收">{{ currentLangCode === 'en' ? 'Litigation & Debt Recovery' : (currentLangCode === 'ar' ? 'التقاضي وتحصيل الديون' : (currentLangCode === 'es' ? 'Litigio y Recuperación de Créditos' : '诉讼与债务追收')) }}</option>
              <option value="继承与家族资产纠纷">{{ currentLangCode === 'en' ? 'Inheritance & Family Assets' : (currentLangCode === 'ar' ? 'الميراث والأصول العائلية' : (currentLangCode === 'es' ? 'Herencia y Patrimonio Familiar' : '继承与家族资产纠纷')) }}</option>
              <option value="不确定，希望先沟通">{{ currentLangCode === 'en' ? 'Not Sure / Needs Consultation' : (currentLangCode === 'ar' ? 'غير متأكد، أرغب في الاستشارة أولاً' : (currentLangCode === 'es' ? 'No estoy seguro, deseo consultar primero' : '不确定，希望先沟通')) }}</option>
            </select>
          </div>
          <div class="field-item">
            <label>{{ i18n.formSummary }}</label>
            <textarea v-model="drawerForm.summary" rows="3" required :placeholder="i18n.formSummaryPlaceholder"></textarea>
          </div>
          <label class="drawer-consent">
            <input type="checkbox" v-model="drawerForm.consent" required />
            <span>{{ i18n.formConsent }}</span>
          </label>
          <button type="submit" class="drawer-submit-btn" :disabled="drawerSubmitting">
            {{ drawerSubmitting ? i18n.formSubmitting : i18n.formSubmit }}
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
            <small>{{ i18n.footerDesc }}</small>
          </div>
          <div class="footer-col">
            <h4>{{ i18n.services }}</h4>
            <a @click.prevent="navigateSection('services')" href="#services">{{ currentLangCode === 'en' ? 'International Trade Disputes' : (currentLangCode === 'ar' ? 'نزاعات التجارة الدولية' : (currentLangCode === 'es' ? 'Disputas Comerciales Internacionales' : '国际贸易争议')) }}</a>
            <a @click.prevent="navigateSection('services')" href="#services">{{ currentLangCode === 'en' ? 'Litigation & Debt Recovery' : (currentLangCode === 'ar' ? 'التقاضي وتحصيل الديون' : (currentLangCode === 'es' ? 'Litigios y Cobro de Deudas' : '诉讼与债务追收')) }}</a>
            <a @click.prevent="navigateSection('services')" href="#services">{{ currentLangCode === 'en' ? 'Inheritance & Family Assets' : (currentLangCode === 'ar' ? 'الميراث والأصول العائلية' : (currentLangCode === 'es' ? 'Herencias y Patrimonio Familiar' : '继承与家族资产纠纷')) }}</a>
          </div>
          <div class="footer-col">
            <h4>{{ currentLangCode === 'en' ? 'Quick Links' : (currentLangCode === 'ar' ? 'روابط سريعة' : (currentLangCode === 'es' ? 'Enlaces Rápidos' : '快速入口')) }}</h4>
            <a @click.prevent="navigateSection('intake')" href="#intake">{{ i18n.quickConsult }}</a>
            <NuxtLink :to="articlesPath">{{ i18n.articles }}</NuxtLink>
            <a @click.prevent="navigateSection('global')" href="#global">{{ i18n.global }}</a>
            <a @click.prevent="navigateSection('team')" href="#team">{{ i18n.team }}</a>
            <a @click.prevent="navigateSection('faq')" href="#faq">{{ i18n.faq }}</a>
          </div>
        </div>
        <div class="footer-meta">
          © 2026 Shenyuan International · 深远(国际)律师事务所<br>
          <span>{{ currentLangCode === 'en'
            ? 'This website provides general information only and does not constitute formal legal advice. Foreign legal proceedings are conducted through locally licensed counsel.'
            : (currentLangCode === 'ar'
              ? 'محتويات هذا الموقع للأغراض الإعلامية العامة فقط ولا تشكل استشارة قانونية رسمية. يتم تقديم الإجراءات القضائية في الخارج من خلال مكاتب المحاماة المرخصة محلياً.'
              : (currentLangCode === 'es'
                ? 'El contenido de este sitio web es solo para fines informativos y no constituye asesoramiento legal formal. Los procedimientos judiciales en el extranjero se llevan a cabo a través de firmas locales asociadas.'
                : '本网站内容仅供一般信息参考，不构成正式法律意见。境外法律程序通过与当地执业律所合作提供。')) }}</span>
        </div>
      </div>
    </footer>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getApiClient, parseApiError } from '@/api/client'
import { useUserGeo } from '@/composables/useUserGeo'
import { I18N_DICT, type SupportedLang } from '@/composables/useI18nDict'

const route = useRoute()
const router = useRouter()

// 语言检测
const currentLangCode = computed<SupportedLang>(() => {
  if (route.path.startsWith('/ar')) return 'ar'
  if (route.path.startsWith('/es')) return 'es'
  if (route.path.startsWith('/en')) return 'en'
  return 'zh'
})

// 多语言当前字典
const i18n = computed(() => I18N_DICT[currentLangCode.value] || I18N_DICT.zh)

// 首页与文章链接动态计算
const homePath = computed(() => {
  if (currentLangCode.value === 'ar') return '/ar'
  if (currentLangCode.value === 'es') return '/es'
  if (currentLangCode.value === 'en') return '/en'
  return '/'
})

const articlesPath = computed(() => {
  if (currentLangCode.value === 'ar') return '/ar/articles'
  if (currentLangCode.value === 'es') return '/es/articles'
  if (currentLangCode.value === 'en') return '/en/articles'
  return '/articles'
})

const isHomePage = computed(() => {
  const p = route.path
  return p === '/' || p === '/en' || p === '/ar' || p === '/es'
})

const isEn = computed(() => currentLangCode.value === 'en')

const { countryInfo } = useUserGeo()

// 语言切换下拉状态
const langMenuOpen = ref(false)
const langDropdownRef = ref<HTMLElement | null>(null)

const currentLangLabel = computed(() => {
  switch (currentLangCode.value) {
    case 'ar': return 'العربية'
    case 'es': return 'Español'
    case 'en': return 'EN'
    default: return '中文'
  }
})

/**
 * 健壮的跨语种路由跳转解析器，彻底杜绝 404
 */
const switchLanguage = (targetLang: SupportedLang) => {
  langMenuOpen.value = false
  if (targetLang === currentLangCode.value) return

  const curPath = route.path
  // 1. 去除当前语言前缀得到干净的根路由
  let basePath = curPath.replace(/^\/(en|ar|es)(\/|$)/, '/')
  if (!basePath.startsWith('/')) basePath = '/' + basePath

  // 2. 根据目标语言进行精准无缝路由跳转
  if (targetLang === 'zh') {
    router.push(basePath)
    return
  }

  const next = basePath === '/' ? `/${targetLang}` : `/${targetLang}${basePath}`
  router.push(next)
}

// 抽屉国家区号，默认跟随 IP 侦测
const drawerCountryDial = ref(countryInfo.value?.dialCode || '+86')
watch(
  () => countryInfo.value?.dialCode,
  (code) => {
    if (code && !drawerCountryDial.value) {
      drawerCountryDial.value = code
    }
  }
)

// 全局监听点击外部关闭语言下拉
const handleLangDropdownClick = (e: MouseEvent) => {
  if (langDropdownRef.value && !langDropdownRef.value.contains(e.target as Node)) {
    langMenuOpen.value = false
  }
}

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
  document.addEventListener('click', handleLangDropdownClick)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  document.removeEventListener('click', handleLangDropdownClick)
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
    let normalizedPhone = drawerForm.value.phone.trim()
    const activeDial = drawerCountryDial.value || countryInfo.value?.dialCode || '+86'
    if (!normalizedPhone.startsWith('+')) {
      normalizedPhone = `${activeDial} ${normalizedPhone}`
    }

    const geoMeta = countryInfo.value && countryInfo.value.code !== 'CN'
      ? ` [访客法域: ${countryInfo.value.nameZh} (${countryInfo.value.code})]`
      : ''

    await getApiClient().post('/api/intakes', {
      name: drawerForm.value.name,
      phone: normalizedPhone,
      email: drawerForm.value.email || undefined,
      matter: drawerForm.value.matter,
      summary: `${drawerForm.value.summary}${geoMeta}`,
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
  transition: background 0.25s ease, box-shadow 0.25s ease, min-height 0.25s ease;
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
  gap: 20px;
  min-height: 58px; /* 从 80px 极致压缩至 58px，释出垂直高度 */
  padding: 4px 0;
}

.site-header.is-scrolled .nav {
  min-height: 52px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: .05em;
  color: #fff;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  color: var(--teal-deep);
  background: #f7f2e9;
  border-radius: 6px;
  font-family: var(--serif);
  font-size: 17px;
  font-weight: 700;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}

.brand-text { display: grid; gap: 1px; }
.brand-text span { font-weight: 700; font-size: 14px; line-height: 1.15; }
.brand-text small { color: rgba(255,255,255,.72); font-size: 10px; font-weight: 500; }

.nav-links {
  display: flex;
  align-items: center;
  gap: 20px;
  font-size: 13.5px;
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
  gap: 10px;
}

/* 多语言下拉组件样式 */
.header-lang-dropdown {
  position: relative;
}

.lang-switch-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 11px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.lang-switch-btn:hover {
  background: rgba(255, 255, 255, 0.16);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.5);
}

.lang-globe-icon {
  font-size: 12px;
  line-height: 1;
}

.current-lang-text {
  font-size: 12px;
}

.dropdown-caret {
  opacity: 0.7;
}

.lang-dropdown-menu {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  width: 150px;
  background: #0b3438;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35);
  padding: 4px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  z-index: 1000;
}

.lang-option {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 7px 10px;
  border: none;
  background: transparent;
  color: #e2e8f0;
  font-size: 12.5px;
  text-align: left;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.lang-option:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.lang-option.is-active {
  background: rgba(241, 182, 143, 0.2);
  color: #f1b68f;
  font-weight: 600;
}

.opt-flag {
  font-size: 14px;
  line-height: 1;
}

.opt-label {
  flex: 1;
}

.nav-cta {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 15px;
  color: #fff;
  background: var(--orange);
  border-radius: 6px;
  font-size: 12.5px;
  font-weight: 700;
  transition: background 0.2s, transform 0.2s;
  white-space: nowrap;
}

.nav-cta:hover {
  background: #c85d2e;
  transform: translateY(-1px);
}

.menu-button {
  display: none;
  padding: 6px;
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

.phone-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.country-dial-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 10px 10px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--teal-deep);
  white-space: nowrap;
  user-select: none;
  flex-shrink: 0;
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
  .nav {
    min-height: 52px;
    gap: 12px;
  }
  .site-header.is-scrolled .nav {
    min-height: 48px;
  }
  .brand-text span {
    font-size: 13px;
  }
  .brand-text small {
    display: none; /* 移动端隐藏小副标，保持高度精致 */
  }
  .brand-mark {
    width: 28px;
    height: 28px;
    font-size: 15px;
  }
  .nav-cta {
    padding: 6px 10px;
    font-size: 11.5px;
  }
  .lang-switch-btn {
    padding: 4px 8px;
    font-size: 11px;
  }
  .current-lang-text {
    font-size: 11px;
  }
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
