import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { HOME_I18N, type HomeTranslation } from '@/composables/useHomeI18n'
import type { SupportedLang } from '@/composables/useI18nDict'

export function useHomeTranslation() {
  const route = useRoute()

  const currentLang = computed<SupportedLang>(() => {
    if (route.path.startsWith('/ar')) return 'ar'
    if (route.path.startsWith('/es')) return 'es'
    if (route.path.startsWith('/en')) return 'en'
    return 'zh'
  })

  const t = computed<HomeTranslation>(() => {
    return HOME_I18N[currentLang.value] || HOME_I18N.zh
  })

  return {
    currentLang,
    isAr: computed(() => currentLang.value === 'ar'),
    isEs: computed(() => currentLang.value === 'es'),
    isEn: computed(() => currentLang.value === 'en'),
    t,
  }
}
