import { computed } from 'vue'
import type { SupportedLang } from '@/composables/useI18nDict'

/**
 * 从 URL path 中精准识别语言前缀，必须是独立段（/ar, /ar/xxx, /es, /es/xxx, /en, /en/xxx）。
 * 严禁使用 startsWith('/ar')，否则会导致 /articles 等中文路由被误判为阿拉伯语 (/ar)！
 */
export function getLangFromPath(path: string): SupportedLang {
  if (/^\/ar($|\/)/.test(path)) return 'ar'
  if (/^\/es($|\/)/.test(path)) return 'es'
  if (/^\/en($|\/)/.test(path)) return 'en'
  return 'zh'
}

export function useCurrentLang() {
  const route = useRoute()
  const currentLang = computed<SupportedLang>(() => getLangFromPath(route.path))
  const isAr = computed(() => currentLang.value === 'ar')
  const isEs = computed(() => currentLang.value === 'es')
  const isEn = computed(() => currentLang.value === 'en')
  return {
    route,
    currentLang,
    isAr,
    isEs,
    isEn,
  }
}
