<template>
  <div class="countries-view">
    <section class="countries-hero">
      <div class="wrap">
        <div class="eyebrow">{{ isEn ? 'Jurisdictions' : '法域覆盖' }}</div>
        <h1>{{ isEn ? 'Cross-Border Legal Services by Jurisdiction' : '按国家与地区查找跨境法律服务' }}</h1>
        <p>
          {{ isEn
            ? 'Trade recovery, judgment enforcement and inheritance each turn on local procedure. Pick a jurisdiction to see the matters we handle there and the practical steps that decide the outcome.'
            : '货款追收、判决执行与跨境继承，成败往往取决于当地程序细节。选择国家或地区，查看该法域下我们办理的事项类型与实务要点。' }}
        </p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div v-if="loading" class="loading-state">
          {{ isEn ? 'Loading jurisdictions...' : '正在加载法域列表...' }}
        </div>

        <div v-else-if="countries.length === 0" class="loading-state">
          {{ isEn ? 'Jurisdiction list is temporarily unavailable.' : '法域列表暂时不可用。' }}
        </div>

        <div v-else class="country-grid">
          <NuxtLink
            v-for="c in countries"
            :key="c.slug"
            :to="isEn ? `/en/countries/${c.slug}` : `/countries/${c.slug}`"
            class="country-card"
          >
            <span class="country-name">{{ isEn ? c.name_en : c.name_zh }}</span>
            <span class="country-name-alt">{{ isEn ? c.name_zh : c.name_en }}</span>
            <h3>{{ isEn ? (c.en_title || c.zh_title) : c.zh_title }}</h3>
            <span class="read-more">{{ isEn ? 'View details →' : '查看详情 →' }}</span>
          </NuxtLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { getApiClient } from '@/api/client'

const route = useRoute()
const isEn = computed(() => route.path.startsWith('/en'))

const { data, pending: loading } = await useAsyncData(
  'countries-index',
  async () => {
    try {
      const res = await getApiClient().get('/api/countries')
      return (res.data || []) as any[]
    } catch (err) {
      console.error('Failed to load countries', err)
      return []
    }
  }
)

const countries = computed<any[]>(() => data.value || [])

// ---- SEO --------------------------------------------------------------
const siteUrl = 'https://shenyuanlegal.com'
const canonical = computed(() => `${siteUrl}${isEn.value ? '/en/countries' : '/countries'}`)

useSeoMeta({
  title: () => isEn.value
    ? 'Jurisdictions | Cross-Border Legal Services by Country | Shenyuan International'
    : '法域覆盖 | 按国家与地区查找跨境法律服务 | 深远(国际)律师事务所',
  description: () => isEn.value
    ? 'Country-by-country guidance on cross-border trade recovery, judgment enforcement and inheritance, covering the United States, Canada, the UK, Australia, Singapore, Hong Kong and more.'
    : '覆盖美国、加拿大、英国、澳大利亚、新加坡、香港等 22 个国家与地区的跨境法律服务指南，涵盖货款追收、判决承认执行与跨国继承。',
  ogTitle: () => isEn.value ? 'Jurisdictions | Shenyuan International' : '法域覆盖 | 深远(国际)律师事务所',
  ogDescription: () => isEn.value
    ? 'Cross-border legal services by jurisdiction.'
    : '按国家与地区查找跨境法律服务。',
  ogType: 'website',
  ogUrl: () => canonical.value,
})

useHead({
  link: [
    { rel: 'canonical', href: () => canonical.value },
    { rel: 'alternate', hreflang: 'zh-CN', href: `${siteUrl}/countries` },
    { rel: 'alternate', hreflang: 'en', href: `${siteUrl}/en/countries` },
    { rel: 'alternate', hreflang: 'x-default', href: `${siteUrl}/countries` },
  ],
})
</script>

<style scoped>
.countries-view {
  background: var(--paper);
  color: var(--ink);
}

.countries-hero {
  padding: 130px 0 60px;
  background: var(--teal-deep);
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #f1b68f;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  margin-bottom: 12px;
}
.eyebrow::before {
  content: "";
  width: 24px;
  height: 2px;
  background: #f1b68f;
}

.countries-hero h1 {
  font-family: var(--serif);
  font-size: clamp(30px, 4vw, 48px);
  margin-bottom: 16px;
  line-height: 1.2;
}

.countries-hero p {
  max-width: 760px;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.7;
  margin: 0;
}

.section {
  padding: 72px 0 96px;
}

.loading-state {
  padding: 48px 0;
  color: var(--muted);
  font-size: 15px;
}

.country-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
}

.country-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 26px 24px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.country-card:hover {
  transform: translateY(-3px);
  border-color: var(--gold);
}

.country-name {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.11em;
  text-transform: uppercase;
  color: var(--gold);
}

.country-name-alt {
  font-size: 12px;
  color: var(--muted);
}

.country-card h3 {
  font-family: var(--serif);
  font-size: 18px;
  line-height: 1.4;
  margin: 6px 0 12px;
  color: var(--teal-deep);
  font-weight: 600;
}

.read-more {
  margin-top: auto;
  font-size: 13px;
  font-weight: 700;
  color: var(--orange);
}

@media (max-width: 900px) {
  .country-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .country-grid { grid-template-columns: 1fr; }
  .countries-hero { padding: 110px 0 48px; }
  .section { padding: 56px 0 72px; }
}
</style>
