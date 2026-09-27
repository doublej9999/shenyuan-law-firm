import axios from 'axios'

function escapeXml(unsafe: string): string {
  return (unsafe || '').replace(/[<>&'"]/g, (c) => {
    switch (c) {
      case '<': return '&lt;'
      case '>': return '&gt;'
      case '&': return '&amp;'
      case '\'': return '&apos;'
      case '"': return '&quot;'
      default: return c
    }
  })
}

function toRfc822(dateStr?: string): string {
  const d = dateStr ? new Date(dateStr) : new Date()
  return isNaN(d.getTime()) ? new Date().toUTCString() : d.toUTCString()
}

export default defineEventHandler(async (event) => {
  setHeader(event, 'content-type', 'application/xml; charset=utf-8')
  setHeader(event, 'cache-control', 'public, s-maxage=3600, stale-while-revalidate=86400')

  const config = useRuntimeConfig(event)
  const base = String(config.public.apiUrl || '').replace(/\/+$/, '')
  const siteUrl = 'https://shenyuanlegal.com'

  let articles: any[] = []
  try {
    const res = await axios.get(`${base}/api/articles`, { timeout: 10000 })
    articles = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    console.error('Failed to fetch articles for RSS feed', e)
  }

  const itemsXml = articles.slice(0, 30).map((art: any) => {
    const title = escapeXml(art.title_zh || art.title_en || '')
    const link = `${siteUrl}/articles/${art.slug}`
    const pubDate = toRfc822(art.published_at || art.created_at)
    const desc = escapeXml(art.description_zh || art.description_en || '')
    const category = escapeXml(art.business || 'general')

    return `    <item>
      <title>${title}</title>
      <link>${link}</link>
      <guid isPermaLink="true">${link}</guid>
      <pubDate>${pubDate}</pubDate>
      <description>${desc}</description>
      <category>${category}</category>
    </item>`
  }).join('\n')

  const rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>深远(国际)律师事务所 · 涉外法律实务专栏</title>
    <link>${siteUrl}/articles</link>
    <description>深远(国际)律师事务所跨境商事争议解决、海外债权追收、跨国继承与家族财富保护最新实操指南与案例研析。</description>
    <language>zh-CN</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <atom:link href="${siteUrl}/feed.xml" rel="self" type="application/rss+xml" />
${itemsXml}
  </channel>
</rss>`

  return rss
})
