<template>
  <div class="country-detail-view">
    <div v-if="loading" class="loading-box">
      {{ isEn ? 'Loading jurisdiction details...' : '正在加载法域信息...' }}
    </div>

    <template v-else-if="country">
      <section class="country-hero">
        <div class="wrap">
          <NuxtLink :to="isEn ? '/en/countries' : '/countries'" class="back-nav">
            &larr; {{ isEn ? 'All jurisdictions' : '全部法域' }}
          </NuxtLink>
          <div class="eyebrow">{{ isEn ? country.name_en : country.name_zh }}</div>
          <h1>{{ isEn ? (country.en_title || country.zh_title) : country.zh_title }}</h1>
          <p>{{ isEn ? (country.en_intro || country.zh_intro) : country.zh_intro }}</p>
        </div>
      </section>

      <section class="section">
        <div class="wrap detail-grid">
          <div class="detail-main">
            <h2 class="block-title">{{ isEn ? "Matters we handle in this jurisdiction" : '我们在该法域办理的事项' }}</h2>
            <ul class="item-list">
              <li v-for="(item, i) in items" :key="i">{{ item }}</li>
            </ul>

            <h2 class="block-title">{{ isEn ? 'Practical points that decide the outcome' : '决定成败的实务要点' }}</h2>
            <ul class="point-list">
              <li v-for="(p, i) in points" :key="i">{{ p }}</li>
            </ul>

            <template v-if="faqs.length">
              <h2 class="block-title">{{ isEn ? 'Frequently asked questions' : '常见问题' }}</h2>
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
              <h3>{{ isEn ? 'Discuss this jurisdiction' : '就该法域进行咨询' }}</h3>
              <p>
                {{ isEn
                  ? 'Send us the facts and documents you have. We will confirm limitation periods, evidence sufficiency and the available routes.'
                  : '提交您掌握的事实与文件，我们将核实诉讼时效、证据充分性与可行路径。' }}
              </p>
              <NuxtLink :to="isEn ? '/en#intake' : '/#intake'" class="button button-primary">
                {{ isEn ? 'Free case assessment →' : '免费案情评估 →' }}
              </NuxtLink>
              <NuxtLink :to="isEn ? '/en/services' : '/services'" class="button button-outline-dark">
                {{ isEn ? 'See practice areas' : '查看服务范围' }}
              </NuxtLink>
            </div>
          </aside>
        </div>
      </section>

      <section class="cta-band">
        <div class="wrap text-center">
          <h2>{{ isEn ? 'Not sure which jurisdiction applies?' : '不确定适用哪个法域？' }}</h2>
          <p>
            {{ isEn
              ? 'Cross-border matters often involve more than one country. Tell us the facts and we will map the forum and the order of steps.'
              : '跨境事项常涉及多个国家。告诉我们事实经过，我们为您梳理管辖法院与步骤顺序。' }}
          </p>
          <NuxtLink :to="isEn ? '/en#intake' : '/#intake'" class="button button-primary">
            {{ isEn ? 'Start a free consultation →' : '开始免费法律咨询 →' }}
          </NuxtLink>
        </div>
      </section>
    </template>

    <div v-else class="not-found">
      <div class="wrap">
        <p>{{ isEn ? 'Jurisdiction not found.' : '未找到该法域页面。' }}</p>
        <NuxtLink :to="isEn ? '/en/countries' : '/countries'" class="button button-primary">
          {{ isEn ? 'Back to all jurisdictions' : '返回法域列表' }}
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { getApiClient } from '@/api/client'

const route = useRoute()
const isEn = computed(() => route.path.startsWith('/en'))

// Server-rendered so the bilingual copy ships in the initial HTML.
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

const items = computed<string[]>(() => {
  const c: any = country.value
  if (!c) return []
  return (isEn.value ? c.items_en : c.items_zh) || []
})

const points = computed<string[]>(() => {
  const c: any = country.value
  if (!c) return []
  return (isEn.value ? c.points_en : c.points_zh) || []
})

const faqs = computed<any[]>(() => {
  const c: any = country.value
  if (!c) return []
  return (isEn.value ? c.faq_en : c.faq_zh) || []
})

// ---- SEO --------------------------------------------------------------
const siteUrl = 'https://shenyuanlegal.com'
const name = computed(() => {
  const c: any = country.value
  if (!c) return ''
  return isEn.value ? c.name_en : c.name_zh
})
const title = computed(() => {
  const c: any = country.value
  if (!c) return ''
  return isEn.value ? (c.en_title || c.zh_title) : c.zh_title
})
const description = computed(() => {
  const c: any = country.value
  if (!c) return ''
  return isEn.value ? (c.en_intro || c.zh_intro) : c.zh_intro
})

const slug = computed(() => String(route.params.slug))
const zhPath = computed(() => `/countries/${slug.value}`)
const enPath = computed(() => `/en/countries/${slug.value}`)
const canonical = computed(() => `${siteUrl}${isEn.value ? enPath.value : zhPath.value}`)

useSeoMeta({
  title: () => title.value
    ? `${title.value} | ${isEn.value ? 'Shenyuan International' : '深远(国际)律师事务所'}`
    : (isEn.value ? 'Shenyuan International' : '深远(国际)律师事务所'),
  description: () => description.value,
  ogTitle: () => title.value,
  ogDescription: () => description.value,
  ogType: 'website',
  ogUrl: () => canonical.value,
})

const faqJsonLd = computed(() => {
  if (!faqs.value.length) return null
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    'inLanguage': isEn.value ? 'en' : 'zh-CN',
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
        'name': isEn.value ? 'Home' : '首页',
        'item': isEn.value ? `${siteUrl}/en` : siteUrl,
      },
      {
        '@type': 'ListItem',
        'position': 2,
        'name': isEn.value ? 'Jurisdictions' : '法域覆盖',
        'item': isEn.value ? `${siteUrl}/en/countries` : `${siteUrl}/countries`,
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
