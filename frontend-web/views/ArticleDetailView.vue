<template>
  <div class="article-detail-view">
    <div class="wrap detail-container">
      <div v-if="loading" class="loading-box">
        {{ isEn ? 'Loading article details...' : '正在加载文章内容...' }}
      </div>

      <article v-else-if="article" class="detail-paper">
        <NuxtLink :to="isEn ? '/en/articles' : '/articles'" class="back-nav">
          &larr; {{ isEn ? 'Back to legal insights' : '返回法律专栏' }}
        </NuxtLink>

        <header class="article-header">
          <div class="meta-row">
            <span class="category-tag">{{ article.business }}</span>
            <span class="date">{{ article.published_at ? article.published_at.substring(0, 10) : '' }}</span>
          </div>
          <h1 class="article-title">{{ isEn ? (article.title_en || article.title_zh) : article.title_zh }}</h1>
        </header>

        <div class="article-body">
          <div class="content-html" v-html="renderedBody"></div>
        </div>

        <div class="article-disclaimer">
          <strong>{{ isEn ? 'Legal Disclaimer' : '免责声明' }}：</strong>
          <span>{{ isEn 
            ? 'The content of this article represents academic analysis and practice observations of Shenyuan International and does not constitute formal legal opinion or attorney-client relationship for any specific matter. For actionable counsel, please arrange a formal case review.' 
            : '本文内容仅供涉外法律实务研讨与一般信息参考，不构成针对任何具体案件的正式法律意见或委托关系。具体法律程序须结合案件全部证据、事实及相关管辖区法规一案一议。' }}</span>
        </div>

        <!-- Article Bottom Consultation Box -->
        <div class="bottom-consult-box">
          <div class="consult-copy">
            <h3>{{ isEn ? 'Facing a similar cross-border legal issue?' : '遇到类似跨境纠纷或需要法律协助？' }}</h3>
            <p>{{ isEn 
              ? 'Our bilingual dispute resolution team can provide an initial case review within 24 hours.' 
              : '提交您的案情简述或扫码微信沟通，我们将在 24 小时内为您出具初步分析建议。' }}</p>
          </div>
          <NuxtLink :to="isEn ? '/en#intake' : '/#intake'" class="button button-primary">
            {{ isEn ? 'Free Legal Consultation →' : '免费法律咨询评估 →' }}
          </NuxtLink>
        </div>
      </article>

      <div v-else class="not-found">
        <p>{{ isEn ? 'Article not found.' : '未找到相关文章。' }}</p>
        <NuxtLink :to="isEn ? '/en/articles' : '/articles'" class="button button-outline">
          {{ isEn ? 'Return to Articles' : '返回专栏列表' }}
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

// Article bodies are fetched during SSR so crawlers receive the full text,
// title, canonical, hreflang and JSON-LD in the initial HTML response.
const { data: article, pending: loading } = await useAsyncData(
  `article-${isEn.value ? 'en' : 'zh'}-${route.params.slug}`,
  async () => {
    try {
      const res = await getApiClient().get(`/api/articles/${route.params.slug}`)
      return res.data
    } catch (err) {
      console.error('Failed to load article detail', err)
      return null
    }
  }
)

// 轻量级安全 Markdown 语义解析器（增强 SEO 语义与阅读排版）
function parseMarkdownToHtml(md: string): string {
  if (!md) return ''
  const lines = md.replace(/\r\n/g, '\n').split('\n')
  const htmlParts: string[] = []
  let inList = false

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i].trimEnd()

    // 列表处理
    if (/^[-*]\s+/.test(line)) {
      if (!inList) {
        htmlParts.push('<ul class="article-list">')
        inList = true
      }
      const itemText = formatInline(line.replace(/^[-*]\s+/, ''))
      htmlParts.push(`<li>${itemText}</li>`)
      continue
    } else if (inList) {
      htmlParts.push('</ul>')
      inList = false
    }

    if (!line.trim()) {
      continue
    }

    // 标题处理
    if (line.startsWith('#### ')) {
      htmlParts.push(`<h4>${formatInline(line.slice(5))}</h4>`)
    } else if (line.startsWith('### ')) {
      htmlParts.push(`<h3>${formatInline(line.slice(4))}</h3>`)
    } else if (line.startsWith('## ')) {
      htmlParts.push(`<h2>${formatInline(line.slice(3))}</h2>`)
    } else if (line.startsWith('# ')) {
      // 避免正文中重复大标题，转为 h2
      htmlParts.push(`<h2>${formatInline(line.slice(2))}</h2>`)
    } else if (line.startsWith('> ')) {
      htmlParts.push(`<blockquote><p>${formatInline(line.slice(2))}</p></blockquote>`)
    } else {
      htmlParts.push(`<p>${formatInline(line)}</p>`)
    }
  }

  if (inList) {
    htmlParts.push('</ul>')
  }

  return htmlParts.join('\n')
}

function formatInline(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
}

const renderedBody = computed(() => {
  if (!article.value) return ''
  const raw = isEn.value
    ? (article.value.body_en || article.value.body_zh)
    : (article.value.body_zh || article.value.body_en)
  return parseMarkdownToHtml(raw)
})

// ---- SEO --------------------------------------------------------------
const siteUrl = 'https://shenyuanlegal.com'

const title = computed(() => {
  const art: any = article.value
  if (!art) return ''
  return isEn.value ? (art.title_en || art.title_zh) : art.title_zh
})

const description = computed(() => {
  const art: any = article.value
  if (!art) return ''
  return isEn.value ? (art.description_en || art.description_zh) : art.description_zh
})

const zhPath = computed(() => `/articles/${route.params.slug}`)
const enPath = computed(() => `/en/articles/${route.params.slug}`)
const canonical = computed(() => `${siteUrl}${isEn.value ? enPath.value : zhPath.value}`)
const siteName = computed(() => isEn.value ? 'Shenyuan International Law Firm' : '深远(国际)律师事务所')

useSeoMeta({
  title: () => title.value ? `${title.value} | ${siteName.value}` : siteName.value,
  description: () => description.value,
  ogTitle: () => title.value || siteName.value,
  ogDescription: () => description.value,
  ogType: 'article',
  ogUrl: () => canonical.value,
  twitterTitle: () => title.value || siteName.value,
  twitterDescription: () => description.value,
})

const articleJsonLd = computed(() => {
  const art: any = article.value
  if (!art) return null
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    'headline': title.value,
    'description': description.value,
    'datePublished': art.published_at || art.created_at,
    'dateModified': art.updated_at || art.published_at,
    'inLanguage': isEn.value ? 'en' : 'zh-CN',
    'author': {
      '@type': 'Organization',
      'name': 'Shenyuan International Legal Team',
      'url': siteUrl,
    },
    'publisher': {
      '@type': 'Organization',
      'name': 'Shenyuan International Law Firm',
      'logo': {
        '@type': 'ImageObject',
        'url': `${siteUrl}/favicon.svg`,
      },
    },
    'mainEntityOfPage': {
      '@type': 'WebPage',
      '@id': canonical.value,
    },
  }
})

const breadcrumbJsonLd = computed(() => {
  if (!article.value) return null
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
        'name': isEn.value ? 'Legal Insights' : '涉外法律专栏',
        'item': isEn.value ? `${siteUrl}/en/articles` : `${siteUrl}/articles`,
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
    if (articleJsonLd.value) {
      scripts.push({ type: 'application/ld+json', innerHTML: JSON.stringify(articleJsonLd.value) })
    }
    if (breadcrumbJsonLd.value) {
      scripts.push({ type: 'application/ld+json', innerHTML: JSON.stringify(breadcrumbJsonLd.value) })
    }
    return scripts
  }),
})
</script>

<style scoped>
.article-detail-view {
  background: var(--paper);
  color: var(--ink);
  padding: 130px 0 80px;
  min-height: 85vh;
}

.detail-container {
  max-width: 860px;
}

.loading-box,
.not-found {
  text-align: center;
  padding: 60px 20px;
  color: var(--muted);
}

.detail-paper {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 44px 48px;
  box-shadow: 0 4px 25px rgba(0,0,0,0.03);
}

.back-nav {
  display: inline-block;
  color: var(--teal);
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 24px;
  transition: color 0.2s;
}

.back-nav:hover {
  color: var(--teal-deep);
}

.article-header {
  border-bottom: 1px solid var(--line);
  padding-bottom: 24px;
  margin-bottom: 32px;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.category-tag {
  background: var(--teal-soft);
  color: var(--teal-deep);
  font-size: 11.5px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 12px;
  text-transform: uppercase;
}

.date {
  color: var(--muted);
  font-size: 13px;
}

.article-title {
  font-family: var(--serif);
  font-size: clamp(26px, 3.5vw, 36px);
  color: var(--ink);
  line-height: 1.25;
  margin: 0;
}

.article-body {
  font-size: 16px;
  line-height: 1.85;
  color: #2c3e50;
  margin-bottom: 40px;
}

/* 语义化排版增强 */
.content-html {
  font-size: 16px;
  line-height: 1.8;
  color: #2c3e50;
}

:deep(.content-html h2) {
  font-family: var(--serif);
  font-size: 22px;
  color: var(--teal-deep);
  margin: 32px 0 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

:deep(.content-html h3) {
  font-size: 18px;
  color: #1f2937;
  margin: 24px 0 12px;
}

:deep(.content-html p) {
  margin: 0 0 18px;
  text-align: justify;
}

:deep(.content-html strong) {
  color: #111827;
  font-weight: 600;
}

:deep(.content-html ul.article-list) {
  margin: 0 0 20px 20px;
  padding-left: 10px;
}

:deep(.content-html ul.article-list li) {
  margin-bottom: 8px;
}

:deep(.content-html blockquote) {
  margin: 20px 0;
  padding: 14px 20px;
  background: #f8fafc;
  border-left: 4px solid var(--teal);
  color: #475569;
  font-style: italic;
  border-radius: 0 4px 4px 0;
}

:deep(.content-html code) {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 14px;
  color: #0f172a;
}

.article-disclaimer {
  background: #fdfbf7;
  border: 1px solid #e1d8c9;
  border-left: 4px solid var(--gold);
  border-radius: 6px;
  padding: 16px 20px;
  font-size: 12.5px;
  line-height: 1.7;
  color: #5c6873;
  margin-bottom: 36px;
}

.article-disclaimer strong {
  color: var(--teal-deep);
}

.bottom-consult-box {
  background: #f4eee4;
  border: 1px solid #e1d8c9;
  border-radius: 8px;
  padding: 24px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.consult-copy h3 {
  font-family: var(--serif);
  font-size: 18px;
  color: var(--teal-deep);
  margin: 0 0 6px;
}

.consult-copy p {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
}

.bottom-consult-box .button {
  flex-shrink: 0;
}

@media (max-width: 680px) {
  .detail-paper {
    padding: 28px 20px;
  }
  .bottom-consult-box {
    flex-direction: column;
    align-items: stretch;
  }
  .bottom-consult-box .button {
    width: 100%;
  }
}
</style>
