// Proxies the backend-generated sitemap onto the public domain.
//
// The Django backend owns sitemap generation because it is the only place that
// knows every article's real `lastmod` and can emit the zh/en `xhtml:link`
// alternates. Keeping a single generator avoids the two sources drifting apart.
export default defineEventHandler(async (event) => {
  setHeader(event, 'content-type', 'application/xml; charset=utf-8')
  setHeader(event, 'cache-control', 'public, s-maxage=3600, stale-while-revalidate=86400')

  return await fetchUpstreamText(event, '/sitemap.xml', 'sitemap')
})
