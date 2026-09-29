<template>
  <div class="country-detail-view" :class="{ 'is-rtl': isAr }">
    <div v-if="loading" class="loading-box">
      {{ isEn ? 'Loading jurisdiction details...' : (isAr ? 'جارٍ تحميل تفاصيل الدولة...' : (isEs ? 'Cargando detalles de la jurisdicción...' : '正在加载法域信息...')) }}
    </div>

    <template v-else-if="country">
      <section class="country-hero">
        <div class="wrap">
          <NuxtLink :to="isAr ? '/ar/countries' : (isEs ? '/es/countries' : (isEn ? '/en/countries' : '/countries'))" class="back-nav">
            <span v-if="isAr">&rarr; جميع الاختصاصات القضائية</span>
            <span v-else-if="isEs">&larr; Todas las jurisdicciones</span>
            <span v-else>&larr; {{ isEn ? 'All jurisdictions' : '全部法域' }}</span>
          </NuxtLink>
          <div class="eyebrow">{{ isEn ? country.name_en : (isAr && country.translations?.ar?.name ? country.translations.ar.name : (isEs && country.translations?.es?.name ? country.translations.es.name : country.name_zh)) }}</div>
          <h1>{{ isEn ? (country.en_title || country.zh_title) : (isAr && country.translations?.ar?.title ? country.translations.ar.title : (isEs && country.translations?.es?.title ? country.translations.es.title : country.zh_title)) }}</h1>
          <p>{{ isEn ? (country.en_intro || country.zh_intro) : (isAr && country.translations?.ar?.intro ? country.translations.ar.intro : (isEs && country.translations?.es?.intro ? country.translations.es.intro : country.zh_intro)) }}</p>
        </div>
      </section>

      <section class="section">
        <div class="wrap detail-grid">
          <div class="detail-main">
            <h2 class="block-title">{{ isEn ? 'Matters we handle in this jurisdiction' : (isAr ? 'القضايا التي نتولاها في هذه الدولة' : (isEs ? 'Asuntos que gestionamos en esta jurisdicción' : '我们在该法域办理的事项')) }}</h2>
            <ul class="item-list">
              <li v-for="(item, i) in items" :key="i">{{ item }}</li>
            </ul>

            <h2 class="block-title">{{ isEn ? 'Practical points that decide the outcome' : (isAr ? 'النقاط الإجرائية التي تحسم النتيجة' : (isEs ? 'Aspectos prácticos determinantes' : '决定成败的实务要点')) }}</h2>
            <ul class="point-list">
              <li v-for="(p, i) in points" :key="i">{{ p }}</li>
            </ul>

            <!-- Related Country Articles -->
            <template v-if="countryArticles.length">
              <h2 class="block-title">{{ isEn ? 'Relevant Legal Guides & Articles' : (isAr ? 'أدلة ومقالات قانونية متعلقة بهذه الدولة' : (isEs ? 'Guías Jurídicas y Artículos Relacionados' : '该法域相关实务文章')) }}</h2>
              <div class="country-articles-grid">
                <NuxtLink
                  v-for="art in countryArticles"
                  :key="art.id"
                  :to="isAr ? `/ar/articles/${art.slug}` : (isEs ? `/es/articles/${art.slug}` : (isEn ? `/en/articles/${art.slug}` : `/articles/${art.slug}`))"
                  class="country-art-card"
                >
                  <span class="c-art-badge">{{ art.business }}</span>
                  <h4 class="c-art-title">{{ isAr ? (art.translations?.ar?.title || art.title_en || art.title_zh) : (isEs ? (art.translations?.es?.title || art.title_en || art.title_zh) : (isEn ? (art.title_en || art.title_zh) : art.title_zh)) }}</h4>
                  <p class="c-art-desc">{{ isAr ? (art.translations?.ar?.description || art.description_en || art.description_zh) : (isEs ? (art.translations?.es?.description || art.description_en || art.description_zh) : (isEn ? (art.description_en || art.description_zh) : art.description_zh)) }}</p>
                </NuxtLink>
              </div>
            </template>

            <template v-if="faqs.length">
              <h2 class="block-title">{{ isEn ? 'Frequently asked questions' : (isAr ? 'الأسئلة الشائعة' : (isEs ? 'Preguntas frecuentes' : '常见问题')) }}</h2>
              <div class="faq-list">
                <details v-for="(f, i) in faqs" :key="i" class="faq-item">
                  <summary>{{ f.question }}</summary>
                  <p>{{ f.answer }}</p>
                </details>
              </div>
            </template>
          </div>

          <aside class="detail-side">
            <div class="side-card">
              <h3>{{ isEn ? 'Discuss this jurisdiction' : (isAr ? 'استشارة بشأن هذه الدولة' : (isEs ? 'Consultar sobre esta jurisdicción' : '就该法域进行咨询')) }}</h3>
              <p>
                {{ isEn
                  ? 'Send us the facts and documents you have. We will confirm limitation periods, evidence sufficiency and the available routes.'
                  : (isAr
                    ? 'أرسل الوقائع والمستندات المتوفرة لديك وسيقوم فريقنا بالتحقق من مدد التقادم وقوة الأدلة والمسارات المتاحة.'
                    : (isEs
                      ? 'Envíenos los hechos y documentos disponibles. Verificaremos plazos de prescripción, suficiencia probatoria y vías viables.'
                      : '提交您掌握的事实与文件，我们将核实诉讼时效、证据充分性与可行路径。')) }}
              </p>
              <NuxtLink :to="isAr ? '/ar#intake' : (isEs ? '/es#intake' : (isEn ? '/en#intake' : '/#intake'))" class="button button-primary">
                {{ isEn ? 'Free case assessment →' : (isAr ? 'تقييم مجاني للموقف القانوني ←' : (isEs ? 'Evaluación Gratuita del Caso →' : '免费案情评估 →')) }}
              </NuxtLink>
              <NuxtLink :to="isAr ? '/ar/services' : (isEs ? '/es/services' : (isEn ? '/en/services' : '/services'))" class="button button-outline-dark">
                {{ isEn ? 'See practice areas' : (isAr ? 'استعراض مجالات الممارسة' : (isEs ? 'Ver áreas de práctica' : '查看服务范围')) }}
              </NuxtLink>
            </div>
          </aside>
        </div>
      </section>

      <section class="cta-band">
        <div class="wrap text-center">
          <h2>{{ isEn ? 'Not sure which jurisdiction applies?' : (isAr ? 'هل أنت غير متأكد من الاختصاص القضائي المنطبق؟' : (isEs ? '¿No está seguro de qué jurisdicción aplica?' : '不确定适用哪个法域？')) }}</h2>
          <p>
            {{ isEn
              ? 'Cross-border matters often involve more than one country. Tell us the facts and we will map the forum and the order of steps.'
              : (isAr
                ? 'غالباً ما تشمل النزاعات العابرة للحدود أكثر من دولة. صف لنا الوقائع وسنحدد لك المحكمة المختصة وترتيب الإجراءات.'
                : (isEs
                  ? 'Los asuntos transfronterizos a menudo involucran varios países. Cuéntenos los hechos y determinaremos el foro y orden procesal.'
                  : '跨境事项常涉及多个国家。告诉我们事实经过，我们为您梳理管辖法院与步骤顺序。')) }}
          </p>
          <NuxtLink :to="isAr ? '/ar#intake' : (isEs ? '/es#intake' : (isEn ? '/en#intake' : '/#intake'))" class="button button-primary">
            {{ isEn ? 'Start a free consultation →' : (isAr ? 'ابدأ استشارة قانونية مجانية ←' : (isEs ? 'Iniciar Consulta Gratuita →' : '开始免费法律咨询 →')) }}
          </NuxtLink>
        </div>
      </section>
    </template>

    <div v-else class="not-found">
      <div class="wrap">
        <p>{{ isEn ? 'Jurisdiction not found.' : (isAr ? 'لم يتم العثور على صفحة الدولة.' : (isEs ? 'Jurisdicción no encontrada.' : '未找到该法域页面。')) }}</p>
        <NuxtLink :to="isAr ? '/ar/countries' : (isEs ? '/es/countries' : (isEn ? '/en/countries' : '/countries'))" class="button button-primary">
          {{ isEn ? 'Back to all jurisdictions' : (isAr ? 'العودة إلى قائمة الدول' : (isEs ? 'Volver a jurisdicciones' : '返回法域列表')) }}
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
const { data: country, pending: loading } = await useAsyncData(
  `country-${route.params.slug}`,
  async () => {
    try {
      const res = await getApiClient().get(`/api/countries/${route.params.slug}`)
      return res.data
    } catch (err) {
      console.error('Failed to load country detail', err)
      return null
    }
  }
)

// Load all articles to find matching articles for this jurisdiction
const { data: allArticles } = await useAsyncData(
  'country-articles-all',
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

const countryArticles = computed(() => {
  const c: any = country.value
  if (!c || !allArticles.value) return []
  const nameZh = c.name_zh || ''
  const nameEn = (c.name_en || '').toLowerCase()
  const slug = (c.slug || '').toLowerCase()

  // Match by country name, slug, or relevant terms
  const matched = allArticles.value.filter((a: any) => {
    const textZh = (a.title_zh || '') + ' ' + (a.description_zh || '') + ' ' + (a.slug || '')
    const textEn = ((a.title_en || '') + ' ' + (a.description_en || '') + ' ' + (a.slug || '')).toLowerCase()
    
    // Check specific keywords
    if (nameZh && textZh.includes(nameZh)) return true
    if (nameEn && textEn.includes(nameEn)) return true
    if (slug === 'united-states' && (textEn.includes('us ') || textEn.includes('u.s.') || textZh.includes('美国') || textZh.includes('美加'))) return true
    if (slug === 'singapore' && (textZh.includes('新加坡') || textEn.includes('singapore'))) return true
    if (slug === 'hong-kong' && (textZh.includes('香港') || textEn.includes('hk') || textEn.includes('hong kong'))) return true
    if (slug === 'russia' && (textZh.includes('俄罗斯') || textEn.includes('russia'))) return true
    if (slug === 'uae' && (textZh.includes('阿联酋') || textZh.includes('迪拜') || textEn.includes('uae') || textEn.includes('dubai'))) return true
    if (slug === 'saudi-arabia' && (textZh.includes('沙特') || textEn.includes('saudi'))) return true
    if (slug === 'mexico' && (textZh.includes('墨西哥') || textEn.includes('mexico'))) return true
    return false
  })

  // Return up to 4 matched articles; if fewer, backfill with top trade/recovery articles
  if (matched.length >= 2) {
    return matched.slice(0, 4)
  }
  const fallback = allArticles.value.filter((a: any) => !matched.includes(a)).slice(0, 3 - matched.length)
  return [...matched, ...fallback]
})

const items = computed<string[]>(() => {
  const c: any = country.value
  if (!c) return []
  if (isEn.value) return c.items_en || []
  if (isAr.value && c.translations?.ar?.items) return c.translations.ar.items
  if (isEs.value && c.translations?.es?.items) return c.translations.es.items
  return c.items_zh || []
})

const points = computed<string[]>(() => {
  const c: any = country.value
  if (!c) return []
  if (isEn.value) return c.points_en || []
  if (isAr.value && c.translations?.ar?.points) return c.translations.ar.points
  if (isEs.value && c.translations?.es?.points) return c.translations.es.points
  return c.points_zh || []
})

const faqs = computed<any[]>(() => {
  const c: any = country.value
  if (!c) return []
  if (isEn.value) return c.faq_en || []
  if (isAr.value && c.translations?.ar?.faq) return c.translations.ar.faq
  if (isEs.value && c.translations?.es?.faq) return c.translations.es.faq
  return c.faq_zh || []
})

// ---- SEO --------------------------------------------------------------
const siteUrl = 'https://shenyuanlegal.com'
const name = computed(() => {
  const c: any = country.value
  if (!c) return ''
  if (isEn.value) return c.name_en
  if (isAr.value && c.translations?.ar?.name) return c.translations.ar.name
  if (isEs.value && c.translations?.es?.name) return c.translations.es.name
  return c.name_zh
})
const title = computed(() => {
  const c: any = country.value
  if (!c) return ''
  if (isEn.value) return c.en_title || c.zh_title
  if (isAr.value && c.translations?.ar?.title) return c.translations.ar.title
  if (isEs.value && c.translations?.es?.title) return c.translations.es.title
  return c.zh_title
})
const description = computed(() => {
  const c: any = country.value
  if (!c) return ''
  if (isEn.value) return c.en_intro || c.zh_intro
  if (isAr.value && c.translations?.ar?.intro) return c.translations.ar.intro
  if (isEs.value && c.translations?.es?.intro) return c.translations.es.intro
  return c.zh_intro
})

const slug = computed(() => String(route.params.slug))
const zhPath = computed(() => `/countries/${slug.value}`)
const enPath = computed(() => `/en/countries/${slug.value}`)
const arPath = computed(() => `/ar/countries/${slug.value}`)
const esPath = computed(() => `/es/countries/${slug.value}`)

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

const faqJsonLd = computed(() => {
  if (!faqs.value.length) return null
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    'inLanguage': isEn.value ? 'en' : (isAr.value ? 'ar' : (isEs.value ? 'es' : 'zh-CN')),
    'mainEntity': faqs.value.map((f: any) => ({
      '@type': 'Question',
      'name': f.question,
      'acceptedAnswer': { '@type': 'Answer', 'text': f.answer },
    })),
  }
})

const breadcrumbJsonLd = computed(() => {
  if (!country.value) return null
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
        'name': isEn.value ? 'Jurisdictions' : (isAr.value ? 'الاختصاصات القضائية' : (isEs.value ? 'Jurisdicciones' : '法域覆盖')),
        'item': isEn.value ? `${siteUrl}/en/countries` : (isAr.value ? `${siteUrl}/ar/countries` : (isEs.value ? `${siteUrl}/es/countries` : `${siteUrl}/countries`)),
      },
      {
        '@type': 'ListItem',
        'position': 3,
        'name': name.value,
        'item': canonical.value,
      },
    ],
  }
})

useHead({
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
    if (faqJsonLd.value) {
      scripts.push({ type: 'application/ld+json', innerHTML: JSON.stringify(faqJsonLd.value) })
    }
    if (breadcrumbJsonLd.value) {
      scripts.push({ type: 'application/ld+json', innerHTML: JSON.stringify(breadcrumbJsonLd.value) })
    }
    return scripts
  }),
})
</script>

<style scoped>
.country-detail-view {
  background: var(--paper);
  color: var(--ink);
}

/* RTL 镜像适配 */
.country-detail-view.is-rtl {
  direction: rtl;
  text-align: right;
}

.country-detail-view.is-rtl .eyebrow {
  flex-direction: row-reverse;
}

.country-detail-view.is-rtl .eyebrow::before {
  margin-left: 8px;
  margin-right: 0;
}

.country-detail-view.is-rtl .item-list li {
  padding: 16px 46px 16px 18px;
}

.country-detail-view.is-rtl .item-list li::before {
  left: auto;
  right: 20px;
}

.country-detail-view.is-rtl .point-list li {
  padding-left: 0;
  padding-right: 26px;
}

.country-detail-view.is-rtl .point-list li::before {
  left: auto;
  right: 4px;
}

.country-detail-view.is-rtl .faq-item summary::after {
  float: left;
}

.loading-box {
  padding: 160px 0;
  text-align: center;
  color: var(--muted);
}

.country-hero {
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

.country-hero h1 {
  font-family: var(--serif);
  font-size: clamp(28px, 3.6vw, 44px);
  line-height: 1.22;
  margin: 0 0 18px;
}

.country-hero p {
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
.block-title + .block-title,
.item-list + .block-title,
.point-list + .block-title,
.faq-list + .block-title { margin-top: 44px; }

.item-list,
.point-list {
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

.point-list li {
  position: relative;
  padding-left: 26px;
  font-size: 15px;
  line-height: 1.7;
  color: #33424f;
}
.point-list li::before {
  content: "";
  position: absolute;
  left: 4px;
  top: 11px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--gold);
}

.country-articles-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 36px;
}

.country-art-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.country-art-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.04);
}

.c-art-badge {
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

.c-art-title {
  font-size: 14.5px;
  color: var(--teal-deep);
  line-height: 1.4;
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.c-art-desc {
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
  .country-articles-grid {
    grid-template-columns: 1fr;
  }
}

.faq-list { display: grid; gap: 10px; }

.faq-item {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px 20px;
}
.faq-item summary {
  cursor: pointer;
  font-weight: 700;
  font-size: 15px;
  color: var(--teal-deep);
  list-style: none;
}
.faq-item summary::-webkit-details-marker { display: none; }
.faq-item summary::after {
  content: "+";
  float: right;
  color: var(--gold);
  font-weight: 700;
}
.faq-item[open] summary::after { content: "−"; }
.faq-item p {
  margin: 12px 0 0;
  font-size: 14px;
  line-height: 1.7;
  color: var(--muted);
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
  .country-hero { padding: 110px 0 48px; }
  .section { padding: 52px 0 72px; }
  .cta-band { padding: 72px 0; }
}
</style>
