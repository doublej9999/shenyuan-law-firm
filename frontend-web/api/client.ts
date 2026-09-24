import axios, { type AxiosInstance } from 'axios'
import { useRuntimeConfig } from '#imports'

// The runtime API base URL is resolved once per server/browser process. It is
// constant for the lifetime of a deployment (Vercel injects it per environment),
// so caching the instance cannot leak state between requests.
let client: AxiosInstance | null = null

export function getApiClient(): AxiosInstance {
  if (client) return client

  let baseURL = ''
  try {
    baseURL = useRuntimeConfig().public.apiUrl || ''
  } catch {
    // Called outside of a Nuxt context (e.g. a unit test) — fall back to a
    // relative URL so the caller still gets a usable instance.
    baseURL = ''
  }

  client = axios.create({
    baseURL,
    timeout: 15000,
    headers: { 'Content-Type': 'application/json' },
  })
  return client
}

export function parseApiError(err: any, isEn = false): string {
  if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
    return isEn
      ? 'Request timed out. The server might be waking up, please retry.'
      : '请求超时。后端服务可能正在冷启动唤醒，请稍后重试。'
  }

  if (!err.response) {
    return isEn
      ? 'Network error. Please check your connection and try again.'
      : '网络连接失败，请检查网络后重试。'
  }

  const status = err.response.status
  const data = err.response.data

  if (status === 502 || status === 503 || status === 504) {
    return isEn
      ? 'Service temporarily unavailable or starting up. Please try again in 15 seconds.'
      : '云端服务正在准备中或唤醒冷启动，请在 15 秒后重试。'
  }

  if (status === 409) {
    return (typeof data?.detail === 'string' && data.detail)
      ? data.detail
      : (isEn ? 'Duplicate submission detected. Please do not submit repeatedly.' : '检测到重复提交，请勿在短时间内重复提交。')
  }

  if (status === 422 || status === 400) {
    if (typeof data?.detail === 'string') {
      return data.detail
    }
    if (Array.isArray(data?.detail)) {
      const messages = data.detail.map((d: any) => d.msg || d.message || JSON.stringify(d)).join('; ')
      return messages || (isEn ? 'Validation error.' : '表单数据校验失败，请检查填写内容。')
    }
  }

  if (typeof data?.detail === 'string') {
    return data.detail
  }

  return isEn ? 'Submission failed, please try again.' : '提交失败，请稍后重试。'
}
