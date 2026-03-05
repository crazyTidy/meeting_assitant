<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useMeetingStore } from '@/stores/meeting'
import { marked } from 'marked'

// Configure marked to treat single line breaks as <br>
marked.setOptions({
  breaks: true,
  gfm: true
})

import type { MeetingStatus } from '@/types'
import { saveAs } from 'file-saver'

const route = useRoute()
const store = useMeetingStore()

const meetingId = computed(() => route.params.id as string)

// Speaker editing (for transcript view)
const editingSpeaker = ref<string | null>(null)
const editingSpeakerName = ref('')
const savingSpeakerName = ref(false)

// Summary editing states
const editingSummary = ref(false)
const editedContent = ref('')
const savingSummary = ref(false)

// Download state
const downloading = ref(false)

// Regeneration states
const regeneratingSummary = ref(false)
const showRegenerateConfirm = ref(false)
const showPreviewDialog = ref(false)
const previewContent = ref('')

const statusConfig: Record<MeetingStatus, { label: string; color: string; bgColor: string }> = {
  pending: { label: '等待处理', color: 'text-espresso-500', bgColor: 'bg-espresso-100' },
  processing: { label: '处理中', color: 'text-accent-gold', bgColor: 'bg-accent-gold/20' },
  completed: { label: '已完成', color: 'text-accent-sage', bgColor: 'bg-accent-sage/20' },
  failed: { label: '处理失败', color: 'text-accent-terracotta', bgColor: 'bg-accent-terracotta/20' }
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
}

const formatTime = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleTimeString('zh-CN', {
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

const renderedSummary = computed(() => {
  if (!store.currentMeeting?.summary?.content) return ''
  return marked(store.currentMeeting.summary.content)
})

// Format timestamp to HH:MM:SS
const formatTimestamp = (seconds: number): string => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  if (h > 0) {
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  }
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

// Use merged segments from backend for transcript display
const timelineData = computed(() => {
  if (!store.currentMeeting?.merged_segments) return []
  // Backend already merged segments with 3-second gap rule
  return store.currentMeeting.merged_segments
})

const getParticipantById = (id: string) => {
  if (!store.currentMeeting?.participants) return null
  return store.currentMeeting.participants.find(p => p.id === id) ||
         store.currentMeeting.participants.find(p => p.speaker_id === id)
}

// Speaker name editing functions (for transcript view)
const cancelEditingSpeaker = () => {
  editingSpeaker.value = null
  editingSpeakerName.value = ''
}

const saveSpeakerName = async (speakerId: string) => {
  if (!editingSpeakerName.value.trim()) {
    cancelEditingSpeaker()
    return
  }

  savingSpeakerName.value = true
  try {
    await store.updateSpeakerName(
      meetingId.value,
      speakerId,
      editingSpeakerName.value.trim()
    )
    cancelEditingSpeaker()
  } catch (e) {
    // Error handled by store
  } finally {
    savingSpeakerName.value = false
  }
}

const handleSpeakerKeydown = (e: KeyboardEvent, speakerId: string) => {
  if (e.key === 'Enter') {
    saveSpeakerName(speakerId)
  } else if (e.key === 'Escape') {
    cancelEditingSpeaker()
  }
}

// Polling for processing status
let pollingInterval: number | null = null
const lastProgress = ref(0)

const startPolling = () => {
  if (pollingInterval) return

  pollingInterval = window.setInterval(async () => {
    if (!store.currentMeeting) return
    if (store.currentMeeting.status !== 'pending' && store.currentMeeting.status !== 'processing') {
      stopPolling()
      return
    }

    try {
      const status = await store.pollStatus(meetingId.value)

      // Check if voice separation is complete (50%) - only refresh once when crossing 50%
      const shouldRefreshDetails =
        status.status === 'completed' || status.status === 'failed' ||
        (status.progress >= 50 && lastProgress.value < 50)

      if (shouldRefreshDetails) {
        // Clear regenerating flag if set
        if (regeneratingSummary.value) {
          regeneratingSummary.value = false
        }
        // Refresh full details to get merged_segments
        await store.fetchMeetingDetail(meetingId.value)

        // Update lastProgress after refresh
        lastProgress.value = store.currentMeeting?.progress || status.progress

        if (status.status === 'completed' || status.status === 'failed') {
          stopPolling()
        }
      } else {
        // Just update lastProgress to track progress
        lastProgress.value = status.progress
      }
    } catch (e) {
      // Ignore polling errors
    }
  }, 3000)
}

const stopPolling = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
}

onMounted(async () => {
  await store.fetchMeetingDetail(meetingId.value)
  if (store.currentMeeting?.status === 'pending' || store.currentMeeting?.status === 'processing') {
    // Initialize lastProgress to current progress so we only refresh when it changes
    lastProgress.value = store.currentMeeting.progress || 0
    startPolling()
  }
})

onUnmounted(() => {
  stopPolling()
})

// Watch for meeting changes to manage polling
watch(() => store.currentMeeting?.status, (newStatus, oldStatus) => {
  if (newStatus === 'pending' || newStatus === 'processing') {
    startPolling()
  } else if ((newStatus === 'completed' || newStatus === 'failed') && (oldStatus === 'processing' || oldStatus === 'pending')) {
    stopPolling()
    // If we were regenerating and it completed, show success message
    if (regeneratingSummary.value) {
      regeneratingSummary.value = false
      if (newStatus === 'completed') {
        // Successfully regenerated - the page will auto-refresh with new content
        // You could show a toast notification here if needed
      }
    }
  }
})

// Copy summary to clipboard
const copySuccess = ref(false)
const copying = ref(false)

const copySummary = async () => {
  if (!store.currentMeeting?.summary?.content) return

  copying.value = true
  try {
    await navigator.clipboard.writeText(store.currentMeeting.summary.content)
    copySuccess.value = true
    setTimeout(() => {
      copySuccess.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  } finally {
    copying.value = false
  }
}

// Summary editing functions
const startEditingSummary = () => {
  if (store.currentMeeting?.summary?.content) {
    editedContent.value = store.currentMeeting.summary.content
    editingSummary.value = true
  }
}

const saveSummary = async () => {
  if (!editedContent.value.trim()) return

  savingSummary.value = true
  try {
    await store.updateSummary(meetingId.value, editedContent.value.trim())
    editingSummary.value = false
  } catch (e) {
    // Error handled by store
  } finally {
    savingSummary.value = false
  }
}

const cancelEditingSummary = () => {
  editingSummary.value = false
  editedContent.value = ''
}

/**
 * Parse markdown and convert to docx paragraphs following 科大讯飞 format
 * 科大讯飞格式：
 * - 主标题：居中，二号黑体
 * - "会议纪要"：三号仿宋居中
 * - 大标题"一、二、三"：三号黑体加粗
 * - 子标题"1. 2. 3."：三号黑体
 * - 正文：三号仿宋，首行缩进2字符
 * - 段落间距：240缇（12磅）
 */

/**
 * Download as DOCX via backend API
 * Backend generates DOCX following Chinese official document standards
 */
const downloadAsDocx = async () => {
  if (!store.currentMeeting?.summary?.content) return

  downloading.value = true
  try {
    // Call backend API to generate DOCX (using proxy path configured in vite.config.ts)
    const response = await fetch(`/api/v1/meetings/${meetingId.value}/download-docx`)

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData?.error?.message || '下载失败')
    }

    // Get blob from response
    const blob = await response.blob()

    // Extract filename from Content-Disposition header or generate default
    let fileName = `${store.currentMeeting.title}_会议纪要.docx`
    const contentDisposition = response.headers.get('Content-Disposition')
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename\*=UTF-8''(.+)/)
      if (filenameMatch) {
        fileName = decodeURIComponent(filenameMatch[1])
      }
    }

    // Download file
    saveAs(blob, fileName)
  } catch (err: any) {
    console.error('Failed to download:', err)
    alert(`下载失败：${err.message || '未知错误'}`)
  } finally {
    downloading.value = false
  }
}

const confirmRegenerate = () => {
  showRegenerateConfirm.value = true
}

const cancelRegenerate = () => {
  showRegenerateConfirm.value = false
}

const handleRegenerateSummary = async () => {
  showRegenerateConfirm.value = false
  regeneratingSummary.value = true

  try {
    // Store the current content for preview later
    if (store.currentMeeting?.summary?.content) {
      previewContent.value = store.currentMeeting.summary.content
    }

    // Start regeneration
    await store.regenerateSummary(meetingId.value)

    // Start polling for completion
    startPolling()
  } catch (e: any) {
    alert(`重新生成失败：${e.message || '未知错误'}`)
    regeneratingSummary.value = false
  }
}

const cancelPreview = () => {
  showPreviewDialog.value = false
  previewContent.value = ''
}
</script>

<template>
  <div class="min-h-[calc(100vh-160px)]">
    <!-- Loading State -->
    <div v-if="store.loading && !store.currentMeeting" class="flex items-center justify-center py-20">
      <div class="text-center">
        <div class="w-12 h-12 mx-auto mb-4 border-2 border-espresso-200 border-t-espresso-600 rounded-full animate-spin"></div>
        <p class="text-espresso-400 font-sans">加载中...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error && !store.currentMeeting" class="flex items-center justify-center py-20">
      <div class="text-center">
        <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-accent-terracotta/10 flex items-center justify-center">
          <svg class="w-8 h-8 text-accent-terracotta" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <p class="text-espresso-600 font-sans">{{ store.error }}</p>
      </div>
    </div>

    <!-- Meeting Content -->
    <template v-else-if="store.currentMeeting">
      <!-- Header Section -->
      <div class="border-b border-cream-300 bg-cream-50/50">
        <div class="max-w-7xl mx-auto px-6 py-8">
          <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div class="animate-fade-up">
              <div class="flex items-center gap-3 mb-2">
                <span
                  class="px-3 py-1 text-xs font-sans rounded-full"
                  :class="[statusConfig[store.currentMeeting.status].color, statusConfig[store.currentMeeting.status].bgColor]"
                >
                  {{ statusConfig[store.currentMeeting.status].label }}
                </span>
                <span v-if="store.currentMeeting.status === 'processing'" class="text-sm text-espresso-400 font-sans">
                  {{ store.currentMeeting.progress }}%
                </span>
              </div>
              <h1 class="masthead text-3xl md:text-4xl mb-3">{{ store.currentMeeting.title }}</h1>
              <div class="flex flex-wrap items-center gap-4 text-sm text-espresso-400 font-sans">
                <span class="flex items-center gap-1.5">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {{ formatDate(store.currentMeeting.created_at) }}
                </span>
                <span class="flex items-center gap-1.5">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {{ formatTime(store.currentMeeting.created_at) }}
                </span>
                <span class="flex items-center gap-1.5">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  时长 {{ formatDuration(store.currentMeeting.duration) }}
                </span>
              </div>
            </div>

            <!-- Progress bar for processing -->
            <div v-if="store.currentMeeting.status === 'processing'" class="md:w-64 animate-fade-up delay-100">
              <div class="h-2 bg-cream-200 rounded-full overflow-hidden">
                <div
                  class="h-full bg-accent-gold rounded-full transition-all duration-500"
                  :style="{ width: `${store.currentMeeting.progress}%` }"
                ></div>
              </div>
              <p class="mt-2 text-xs text-espresso-400 font-sans text-right">正在处理中...</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Processing State - only show if no merged segments yet (initial processing) -->
      <div v-if="(store.currentMeeting.status === 'pending' || store.currentMeeting.status === 'processing') && !store.currentMeeting.merged_segments?.length" class="max-w-7xl mx-auto px-6 py-20">
        <div class="text-center animate-fade-up">
          <div class="w-24 h-24 mx-auto mb-6 rounded-full bg-cream-200 flex items-center justify-center">
            <svg class="w-12 h-12 text-espresso-400 animate-pulse-soft" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h3 class="font-display text-2xl text-espresso-700 mb-2">正在处理您的会议录音</h3>
          <p class="text-espresso-400 font-sans mb-6">
            系统正在进行人声分离和会议纪要生成，请稍候...
          </p>
          <div class="inline-flex items-center gap-2 px-4 py-2 bg-cream-200 rounded-full text-sm font-sans text-espresso-500">
            <span class="w-2 h-2 bg-accent-gold rounded-full animate-pulse"></span>
            处理进度：{{ store.currentMeeting.progress }}%
          </div>
        </div>
      </div>

      <!-- Split View - show whenever we have data (regardless of overall status) -->
      <div v-else class="max-w-7xl mx-auto">
        <div class="flex flex-col lg:flex-row min-h-[calc(100vh-280px)]">
          <!-- Left Panel - Transcript (逐字稿) -->
          <aside class="lg:w-96 xl:w-[450px] border-b lg:border-b-0 lg:border-r border-cream-300 bg-cream-50/30">
            <div class="p-6 sticky top-20 max-h-[calc(100vh-200px)] overflow-y-auto">
              <div class="flex items-center justify-between mb-6">
                <h2 class="font-display text-xl text-espresso-700">逐字稿</h2>
                <span v-if="timelineData.length > 0" class="text-sm text-espresso-400 font-sans">
                  {{ timelineData.length }} 条
                </span>
              </div>

              <div v-if="timelineData.length > 0" class="space-y-3 animate-fade-up">
                <div
                  v-for="(segment, index) in timelineData"
                  :key="segment.id"
                  class="group p-3 bg-white rounded-lg border border-cream-200 hover:border-espresso-300 transition-all animate-slide-in"
                  :style="{ animationDelay: `${index * 30}ms` }"
                >
                  <div class="flex items-start gap-3">
                    <!-- Timeline Indicator -->
                    <div class="flex flex-col items-center pt-1">
                      <div class="w-2 h-2 rounded-full bg-accent-gold"></div>
                      <div v-if="index < timelineData.length - 1" class="w-0.5 h-full bg-cream-200 my-1"></div>
                    </div>

                    <!-- Segment Content -->
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-2 mb-1">
                        <span class="px-2 py-0.5 text-xs font-sans rounded-full bg-espresso-100 text-espresso-600">
                          {{ formatTimestamp(segment.start_time) }} - {{ formatTimestamp(segment.end_time) }}
                        </span>

                        <!-- Speaker name display with edit functionality -->
                        <div v-if="editingSpeaker !== segment.speaker_id" class="flex items-center gap-1 group">
                          <div class="w-5 h-5 rounded-full bg-gradient-to-br from-espresso-200 to-espresso-300 flex items-center justify-center">
                            <span class="text-[10px] font-sans font-medium text-espresso-700">
                              {{ getParticipantById(segment.participant_id || segment.speaker_id)?.display_name?.charAt(0) || '?' }}
                            </span>
                          </div>
                          <span class="text-xs font-sans text-espresso-600 truncate max-w-[120px]">
                            {{ getParticipantById(segment.participant_id || segment.speaker_id)?.display_name || segment.speaker_id }}
                          </span>
                          <!-- Edit button -->
                          <button
                            @click="editingSpeaker = segment.speaker_id; editingSpeakerName = getParticipantById(segment.participant_id || segment.speaker_id)?.display_name || segment.speaker_id"
                            class="p-0.5 text-espresso-400 hover:text-espresso-600 opacity-0 group-hover:opacity-100 transition-all"
                            title="编辑人名"
                          >
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                            </svg>
                          </button>
                        </div>

                        <!-- Editing state for speaker name -->
                        <div v-else class="flex items-center gap-1">
                          <input
                            v-model="editingSpeakerName"
                            type="text"
                            class="w-24 px-2 py-0.5 text-xs bg-white border border-espresso-300 rounded font-sans focus:outline-none focus:border-espresso-500"
                            @keydown="handleSpeakerKeydown($event, segment.speaker_id)"
                            autofocus
                          />
                          <button
                            @click="cancelEditingSpeaker"
                            class="p-1 text-espresso-400 hover:text-espresso-600 transition-all"
                            title="取消"
                            :disabled="savingSpeakerName"
                          >
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                          <button
                            @click="saveSpeakerName(segment.speaker_id)"
                            class="p-1 text-accent-sage hover:text-accent-sage/80 transition-all"
                            title="保存"
                            :disabled="savingSpeakerName"
                          >
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                            </svg>
                          </button>
                        </div>
                      </div>

                      <p v-if="segment.transcript" class="text-sm text-espresso-700 font-sans leading-relaxed">
                        {{ segment.transcript }}
                      </p>
                      <p v-else class="text-sm text-espresso-400 font-sans italic">
                        （暂无转写文本）
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else class="text-center py-12 text-espresso-400 font-sans animate-fade-up">
                暂无发言记录
              </div>
            </div>
          </aside>

          <!-- Right Panel - Summary -->
          <main class="flex-1 p-6 lg:p-10 flex flex-col">
            <div class="flex-1 overflow-y-auto max-h-[calc(100vh-200px)]" :class="{ 'overflow-hidden': regeneratingSummary && store.currentMeeting.summary }">
              <div class="max-w-3xl relative">
                <!-- Regenerating overlay - positioned relative to content area -->
                <!-- Only show during actual regeneration (regeneratingSummary flag), not during initial processing -->
                <div
                  v-if="regeneratingSummary && store.currentMeeting.summary"
                  class="absolute inset-0 bg-white/90 backdrop-blur-sm z-10 flex items-center justify-center rounded-lg -m-6"
                >
                  <div class="text-center">
                    <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-accent-gold/10 flex items-center justify-center">
                      <svg class="w-8 h-8 text-accent-gold animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </div>
                    <h3 class="font-display text-lg text-espresso-700 mb-2">正在重新生成会议纪要...</h3>
                    <p class="text-sm text-espresso-400 font-sans">
                      {{ store.currentMeeting.progress }}% 完成
                    </p>
                  </div>
                </div>

                <!-- Content wrapper -->
                <div>
              <div class="flex items-center justify-between mb-8">
                <h2 class="font-display text-2xl text-espresso-700">会议纪要</h2>
                <div class="flex items-center gap-3">
                  <!-- Regenerate button - show when we have data (merged_segments) to regenerate from -->
                  <button
                    v-if="store.currentMeeting.merged_segments?.length && !editingSummary"
                    @click="confirmRegenerate"
                    :disabled="regeneratingSummary"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-sans rounded-lg border transition-all"
                    :class="regeneratingSummary
                      ? 'bg-espresso-100 border-espresso-200 text-espresso-400 cursor-not-allowed'
                      : 'bg-accent-gold/10 border-accent-gold text-accent-gold hover:bg-accent-gold/20'"
                    title="重新生成纪要"
                  >
                    <svg class="w-4 h-4" :class="{ 'animate-spin': regeneratingSummary }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    <span>{{ regeneratingSummary ? '重新生成中...' : '重新生成' }}</span>
                  </button>
                  <!-- Edit button (only show when not editing and has summary) -->
                  <button
                    v-if="store.currentMeeting.summary && !editingSummary"
                    @click="startEditingSummary"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-sans rounded-lg border border-cream-300 bg-white text-espresso-600 hover:border-espresso-400 hover:bg-cream-50 transition-all"
                    title="编辑纪要"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    <span>编辑</span>
                  </button>
                  <!-- Save/Cancel buttons (show when editing) -->
                  <template v-if="editingSummary">
                    <button
                      @click="saveSummary"
                      :disabled="savingSummary"
                      class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-sans rounded-lg border transition-all"
                      :class="savingSummary
                        ? 'bg-espresso-100 border-espresso-200 text-espresso-400 cursor-not-allowed'
                        : 'bg-accent-sage/10 border-accent-sage text-accent-sage hover:bg-accent-sage/20'"
                      title="保存修改"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M5 13l4 4L19 7" />
                      </svg>
                      <span>{{ savingSummary ? '保存中...' : '保存' }}</span>
                    </button>
                    <button
                      @click="cancelEditingSummary"
                      :disabled="savingSummary"
                      class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-sans rounded-lg border border-cream-300 bg-white text-espresso-600 hover:border-espresso-400 hover:bg-cream-50 transition-all"
                      title="取消编辑"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M6 18L18 6M6 6l12 12" />
                      </svg>
                      <span>取消</span>
                    </button>
                  </template>
                  <!-- Copy button -->
                  <button
                    v-if="store.currentMeeting.summary && !editingSummary"
                    @click="copySummary"
                    :disabled="copying"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-sans rounded-lg border transition-all"
                    :class="copySuccess
                      ? 'bg-accent-sage/10 border-accent-sage text-accent-sage'
                      : 'bg-white border-cream-300 text-espresso-600 hover:border-espresso-400 hover:bg-cream-50'"
                    :title="copySuccess ? '已复制!' : '复制纪要'"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path v-if="!copySuccess" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M5 13l4 4L19 7" />
                    </svg>
                    <span>{{ copySuccess ? '已复制' : '复制' }}</span>
                  </button>
                  <!-- Download button -->
                  <button
                    v-if="store.currentMeeting.summary && !editingSummary"
                    @click="downloadAsDocx"
                    :disabled="downloading"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-sans rounded-lg border transition-all"
                    :class="downloading
                      ? 'bg-espresso-100 border-espresso-200 text-espresso-400 cursor-not-allowed'
                      : 'bg-white border-cream-300 text-espresso-600 hover:border-espresso-400 hover:bg-cream-50'"
                    title="下载为Word文档"
                  >
                    <svg class="w-4 h-4" :class="{ 'animate-spin': downloading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path v-if="!downloading" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    <span>{{ downloading ? '生成中...' : '下载' }}</span>
                  </button>
                </div>
              </div>

              <div v-if="store.currentMeeting.summary" class="animate-fade-up">
                <!-- View mode: rendered markdown -->
                <article
                  v-if="!editingSummary"
                  class="markdown-content prose prose-espresso max-w-none"
                  v-html="renderedSummary"
                ></article>
                <!-- Edit mode: textarea -->
                <div v-else class="space-y-4">
                  <div class="relative">
                    <textarea
                      v-model="editedContent"
                      class="w-full min-h-[400px] p-4 bg-white border border-cream-300 rounded-lg text-espresso-700 font-sans leading-relaxed focus:outline-none focus:border-espresso-500 focus:ring-2 focus:ring-espresso-500/20 resize-y"
                      placeholder="在此编辑会议纪要内容（支持Markdown格式）..."
                    ></textarea>
                    <!-- Character count -->
                    <div class="absolute bottom-3 right-3 px-2 py-1 bg-cream-100 rounded text-xs text-espresso-500 font-sans">
                      {{ editedContent.length }} 字符
                    </div>
                  </div>
                  <p class="text-sm text-espresso-400 font-sans">
                    <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    支持 Markdown 格式：**粗体**、*斜体*、# 标题、- 列表等
                  </p>
                </div>
              </div>

              <!-- No summary / Failed state -->
              <div v-else class="text-center py-12">
                <!-- Failed with error message -->
                <div v-if="store.currentMeeting.status === 'failed' && store.currentMeeting.error_message" class="space-y-4">
                  <div class="w-16 h-16 mx-auto rounded-full bg-accent-terracotta/10 flex items-center justify-center">
                    <svg class="w-8 h-8 text-accent-terracotta" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                  <h3 class="font-display text-lg text-espresso-700">会议纪要生成失败</h3>
                  <p class="text-sm text-espresso-400 font-sans max-w-md mx-auto">
                    {{ store.currentMeeting.error_message }}
                  </p>
                  <button
                    @click="confirmRegenerate"
                    :disabled="regeneratingSummary"
                    class="inline-flex items-center gap-2 px-4 py-2 text-sm font-sans rounded-lg bg-accent-gold text-white hover:bg-accent-gold/80 transition-all"
                  >
                    <svg class="w-4 h-4" :class="{ 'animate-spin': regeneratingSummary }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    <span>{{ regeneratingSummary ? '重新生成中...' : '重新生成会议纪要' }}</span>
                  </button>
                </div>
                <!-- Still processing (initial generation) -->
                <div v-else-if="store.currentMeeting.status === 'processing'" class="space-y-4">
                  <div class="w-16 h-16 mx-auto rounded-full bg-accent-gold/10 flex items-center justify-center">
                    <svg class="w-8 h-8 text-accent-gold animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </div>
                  <h3 class="font-display text-lg text-espresso-700">正在生成会议纪要...</h3>
                  <p class="text-sm text-espresso-400 font-sans">
                    {{ store.currentMeeting.progress }}% 完成
                  </p>
                </div>
                <!-- No summary (other cases) -->
                <div v-else class="text-espresso-400 font-sans">
                  暂无会议纪要
                </div>
              </div>
              <!-- Content wrapper end -->
            </div>
            <!-- max-w-3xl relative end -->
            </div>
            <!-- flex-1 overflow-y-auto end -->
          </div>
          <!-- main end -->
          </main>
        </div>
      </div>
    </template>

    <!-- Regenerate Confirm Dialog -->
    <div
      v-if="showRegenerateConfirm"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 animate-fade-in"
      @click.self="cancelRegenerate"
    >
      <div class="bg-white rounded-xl shadow-2xl p-6 max-w-md mx-4 animate-slide-up">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-accent-gold/10 flex items-center justify-center">
            <svg class="w-5 h-5 text-accent-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
          <h3 class="font-display text-lg text-espresso-700">重新生成会议纪要</h3>
        </div>
        <p class="text-espresso-600 font-sans mb-6">
          确定要重新生成会议纪要吗？这将基于现有的发言记录生成新的会议纪要，当前纪要内容将被替换。
        </p>
        <div class="flex justify-end gap-3">
          <button
            @click="cancelRegenerate"
            class="px-4 py-2 text-sm font-sans rounded-lg border border-cream-300 bg-white text-espresso-600 hover:border-espresso-400 hover:bg-cream-50 transition-all"
          >
            取消
          </button>
          <button
            @click="handleRegenerateSummary"
            class="px-4 py-2 text-sm font-sans rounded-lg bg-accent-gold text-white hover:bg-accent-gold/80 transition-all"
          >
            重新生成
          </button>
        </div>
      </div>
    </div>

    <!-- Preview Dialog (shown after regeneration completes) -->
    <div
      v-if="showPreviewDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 animate-fade-in"
      @click.self="cancelPreview"
    >
      <div class="bg-white rounded-xl shadow-2xl p-6 max-w-2xl mx-4 animate-slide-up max-h-[80vh] overflow-hidden flex flex-col">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-accent-sage/10 flex items-center justify-center">
              <svg class="w-5 h-5 text-accent-sage" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 class="font-display text-lg text-espresso-700">会议纪要已重新生成</h3>
          </div>
          <button
            @click="cancelPreview"
            class="p-1 text-espresso-400 hover:text-espresso-600 transition-all"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto mb-4 p-4 bg-cream-50 rounded-lg">
          <div class="markdown-content prose prose-espresso max-w-none" v-html="renderedSummary"></div>
        </div>
        <p class="text-sm text-espresso-500 font-sans mb-4">
          新的会议纪要已自动更新。您可以继续编辑或关闭此窗口。
        </p>
        <div class="flex justify-end">
          <button
            @click="cancelPreview"
            class="px-4 py-2 text-sm font-sans rounded-lg bg-accent-sage text-white hover:bg-accent-sage/80 transition-all"
          >
            确定
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Custom styles for markdown content */
:deep(.markdown-content h2:first-child) {
  margin-top: 0;
}

/* Ensure line breaks are rendered correctly */
:deep(.markdown-content p) {
  white-space: pre-line;
  margin-bottom: 1em;
}

/* Ensure bold text displays correctly */
:deep(.markdown-content strong) {
  font-weight: 600;
}
</style>
