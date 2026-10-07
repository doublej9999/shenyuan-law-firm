import { defineEventHandler, getRequestURL, sendRedirect } from 'h3'

export default defineEventHandler((event) => {
  const url = getRequestURL(event)
  const pathname = url.pathname

  // 根路径 '/' 或以 '/_nuxt', '/api', '/sitemap.xml', '/robots.txt' 开头的静态/接口资源不处理
  if (pathname === '/' || pathname.startsWith('/_') || pathname.startsWith('/api') || pathname.includes('.')) {
    return
  }

  // 若以 '/' 结尾，301 永久重定向至去除尾随斜杠的规范地址，彻底解决 URL 重复与 Canonical 不一致
  if (pathname.length > 1 && pathname.endsWith('/')) {
    const cleanPath = pathname.replace(/\/+$/, '')
    const target = cleanPath + (url.search || '')
    return sendRedirect(event, target, 301)
  }
})
