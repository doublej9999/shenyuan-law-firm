// Explicit Nitro handler for sitemap.xml. The .get suffix prevents the SPA
// fallback from serving index.html for this crawler-critical endpoint.
export default defineEventHandler(async (event) => {
  setHeader(event, 'content-type', 'application/xml; charset=utf-8')
  setHeader(event, 'cache-control', 'public, s-maxage=3600, stale-while-revalidate=86400')
  return await fetchUpstreamText(event, '/sitemap.xml', 'sitemap')
})
