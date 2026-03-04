<template>
  <div class="audio-recorder">
    <div class="recorder-controls">
      <el-button
        :type="isRecording ? 'danger' : 'primary'"
        :icon="isRecording ? 'VideoPause' : 'VideoPlay'"
        @click="toggleRecording"
        size="large"
      >
        {{ isRecording ? '暂停录音' : '开始录音' }}
      </el-button>

      <el-button
        v-if="isRecording || isPaused"
        type="warning"
        icon="VideoStop"
        @click="stopRecording"
        size="large"
      >
        结束转录
      </el-button>
    </div>

    <div v-if="isRecording || isPaused" class="recording-status">
      <el-badge :value="formatDuration(recordingTime)" class="recording-badge">
        <div class="recording-indicator" :class="{ paused: isPaused }"></div>
      </el-badge>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue';

const emit = defineEmits<{
  (e: 'audioData', data: ArrayBuffer): void;
  (e: 'recordingState', isRecording: boolean): void;
}>();

const isRecording = ref(false);
const isPaused = ref(false);
const recordingTime = ref(0);
let mediaRecorder: MediaRecorder | null = null;
let audioContext: AudioContext | null = null;
let processor: ScriptProcessorNode | null = null;
let source: MediaStreamAudioSourceNode | null = null;
let timer: number | null = null;

async function toggleRecording() {
  if (isRecording.value) {
    pauseRecording();
  } else {
    await startRecording();
  }
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    audioContext = new AudioContext({ sampleRate: 16000 });
    source = audioContext.createMediaStreamSource(stream);

    processor = audioContext.createScriptProcessor(4096, 1, 1);

    processor.onaudioprocess = (e) => {
      if (isRecording.value && !isPaused.value) {
        const audioData = e.inputBuffer.getChannelData(0);
        const float32Array = new Float32Array(audioData);
        emit('audioData', float32Array.buffer);
      }
    };

    source.connect(processor);
    processor.connect(audioContext.destination);

    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();

    isRecording.value = true;
    isPaused.value = false;
    emit('recordingState', true);

    // Start timer
    timer = window.setInterval(() => {
      recordingTime.value++;
    }, 1000);

  } catch (error) {
    console.error('Error starting recording:', error);
    ElMessage.error('无法访问麦克风');
  }
}

function pauseRecording() {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.pause();
    isPaused.value = true;
    if (timer) clearInterval(timer);
  }
}

function stopRecording() {
  if (mediaRecorder) {
    mediaRecorder.stop();
    mediaRecorder.stream.getTracks().forEach(track => track.stop());
  }

  if (processor) {
    processor.disconnect();
  }

  if (source) {
    source.disconnect();
  }

  if (audioContext) {
    audioContext.close();
  }

  if (timer) clearInterval(timer);

  isRecording.value = false;
  isPaused.value = false;
  recordingTime.value = 0;
  emit('recordingState', false);
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

onUnmounted(() => {
  stopRecording();
});
</script>

<style scoped>
.audio-recorder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 20px;
}

.recorder-controls {
  display: flex;
  gap: 12px;
}

.recording-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.recording-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #f56c6c;
  animation: pulse 1.5s infinite;
}

.recording-indicator.paused {
  background-color: #e6a23c;
  animation: none;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
