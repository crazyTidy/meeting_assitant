import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/meetings'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
      meta: { public: true }
    },
    {
      path: '/upload',
      name: 'Upload',
      component: () => import('@/views/UploadView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/meetings',
      name: 'MeetingList',
      component: () => import('@/views/MeetingListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/meetings/:id',
      name: 'MeetingDetail',
      component: () => import('@/views/MeetingDetailView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// Navigation guard for authentication
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  // Initialize user store if not already initialized
  if (!userStore.user && !userStore.loading) {
    await userStore.initUser()
  }

  const isAuthenticated = userStore.isLoggedIn
  const requiresAuth = to.meta.requiresAuth
  const isPublicRoute = to.meta.public

  // If route requires auth and user is not authenticated, redirect to login
  if (requiresAuth && !isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  }
  // If user is authenticated and trying to access login page, redirect to meetings
  else if (isAuthenticated && isPublicRoute && to.name === 'Login') {
    next({ name: 'MeetingList' })
  }
  else {
    next()
  }
})

export default router
