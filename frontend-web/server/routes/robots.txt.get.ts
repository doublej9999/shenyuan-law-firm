// Explicit Nitro handler for robots.txt so the SPA fallback cannot return HTML.
export default defineEventHandler(async (event) => {
  setHeader(event, 'content-type', 'text/plain; charset=utf-8')
  setHeader(event, 'cache-control', 'public, s-maxage=3600, stale-while-revalidate=86400')
  return await fetchUpstreamText(event, '/robots.txt', 'robots')
})
