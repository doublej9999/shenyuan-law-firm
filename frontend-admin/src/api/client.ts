import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 10000,
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
      ElMessage.error('Token 无效或已过期，请重新登录')
      localStorage.removeItem('shenyuan_admin_token')
      window.location.href = '/login'
    } else {
      ElMessage.error(err.response?.data?.detail || '网络请求错误')
    }
    return Promise.reject(err)
  }
)

export default api
