<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMeetingStore } from '@/stores/meeting'

const router = useRouter()
const store = useMeetingStore()

const title = ref('')
const audioFile = ref<File | null>(null)
const isDragging = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const errorMessage = ref('')

const fileInputRef = ref<HTMLInputElement | null>(null)

const allowedExtensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']

const canSubmit = computed(() => {
  return title.value.trim() && audioFile.value && !isUploading.value
})

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false

  const files = e.dataTransfer?.files
  const file = files?.[0]
  if (file) {
    validateAndSetFile(file)
  }
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    validateAndSetFile(file)
  }
}

const validateAndSetFile = (file: File) => {
  errorMessage.value = ''

  const ext = '.' + file.name.split('.').pop()?.toLowerCase()
  if (!allowedExtensions.includes(ext)) {
    errorMessage.value = `不支持的文件格式。支持的格式：${allowedExtensions.join(', ')}`
    return
  }

  const maxSize = 100 * 1024 * 1024 // 100MB
  if (file.size > maxSize) {
    errorMessage.value = '文件过大，最大支持 100MB'
    return
  }

  audioFile.value = file

  // Auto-fill title if empty
  if (!title.value) {
    title.value = file.name.replace(/\.[^/.]+$/, '')
  }
}

const removeFile = () => {
  audioFile.value = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

const handleSubmit = async () => {
  if (!canSubmit.value) return

  isUploading.value = true
  errorMessage.value = ''
  uploadProgress.value = 0

  try {
    // Simulate upload progress
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 200)

    const meeting = await store.createMeeting(title.value.trim(), audioFile.value!)

    clearInterval(progressInterval)
    uploadProgress.value = 100

    // Navigate to meeting detail
    setTimeout(() => {
      router.push(`/meetings/${meeting.id}`)
    }, 500)
  } catch (e: any) {
    errorMessage.value = e.message || '上传失败，请重试'
    isUploading.value = false
    uploadProgress.value = 0
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto px-6 py-12">
    <!-- Page Header -->
    <div class="text-center mb-12 animate-fade-up">
      <p class="subhead mb-3">New Meeting</p>
      <h2 class="masthead mb-4">上传会议录音</h2>
      <p class="text-espresso-500 font-body max-w-md mx-auto">
        上传音频文件，我们将自动识别说话人并生成会议纪要
      </p>
    </div>

    <!-- Upload Card -->
    <div class="card-paper p-8 animate-fade-up delay-100">
      <!-- Drop Zone -->
      <div
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
        @click="fileInputRef?.click()"
        class="relative border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all duration-300"
        :class="{
          'border-espresso-400 bg-cream-200': isDragging,
          'border-cream-300 hover:border-espresso-300 hover:bg-cream-100': !isDragging && !audioFile,
          'border-accent-sage bg-accent-sage/5': audioFile
        }"
      >
        <input
          ref="fileInputRef"
          type="file"
          accept=".mp3,.wav,.m4a,.flac,.ogg"
          class="hidden"
          @change="handleFileSelect"
        />

        <!-- No file state -->
        <template v-if="!audioFile">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-cream-200 flex items-center justify-center">
            <svg class="w-8 h-8 text-espresso-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <p class="font-sans text-espresso-600 mb-2">
            <span class="font-medium">点击上传</span> 或拖拽文件到此处
          </p>
          <p class="text-sm text-espresso-400">
            支持 MP3, WAV, M4A, FLAC, OGG 格式，最大 100MB
          </p>
        </template>

        <!-- File selected state -->
        <template v-else>
          <div class="flex items-center justify-center gap-4">
            <div class="w-12 h-12 rounded-full bg-accent-sage/20 flex items-center justify-center">
              <svg class="w-6 h-6 text-accent-sage" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
              </svg>
            </div>
            <div class="text-left">
              <p class="font-sans font-medium text-espresso-700">{{ audioFile.name }}</p>
              <p class="text-sm text-espresso-400">{{ formatFileSize(audioFile.size) }}</p>
            </div>
            <button
              @click.stop="removeFile"
              class="ml-auto p-2 text-espresso-400 hover:text-accent-terracotta transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </template>
      </div>

      <!-- Title Input -->
      <div class="mt-8">
        <label class="block text-sm font-sans font-medium text-espresso-600 mb-2">
          会议标题
        </label>
        <input
          v-model="title"
          type="text"
          placeholder="例如：周一产品评审会"
          class="input-editorial"
          maxlength="255"
        />
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="mt-4 p-4 bg-accent-terracotta/10 border border-accent-terracotta/30 rounded-lg">
        <p class="text-sm text-accent-terracotta font-sans">{{ errorMessage }}</p>
      </div>

      <!-- Progress Bar -->
      <div v-if="isUploading" class="mt-6">
        <div class="flex items-center justify-between text-sm font-sans mb-2">
          <span class="text-espresso-600">正在上传...</span>
          <span class="text-espresso-400">{{ uploadProgress }}%</span>
        </div>
        <div class="h-1 bg-cream-200 rounded-full overflow-hidden">
          <div
            class="h-full bg-espresso-600 rounded-full transition-all duration-300"
            :style="{ width: `${uploadProgress}%` }"
          ></div>
        </div>
      </div>

      <!-- Submit Button -->
      <div class="mt-8 flex justify-end">
        <button
          @click="handleSubmit"
          :disabled="!canSubmit"
          class="btn-primary px-8"
        >
          <svg v-if="isUploading" class="w-5 h-5 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <template v-if="!isUploading">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            开始处理
          </template>
          <template v-else>处理中...</template>
        </button>
      </div>
    </div>

    <!-- Help Text -->
    <div class="mt-8 text-center text-sm text-espresso-400 font-sans animate-fade-up delay-200">
      <p>上传后，系统将自动进行人声分离和会议纪要生成</p>
      <p class="mt-1">处理过程可能需要几分钟，您可以在列表页查看进度</p>
    </div>
  </div>
</template>
