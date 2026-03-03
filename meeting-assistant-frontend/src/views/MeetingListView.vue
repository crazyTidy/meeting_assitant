<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMeetingStore } from '@/stores/meeting'
import type { Meeting, MeetingStatus, ProcessingStage } from '@/types'

const router = useRouter()
const store = useMeetingStore()

const searchInput = ref('')
const searchDebounceTimer = ref<number | null>(null)
const deleteConfirmId = ref<string | null>(null)

const statusConfig: Record<MeetingStatus, { label: string; class: string }> = {
  pending: { label: '等待处理', class: 'pending' },
  processing: { label: '处理中', class: 'processing' },
  completed: { label: '已完成', class: 'completed' },
  failed: { label: '处理失败', class: 'failed' }
}

// 阶段配置
const stageConfig: Record<ProcessingStage, { label: string; description: string; milestone: boolean }> = {
  initializing: { label: '初始化', description: '初始化处理中...', milestone: false },
  separating: { label: '人声分离', description: '人声分离进行中...', milestone: false },
  separation_completed: { label: '人声分离完成', description: '人声分离完成 ✅', milestone: true },
  summarizing: { label: 'AI总结', description: 'AI总结生成中...', milestone: false },
  completed: { label: '处理完成', description: '全部完成 ✅', milestone: true }
}

// 获取阶段显示信息
const getStageInfo = (stage?: ProcessingStage) => {
  if (!stage) return null
  return stageConfig[stage] || null
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatDuration = (seconds?: number): string => {
  if (!seconds) return '--'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  // Format as HH:MM:SS
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

const handleSearch = () => {
  if (searchDebounceTimer.value) {
    clearTimeout(searchDebounceTimer.value)
  }
  searchDebounceTimer.value = window.setTimeout(() => {
    store.setSearch(searchInput.value)
  }, 300)
}

const goToDetail = (meeting: Meeting) => {
  router.push(`/meetings/${meeting.id}`)
}

const handleDownload = async (meeting: Meeting, e: Event) => {
  e.stopPropagation()
  try {
    await store.downloadAudio(meeting.id, meeting.title)
  } catch (e) {
    // Error handled by store
  }
}

const confirmDelete = (meetingId: string, e: Event) => {
  e.stopPropagation()
  deleteConfirmId.value = meetingId
}

const cancelDelete = () => {
  deleteConfirmId.value = null
}

const handleDelete = async (meetingId: string) => {
  try {
    await store.deleteMeeting(meetingId)
    deleteConfirmId.value = null
  } catch (e) {
    // Error handled by store
  }
}

const goToPage = (page: number) => {
  store.setPage(page)
}

// Poll for processing meetings
let pollingInterval: number | null = null

const startPolling = () => {
  if (pollingInterval) return

  pollingInterval = window.setInterval(async () => {
    const processingMeetings = store.meetings.filter(
      m => m.status === 'pending' || m.status === 'processing'
    )

    for (const meeting of processingMeetings) {
      try {
        await store.pollStatus(meeting.id)
      } catch (e) {
        // Ignore polling errors
      }
    }
  }, 3000)
}

const stopPolling = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
}

onMounted(() => {
  store.fetchMeetings()
  startPolling()
})

// Clean up on unmount
import { onUnmounted } from 'vue'
onUnmounted(() => {
  stopPolling()
})

// Watch for search changes
watch(searchInput, handleSearch)
</script>

<template>
  <div class="max-w-5xl mx-auto px-6 py-12">
    <!-- Page Header -->
    <div class="mb-10 animate-fade-up">
      <p class="subhead mb-3">Meeting Archive</p>
      <h2 class="masthead">会议记录</h2>
    </div>

    <!-- Search Bar -->
    <div class="mb-8 animate-fade-up delay-100">
      <div class="relative">
        <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-espresso-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          v-model="searchInput"
          type="text"
          placeholder="搜索会议..."
          class="w-full pl-12 pr-4 py-3 bg-cream-50 border border-cream-300 rounded-lg
                 font-sans text-ink placeholder:text-espresso-300
                 focus:outline-none focus:border-espresso-400 focus:ring-1 focus:ring-espresso-400
                 transition-all duration-200"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="store.loading && store.meetings.length === 0" class="text-center py-20">
      <div class="w-12 h-12 mx-auto mb-4 border-2 border-espresso-200 border-t-espresso-600 rounded-full animate-spin"></div>
      <p class="text-espresso-400 font-sans">加载中...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="store.isEmpty" class="text-center py-20 animate-fade-up">
      <div class="w-20 h-20 mx-auto mb-6 rounded-full bg-cream-200 flex items-center justify-center">
        <svg class="w-10 h-10 text-espresso-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      </div>
      <h3 class="font-display text-2xl text-espresso-700 mb-2">暂无会议记录</h3>
      <p class="text-espresso-400 font-sans mb-6">上传您的第一个会议录音开始使用</p>
      <router-link to="/upload" class="btn-primary">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 4v16m8-8H4" />
        </svg>
        新建会议
      </router-link>
    </div>

    <!-- Meeting List -->
    <div v-else class="space-y-4">
      <div
        v-for="(meeting, index) in store.meetings"
        :key="meeting.id"
        @click="goToDetail(meeting)"
        class="card-paper p-6 cursor-pointer animate-fade-up"
        :style="{ animationDelay: `${100 + index * 50}ms` }"
      >
        <div class="flex items-start justify-between gap-4">
          <!-- Meeting Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-3 mb-2">
              <span
                :class="['ink-drop', statusConfig[meeting.status].class]"
                :title="statusConfig[meeting.status].label"
              ></span>
              <h3 class="font-display text-xl text-espresso-700 truncate">
                {{ meeting.title }}
              </h3>
            </div>
            <div class="flex items-center gap-4 text-sm text-espresso-400 font-sans">
              <span class="flex items-center gap-1.5">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {{ formatDate(meeting.created_at) }}
              </span>
              <span class="flex items-center gap-1.5">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ formatDuration(meeting.duration) }}
              </span>
            </div>

            <!-- Progress bar for processing -->
            <div v-if="meeting.status === 'processing'" class="mt-3">
              <div class="flex items-center justify-between text-xs font-sans mb-1">
                <span class="text-accent-gold">
                  {{ getStageInfo(meeting.stage)?.description || statusConfig[meeting.status].label }}
                </span>
                <span class="text-espresso-400">{{ meeting.progress }}%</span>
              </div>
              <div class="h-2 bg-cream-200 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-500 relative bg-accent-gold"
                  :style="{ width: `${meeting.progress}%` }"
                >
                  <!-- Milestone marker at 50% -->
                  <div
                    v-if="meeting.progress >= 50"
                    class="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-white border-2 border-current rounded-full"
                  ></div>
                </div>
              </div>
              <!-- Stage milestone indicator -->
              <div class="flex items-center justify-between text-xs font-sans mt-1">
                <span
                  class="transition-colors duration-300"
                  :class="{
                    'text-accent-sage': meeting.progress >= 50,
                    'text-espresso-300': meeting.progress < 50
                  }"
                >
                  {{ meeting.progress >= 50 ? '✅ 人声分离完成' : '○ 人声分离中' }}
                </span>
                <span
                  class="transition-colors duration-300"
                  :class="{
                    'text-espresso-300': meeting.progress < 100
                  }"
                >
                  {{ meeting.progress >= 100 ? '✅ 总结完成' : '○ 总结生成中' }}
                </span>
              </div>
            </div>

            <!-- Partial completion notice for failed meetings -->
            <div v-if="meeting.status === 'failed' && meeting.progress === 50" class="mt-2 p-2 bg-accent-sage/10 border border-accent-sage/30 rounded-md">
              <p class="text-xs text-accent-sage font-sans">
                <span class="font-medium">部分完成：</span>人声分离已完成，总结生成失败。参与者数据已保留。
              </p>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2" @click.stop>
            <span
              class="px-3 py-1 text-xs font-sans rounded-full"
              :class="{
                'bg-espresso-100 text-espresso-500': meeting.status === 'pending',
                'bg-accent-gold/20 text-accent-gold': meeting.status === 'processing',
                'bg-accent-sage/20 text-accent-sage': meeting.status === 'completed',
                'bg-accent-terracotta/20 text-accent-terracotta': meeting.status === 'failed'
              }"
            >
              {{ statusConfig[meeting.status].label }}
            </span>

            <!-- Delete Button -->
            <div class="flex items-center gap-1">
              <!-- Download Button -->
              <button
                @click="handleDownload(meeting, $event)"
                class="p-2 text-espresso-400 hover:text-espresso-700 transition-colors"
                title="下载音频"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </button>

              <!-- Delete Button with Confirmation -->
              <div class="relative">
                <button
                  @click="confirmDelete(meeting.id, $event)"
                  class="p-2 text-espresso-400 hover:text-accent-terracotta transition-colors"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>

                <!-- Delete Confirmation Popover -->
                <div
                  v-if="deleteConfirmId === meeting.id"
                  class="absolute right-0 top-full mt-2 p-4 bg-cream-50 rounded-lg shadow-paper-hover z-10 min-w-[200px]"
                >
                  <p class="text-sm text-espresso-600 mb-3 font-sans">确定删除此会议？</p>
                  <div class="flex gap-2">
                    <button @click="cancelDelete" class="btn-ghost flex-1 text-xs">取消</button>
                    <button @click="handleDelete(meeting.id)" class="btn-primary flex-1 text-xs bg-accent-terracotta hover:bg-accent-terracotta/90">删除</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="store.pages > 1" class="mt-8 flex items-center justify-center gap-2 animate-fade-up">
      <button
        @click="goToPage(store.page - 1)"
        :disabled="store.page <= 1"
        class="btn-ghost disabled:opacity-30"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      <template v-for="p in store.pages" :key="p">
        <button
          v-if="p === 1 || p === store.pages || (p >= store.page - 1 && p <= store.page + 1)"
          @click="goToPage(p)"
          class="w-10 h-10 rounded-lg font-sans text-sm transition-all"
          :class="p === store.page
            ? 'bg-espresso-700 text-cream-50'
            : 'text-espresso-500 hover:bg-cream-200'"
        >
          {{ p }}
        </button>
        <span
          v-else-if="p === store.page - 2 || p === store.page + 2"
          class="text-espresso-300"
        >
          ...
        </span>
      </template>

      <button
        @click="goToPage(store.page + 1)"
        :disabled="store.page >= store.pages"
        class="btn-ghost disabled:opacity-30"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>

    <!-- Summary -->
    <div v-if="store.total > 0" class="mt-6 text-center text-sm text-espresso-400 font-sans">
      共 {{ store.total }} 条记录
    </div>
  </div>
</template>
