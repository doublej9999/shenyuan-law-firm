// See sitemap.xml.ts — the backend is the single source of truth for robots.txt,
// so that the `Sitemap:` and `llms.txt` advertisements can never disagree with
// the sitemap that is actually served.
export default defineEventHandler(async (event) => {
  setHeader(event, 'content-type', 'text/plain; charset=utf-8')
  setHeader(event, 'cache-control', 'public, s-maxage=3600, stale-while-revalidate=86400')

  return await fetchUpstreamText(event, '/robots.txt', 'robots')
})
