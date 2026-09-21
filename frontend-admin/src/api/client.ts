import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('shenyuan_admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem('shenyuan_admin_token')
      if (window.location.pathname !== '/login') {
        alert('登录 Token 无效或已过期，请重新登录')
        window.location.href = '/login'
      }
    } else {
      const msg = err.response?.data?.detail || '网络请求错误，请稍后重试'
      console.error('API Error:', msg)
    }
    return Promise.reject(err)
  }
)

export default api
