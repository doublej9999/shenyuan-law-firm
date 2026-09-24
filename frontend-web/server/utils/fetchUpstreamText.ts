import axios from 'axios'
import type { H3Event } from 'h3'

/**
 * Fetches a text resource that is authored by the Django backend.
 *
 * The backend is the single source of truth for `sitemap.xml`, `robots.txt` and
 * `llms.txt`: it is the only place that knows every article's real `lastmod` and
 * can emit the zh/en `xhtml:link` alternates. Proxying keeps that one generator
 * from drifting away from what the public domain actually serves.
 *
 * `axios` is used rather than the global `fetch` because it honours the
 * `HTTP(S)_PROXY` environment variables. Nitro's `fetch` (undici) ignores them,
 * which makes local builds behind a proxy fail while working fine on Vercel.
 */
export async function fetchUpstreamText(event: H3Event, path: string, label: string): Promise<string> {
  const config = useRuntimeConfig(event)
  const base = String(config.public.apiUrl || '').replace(/\/+$/, '')

  try {
    const res = await axios.get<string>(`${base}${path}`, {
      timeout: 10000,
      responseType: 'text',
      // Handle status codes ourselves so an upstream 404 is not reported as 503.
      validateStatus: () => true,
    })

    if (res.status === 404) {
      throw createError({ statusCode: 404, statusMessage: `${path} is not published by the backend` })
    }
    if (res.status >= 400) {
      throw new Error(`upstream responded ${res.status}`)
    }

    return String(res.data ?? '')
  } catch (err: any) {
    if (err?.statusCode) throw err
    console.error(`[${label}] upstream fetch failed`, err)
    // A 503 (not a 200 with an empty body) is the correct signal: crawlers retry.
    throw createError({ statusCode: 503, statusMessage: `${label} temporarily unavailable` })
  }
}
