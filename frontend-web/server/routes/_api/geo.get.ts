import { defineEventHandler, getHeader } from 'h3'

export default defineEventHandler((event) => {
  // 提取边缘注入的地理信息（优先 Vercel，次选 Cloudflare）
  const countryHeader =
    getHeader(event, 'x-vercel-ip-country') ||
    getHeader(event, 'cf-ipcountry') ||
    'CN'

  const cityHeader =
    getHeader(event, 'x-vercel-ip-city') ||
    getHeader(event, 'cf-ipcity') ||
    ''

  const country = String(countryHeader).trim().toUpperCase()
  let city = String(cityHeader).trim()
  try {
    city = decodeURIComponent(city)
  } catch {
    // ignore
  }

  const userAgent = getHeader(event, 'user-agent') || ''
  const isBot = /googlebot|bingbot|baiduspider|yandex|duckduckbot|slurp|twitterbot|facebookexternalhit|ahrefsbot|semrushbot/i.test(userAgent)

  return {
    country,
    city,
    isBot,
    timestamp: Date.now(),
  }
})
