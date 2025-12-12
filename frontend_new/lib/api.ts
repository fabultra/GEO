/**
 * API Client for GEO Backend
 * Axios wrapper with authentication
 */
import axios, { AxiosInstance, AxiosError } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any

    // Handle 401 - Try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })

          const { access_token } = response.data
          localStorage.setItem('access_token', access_token)

          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed - logout
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// API methods
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),

  register: (data: {
    email: string
    password: string
    first_name?: string
    last_name?: string
  }) => api.post('/auth/register', data),

  logout: () => api.post('/auth/logout'),

  me: () => api.get('/users/me'),
}

export const analysisAPI = {
  list: () => api.get('/analyses'),

  create: (url: string) => api.post('/analyses', { url }),

  get: (id: string) => api.get(`/analyses/${id}`),

  delete: (id: string) => api.delete(`/analyses/${id}`),

  getStatus: (id: string) => api.get(`/analyses/${id}/status`),
}

export const reportAPI = {
  get: (analysisId: string) => api.get(`/reports/${analysisId}`),

  export: (analysisId: string, format: 'pdf' | 'json' | 'csv') =>
    api.post(`/reports/${analysisId}/export`, { format }, { responseType: 'blob' }),
}

export const adminAPI = {
  users: () => api.get('/admin/users'),

  analyses: () => api.get('/admin/analyses'),

  stats: () => api.get('/admin/stats'),

  updateSubscription: (userId: string, data: any) =>
    api.put(`/admin/users/${userId}/subscription`, data),
}

export default api
