<template>
  <div class="error-page" :class="{ 'is-rtl': isAr }">
    <div class="wrap">
      <div class="code">{{ error?.statusCode || 500 }}</div>
      <h1>{{ heading }}</h1>
      <p>{{ message }}</p>
      <div class="actions">
        <NuxtLink :to="homePath" class="button button-primary">
          {{ isEn ? 'Back to homepage' : (isAr ? 'العودة إلى الصفحة الرئيسية' : (isEs ? 'Volver al inicio' : '返回首页')) }}
        </NuxtLink>
        <NuxtLink :to="servicesPath" class="button button-outline">
          {{ isEn ? 'View practice areas' : (isAr ? 'عرض مجالات الممارسة' : (isEs ? 'Ver áreas de práctica' : '查看服务范围')) }}
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ error: { statusCode?: number; statusMessage?: string; message?: string } }>()

const route = useRoute()
const currentLang = computed<'zh' | 'en' | 'ar' | 'es'>(() => {
  if (route.path.startsWith('/ar')) return 'ar'
  if (route.path.startsWith('/es')) return 'es'
  if (route.path.startsWith('/en')) return 'en'
  return 'zh'
})
const isAr = computed(() => currentLang.value === 'ar')
const isEs = computed(() => currentLang.value === 'es')
const isEn = computed(() => currentLang.value === 'en')

const homePath = computed(() => {
  if (isAr.value) return '/ar'
  if (isEs.value) return '/es'
  if (isEn.value) return '/en'
  return '/'
})

const servicesPath = computed(() => {
  if (isAr.value) return '/ar/services'
  if (isEs.value) return '/es/services'
  if (isEn.value) return '/en/services'
  return '/services'
})

const heading = computed(() => {
  if (props.error?.statusCode === 404) {
    if (isAr.value) return 'الصفحة غير موجودة'
    if (isEs.value) return 'Página no encontrada'
    if (isEn.value) return 'Page not found'
    return '页面未找到'
  }
  if (isAr.value) return 'حدث خطأ غير متوقع'
  if (isEs.value) return 'Se produjo un error inesperado'
  if (isEn.value) return 'Something went wrong'
  return '页面出现异常'
})

const message = computed(() => {
  if (props.error?.statusCode === 404) {
    if (isAr.value) return 'الصفحة التي طلبتها غير متوفرة أو تم نقلها. يمكنك تصفح مجالات الممارسة أو المقالات القانونية.'
    if (isEs.value) return 'La página que solicitó no existe o ha sido movida. Puede consultar nuestras áreas de práctica o los artículos legales.'
    if (isEn.value) return 'The page you requested does not exist or has been moved. Try the practice areas or the legal insights index.'
    return '您访问的页面不存在或已被移动。您可以查看服务范围或法律专栏。'
  }
  if (isAr.value) return 'حدث خطأ غير متوقع أثناء معالجة الطلب. يرجى المحاولة مرة أخرى أو الاتصال بنا.'
  if (isEs.value) return 'Ocurrió un error inesperado. Por favor intente nuevamente o contáctenos.'
  if (isEn.value) return 'An unexpected error occurred. Please try again, or contact us if the problem persists.'
  return '页面发生意外错误，请重试；若问题持续，请联系我们。'
})

useHead({
  title: () => `${heading.value} | ${isEn.value ? 'Shenyuan International' : (isAr.value ? 'مكتب شينيوان الدولي' : (isEs.value ? 'Shenyuan International' : '深远(国际)律师事务所'))}`,
  meta: [{ name: 'robots', content: 'noindex, follow' }],
})
</script>

<style scoped>
.error-page {
  min-height: 70vh;
  display: flex;
  align-items: center;
  padding: 160px 0 120px;
  background: var(--paper);
  color: var(--ink);
}

/* RTL 镜像适配 */
.error-page.is-rtl {
  direction: rtl;
  text-align: right;
}

.code {
  font-family: var(--serif);
  font-size: 72px;
  line-height: 1;
  color: var(--gold);
  margin-bottom: 12px;
}

.error-page h1 {
  font-family: var(--serif);
  font-size: clamp(28px, 3.4vw, 40px);
  color: var(--teal-deep);
  margin: 0 0 14px;
}

.error-page p {
  max-width: 620px;
  color: var(--muted);
  font-size: 16px;
  line-height: 1.7;
  margin: 0 0 28px;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  min-height: 46px;
  padding: 0 20px;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 700;
  transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease;
}

.button:hover { transform: translateY(-2px); }
.button-primary { color: #fff; background: var(--orange); }
.button-primary:hover { background: #c85d2e; }
.button-outline {
  color: var(--teal-deep);
  background: transparent;
  border-color: var(--line);
}
.button-outline:hover { background: var(--cream); }
</style>
