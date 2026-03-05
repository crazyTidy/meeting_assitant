<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// Form data
const tokenInput = ref('')
const useDevMode = ref(true)
const loading = ref(false)

// Computed
const canSubmit = computed(() => {
  return useDevMode.value || tokenInput.value.trim().length > 0
})

const loginModeTitle = computed(() => {
  return useDevMode.value ? '开发模式登录' : 'Token登录'
})

// Actions
async function handleLogin() {
  loading.value = true

  try {
    if (useDevMode.value) {
      // 开发模式登录
      await userStore.devLogin()
    } else {
      // Token登录
      await userStore.login({
        token: tokenInput.value
      })
    }

    // 登录成功，跳转到会议列表
    router.push('/meetings')
  } catch (e: any) {
    console.error('Login failed:', e)
    // Error is already in store
  } finally {
    loading.value = false
  }
}

function toggleLoginMode() {
  useDevMode.value = !useDevMode.value
  tokenInput.value = ''
  userStore.clearError()
}

// Check if already logged in
onMounted(async () => {
  await userStore.initUser()
  if (userStore.isLoggedIn) {
    router.push('/meetings')
  }
})
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      <!-- Logo/Brand -->
      <div class="logo-section">
        <div class="logo-icon">
          <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        </div>
        <h1 class="app-title">Meeting Assistant</h1>
        <p class="app-subtitle">智能会议纪要系统</p>
      </div>

      <!-- Login Card -->
      <div class="login-card">
        <h2 class="login-title">{{ loginModeTitle }}</h2>

        <!-- Error Message -->
        <div v-if="userStore.error" class="error-message">
          <p>{{ userStore.error }}</p>
        </div>

        <!-- Dev Mode Info -->
        <div v-if="useDevMode" class="info-box dev-mode">
          <p class="info-title">ℹ️ 开发模式</p>
          <p class="info-text">使用测试用户直接登录，无需输入Token。</p>
        </div>

        <!-- Token Input -->
        <div v-else class="token-section">
          <label class="token-label">JWT Token</label>
          <textarea
            v-model="tokenInput"
            class="token-input"
            rows="4"
            placeholder="粘贴您的JWT Token..."
          ></textarea>
          <p class="token-hint">Token由外部用户系统提供，用于身份验证</p>
        </div>

        <!-- Submit Button -->
        <button
          @click="handleLogin"
          :disabled="!canSubmit || loading"
          class="submit-btn"
          :class="{ disabled: !canSubmit || loading }"
        >
          <span v-if="loading">登录中...</span>
          <span v-else>进入系统</span>
        </button>

        <!-- Toggle Mode Button -->
        <div class="toggle-section">
          <button
            @click="toggleLoginMode"
            class="toggle-btn"
          >
            {{ useDevMode ? '🔑 切换到Token登录' : '⚡ 切换到开发模式' }}
          </button>
        </div>
      </div>

      <!-- Footer -->
      <div class="footer">
        <p>Meeting Assistant © 2026</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fefefe 0%, #f5f5f4 100%);
  padding: 20px;
}

.login-box {
  width: 100%;
  max-width: 420px;
}

.logo-section {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #3c3c3b;
  margin-bottom: 16px;
  color: #fafaf9;
}

.app-title {
  font-size: 24px;
  font-weight: 500;
  color: #3c3c3b;
  margin: 0 0 4px 0;
}

.app-subtitle {
  font-size: 14px;
  color: #78716c;
  margin: 0;
}

.login-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid #e7e5e4;
  padding: 32px;
}

.login-title {
  font-size: 18px;
  font-weight: 500;
  color: #3c3c3b;
  margin: 0 0 24px 0;
}

.error-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 24px;
}

.error-message p {
  color: #dc2626;
  font-size: 14px;
  margin: 0;
}

.info-box {
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}

.info-box.dev-mode {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
}

.info-title {
  font-weight: 500;
  margin: 0 0 8px 0;
  font-size: 14px;
}

.info-text {
  margin: 0;
  font-size: 14px;
  color: #166534;
}

.token-section {
  margin-bottom: 24px;
}

.token-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #3c3c3b;
  margin-bottom: 8px;
}

.token-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #d6d3d1;
  border-radius: 8px;
  font-family: monospace;
  font-size: 14px;
  resize: none;
  box-sizing: border-box;
}

.token-input:focus {
  outline: none;
  border-color: #84cc16;
  box-shadow: 0 0 0 3px rgba(132, 204, 22, 0.1);
}

.token-hint {
  font-size: 12px;
  color: #78716c;
  margin: 8px 0 0 0;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background: #3c3c3b;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover:not(.disabled) {
  background: #292524;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.submit-btn.disabled {
  background: #e7e5e4;
  color: #a8a29e;
  cursor: not-allowed;
}

.toggle-section {
  margin-top: 20px;
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e7e5e4;
}

.toggle-btn {
  background: none;
  border: none;
  color: #3c3c3b;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 6px;
  transition: background 0.2s;
}

.toggle-btn:hover {
  background: #f5f5f4;
}

.footer {
  margin-top: 24px;
  text-align: center;
}

.footer p {
  font-size: 14px;
  color: #78716c;
  margin: 0;
}
</style>
