<template>
  <div class="service-detail-view" :class="{ 'is-rtl': isAr }">
    <div v-if="loading" class="loading-box">
      {{ isEn ? 'Loading practice area...' : (isAr ? 'جارٍ تحميل تفاصيل الخدمة...' : (isEs ? 'Cargando área de práctica...' : '正在加载服务详情...')) }}
    </div>

    <template v-else-if="service">
      <section class="service-hero">
        <div class="wrap">
          <NuxtLink :to="isAr ? '/ar/services' : (isEs ? '/es/services' : (isEn ? '/en/services' : '/services'))" class="back-nav">
            <span v-if="isAr">&rarr; جميع مجالات الممارسة</span>
            <span v-else-if="isEs">&larr; Todas las áreas de práctica</span>
            <span v-else>&larr; {{ isEn ? 'All practice areas' : '全部服务范围' }}</span>
          </NuxtLink>
          <div class="eyebrow">{{ service.number }}</div>
          <h1>{{ isEn ? (service.en_title || service.zh_title) : (isAr && service.translations?.ar?.title ? service.translations.ar.title : (isEs && service.translations?.es?.title ? service.translations.es.title : service.zh_title)) }}</h1>
          <p>{{ isEn ? (service.en_intro || service.zh_intro) : (isAr && service.translations?.ar?.intro ? service.translations.ar.intro : (isEs && service.translations?.es?.intro ? service.translations.es.intro : service.zh_intro)) }}</p>
        </div>
      </section>

      <section class="section">
        <div class="wrap detail-grid">
          <div class="detail-main">
            <h2 class="block-title">{{ isEn ? 'Matters we handle' : (isAr ? 'القضايا التي نتولاها' : (isEs ? 'Asuntos que gestionamos' : '我们办理的事项')) }}</h2>
            <ul class="item-list">
              <li v-for="(item, i) in items" :key="i">{{ item }}</li>
            </ul>

            <h2 class="block-title">{{ isEn ? 'What to prepare first' : (isAr ? 'المستندات المقترح تجهيزها مسبقاً' : (isEs ? 'Documentación inicial requerida' : '建议先准备的材料')) }}</h2>
            <ul class="check-list">
              <li v-for="(m, i) in materials" :key="i">{{ m }}</li>
            </ul>
          
            <!-- High-Frequency Jurisdictions for this Service -->
            <h2 class="block-title">{{ isEn ? 'Key Jurisdictions Covered' : (isAr ? 'أبرز الدول والاختصاصات القضائية' : (isEs ? 'Jurisdicciones Clave de Colaboración' : '核心协做法域')) }}</h2>
            <div class="service-jurisdictions-grid">
              <NuxtLink
                v-for="c in relevantCountries"
                :key="c.slug"
                :to="isAr ? `/ar/countries/${c.slug}` : (isEs ? `/es/countries/${c.slug}` : (isEn ? `/en/countries/${c.slug}` : `/countries/${c.slug}`))"
                class="service-j-card"
              >
                <span class="j-dot"></span>
                <span class="j-name">{{ isEn ? c.name_en : (isAr ? c.name_ar : (isEs ? c.name_es : c.name_zh)) }}</span>
                <span class="j-arrow">{{ isAr ? '&larr;' : '&rarr;' }}</span>
              </NuxtLink>
            </div>

            <!-- Related Practice Guides & Articles -->
            <template v-if="serviceArticles.length">
              <h2 class="block-title">{{ isEn ? 'Featured Practice Guides' : (isAr ? 'أدلة ودراسات قانونية مختارة' : (isEs ? 'Guías Prácticas y Artículos Destacados' : '精选实务案例与指南')) }}</h2>
              <div class="service-articles-grid">
                <NuxtLink
                  v-for="art in serviceArticles"
                  :key="art.id"
                  :to="isAr ? `/ar/articles/${art.slug}` : (isEs ? `/es/articles/${art.slug}` : (isEn ? `/en/articles/${art.slug}` : `/articles/${art.slug}`))"
                  class="service-art-card"
                >
                  <span class="s-art-badge">{{ art.business }}</span>
                  <h4 class="s-art-title">{{ isAr ? (art.translations?.ar?.title || art.title_en || art.title_zh) : (isEs ? (art.translations?.es?.title || art.title_en || art.title_zh) : (isEn ? (art.title_en || art.title_zh) : art.title_zh)) }}</h4>
                  <p class="s-art-desc">{{ isAr ? (art.translations?.ar?.description || art.description_en || art.description_zh) : (isEs ? (art.translations?.es?.description || art.description_en || art.description_zh) : (isEn ? (art.description_en || art.description_zh) : art.description_zh)) }}</p>
                </NuxtLink>
              </div>
            </template>
          </div>

          <aside class="detail-side">
            <div class="side-card">
              <h3>{{ isEn ? 'Discuss this matter' : (isAr ? 'استشارة بخصوص هذا النزاع' : (isEs ? 'Consultar sobre este asunto' : '就该事项进行咨询')) }}</h3>
              <p>
                {{ isEn
                  ? 'Send us the facts and the documents you already have. We will confirm limitation periods, evidence sufficiency and the routes available to you.'
                  : (isAr
                    ? 'أرسل الوقائع والمستندات المتوفرة لديك وسيقوم فريقنا بالتحقق من مدد التقادم وقوة الأدلة والمسارات المتاحة.'
                    : (isEs
                      ? 'Envíenos los hechos y documentos disponibles. Verificaremos plazos de prescripción, suficiencia probatoria y vías viables.'
                      : '提交您掌握的事实与现有文件，我们将核实诉讼时效、证据充分性与可行路径。')) }}
              </p>
              <NuxtLink :to="isAr ? '/ar#intake' : (isEs ? '/es#intake' : (isEn ? '/en#intake' : '/#intake'))" class="button button-primary">
                {{ isEn ? 'Free case assessment →' : (isAr ? 'تقييم مجاني للموقف القانوني ←' : (isEs ? 'Evaluación Gratuita del Caso →' : '免费案情评估 →')) }}
              </NuxtLink>
              <NuxtLink :to="isAr ? '/ar/countries' : (isEs ? '/es/countries' : (isEn ? '/en/countries' : '/countries'))" class="button button-outline-dark">
                {{ isEn ? 'Browse jurisdictions' : (isAr ? 'تصفح الدول والاختصاصات' : (isEs ? 'Explorar por jurisdicción' : '按法域查找')) }}
              </NuxtLink>
            </div>
          </aside>
        </div>
      </section>

      <section class="cta-band">
        <div class="wrap text-center">
          <h2>{{ isEn ? 'Not sure this is the right route?' : (isAr ? 'هل أنت غير متأكد من المسار القانوني الملائم؟' : (isEs ? '¿No está seguro si este es el procedimiento adecuado?' : '不确定是否属于这类事项？')) }}</h2>
          <p>
            {{ isEn
              ? 'Most cross-border matters span several practice areas. Describe the facts and we will map the options and the order of steps.'
              : (isAr
                ? 'غالباً ما تتداخل القضايا العابرة للحدود في عدة مجالات قانونية. صف لنا الوقائع وسنحدد لك البدائل وترتيب الخطوات.'
                : (isEs
                  ? 'Los conflictos transfronterizos suelen abarcar varias áreas. Describa su situación y trazaremos las opciones y el orden procesal.'
                  : '跨境事项常同时涉及多个服务范围。描述事实经过，我们为您梳理可选路径与步骤顺序。')) }}
          </p>
          <NuxtLink :to="isAr ? '/ar#intake' : (isEs ? '/es#intake' : (isEn ? '/en#intake' : '/#intake'))" class="button button-primary">
            {{ isEn ? 'Start a free consultation →' : (isAr ? 'ابدأ استشارة قانونية مجانية ←' : (isEs ? 'Iniciar Consulta Gratuita →' : '开始免费法律咨询 →')) }}
          </NuxtLink>
        </div>
      </section>
    </template>

    <div v-else class="not-found">
      <div class="wrap">
        <p>{{ isEn ? 'Practice area not found.' : (isAr ? 'لم يتم العثور على صفحة الخدمة.' : (isEs ? 'Área de práctica no encontrada.' : '未找到该服务页面。')) }}</p>
        <NuxtLink :to="isAr ? '/ar/services' : (isEs ? '/es/services' : (isEn ? '/en/services' : '/services'))" class="button button-primary">
          {{ isEn ? 'Back to all practice areas' : (isAr ? 'العودة إلى مجالات الممارسة' : (isEs ? 'Volver a todas las áreas' : '返回服务范围')) }}
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { getApiClient } from '@/api/client'

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

// Server-rendered so the copy ships in the initial HTML.
const { data: service, pending: loading } = await useAsyncData(
  `service-${route.params.slug}`,
  async () => {
    try {
      const res = await getApiClient().get(`/api/services/${route.params.slug}`)
      return res.data
    } catch (err) {
      console.error('Failed to load service detail', err)
      return null
    }
  }
)

const items = computed<string[]>(() => {
  const s: any = service.value
  if (!s) return []
  if (isEn.value) return s.items_en || []
  if (isAr.value && s.translations?.ar?.items) return s.translations.ar.items
  if (isEs.value && s.translations?.es?.items) return s.translations.es.items
  return s.items_zh || []
})

// Load all articles to display service-specific featured articles
const { data: allArticles } = await useAsyncData(
  'service-articles-all',
  async () => {
    try {
      const res = await getApiClient().get('/api/articles')
      if (Array.isArray(res.data) && res.data.length > 0) return res.data
    } catch (e) {
      // fallback
    }
    try {
      const data: any = await $fetch('https://shenyuan-backend.vercel.app/api/articles')
      return Array.isArray(data) ? data : []
    } catch (e) {
      return []
    }
  }
)

const serviceArticles = computed(() => {
  const s: any = service.value
  if (!s || !allArticles.value) return []
  const currentSlug = String(route.params.slug)
  // Match articles by service business category
  return allArticles.value
    .filter((a: any) => a.business === currentSlug)
    .slice(0, 4)
})

const relevantCountries = computed(() => [
  { slug: 'united-states', name_zh: '美国', name_en: 'United States', name_ar: 'الولايات المتحدة', name_es: 'Estados Unidos' },
  { slug: 'singapore', name_zh: '新加坡', name_en: 'Singapore', name_ar: 'سنغافورة', name_es: 'Singapur' },
  { slug: 'hong-kong', name_zh: '香港', name_en: 'Hong Kong', name_ar: 'هونغ كونغ', name_es: 'Hong Kong' },
  { slug: 'united-kingdom', name_zh: '英国', name_en: 'United Kingdom', name_ar: 'المملكة المتحدة', name_es: 'Reino Unido' },
  { slug: 'australia', name_zh: '澳大利亚', name_en: 'Australia', name_ar: 'أستراليا', name_es: 'Australia' },
  { slug: 'germany', name_zh: '德国', name_en: 'Germany', name_ar: 'ألمانيا', name_es: 'Alemania' },
])

const materials = computed<string[]>(() => {
  const s: any = service.value
  if (!s) return []
  if (isEn.value) return s.materials_en || []
  if (isAr.value && s.translations?.ar?.materials) return s.translations.ar.materials
  if (isEs.value && s.translations?.es?.materials) return s.translations.es.materials
  return s.materials_zh || []
})

// ---- SEO --------------------------------------------------------------
const siteUrl = 'https://shenyuanlegal.com'
const title = computed(() => {
  const s: any = service.value
  if (!s) return ''
  if (isEn.value) return s.en_title || s.zh_title
  if (isAr.value && s.translations?.ar?.title) return s.translations.ar.title
  if (isEs.value && s.translations?.es?.title) return s.translations.es.title
  return s.zh_title
})
const description = computed(() => {
  const s: any = service.value
  if (!s) return ''
  if (isEn.value) return s.en_intro || s.zh_intro
  if (isAr.value && s.translations?.ar?.intro) return s.translations.ar.intro
  if (isEs.value && s.translations?.es?.intro) return s.translations.es.intro
  return s.zh_intro
})

const slug = computed(() => String(route.params.slug))
const zhPath = computed(() => `/services/${slug.value}`)
const enPath = computed(() => `/en/services/${slug.value}`)
const arPath = computed(() => `/ar/services/${slug.value}`)
const esPath = computed(() => `/es/services/${slug.value}`)

const canonical = computed(() => {
  if (isAr.value) return `${siteUrl}${arPath.value}`
  if (isEs.value) return `${siteUrl}${esPath.value}`
  if (isEn.value) return `${siteUrl}${enPath.value}`
  return `${siteUrl}${zhPath.value}`
})

useSeoMeta({
  title: () => title.value
    ? `${title.value} | ${isEn.value ? 'Shenyuan International' : (isAr.value ? 'مكتب شينيوان الدولي' : (isEs.value ? 'Shenyuan International' : '深远(国际)律师事务所'))}`
    : 'Shenyuan International',
  description: () => description.value,
  ogTitle: () => title.value,
  ogDescription: () => description.value,
  ogType: 'website',
  ogUrl: () => canonical.value,
  ogImage: () => `${siteUrl}/og-image.png`,
  twitterCard: 'summary_large_image',
  twitterTitle: () => title.value,
  twitterDescription: () => description.value,
  twitterImage: () => `${siteUrl}/og-image.png`,
})

const serviceJsonLd = computed(() => {
  const s: any = service.value
  if (!s) return null
  return {
    '@context': 'https://schema.org',
    '@type': 'LegalService',
    'name': `${title.value} | ${isEn.value ? 'Shenyuan International' : (isAr.value ? 'مكتب شينيوان الدولي' : (isEs.value ? 'Shenyuan International' : '深远(国际)律师事务所'))}`,
    'description': description.value,
    'url': canonical.value,
    'inLanguage': isEn.value ? 'en' : (isAr.value ? 'ar' : (isEs.value ? 'es' : 'zh-CN')),
    'provider': {
      '@type': 'LegalService',
      'name': 'Shenyuan International Law Firm',
      'url': siteUrl,
    },
    'serviceType': s.zh_title,
    'areaServed': 'Global',
  }
})

const breadcrumbJsonLd = computed(() => {
  if (!service.value) return null
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    'itemListElement': [
      {
        '@type': 'ListItem',
        'position': 1,
        'name': isEn.value ? 'Home' : (isAr.value ? 'الرئيسية' : (isEs.value ? 'Inicio' : '首页')),
        'item': isEn.value ? `${siteUrl}/en` : (isAr.value ? `${siteUrl}/ar` : (isEs.value ? `${siteUrl}/es` : siteUrl)),
      },
      {
        '@type': 'ListItem',
        'position': 2,
        'name': isEn.value ? 'Practice Areas' : (isAr.value ? 'مجالات الممارسة' : (isEs.value ? 'Áreas de Práctica' : '服务范围')),
        'item': isEn.value ? `${siteUrl}/en/services` : (isAr.value ? `${siteUrl}/ar/services` : (isEs.value ? `${siteUrl}/es/services` : `${siteUrl}/services`)),
      },
      {
        '@type': 'ListItem',
        'position': 3,
        'name': title.value,
        'item': canonical.value,
      },
    ],
  }
})

useHead({
  htmlAttrs: computed(() => ({
    lang: isAr.value ? 'ar' : (isEs.value ? 'es' : (isEn.value ? 'en' : 'zh-CN')),
    dir: isAr.value ? 'rtl' : 'ltr',
  })),
  link: [
    { rel: 'canonical', href: () => canonical.value },
    { rel: 'alternate', hreflang: 'zh-CN', href: () => `${siteUrl}${zhPath.value}` },
    { rel: 'alternate', hreflang: 'en', href: () => `${siteUrl}${enPath.value}` },
    { rel: 'alternate', hreflang: 'ar', href: () => `${siteUrl}${arPath.value}` },
    { rel: 'alternate', hreflang: 'es', href: () => `${siteUrl}${esPath.value}` },
    { rel: 'alternate', hreflang: 'x-default', href: () => `${siteUrl}${zhPath.value}` },
  ],
  script: computed(() => {
    const scripts: any[] = []
    if (serviceJsonLd.value) {
      scripts.push({ type: 'application/ld+json', innerHTML: JSON.stringify(serviceJsonLd.value) })
    }
    if (breadcrumbJsonLd.value) {
      scripts.push({ type: 'application/ld+json', innerHTML: JSON.stringify(breadcrumbJsonLd.value) })
    }
    return scripts
  }),
})
</script>

<style scoped>
.service-detail-view {
  background: var(--paper);
  color: var(--ink);
}

/* RTL 镜像适配 */
.service-detail-view.is-rtl {
  direction: rtl;
  text-align: right;
}

.service-detail-view.is-rtl .eyebrow {
  flex-direction: row-reverse;
}

.service-detail-view.is-rtl .eyebrow::before {
  margin-left: 8px;
  margin-right: 0;
}

.service-detail-view.is-rtl .item-list li {
  padding: 16px 46px 16px 18px;
}

.service-detail-view.is-rtl .item-list li::before {
  left: auto;
  right: 20px;
}

.service-detail-view.is-rtl .check-list li {
  padding: 14px 46px 14px 18px;
}

.service-detail-view.is-rtl .check-list li::before {
  left: auto;
  right: 20px;
}

.service-detail-view.is-rtl .j-arrow {
  margin-left: 0;
  margin-right: auto;
}

.loading-box {
  padding: 160px 0;
  text-align: center;
  color: var(--muted);
}

.service-hero {
  padding: 130px 0 64px;
  background: var(--teal-deep);
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.back-nav {
  display: inline-block;
  margin-bottom: 18px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.72);
}
.back-nav:hover { color: #fff; }

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #f1b68f;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  margin-bottom: 14px;
}
.eyebrow::before {
  content: "";
  width: 24px;
  height: 2px;
  background: #f1b68f;
}

.service-hero h1 {
  font-family: var(--serif);
  font-size: clamp(28px, 3.6vw, 44px);
  line-height: 1.22;
  margin: 0 0 18px;
}

.service-hero p {
  max-width: 760px;
  margin: 0;
  font-size: 16px;
  line-height: 1.75;
  color: rgba(255, 255, 255, 0.82);
}

.section { padding: 72px 0 96px; }

.detail-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 48px;
  align-items: start;
}

.block-title {
  font-family: var(--serif);
  font-size: 22px;
  color: var(--teal-deep);
  margin: 0 0 18px;
}
.item-list + .block-title,
.check-list + .block-title { margin-top: 44px; }

.item-list,
.check-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 12px;
}

.item-list li {
  position: relative;
  padding: 16px 18px 16px 46px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  font-size: 15px;
  line-height: 1.6;
}
.item-list li::before {
  content: "";
  position: absolute;
  left: 20px;
  top: 24px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--orange);
}

.check-list li {
  position: relative;
  padding: 14px 18px 14px 46px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  font-size: 15px;
  line-height: 1.6;
}
.check-list li::before {
  content: "";
  position: absolute;
  left: 20px;
  top: 22px;
  width: 10px;
  height: 6px;
  border-left: 2px solid var(--gold);
  border-bottom: 2px solid var(--gold);
  transform: rotate(-45deg);
}

.service-jurisdictions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 40px;
}

.service-j-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink);
  transition: all 0.2s ease;
}

.service-j-card:hover {
  border-color: var(--teal);
  color: var(--teal-deep);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.j-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--gold);
}

.j-arrow {
  margin-left: auto;
  color: var(--muted);
  font-size: 12px;
}

.service-articles-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 36px;
}

.service-art-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.service-art-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.04);
}

.s-art-badge {
  align-self: flex-start;
  font-size: 11px;
  font-weight: 700;
  color: var(--teal-deep);
  background: var(--teal-soft);
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.s-art-title {
  font-size: 14.5px;
  color: var(--teal-deep);
  line-height: 1.4;
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.s-art-desc {
  font-size: 12.5px;
  color: var(--muted);
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@media (max-width: 600px) {
  .service-jurisdictions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .service-articles-grid {
    grid-template-columns: 1fr;
  }
}

.side-card {
  position: sticky;
  top: 100px;
  padding: 28px 24px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.side-card h3 {
  font-family: var(--serif);
  font-size: 19px;
  color: var(--teal-deep);
  margin: 0 0 10px;
}
.side-card p {
  font-size: 14px;
  line-height: 1.65;
  color: var(--muted);
  margin: 0 0 20px;
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
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease;
}
.button:hover { transform: translateY(-2px); }
.button-primary { color: #fff; background: var(--orange); }
.button-primary:hover { background: #c85d2e; }
.button-outline-dark {
  color: var(--teal-deep);
  background: transparent;
  border-color: var(--line);
}
.button-outline-dark:hover { background: var(--cream); }

.side-card .button { width: 100%; }
.side-card .button + .button { margin-top: 10px; }

.cta-band {
  padding: 96px 0;
  color: #f8f5ef;
  background: var(--teal-deep);
}
.text-center { text-align: center; }
.cta-band h2 {
  font-family: var(--serif);
  font-size: clamp(26px, 3vw, 36px);
  max-width: 760px;
  margin: 0 auto;
}
.cta-band p {
  max-width: 600px;
  margin: 18px auto 26px;
  color: rgba(255, 255, 255, 0.72);
  font-size: 16px;
  line-height: 1.7;
}

.not-found {
  padding: 180px 0 140px;
  text-align: center;
}
.not-found p { color: var(--muted); margin-bottom: 20px; }

@media (max-width: 900px) {
  .detail-grid { grid-template-columns: 1fr; gap: 40px; }
  .side-card { position: static; }
}
@media (max-width: 600px) {
  .service-hero { padding: 110px 0 48px; }
  .section { padding: 52px 0 72px; }
  .cta-band { padding: 72px 0; }
}
</style>
