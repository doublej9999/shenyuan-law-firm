<template>
  <div class="articles-view" :class="{ 'is-rtl': isAr }">
    <!-- Top Hero Banner -->
    <section class="articles-hero">
      <div class="wrap">
        <div class="eyebrow">{{ isAr ? 'الرؤى القانونية' : (isEs ? 'Perspectivas Jurídicas' : (isEn ? 'Legal Insights' : '法律专栏')) }}</div>
        <h1>{{ isAr ? 'رؤى الممارسة القانونية الدولية وحلول النزاعات' : (isEs ? 'Perspectivas de Práctica Jurídica Internacional y Resolución de Disputas' : (isEn ? 'Cross-Border Practice Insights & Case Studies' : '涉外法律实务与经贸合规前沿')) }}</h1>
        <p>
          {{ isAr
            ? 'دراسات عملية وتوجيهات إجرائية حول التقاضي التجاري الدولي، وتحصيل الديون العابرة للحدود، وإنفاذ الأحكام في منطقة الشرق الأوسط والصين.'
            : (isEs
              ? 'Análisis originales y orientación procesal sobre litigios de comercio internacional, recuperación de créditos transfronterizos y ejecución judicial.'
              : (isEn 
                ? 'Original analyses and procedural guidance on international trade litigation, cross-border debt recovery, and multi-jurisdiction probate.' 
                : '由深远合伙人及资深涉外律师撰写，深入剖析跨境贸易纠纷、海外欠款追索、域外财产执行及跨国遗产公证的实操要点。')) }}
        </p>
      </div>
    </section>

    <!-- Content List -->
    <section class="section">
      <div class="wrap articles-container">
        <!-- Filter Bar -->
        <div class="filter-bar">
          <button 
            class="filter-pill" 
            :class="{ active: selectedFilter === 'ALL' }"
            @click="selectedFilter = 'ALL'"
          >
            {{ isEn ? 'All Articles' : '全部文章' }}
          </button>
          <button 
            class="filter-pill" 
            :class="{ active: selectedFilter === 'TRADE' }"
            @click="selectedFilter = 'TRADE'"
          >
            {{ isEn ? 'International Trade' : '国际贸易' }}
          </button>
          <button 
            class="filter-pill" 
            :class="{ active: selectedFilter === 'RECOVERY' }"
            @click="selectedFilter = 'RECOVERY'"
          >
            {{ isEn ? 'Litigation & Recovery' : '诉讼与追收' }}
          </button>
          <button 
            class="filter-pill" 
            :class="{ active: selectedFilter === 'LEGACY' }"
            @click="selectedFilter = 'LEGACY'"
          >
            {{ isEn ? 'Inheritance & Legacy' : '继承与家族资产' }}
          </button>
        </div>

        <div v-if="loading" class="loading-state">
          <span>{{ isEn ? 'Loading legal insights...' : '正在加载法律专栏文章...' }}</span>
        </div>

        <div v-else-if="filteredArticles.length === 0" class="empty-state">
          <p>{{ isEn ? 'No articles found in this category.' : '该分类下暂无文章。' }}</p>
        </div>

        <div v-else class="articles-grid">
          <article v-for="item in filteredArticles" :key="item.id" class="article-card">
            <div class="card-meta-top">
              <span class="category-badge">{{ item.business }}</span>
              <span class="date">{{ item.published_at ? item.published_at.substring(0, 10) : '' }}</span>
            </div>
            <h3>
              <NuxtLink :to="isAr ? `/ar/articles/${item.slug}` : (isEs ? `/es/articles/${item.slug}` : (isEn ? `/en/articles/${item.slug}` : `/articles/${item.slug}`))">
                {{ isAr ? (item.translations?.ar?.title || item.title_en || item.title_zh) : (isEs ? (item.translations?.es?.title || item.title_en || item.title_zh) : (isEn ? (item.title_en || item.title_zh) : item.title_zh)) }}
              </NuxtLink>
            </h3>
            <p class="desc">
              {{ isAr ? (item.translations?.ar?.description || item.description_en || item.description_zh) : (isEs ? (item.translations?.es?.description || item.description_en || item.description_zh) : (isEn ? (item.description_en || item.description_zh) : item.description_zh)) }}
            </p>
            <div class="card-footer">
              <NuxtLink :to="isAr ? `/ar/articles/${item.slug}` : (isEs ? `/es/articles/${item.slug}` : (isEn ? `/en/articles/${item.slug}` : `/articles/${item.slug}`))" class="read-more">
                {{ isAr ? 'اقرأ المقال كاملاً ←' : (isEs ? 'Leer artículo completo →' : (isEn ? 'Read full article →' : '阅读全文 →')) }}
              </NuxtLink>
            </div>
          </article>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
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

const selectedFilter = ref('ALL')

// Fetched during SSR so the article list is present in the initial HTML.
const { data: articlesData, pending: loading } = await useAsyncData(
  `articles-${currentLang.value}`,
  async () => {
    try {
      const res = await getApiClient().get('/api/articles')
      if (Array.isArray(res.data) && res.data.length > 0) return res.data
    } catch (err) {
      // fallback to direct $fetch
    }
    try {
      const data: any = await $fetch('https://shenyuan-backend.vercel.app/api/articles')
      return Array.isArray(data) ? data : []
    } catch (err) {
      console.error('Failed to load articles', err)
      return []
    }
  }
)

const articles = computed<any[]>(() => articlesData.value || [])

const filteredArticles = computed(() => {
  if (selectedFilter.value === 'ALL') return articles.value
  return articles.value.filter(a => {
    const b = (a.business || '').toUpperCase()
    return b.includes(selectedFilter.value)
  })
})

const siteUrl = 'https://shenyuanlegal.com'
const canonical = computed(() => {
  if (isAr.value) return `${siteUrl}/ar/articles`
  if (isEs.value) return `${siteUrl}/es/articles`
  if (isEn.value) return `${siteUrl}/en/articles`
  return `${siteUrl}/articles`
})

useSeoMeta({
  title: () => isAr.value
    ? 'الرؤى القانونية الدولية | دراسات الممارسة وقضايا التحصيل | مكتب شينيوان للمحاماة'
    : (isEs.value
      ? 'Perspectivas Jurídicas | Práctica Internacional y Cobro de Deudas | Shenyuan'
      : (isEn.value
        ? 'Legal Insights | Cross-Border Practice & Case Studies | Shenyuan International'
        : '涉外法律专栏 | 跨境实务与案例研究 | 深远(国际)律师事务所')),
  description: () => isAr.value
    ? 'تحليلات قانونية معمقة حول نزاعات التجارة الدولية وتحصيل الديون العابرة للحدود وقضايا الإرث العائلي.'
    : (isEs.value
      ? 'Análisis jurídicos sobre litigios comerciales internacionales, recuperación de deudas transfronterizas y sucesiones.'
      : (isEn.value
        ? 'Original analyses on international trade litigation, cross-border debt recovery and multi-jurisdiction probate, written by the Shenyuan International legal team.'
        : '由深远合伙人及资深涉外律师撰写，深入剖析跨境贸易纠纷、海外欠款追索、域外财产执行及跨国遗产公证的实操要点。')),
  ogTitle: () => isAr.value ? 'الرؤى القانونية | Shenyuan International' : (isEs.value ? 'Perspectivas Jurídicas | Shenyuan' : (isEn.value ? 'Legal Insights | Shenyuan International' : '涉外法律专栏 | 深远(国际)律师事务所')),
  ogDescription: () => isAr.value ? 'دراسات عملية وتوجيهات إجرائية حول التقاضي الدولي.' : (isEs.value ? 'Análisis jurídicos sobre litigios comerciales internacionales.' : (isEn.value ? 'Cross-border practice insights and case studies.' : '跨境实务洞察与案例分析。')),
  ogType: 'website',
  ogUrl: () => canonical.value,
  ogImage: () => `${siteUrl}/og-image.png`,
  twitterCard: 'summary_large_image',
  twitterTitle: () => isAr.value ? 'الرؤى القانونية | Shenyuan International' : (isEs.value ? 'Perspectivas Jurídicas | Shenyuan' : (isEn.value ? 'Legal Insights | Shenyuan International' : '涉外法律专栏 | 深远(国际)律师事务所')),
  twitterDescription: () => isAr.value ? 'دراسات عملية وتوجيهات إجرائية حول التقاضي الدولي.' : (isEs.value ? 'Análisis jurídicos sobre litigios comerciales internacionales.' : (isEn.value ? 'Cross-border practice insights and case studies.' : '跨境实务洞察与案例分析。')),
  twitterImage: () => `${siteUrl}/og-image.png`,
})

useHead({
  htmlAttrs: computed(() => ({
    lang: isAr.value ? 'ar' : (isEs.value ? 'es' : (isEn.value ? 'en' : 'zh-CN')),
    dir: isAr.value ? 'rtl' : 'ltr',
  })),
  link: [
    { rel: 'canonical', href: () => canonical.value },
    { rel: 'alternate', hreflang: 'zh-CN', href: `${siteUrl}/articles` },
    { rel: 'alternate', hreflang: 'en', href: `${siteUrl}/en/articles` },
    { rel: 'alternate', hreflang: 'ar', href: `${siteUrl}/ar/articles` },
    { rel: 'alternate', hreflang: 'es', href: `${siteUrl}/es/articles` },
    { rel: 'alternate', hreflang: 'x-default', href: `${siteUrl}/articles` },
    { rel: 'alternate', type: 'application/rss+xml', title: 'Shenyuan Legal RSS Feed', href: `${siteUrl}/feed.xml` },
  ],
})
</script>

<style scoped>
.articles-view {
  background: var(--paper);
  color: var(--ink);
  min-height: 80vh;
}

.articles-hero {
  padding: 130px 0 60px;
  background: var(--teal-deep);
  color: #fff;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.articles-hero .eyebrow {
  color: #f1b68f;
  margin-bottom: 12px;
}
.articles-hero .eyebrow::before {
  background: #f1b68f;
}

.articles-hero h1 {
  font-family: var(--serif);
  font-size: clamp(30px, 4vw, 46px);
  margin-bottom: 16px;
  line-height: 1.2;
}

.articles-hero p {
  max-width: 720px;
  font-size: 16px;
  color: rgba(255,255,255,0.8);
  line-height: 1.7;
}

.articles-container {
  max-width: 1040px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 32px;
  flex-wrap: wrap;
}

.filter-pill {
  background: var(--surface);
  border: 1px solid var(--line);
  color: var(--muted);
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s ease;
  cursor: pointer;
}

.filter-pill:hover,
.filter-pill.active {
  background: var(--teal-deep);
  color: #fff;
  border-color: var(--teal-deep);
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--muted);
  font-size: 15px;
}

.articles-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.article-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 28px 32px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.article-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow);
}

.card-meta-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.category-badge {
  background: var(--teal-soft);
  color: var(--teal-deep);
  font-size: 11.5px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.date {
  color: var(--muted);
  font-size: 12px;
}

.article-card h3 {
  font-family: var(--serif);
  font-size: 21px;
  margin: 0 0 12px;
  line-height: 1.35;
}

.article-card h3 a {
  color: var(--ink);
  transition: color 0.2s;
}

.article-card h3 a:hover {
  color: var(--orange);
}

.desc {
  color: #435363;
  font-size: 14.5px;
  line-height: 1.65;
  margin-bottom: 20px;
}

.card-footer {
  border-top: 1px solid #f4eee4;
  padding-top: 14px;
}

.read-more {
  color: var(--teal);
  font-weight: 700;
  font-size: 13.5px;
  transition: color 0.2s;
}

.read-more:hover {
  color: var(--teal-deep);
}

/* 阿拉伯语（RTL）排版支持 */
.is-rtl {
  direction: rtl;
  text-align: right;
}

.is-rtl .eyebrow,
.is-rtl .articles-hero p,
.is-rtl .article-card h3,
.is-rtl .desc,
.is-rtl .card-footer {
  direction: rtl;
  text-align: right;
}
</style>
