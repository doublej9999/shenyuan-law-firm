import { ref, computed } from 'vue'

export interface GeoCountryMeta {
  code: string
  nameZh: string
  nameEn: string
  flag: string
  dialCode: string
  jurisdictionSlug?: string
  isChineseRegion?: boolean
}

export const GEO_COUNTRY_MAP: Record<string, GeoCountryMeta> = {
  CN: { code: 'CN', nameZh: '中国大陆', nameEn: 'China', flag: '🇨🇳', dialCode: '+86', isChineseRegion: true },
  HK: { code: 'HK', nameZh: '中国香港', nameEn: 'Hong Kong', flag: '🇭🇰', dialCode: '+852', jurisdictionSlug: 'hong-kong', isChineseRegion: true },
  MO: { code: 'MO', nameZh: '中国澳门', nameEn: 'Macau', flag: '🇲🇴', dialCode: '+853', isChineseRegion: true },
  TW: { code: 'TW', nameZh: '中国台湾', nameEn: 'Taiwan', flag: '🇹🇼', dialCode: '+886', isChineseRegion: true },
  SG: { code: 'SG', nameZh: '新加坡', nameEn: 'Singapore', flag: '🇸🇬', dialCode: '+65', jurisdictionSlug: 'singapore' },
  US: { code: 'US', nameZh: '美国', nameEn: 'United States', flag: '🇺🇸', dialCode: '+1', jurisdictionSlug: 'united-states' },
  GB: { code: 'GB', nameZh: '英国', nameEn: 'United Kingdom', flag: '🇬🇧', dialCode: '+44', jurisdictionSlug: 'united-kingdom' },
  AU: { code: 'AU', nameZh: '澳大利亚', nameEn: 'Australia', flag: '🇦🇺', dialCode: '+61', jurisdictionSlug: 'australia' },
  CA: { code: 'CA', nameZh: '加拿大', nameEn: 'Canada', flag: '🇨🇦', dialCode: '+1', jurisdictionSlug: 'canada' },
  AE: { code: 'AE', nameZh: '阿联酋', nameEn: 'UAE', flag: '🇦🇪', dialCode: '+971', jurisdictionSlug: 'united-arab-emirates' },
  DE: { code: 'DE', nameZh: '德国', nameEn: 'Germany', flag: '🇩🇪', dialCode: '+49', jurisdictionSlug: 'germany' },
  JP: { code: 'JP', nameZh: '日本', nameEn: 'Japan', flag: '🇯🇵', dialCode: '+81', jurisdictionSlug: 'japan' },
  NZ: { code: 'NZ', nameZh: '新西兰', nameEn: 'New Zealand', flag: '🇳🇿', dialCode: '+64', jurisdictionSlug: 'new-zealand' },
  MY: { code: 'MY', nameZh: '马来西亚', nameEn: 'Malaysia', flag: '🇲🇾', dialCode: '+60', jurisdictionSlug: 'malaysia' },
  FR: { code: 'FR', nameZh: '法国', nameEn: 'France', flag: '🇫🇷', dialCode: '+33', jurisdictionSlug: 'france' },
  CH: { code: 'CH', nameZh: '瑞士', nameEn: 'Switzerland', flag: '🇨🇭', dialCode: '+41', jurisdictionSlug: 'switzerland' },
  KR: { code: 'KR', nameZh: '韩国', nameEn: 'South Korea', flag: '🇰🇷', dialCode: '+82', jurisdictionSlug: 'south-korea' },
  TH: { code: 'TH', nameZh: '泰国', nameEn: 'Thailand', flag: '🇹🇭', dialCode: '+66', jurisdictionSlug: 'thailand' },
  VN: { code: 'VN', nameZh: '越南', nameEn: 'Vietnam', flag: '🇻🇳', dialCode: '+84', jurisdictionSlug: 'vietnam' },
  NL: { code: 'NL', nameZh: '荷兰', nameEn: 'Netherlands', flag: '🇳🇱', dialCode: '+31', jurisdictionSlug: 'netherlands' },
  IT: { code: 'IT', nameZh: '意大利', nameEn: 'Italy', flag: '🇮🇹', dialCode: '+39', jurisdictionSlug: 'italy' },
  ES: { code: 'ES', nameZh: '西班牙', nameEn: 'Spain', flag: '🇪🇸', dialCode: '+34', jurisdictionSlug: 'spain' },
  BR: { code: 'BR', nameZh: '巴西', nameEn: 'Brazil', flag: '🇧🇷', dialCode: '+55', jurisdictionSlug: 'brazil' },
  IN: { code: 'IN', nameZh: '印度', nameEn: 'India', flag: '🇮🇳', dialCode: '+91', jurisdictionSlug: 'india' },
  IE: { code: 'IE', nameZh: '爱尔兰', nameEn: 'Ireland', flag: '🇮🇪', dialCode: '+353', jurisdictionSlug: 'ireland' },
  SA: { code: 'SA', nameZh: '沙特阿拉伯', nameEn: 'Saudi Arabia', flag: '🇸🇦', dialCode: '+966' },
  ID: { code: 'ID', nameZh: '印度尼西亚', nameEn: 'Indonesia', flag: '🇮🇩', dialCode: '+62' },
  PH: { code: 'PH', nameZh: '菲律宾', nameEn: 'Philippines', flag: '🇵🇭', dialCode: '+63' },
  MX: { code: 'MX', nameZh: '墨西哥', nameEn: 'Mexico', flag: '🇲🇽', dialCode: '+52' },
  RU: { code: 'RU', nameZh: '俄罗斯', nameEn: 'Russia', flag: '🇷🇺', dialCode: '+7' },
}

export function useUserGeo() {
  const route = useRoute()
  const isEn = computed(() => route.path.startsWith('/en'))

  // 跨 SSR/客户端持久化状态
  const userGeo = useState<{ country: string; isBot: boolean }>('user-geo-state', () => {
    let country = 'CN'
    let isBot = false

    if (import.meta.server) {
      const headers = useRequestHeaders([
        'x-vercel-ip-country',
        'cf-ipcountry',
        'user-agent',
      ])
      const headerCountry = (headers['x-vercel-ip-country'] || headers['cf-ipcountry'] || '').trim().toUpperCase()
      if (headerCountry) {
        country = headerCountry
      }
      const ua = headers['user-agent'] || ''
      isBot = /googlebot|bingbot|baiduspider|yandex|duckduckbot|slurp|twitterbot|facebookexternalhit|ahrefsbot|semrushbot/i.test(ua)
    }

    return { country, isBot }
  })

  // Cookie 记忆：关闭横幅后 30 天内不再弹出
  const dismissedCookie = useCookie<boolean | string>('shenyuan_geo_dismissed', {
    maxAge: 60 * 60 * 24 * 30, // 30 days
    sameSite: 'lax',
  })

  const isDismissed = computed(() => Boolean(dismissedCookie.value))

  const countryInfo = computed<GeoCountryMeta>(() => {
    const code = userGeo.value.country || 'CN'
    if (GEO_COUNTRY_MAP[code]) {
      return GEO_COUNTRY_MAP[code]
    }
    // 未知国家兜底
    return {
      code,
      nameZh: code,
      nameEn: code,
      flag: '🌐',
      dialCode: '+86',
      isChineseRegion: false,
    }
  })

  // 当前用户所在法域的落地页链接（若有）
  const targetJurisdictionUrl = computed(() => {
    const slug = countryInfo.value.jurisdictionSlug
    if (!slug) return null
    return isEn.value ? `/en/countries/${slug}` : `/countries/${slug}`
  })

  // 检查是否已经在当前检测到的法域详情页
  const isAlreadyOnTargetJurisdictionPage = computed(() => {
    const slug = countryInfo.value.jurisdictionSlug
    if (!slug) return false
    return route.path.includes(`/countries/${slug}`)
  })

  // 计算推荐横幅应显示的内容
  const smartRecommendation = computed(() => {
    // 爬虫或用户已关闭则不显示
    if (userGeo.value.isBot || isDismissed.value) {
      return null
    }

    const { code, nameZh, nameEn, flag, isChineseRegion, jurisdictionSlug } = countryInfo.value

    // 1. 如果用户在中国大陆 (CN)，默认属于本国母体，不强弹切换横幅
    if (code === 'CN') {
      return null
    }

    // 2. 如果当前在英文版面，但用户来自中国、港澳台地区 (CN/HK/MO/TW)
    if (isEn.value && isChineseRegion) {
      return {
        type: 'switch-lang' as const,
        flag,
        text: `Visiting from ${nameEn}? We offer comprehensive Chinese language services.`,
        actionLabel: '切换至中文版',
        actionUrl: route.path.replace(/^\/en/, '') || '/',
      }
    }

    // 3. 如果当前在中文版面，但用户来自海外非中文地区（如 US, GB, AU, AE, DE 等）
    if (!isEn.value && !isChineseRegion) {
      // 若该国家对应我们专属的 22 个法域之一，且当前不在该法域页
      if (jurisdictionSlug && !isAlreadyOnTargetJurisdictionPage.value) {
        return {
          type: 'jurisdiction-guide' as const,
          flag,
          text: `检测到您来自${nameZh}。深远涉外团队提供${nameZh}诉讼清收、合规与双语服务。`,
          actionLabel: `查看${nameZh}指引 →`,
          actionUrl: `/countries/${jurisdictionSlug}`,
          langSwitchLabel: 'English',
          langSwitchUrl: `/en${route.path === '/' ? '' : route.path}`,
        }
      }

      // 非专属法域但属于海外国家，提示可切换至 English
      return {
        type: 'switch-lang' as const,
        flag,
        text: `Welcome from ${nameEn}! Browse our cross-border dispute resolution services in English.`,
        actionLabel: 'Switch to English',
        actionUrl: `/en${route.path === '/' ? '' : route.path}`,
      }
    }

    // 4. 如果当前在英文版面，用户来自具有专属法域的国家（如 SG, AE, US 等），且不在该法域页
    if (isEn.value && jurisdictionSlug && !isAlreadyOnTargetJurisdictionPage.value) {
      return {
        type: 'jurisdiction-guide' as const,
        flag,
        text: `Visiting from ${nameEn}? Explore our local ${nameEn} cross-border legal solutions.`,
        actionLabel: `View ${nameEn} Guide →`,
        actionUrl: `/en/countries/${jurisdictionSlug}`,
      }
    }

    return null
  })

  // 用户主动关闭横幅
  const dismissBanner = () => {
    dismissedCookie.value = 'true'
  }

  return {
    userGeo,
    countryInfo,
    targetJurisdictionUrl,
    isAlreadyOnTargetJurisdictionPage,
    smartRecommendation,
    dismissBanner,
  }
}
