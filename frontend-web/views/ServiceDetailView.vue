<template>
  <div class="service-detail-view">
    <div v-if="loading" class="loading-box">
      {{ isEn ? 'Loading practice area...' : '正在加载服务详情...' }}
    </div>

    <template v-else-if="service">
      <section class="service-hero">
        <div class="wrap">
          <NuxtLink :to="isEn ? '/en/services' : '/services'" class="back-nav">
            &larr; {{ isEn ? 'All practice areas' : '全部服务范围' }}
          </NuxtLink>
          <div class="eyebrow">{{ service.number }}</div>
          <h1>{{ isEn ? (service.en_title || service.zh_title) : service.zh_title }}</h1>
          <p>{{ isEn ? (service.en_intro || service.zh_intro) : service.zh_intro }}</p>
        </div>
      </section>

      <section class="section">
        <div class="wrap detail-grid">
          <div class="detail-main">
            <h2 class="block-title">{{ isEn ? 'Matters we handle' : '我们办理的事项' }}</h2>
            <ul class="item-list">
              <li v-for="(item, i) in items" :key="i">{{ item }}</li>
            </ul>

            <h2 class="block-title">{{ isEn ? 'What to prepare first' : '建议先准备的材料' }}</h2>
            <ul class="check-list">
              <li v-for="(m, i) in materials" :key="i">{{ m }}</li>
            </ul>
          </div>

          <aside class="detail-side">
            <div class="side-card">
              <h3>{{ isEn ? 'Discuss this matter' : '就该事项进行咨询' }}</h3>
              <p>
                {{ isEn
                  ? 'Send us the facts and the documents you already have. We will confirm limitation periods, evidence sufficiency and the routes available to you.'
                  : '提交您掌握的事实与现有文件，我们将核实诉讼时效、证据充分性与可行路径。' }}
              </p>
              <NuxtLink :to="isEn ? '/en#intake' : '/#intake'" class="button button-primary">
                {{ isEn ? 'Free case assessment →' : '免费案情评估 →' }}
              </NuxtLink>
              <NuxtLink :to="isEn ? '/en/countries' : '/countries'" class="button button-outline-dark">
                {{ isEn ? 'Browse jurisdictions' : '按法域查找' }}
              </NuxtLink>
            </div>
          </aside>
        </div>
      </section>

      <section class="cta-band">
        <div class="wrap text-center">
          <h2>{{ isEn ? 'Not sure this is the right route?' : '不确定是否属于这类事项？' }}</h2>
          <p>
            {{ isEn
              ? 'Most cross-border matters span several practice areas. Describe the facts and we will map the options and the order of steps.'
              : '跨境事项常同时涉及多个服务范围。描述事实经过，我们为您梳理可选路径与步骤顺序。' }}
          </p>
          <NuxtLink :to="isEn ? '/en#intake' : '/#intake'" class="button button-primary">
            {{ isEn ? 'Start a free consultation →' : '开始免费法律咨询 →' }}
          </NuxtLink>
        </div>
      </section>
    </template>

    <div v-else class="not-found">
      <div class="wrap">
        <p>{{ isEn ? 'Practice area not found.' : '未找到该服务页面。' }}</p>
        <NuxtLink :to="isEn ? '/en/services' : '/services'" class="button button-primary">
          {{ isEn ? 'Back to all practice areas' : '返回服务范围' }}
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
  return (isEn.value ? s.items_en : s.items_zh) || []
})

const materials = computed<string[]>(() => {
  const s: any = service.value
  if (!s) return []
  return (isEn.value ? s.materials_en : s.materials_zh) || []
})

// ---- SEO --------------------------------------------------------------
const siteUrl = 'https://shenyuanlegal.com'
const title = computed(() => {
  const s: any = service.value
  if (!s) return ''
  return isEn.value ? (s.en_title || s.zh_title) : s.zh_title
})
const description = computed(() => {
  const s: any = service.value
  if (!s) return ''
  return isEn.value ? (s.en_intro || s.zh_intro) : s.zh_intro
})

const slug = computed(() => String(route.params.slug))
const zhPath = computed(() => `/services/${slug.value}`)
const enPath = computed(() => `/en/services/${slug.value}`)
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

const serviceJsonLd = computed(() => {
  if (!service.value) return null
  return {
    '@context': 'https://schema.org',
    '@type': 'Service',
    'name': title.value,
    'description': description.value,
    'serviceType': title.value,
    'inLanguage': isEn.value ? 'en' : 'zh-CN',
    'provider': {
      '@type': 'LegalService',
      'name': isEn.value ? 'Shenyuan International Law Firm' : '深远(国际)律师事务所',
      'url': isEn.value ? `${siteUrl}/en` : siteUrl,
    },
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
        'name': isEn.value ? 'Home' : '首页',
        'item': isEn.value ? `${siteUrl}/en` : siteUrl,
      },
      {
        '@type': 'ListItem',
        'position': 2,
        'name': isEn.value ? 'Practice areas' : '服务范围',
        'item': isEn.value ? `${siteUrl}/en/services` : `${siteUrl}/services`,
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
  link: [
    { rel: 'canonical', href: () => canonical.value },
    { rel: 'alternate', hreflang: 'zh-CN', href: () => `${siteUrl}${zhPath.value}` },
    { rel: 'alternate', hreflang: 'en', href: () => `${siteUrl}${enPath.value}` },
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
