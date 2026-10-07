// Nuxt 3 configuration for the Shenyuan International public website.
//
// The site is bilingual with a `/en` prefix for English. Route paths are kept
// byte-for-byte identical to the previous Vue SPA so that existing URLs, canonicals
// and inbound links keep working.

export default defineNuxtConfig({
  ssr: true,

  compatibilityDate: '2024-11-01',

  devtools: { enabled: false },

  // Styles live inside the SFCs, exactly as they did in the SPA. The global
  // reset and CSS custom properties are emitted from `app.vue`.
  css: [],

  runtimeConfig: {
    public: {
      // `NUXT_PUBLIC_API_URL` (or the legacy `VITE_API_URL`) is injected by Vercel
      // per environment: production -> shenyuan-backend, preview -> dev backend.
      apiUrl:
        process.env.NUXT_PUBLIC_API_URL ||
        process.env.VITE_API_URL ||
        'https://shenyuan-backend.vercel.app',
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'https://shenyuanlegal.com',
      gaMeasurementId: process.env.NUXT_PUBLIC_GA_MEASUREMENT_ID || '',
    },
  },

  app: {
    head: {
      htmlAttrs: { lang: 'zh-CN' },
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1.0' },
        { property: 'og:site_name', content: 'Shenyuan International' },
        { property: 'og:type', content: 'website' },
        { name: 'twitter:card', content: 'summary_large_image' },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'apple-touch-icon', href: '/favicon.svg' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;600;700&family=Playfair+Display:wght@600;700&display=swap',
        },
      ],
    },
  },

  nitro: {
    // The preset is left to auto-detection: Vercel sets VERCEL=1 during its build
    // so Nuxt selects the `vercel` preset, while `NITRO_PRESET=node-server`
    // (see Dockerfile) produces a portable output.
    compressPublicAssets: true,
  },

  routeRules: {
    // 代理所有 /api/** 请求到真实后端 Django 服务，彻底解决跨域与边缘请求失效问题
    '/api/**': { proxy: 'https://shenyuan-backend.vercel.app/api/**' },
    // Article detail pages are revalidated at the edge; the copy is CMS-managed.
    '/articles/**': { swr: 300 },
    '/en/articles/**': { swr: 300 },

    // 历史旧路径与已废弃页面 301 永久重定向，保留并传递 Google 权重，根除 GSC 404 错误
    '/about': { redirect: { to: '/#team', statusCode: 301 } },
    '/en/about': { redirect: { to: '/en#team', statusCode: 301 } },
    '/ar/about': { redirect: { to: '/ar#team', statusCode: 301 } },
    '/es/about': { redirect: { to: '/es#team', statusCode: 301 } },

    '/fees': { redirect: { to: '/#intake', statusCode: 301 } },
    '/en/fees': { redirect: { to: '/en#intake', statusCode: 301 } },
    '/ar/fees': { redirect: { to: '/ar#intake', statusCode: 301 } },
    '/es/fees': { redirect: { to: '/es#intake', statusCode: 301 } },

    '/privacy': { redirect: { to: '/#intake', statusCode: 301 } },
    '/en/privacy': { redirect: { to: '/en#intake', statusCode: 301 } },
    '/ar/privacy': { redirect: { to: '/ar#intake', statusCode: 301 } },
    '/es/privacy': { redirect: { to: '/es#intake', statusCode: 301 } },

    '/cases': { redirect: { to: '/#cases', statusCode: 301 } },
    '/en/cases': { redirect: { to: '/en#cases', statusCode: 301 } },
    '/ar/cases': { redirect: { to: '/ar#cases', statusCode: 301 } },
    '/es/cases': { redirect: { to: '/es#cases', statusCode: 301 } },

    '/faq': { redirect: { to: '/#faq', statusCode: 301 } },
    '/en/faq': { redirect: { to: '/en#faq', statusCode: 301 } },
    '/ar/faq': { redirect: { to: '/ar#faq', statusCode: 301 } },
    '/es/faq': { redirect: { to: '/es#faq', statusCode: 301 } },
  },

  typescript: {
    strict: false,
    typeCheck: false,
  },
})
