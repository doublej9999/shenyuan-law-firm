// Serves the backend-generated /llms.txt (the LLM-facing site summary) on the
// public domain, so https://shenyuanlegal.com/llms.txt resolves for AI crawlers.
export default defineEventHandler(async (event) => {
  setHeader(event, 'content-type', 'text/plain; charset=utf-8')
  setHeader(event, 'cache-control', 'public, s-maxage=3600, stale-while-revalidate=86400')

  return await fetchUpstreamText(event, '/llms.txt', 'llms')
})
