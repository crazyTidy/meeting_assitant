import axios from 'axios'
import type { User, LoginRequest, LoginResponse } from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - add token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors
api.interceptors.response.use(
  response => response,
  error => {
    const message = error.response?.data?.detail?.error?.message
      || error.response?.data?.message
      || error.message
      || '请求失败'
    return Promise.reject(new Error(message))
  }
)

export const userApi = {
  /**
   * 用户登录
   * 支持两种模式：
   * 1. Token登录：传入JWT token
   * 2. 开发模式：不传token，使用开发测试用户
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/users/login', data)
    // 保存token到localStorage
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
    }
    return response.data
  },

  /**
   * 获取当前登录用户信息
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/users/me')
    return response.data
  },

  /**
   * 用户登出
   * 前端清除token即可
   */
  logout(): void {
    localStorage.removeItem('access_token')
  },

  /**
   * 获取应用配置
   */
  async getConfig(): Promise<{ dev_mode: boolean; dev_user_info?: User }> {
    const response = await api.get('/users/config')
    return response.data
  }
}

export default api
