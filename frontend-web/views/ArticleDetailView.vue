<template>
  <div class="article-detail-view" :class="{ 'is-rtl': isAr }">
    <div class="wrap detail-container">
      <div v-if="loading" class="loading-box">
        {{ isAr ? 'جارٍ تحميل تفاصيل المقال القانوني...' : (isEn ? 'Loading article details...' : '正在加载文章内容...') }}
      </div>

      <article v-else-if="article" class="detail-paper" :class="{ 'is-rtl': isAr }">
        <NuxtLink :to="isAr ? '/ar/articles' : (isEn ? '/en/articles' : '/articles')" class="back-nav">
          <span v-if="isAr">&rarr; العودة إلى الرؤى القانونية</span>
          <span v-else>&larr; {{ isEn ? 'Back to legal insights' : '返回法律专栏' }}</span>
        </NuxtLink>

        <header class="article-header">
          <div class="meta-row">
            <span class="category-tag">{{ article.business }}</span>
            <span class="date">{{ article.published_at ? article.published_at.substring(0, 10) : '' }}</span>
          </div>
          <h1 class="article-title">{{ title }}</h1>
        </header>

        <!-- GEO & Key Takeaways / Executive Summary Card -->
        <div v-if="keyTakeaways.length" class="geo-takeaways-card">
          <div class="takeaways-header">
            <span class="takeaways-icon">⚡</span>
            <h4>{{ isEn ? 'Executive Summary & Key Action Points' : '核心实务要点速读（TL;DR）' }}</h4>
          </div>
          <ul class="takeaways-list">
            <li v-for="(item, idx) in keyTakeaways" :key="idx">{{ item }}</li>
          </ul>
        </div>

        <div class="article-body">
          <div class="content-html" v-html="renderedBody"></div>
        </div>

        <!-- Article FAQ & Rich Snippet Module -->
        <div v-if="articleFaqs.length" class="article-faq-section">
          <h3 class="faq-head-title">{{ isEn ? 'Frequently Asked Questions' : '常见问题解答与实务要点' }}</h3>
          <div class="faq-accordion">
            <details v-for="(f, i) in articleFaqs" :key="i" class="art-faq-item">
              <summary>{{ f.question }}</summary>
              <p>{{ f.answer }}</p>
            </details>
          </div>
        </div>

        <div class="article-disclaimer">
          <strong>{{ isEn ? 'Legal Disclaimer' : '免责声明' }}：</strong>
          <span>{{ isEn 
            ? 'The content of this article represents academic analysis and practice observations of Shenyuan International and does not constitute formal legal opinion or attorney-client relationship for any specific matter. For actionable counsel, please arrange a formal case review.' 
            : '本文内容仅供涉外法律实务研讨与一般信息参考，不构成针对任何具体案件的正式法律意见或委托关系。具体法律程序须结合案件全部证据、事实及相关管辖区法规一案一议。' }}</span>
        </div>

        <!-- Related Articles / Topic Cluster -->
        <div v-if="relatedArticles.length" class="related-articles-section">
          <div class="related-head">
            <h3>{{ isEn ? 'Related Legal Insights' : '相关法律实务与推荐阅读' }}</h3>
            <NuxtLink :to="isEn ? '/en/articles' : '/articles'" class="more-link">
              {{ isEn ? 'View all' : '查看全部' }} &rarr;
            </NuxtLink>
          </div>
          <div class="related-grid">
            <NuxtLink
              v-for="rel in relatedArticles"
              :key="rel.id"
              :to="isEn ? `/en/articles/${rel.slug}` : `/articles/${rel.slug}`"
              class="related-card"
            >
              <span class="rel-badge">{{ rel.business }}</span>
              <h4 class="rel-title">{{ isEn ? (rel.title_en || rel.title_zh) : rel.title_zh }}</h4>
              <p class="rel-desc">{{ isEn ? (rel.description_en || rel.description_zh) : rel.description_zh }}</p>
            </NuxtLink>
          </div>
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
const currentLang = computed<'zh' | 'en' | 'ar' | 'es'>(() => {
  if (route.path.startsWith('/ar')) return 'ar'
  if (route.path.startsWith('/es')) return 'es'
  if (route.path.startsWith('/en')) return 'en'
  return 'zh'
})
const isAr = computed(() => currentLang.value === 'ar')
const isEs = computed(() => currentLang.value === 'es')
const isEn = computed(() => currentLang.value === 'en')

// Article bodies are fetched during SSR so crawlers receive the full text,
// title, canonical, hreflang and JSON-LD in the initial HTML response.
// Load all articles to derive related recommendations within the same topic cluster
const { data: allArticles } = await useAsyncData(
  'all-articles-cluster',
  async () => {
    try {
      const res = await getApiClient().get('/api/articles')
      if (Array.isArray(res.data) && res.data.length > 0) return res.data
    } catch (e) {
      // fallback to direct $fetch
    }
    try {
      const data: any = await $fetch('https://shenyuan-backend.vercel.app/api/articles')
      return Array.isArray(data) ? data : []
    } catch (e) {
      return []
    }
  }
)

// FAQ dataset mapped by business category for on-page Q&A and FAQPage JSON-LD
// Extract structured key takeaways / executive summary for GEO & rapid answer engines
const keyTakeaways = computed(() => {
  const art: any = article.value
  if (!art) return []
  const desc = isEn.value ? (art.description_en || art.description_zh) : art.description_zh
  const b = art.business || 'trade'

  if (isEn.value) {
    if (b === 'trade') {
      return [
        'Document Trail: Secure contracts, invoices, bills of lading, customs clearances, and bank slips before formal notice.',
        'Limitation Audit: Confirm the applicable limitation window (commonly 2–6 years depending on foreign or PRC law).',
        'Structured Notice: Issue a formal bilingual attorney demand letter to set firm cure deadlines and preserve rights.'
      ]
    } else if (b === 'recovery') {
      return [
        'Asset Tracing: Verify corporate registry, property, bank, and transaction records prior to alerting the debtor.',
        'Preservation Orders: Apply for freezing injunctions or interim measures to safeguard enforceable assets.',
        'Cross-Border Enforcement: Enforce arbitral awards via New York Convention or money judgments via bilateral reciprocity.'
      ]
    } else {
      return [
        'Jurisdiction Mapping: Real property is strictly governed by the lex situs; cross-border wills require local probate.',
        'Notarisation & Apostille: Kinship, wills, and death certificates must be apostilled/legalised for local admissibility.',
        'Estate Inventory: Account for tax filings, foreign exchange regulations, and creditor liabilities before distribution.'
      ]
    }
  } else {
    if (b === 'trade') {
      return [
        '锁定证据底牌：在正式发函前，集中保存合同、订单、发票、提单、报关单及微信邮件对账凭单原件。',
        '核实诉讼时效：跨境商事时效常见为 2~6 年，若客户曾书面认账，可重新起算或中断，务必尽早确权。',
        '阶梯维权策略：先发正式涉外律师函设定限期和解窗口；谈判无果时果断衔接仲裁或涉外诉讼。'
      ]
    } else if (b === 'recovery') {
      return [
        '境内外财产调查：重点核查债务人名下房产、股权、银行存款及关联交易，摸清真实执行能力。',
        '同步申请财产保全：在债务人转移或隐匿资产前取得法院冻结令，确保护城河与执行标的安全。',
        '判决/裁决跨国兑现：仲裁裁决依托《纽约公约》在160多国直接申请执行，涉外判决依互惠/条约推进。'
      ]
    } else {
      return [
        '区分不动产与动产属地：跨境不动产继承适用遗产所在地法，国内遗嘱通常需经当地遗嘱认证（Probate）。',
        '一揽子公证与海牙认证：亲属关系证明、死亡证明及授权委托书需一次性做足公证与海牙附加证明书（Apostille）。',
        '统筹税费与外汇合规：兼顾境外遗产税申报与合法继承资金合规结汇汇回，避免程序返工与合规风险。'
      ]
    }
  }
})

const articleFaqs = computed(() => {
  const art: any = article.value
  if (!art) return []
  const b = art.business || 'trade'

  if (b === 'trade') {
    return isEn.value ? [
      {
        question: 'What is the most critical first step in an international trade payment dispute?',
        answer: 'Immediately preserve all documentary evidence (contracts, bills of lading, customs declarations, communication trails, and acknowledged statements of account) and verify whether the statute of limitations is at risk.'
      },
      {
        question: 'Can cross-border trade disputes be resolved without going to court?',
        answer: 'Yes. A structured bilingual attorney demand letter combined with staged commercial negotiation and asset-tracing pressure resolves a substantial portion of cross-border debt defaults.'
      }
    ] : [
      {
        question: '发生跨境贸易货款拖欠时，第一步最关键的动作是什么？',
        answer: '第一时间固定全部书面与电子证据链（合同、提单、报关单、对账单与邮件微信记录），并立即核实涉外法律适用的诉讼时效，避免权利因拖延而灭失。'
      },
      {
        question: '涉外贸易纠纷必须到境外打官司吗？是否有更高效的解决途径？',
        answer: '不一定。大部分跨国商事欠款可通过专业涉外律师函、针对性调查财产线索施加谈判压力、以及分期担保协议在诉讼前达成和解，大幅节约境外诉讼周期与成本。'
      }
    ]
  } else if (b === 'recovery') {
    return isEn.value ? [
      {
        question: 'Can a Chinese court judgment or arbitral award be enforced overseas?',
        answer: 'Yes. Arbitral awards are widely enforceable under the New York Convention across 160+ jurisdictions. Court judgments can be enforced in jurisdictions recognizing reciprocity or bilateral treaties.'
      },
      {
        question: 'What should creditors do if a debtor attempts to hide or transfer assets abroad?',
        answer: 'Initiate lawful cross-border asset tracing promptly and apply for freezing orders or interim preservation relief before the competent local court to secure enforceable assets.'
      }
    ] : [
      {
        question: '中国法院的胜诉判决或仲裁裁决能否在境外申请执行？',
        answer: '可以。仲裁裁决可通过《纽约公约》在 160 多个缔约国申请承认与执行；法院判决可依据双边司法协助条约或互惠原则在境外目标法院申请承认后执行。'
      },
      {
        question: '如果债务人将资金或房产转移至海外，债权人该如何应对？',
        answer: '应尽早通过合法途径开展境内外资产线索调查，并在具备管辖权的法域申请临时财产保全、冻结令或撤销恶意转移之诉，防止最终执行落空。'
      }
    ]
  } else {
    // legacy
    return isEn.value ? [
      {
        question: 'Does a will made in China automatically govern overseas properties and accounts?',
        answer: 'Not necessarily. Real estate typically follows the lex situs (law of the jurisdiction where the property is located). Cross-border inheritance often requires local probate or estate administration.'
      },
      {
        question: 'What documents are required for heirs in China to claim an overseas inheritance?',
        answer: 'Heirs usually need notarized and legalized/apostilled proof of kinship, local death certificates, wills (if any), and estate inventories to initiate formal local probate proceedings.'
      }
    ] : [
      {
        question: '在中国立的遗嘱能否直接处分海外的不动产和银行存款？',
        answer: '不一定。涉外继承中不动产通常适用不动产所在地法律，中国遗嘱在海外普通法系国家常需通过当地遗嘱认证（Probate）程序并检验形式合规性。'
      },
      {
        question: '国内继承人办理海外亲属遗产继承通常需要准备哪些公证认证文件？',
        answer: '一般需要办理死亡证明、亲属关系证明、法定遗嘱（如有）及海牙认证（Apostille）或领事认证，并委托当地具有执业资质的律师向遗产所在地法院申请遗产清点与过户。'
      }
    ]
  }
})

const relatedArticles = computed(() => {
  const current = article.value
  if (!current || !allArticles.value) return []
  return allArticles.value
    .filter((a: any) => a.slug !== current.slug && (a.business === current.business || !current.business))
    .slice(0, 3)
})

const { data: article, pending: loading } = await useAsyncData(
  `article-${currentLang.value}-${route.params.slug}`,
  async () => {
    const slug = route.params.slug
    try {
      const res = await getApiClient().get(`/api/articles/${slug}`)
      if (res?.data?.slug) return res.data
    } catch (err) {
      // fallback to direct $fetch
    }
    try {
      const data: any = await $fetch(`https://shenyuan-backend.vercel.app/api/articles/${slug}`)
      if (data?.slug) return data
    } catch (err) {
      console.error('Failed to load article detail', err)
    }
    return null
  }
)

// 轻量级安全 Markdown 语义解析器（增强 SEO 语义、表格解析与阅读排版）
function parseMarkdownToHtml(md: string): string {
  if (!md) return ''
  const lines = md.replace(/\r\n/g, '\n').split('\n')
  const htmlParts: string[] = []
  let inList = false
  let inTable = false
  let tableHeaders: string[] = []
  let tableRows: string[][] = []

  const flushTable = () => {
    if (!inTable) return
    let tHtml = '<div class="article-table-wrap"><table class="article-table">'
    if (tableHeaders.length) {
      tHtml += '<thead><tr>'
      for (const h of tableHeaders) {
        tHtml += `<th>${formatInline(h)}</th>`
      }
      tHtml += '</tr></thead>'
    }
    if (tableRows.length) {
      tHtml += '<tbody>'
      for (const row of tableRows) {
        tHtml += '<tr>'
        for (const cell of row) {
          tHtml += `<td>${formatInline(cell)}</td>`
        }
        tHtml += '</tr>'
      }
      tHtml += '</tbody>'
    }
    tHtml += '</table></div>'
    htmlParts.push(tHtml)
    inTable = false
    tableHeaders = []
    tableRows = []
  }

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i].trimEnd()
    const trimmed = line.trim()

    // 表格解析：行以 | 开头并以 | 结尾且含有分割管道
    const isTableRow = trimmed.startsWith('|') && trimmed.endsWith('|') && trimmed.includes('|')

    if (isTableRow) {
      if (inList) {
        htmlParts.push('</ul>')
        inList = false
      }
      const rawCells = trimmed.split('|').slice(1, -1).map(c => c.trim())
      // 检查是否为分隔行，例如 |---|---|---|
      const isSeparator = rawCells.length > 0 && rawCells.every(c => /^:?-+:?$/.test(c))
      if (isSeparator) {
        continue
      }
      if (!inTable) {
        inTable = true
        tableHeaders = rawCells
      } else {
        tableRows.push(rawCells)
      }
      continue
    } else if (inTable) {
      flushTable()
    }

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
  if (inTable) {
    flushTable()
  }

  return htmlParts.join('\n')
}

function formatInline(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, text, url) => `<a href="${url}" class="article-link">${text}</a>`)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
}

const arTrans = computed(() => {
  const trans = (article.value as any)?.translations
  return (trans && typeof trans === 'object') ? trans.ar : null
})

const esTrans = computed(() => {
  const trans = (article.value as any)?.translations
  return (trans && typeof trans === 'object') ? trans.es : null
})

const renderedBody = computed(() => {
  if (!article.value) return ''
  if (isAr.value) {
    if (arTrans.value?.body) {
      return parseMarkdownToHtml(arTrans.value.body)
    }
    const fallbackText = `> ⚠️ **ملاحظة:** الترجمة العربية لهذا الدليل قيد الاعتماد والمراجعة القانونية.\n\n` +
      (article.value.body_en || article.value.body_zh)
    return parseMarkdownToHtml(fallbackText)
  }
  if (isEs.value) {
    if (esTrans.value?.body) {
      return parseMarkdownToHtml(esTrans.value.body)
    }
    const fallbackText = `> ⚠️ **Nota:** La versión oficial en español de esta guía jurídica está en proceso de revisión legal.\n\n` +
      (article.value.body_en || article.value.body_zh)
    return parseMarkdownToHtml(fallbackText)
  }
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
  if (isAr.value && arTrans.value?.title) return arTrans.value.title
  if (isEs.value && esTrans.value?.title) return esTrans.value.title
  return isEn.value ? (art.title_en || art.title_zh) : art.title_zh
})

const description = computed(() => {
  const art: any = article.value
  if (!art) return ''
  if (isAr.value && arTrans.value?.description) return arTrans.value.description
  if (isEs.value && esTrans.value?.description) return esTrans.value.description
  return isEn.value ? (art.description_en || art.description_zh) : art.description_zh
})

const zhPath = computed(() => `/articles/${route.params.slug}`)
const enPath = computed(() => `/en/articles/${route.params.slug}`)
const arPath = computed(() => `/ar/articles/${route.params.slug}`)
const esPath = computed(() => `/es/articles/${route.params.slug}`)

const canonical = computed(() => {
  if (isAr.value) return `${siteUrl}${arPath.value}`
  if (isEs.value) return `${siteUrl}${esPath.value}`
  if (isEn.value) return `${siteUrl}${enPath.value}`
  return `${siteUrl}${zhPath.value}`
})

const siteName = computed(() => {
  if (isAr.value) return 'مكتب شينيوان الدولي للمحاماة (Shenyuan International)'
  if (isEs.value) return 'Bufete de Abogados Internacional Shenyuan'
  return isEn.value ? 'Shenyuan International Law Firm' : '深远(国际)律师事务所'
})

const hasArabic = computed(() => {
  const trans = (article.value as any)?.translations
  return Boolean(trans && trans.ar && (trans.ar.title || trans.ar.body))
})

const hasSpanish = computed(() => {
  const trans = (article.value as any)?.translations
  return Boolean(trans && trans.es && (trans.es.title || trans.es.body))
})

const alternateLinks = computed(() => {
  const links = [
    { rel: 'canonical', href: () => canonical.value },
    { rel: 'alternate', hreflang: 'zh-CN', href: () => `${siteUrl}${zhPath.value}` },
    { rel: 'alternate', hreflang: 'en', href: () => `${siteUrl}${enPath.value}` },
  ]
  // 严格遵守 SEO 原则：当且仅当存在真实阿语/西语内容时，向搜索引擎声明 hreflang
  if (hasArabic.value || isAr.value) {
    links.push({ rel: 'alternate', hreflang: 'ar', href: () => `${siteUrl}${arPath.value}` })
  }
  if (hasSpanish.value || isEs.value) {
    links.push({ rel: 'alternate', hreflang: 'es', href: () => `${siteUrl}${esPath.value}` })
  }
  links.push({ rel: 'alternate', hreflang: 'x-default', href: () => `${siteUrl}${zhPath.value}` })
  return links
})

useSeoMeta({
  title: () => title.value ? `${title.value} | ${siteName.value}` : siteName.value,
  description: () => description.value,
  ogTitle: () => title.value || siteName.value,
  ogDescription: () => description.value,
  ogType: 'article',
  ogUrl: () => canonical.value,
  ogImage: () => `${siteUrl}/og-image.png`,
  twitterCard: 'summary_large_image',
  twitterTitle: () => title.value || siteName.value,
  twitterDescription: () => description.value,
  twitterImage: () => `${siteUrl}/og-image.png`,
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

const faqJsonLd = computed(() => {
  if (!articleFaqs.value.length) return null
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    'inLanguage': isEn.value ? 'en' : 'zh-CN',
    'mainEntity': articleFaqs.value.map((f: any) => ({
      '@type': 'Question',
      'name': f.question,
      'acceptedAnswer': {
        '@type': 'Answer',
        'text': f.answer,
      },
    })),
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
  htmlAttrs: computed(() => ({
    lang: isAr.value ? 'ar' : (isEn.value ? 'en' : 'zh-CN'),
    dir: isAr.value ? 'rtl' : 'ltr',
  })),
  link: alternateLinks,
  script: computed(() => {
    const scripts: any[] = []
    if (articleJsonLd.value) {
      scripts.push({ type: 'application/ld+json', innerHTML: JSON.stringify(articleJsonLd.value) })
    }
    if (breadcrumbJsonLd.value) {
      scripts.push({ type: 'application/ld+json', innerHTML: JSON.stringify(breadcrumbJsonLd.value) })
    }
    if (faqJsonLd.value) {
      scripts.push({ type: 'application/ld+json', innerHTML: JSON.stringify(faqJsonLd.value) })
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

.geo-takeaways-card {
  background: #fbf9f4;
  border: 1px solid #e2d8c7;
  border-left: 4px solid var(--teal);
  border-radius: 8px;
  padding: 20px 24px;
  margin-bottom: 32px;
}

.takeaways-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.takeaways-icon {
  font-size: 16px;
  color: var(--orange);
}

.takeaways-header h4 {
  font-family: var(--serif);
  font-size: 16.5px;
  color: var(--teal-deep);
  margin: 0;
}

.takeaways-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}

.takeaways-list li {
  position: relative;
  padding-left: 20px;
  font-size: 13.5px;
  line-height: 1.6;
  color: #3b4b59;
}

.takeaways-list li::before {
  content: "•";
  position: absolute;
  left: 6px;
  top: 0;
  color: var(--gold);
  font-size: 18px;
  line-height: 1.4;
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
  text-align: left;
  letter-spacing: normal;
  word-spacing: normal;
  word-break: break-word;
}

:deep(.content-html a.article-link) {
  color: var(--teal);
  font-weight: 500;
  text-decoration: underline;
  text-underline-offset: 3px;
  transition: color 0.15s ease;
}
:deep(.content-html a.article-link:hover) {
  color: var(--gold);
}

/* 规范化法务表格（严格向左对齐，字间距自然） */
:deep(.article-table-wrap) {
  width: 100%;
  overflow-x: auto;
  margin: 24px 0 28px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

:deep(.article-table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  line-height: 1.6;
  text-align: left;
  letter-spacing: normal;
  word-spacing: normal;
}

:deep(.article-table th) {
  background: #f8fafc;
  color: var(--teal-deep);
  font-weight: 700;
  padding: 12px 16px;
  text-align: left;
  border-bottom: 2px solid #e2e8f0;
  border-right: 1px solid #f1f5f9;
  white-space: nowrap;
  letter-spacing: normal;
  word-spacing: normal;
}

:deep(.article-table th:last-child) {
  border-right: none;
}

:deep(.article-table td) {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f1f5f9;
  border-right: 1px solid #f8fafc;
  color: #334155;
  vertical-align: top;
  letter-spacing: normal;
  word-spacing: normal;
}

:deep(.article-table td:last-child) {
  border-right: none;
}

:deep(.article-table tbody tr:nth-child(even)) {
  background: rgba(248, 250, 252, 0.6);
}

:deep(.article-table tbody tr:hover) {
  background: rgba(241, 245, 249, 0.8);
}

:deep(.article-table tbody tr:last-child td) {
  border-bottom: none;
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

.article-faq-section {
  margin: 36px 0 28px;
  padding-top: 24px;
  border-top: 1px solid var(--line);
}

.faq-head-title {
  font-family: var(--serif);
  font-size: 19px;
  color: var(--teal-deep);
  margin: 0 0 16px;
}

.faq-accordion {
  display: grid;
  gap: 12px;
}

.art-faq-item {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px 20px;
}

.art-faq-item summary {
  font-size: 15px;
  font-weight: 700;
  color: var(--teal-deep);
  cursor: pointer;
  list-style: none;
}
.art-faq-item summary::-webkit-details-marker { display: none; }
.art-faq-item summary::after {
  content: "+";
  float: right;
  color: var(--gold);
  font-weight: 700;
}
.art-faq-item[open] summary::after { content: "−"; }

.art-faq-item p {
  margin: 12px 0 0;
  font-size: 14px;
  line-height: 1.7;
  color: #3b4b59;
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

.related-articles-section {
  margin: 40px 0 36px;
  padding-top: 32px;
  border-top: 1px solid var(--line);
}

.related-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.related-head h3 {
  font-family: var(--serif);
  font-size: 20px;
  color: var(--teal-deep);
  margin: 0;
}

.related-head .more-link {
  font-size: 13px;
  color: var(--teal);
  font-weight: 700;
}
.related-head .more-link:hover {
  color: var(--teal-deep);
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.related-card {
  background: var(--paper-card);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 18px 16px;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.related-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.04);
}

.rel-badge {
  align-self: flex-start;
  font-size: 11px;
  font-weight: 700;
  color: var(--teal-deep);
  background: var(--teal-soft);
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.rel-title {
  font-size: 14.5px;
  color: var(--ink);
  line-height: 1.4;
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.rel-desc {
  font-size: 12.5px;
  color: var(--muted);
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@media (max-width: 768px) {
  .related-grid {
    grid-template-columns: 1fr;
  }
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

/* 阿拉伯语（RTL）文字与排版适配 */
.is-rtl {
  direction: rtl;
  text-align: right;
}

.is-rtl .back-nav {
  display: inline-block;
  text-align: right;
}

.is-rtl :deep(.content-html p),
.is-rtl :deep(.content-html h2),
.is-rtl :deep(.content-html h3),
.is-rtl :deep(.content-html h4),
.is-rtl :deep(.content-html ul) {
  direction: rtl;
  text-align: right;
}

.is-rtl :deep(.article-table th),
.is-rtl :deep(.article-table td) {
  text-align: right;
  direction: rtl;
}

.is-rtl :deep(.content-html blockquote) {
  border-left: none;
  border-right: 4px solid var(--teal);
  border-radius: 4px 0 0 4px;
}
</style>
