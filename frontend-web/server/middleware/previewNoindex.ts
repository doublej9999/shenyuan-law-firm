/**
 * Preview deployments must never be indexed.
 *
 * Every branch gets its own `*.vercel.app` host that serves the same Chinese and
 * English copy as production. Without this header those hosts would be crawled
 * as duplicate content, which is the classic way a preview setup damages the
 * site it is meant to protect.
 */
export default defineEventHandler((event) => {
  if (process.env.VERCEL_ENV === 'preview') {
    setHeader(event, 'x-robots-tag', 'noindex, nofollow')
  }
})
