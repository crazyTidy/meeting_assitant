import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/meetings'
    },
    {
      path: '/upload',
      name: 'Upload',
      component: () => import('@/views/UploadView.vue')
    },
    {
      path: '/meetings',
      name: 'MeetingList',
      component: () => import('@/views/MeetingListView.vue')
    },
    {
      path: '/meetings/:id',
      name: 'MeetingDetail',
      component: () => import('@/views/MeetingDetailView.vue')
    }
  ]
})

export default router
