<script setup lang="ts">
import { ref, onUnmounted } from 'vue'

const emit = defineEmits<{
  (e: 'audioData', data: ArrayBuffer): void
  (e: 'recordingState', isRecording: boolean): void
}>()

const isRecording = ref(false)
const isPaused = ref(false)
const recordingTime = ref(0)
const errorMessage = ref('')
let mediaRecorder: MediaRecorder | null = null
let audioContext: AudioContext | null = null
let processor: ScriptProcessorNode | null = null
let source: MediaStreamAudioSourceNode | null = null
let timer: number | null = null

async function toggleRecording() {
  if (isRecording.value) {
    pauseRecording()
  } else {
    await startRecording()
  }
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

    audioContext = new AudioContext({ sampleRate: 16000 })
    source = audioContext.createMediaStreamSource(stream)

    processor = audioContext.createScriptProcessor(4096, 1, 1)

    processor.onaudioprocess = (e) => {
      if (isRecording.value && !isPaused.value) {
        const audioData = e.inputBuffer.getChannelData(0)
        const float32Array = new Float32Array(audioData)
        emit('audioData', float32Array.buffer)
      }
    }

    source.connect(processor)
    processor.connect(audioContext.destination)

    mediaRecorder = new MediaRecorder(stream)
    mediaRecorder.start()

    isRecording.value = true
    isPaused.value = false
    errorMessage.value = ''
    emit('recordingState', true)

    // Start timer
    timer = window.setInterval(() => {
      recordingTime.value++
    }, 1000)

  } catch (error) {
    console.error('Error starting recording:', error)
    errorMessage.value = '无法访问麦克风，请检查权限设置'
  }
}

function pauseRecording() {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.pause()
    isPaused.value = true
    if (timer) clearInterval(timer)
  }
}

function resumeRecording() {
  if (mediaRecorder && mediaRecorder.state === 'paused') {
    mediaRecorder.resume()
    isPaused.value = false
    timer = window.setInterval(() => {
      recordingTime.value++
    }, 1000)
  }
}

function stopRecording() {
  if (mediaRecorder) {
    mediaRecorder.stop()
    mediaRecorder.stream.getTracks().forEach(track => track.stop())
  }

  if (processor) {
    processor.disconnect()
  }

  if (source) {
    source.disconnect()
  }

  if (audioContext) {
    audioContext.close()
  }

  if (timer) clearInterval(timer)

  isRecording.value = false
  isPaused.value = false
  recordingTime.value = 0
  emit('recordingState', false)
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

onUnmounted(() => {
  stopRecording()
})
</script>

<template>
  <div class="audio-recorder">
    <!-- Error Message -->
    <div v-if="errorMessage" class="mb-4 p-4 bg-accent-terracotta/10 border border-accent-terracotta/30 rounded-lg">
      <p class="text-sm text-accent-terracotta font-sans">{{ errorMessage }}</p>
    </div>

    <!-- Recording Controls -->
    <div class="recorder-controls flex items-center justify-center gap-4">
      <button
        v-if="!isRecording"
        @click="toggleRecording"
        class="btn-primary flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
        开始录音
      </button>

      <template v-else>
        <button
          v-if="!isPaused"
          @click="pauseRecording"
          class="btn-ghost flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          暂停
        </button>

        <button
          v-else
          @click="resumeRecording"
          class="btn-primary flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          继续
        </button>

        <button
          @click="stopRecording"
          class="btn-ghost text-accent-terracotta hover:bg-accent-terracotta/10 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 10h6v4H9z" />
          </svg>
          停止
        </button>
      </template>
    </div>

    <!-- Recording Status -->
    <div v-if="isRecording || isPaused" class="recording-status flex items-center justify-center gap-3 mt-4">
      <div class="flex items-center gap-2">
        <div
          class="recording-indicator"
          :class="{ paused: isPaused }"
        ></div>
        <span class="text-lg font-mono text-espresso-700">{{ formatDuration(recordingTime) }}</span>
      </div>
      <span
        class="text-sm font-sans"
        :class="{
          'text-accent-sage': isRecording && !isPaused,
          'text-espresso-400': isPaused
        }"
      >
        {{ isPaused ? '已暂停' : '录音中...' }}
      </span>
    </div>

    <!-- Help Text -->
    <p v-if="!isRecording" class="text-center text-sm text-espresso-400 font-sans mt-4">
      点击"开始录音"开始实时转录，点击"停止"结束录音
    </p>
  </div>
</template>

<style scoped>
.audio-recorder {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.recording-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #ef4444;
  animation: pulse 1.5s infinite;
}

.recording-indicator.paused {
  background-color: #f59e0b;
  animation: none;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
