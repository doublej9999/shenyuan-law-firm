// Explicit Nitro route for /llms-full.txt
export default defineEventHandler(async (event) => {
  setHeader(event, 'content-type', 'text/plain; charset=utf-8')
  setHeader(event, 'cache-control', 'public, s-maxage=3600, stale-while-revalidate=86400')
  return await fetchUpstreamText(event, '/llms-full.txt', 'llms-full')
})
