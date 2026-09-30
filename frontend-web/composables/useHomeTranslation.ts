import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { HOME_I18N, type HomeTranslation } from '@/composables/useHomeI18n'
import type { SupportedLang } from '@/composables/useI18nDict'
import { useCurrentLang } from '@/composables/useCurrentLang'

export function useHomeTranslation() {
  const { currentLang, isAr, isEs, isEn } = useCurrentLang()

  const t = computed<HomeTranslation>(() => {
    return HOME_I18N[currentLang.value] || HOME_I18N.zh
  })

  return {
    currentLang,
    isAr,
    isEs,
    isEn,
    t,
  }
}
