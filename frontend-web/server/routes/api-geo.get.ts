import { defineEventHandler, getHeaders, getHeader } from 'h3'

export default defineEventHandler((event) => {
  const allHeaders = getHeaders(event)
  const country =
    getHeader(event, 'x-vercel-ip-country') ||
    getHeader(event, 'cf-ipcountry') ||
    getHeader(event, 'x-country-code') ||
    'CN'

  const city =
    getHeader(event, 'x-vercel-ip-city') ||
    getHeader(event, 'cf-ipcity') ||
    ''

  const userAgent = getHeader(event, 'user-agent') || ''

  // 收集所有与地理相关的 headers，便于调试
  const geoHeaders: Record<string, string> = {}
  for (const [k, v] of Object.entries(allHeaders)) {
    if (k.includes('country') || k.includes('city') || k.includes('geo') || k.includes('vercel') || k.includes('cf-')) {
      geoHeaders[k] = String(v)
    }
  }

  return {
    country: String(country).toUpperCase(),
    city: String(city),
    isBot: /googlebot|bingbot|baiduspider|yandex|duckduckbot|slurp|twitterbot|facebookexternalhit/i.test(userAgent),
    geoHeaders,
  }
})
