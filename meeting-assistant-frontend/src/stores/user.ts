import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginRequest } from '@/types'
import { userApi } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const loading = ref(false)
  const error = ref<string | null>(null)
  const devMode = ref(false)

  // Computed
  const isLoggedIn = computed(() => !!user.value)
  const userName = computed(() => user.value?.real_name || user.value?.username || '未登录')
  const userDepartment = computed(() => user.value?.department_name || '')

  // Actions
  /**
   * 初始化用户信息
   * 检查localStorage中的token并获取用户信息
   */
  async function initUser() {
    const savedToken = localStorage.getItem('access_token')
    if (savedToken) {
      token.value = savedToken
      await fetchCurrentUser()
    } else {
      // 开发模式下可以直接使用测试用户
      await checkDevMode()
    }
  }

  /**
   * 检查是否为开发模式
   */
  async function checkDevMode() {
    try {
      const config = await userApi.getConfig()
      devMode.value = config.dev_mode
      if (config.dev_mode && config.dev_user_info) {
        user.value = config.dev_user_info
      }
    } catch (e) {
      // 忽略错误
    }
  }

  /**
   * 用户登录
   */
  async function login(loginData: LoginRequest) {
    loading.value = true
    error.value = null

    try {
      const response = await userApi.login(loginData)
      token.value = response.access_token || null

      // 获取用户信息
      await fetchCurrentUser()

      return response
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取当前用户信息
   */
  async function fetchCurrentUser() {
    loading.value = true
    error.value = null

    try {
      user.value = await userApi.getCurrentUser()
    } catch (e: any) {
      error.value = e.message
      // 如果获取用户信息失败，清除无效的token
      if (e.message?.includes('401') || e.message?.includes('403')) {
        token.value = null
        localStorage.removeItem('access_token')
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户登出
   */
  async function logout() {
    userApi.logout()
    user.value = null
    token.value = null
    error.value = null
  }

  /**
   * 开发模式登录（使用测试用户）
   */
  async function devLogin() {
    loading.value = true
    error.value = null

    try {
      await checkDevMode()
      if (devMode.value) {
        // 开发模式不需要token，直接使用测试用户
        return { success: true }
      } else {
        throw new Error('当前不是开发模式')
      }
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    user,
    token,
    loading,
    error,
    devMode,
    // Computed
    isLoggedIn,
    userName,
    userDepartment,
    // Actions
    initUser,
    checkDevMode,
    login,
    fetchCurrentUser,
    logout,
    devLogin,
    clearError
  }
})
