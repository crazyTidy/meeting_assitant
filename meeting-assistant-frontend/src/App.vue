<script setup lang="ts">
import { RouterView, RouterLink, useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const isDetailPage = computed(() => route.name === 'MeetingDetail')
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <!-- Header -->
    <header class="sticky top-0 z-50 bg-cream-100/95 backdrop-blur-sm border-b border-cream-300">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <!-- Logo / Brand -->
        <RouterLink to="/meetings" class="group flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-espresso-700 flex items-center justify-center
                      group-hover:bg-espresso-800 transition-colors">
            <svg class="w-5 h-5 text-cream-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </div>
          <div>
            <h1 class="font-display text-xl font-medium text-espresso-800 tracking-tight">
              Meeting Assistant
            </h1>
            <p class="text-xs font-sans text-espresso-400 tracking-wide">智能会议纪要</p>
          </div>
        </RouterLink>

        <!-- Navigation -->
        <nav class="flex items-center gap-2" v-if="!isDetailPage">
          <RouterLink
            to="/meetings"
            class="btn-ghost"
            :class="{ 'bg-cream-200': route.name === 'MeetingList' }"
          >
            会议列表
          </RouterLink>
          <RouterLink to="/upload" class="btn-primary">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 4v16m8-8H4" />
            </svg>
            新建会议
          </RouterLink>
        </nav>

        <!-- Back button for detail page -->
        <RouterLink v-else to="/meetings" class="btn-ghost">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回列表
        </RouterLink>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1">
      <RouterView v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </RouterView>
    </main>

    <!-- Footer -->
    <footer class="border-t border-cream-300 py-6">
      <div class="max-w-7xl mx-auto px-6 flex items-center justify-between text-sm text-espresso-400 font-sans">
        <p>Meeting Assistant &copy; 2026</p>
        <p class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-accent-sage"></span>
          系统运行正常
        </p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
