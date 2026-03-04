<template>
  <div class="realtime-transcription">
    <el-page-header @back="goBack" title="返回">
      <template #content>
        <span class="page-title">实时会议转录</span>
      </template>
    </el-page-header>

    <el-card class="main-card" v-if="!isConnected">
      <el-form label-width="100px">
        <el-form-item label="会议标题">
          <el-input v-model="meetingTitle" placeholder="请输入会议标题" />
        </el-form-item>
        <el-form-item label="语言">
          <el-select v-model="language">
            <el-option label="中文" value="zh" />
            <el-option label="English" value="en" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="startSession">开始会议</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <div v-else class="transcription-area">
      <el-card class="controls-card">
        <AudioRecorder
          @audioData="handleAudioData"
          @recordingState="handleRecordingState"
        />
        <div class="connection-status">
          <el-tag :type="isRecording ? 'success' : 'info'">
            {{ isRecording ? '录音中' : '已暂停' }}
          </el-tag>
          <el-tag type="success">已连接</el-tag>
        </div>
      </el-card>

      <el-card class="transcript-card">
        <template #header>
          <div class="card-header">
            <span>转录内容</span>
            <el-button text @click="clearTranscript">清空</el-button>
          </div>
        </template>

        <div class="transcript-content">
          <div
            v-for="segment in transcripts"
            :key="segment.segment_id"
            class="transcript-segment"
          >
            <span class="speaker-label">{{ segment.speaker }}:</span>
            <span class="transcript-text">{{ segment.text }}</span>
            <span class="time-stamp">{{ formatTime(segment.start_time) }}</span>
          </div>

          <el-empty v-if="transcripts.length === 0" description="暂无转录内容" />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import AudioRecorder from '@/components/AudioRecorder.vue';
import { TranscriptionWebSocket } from '@/utils/websocket';
import type { TranscriptSegment } from '@/types/realtime';

const router = useRouter();

const meetingTitle = ref('');
const language = ref('zh');
const isConnected = ref(false);
const isRecording = ref(false);
const transcripts = ref<TranscriptSegment[]>([]);
const wsClient = ref<TranscriptionWebSocket | null>(null);
const meetingId = ref('');

async function startSession() {
  if (!meetingTitle.value) {
    ElMessage.warning('请输入会议标题');
    return;
  }

  wsClient.value = new TranscriptionWebSocket(import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000');

  try {
    await wsClient.value.connect(
      {
        title: meetingTitle.value,
        language: language.value
      },
      {
        onConnected: (id) => {
          meetingId.value = id;
          isConnected.value = true;
          ElMessage.success('转录服务已连接');
        },
        onTranscript: (segment) => {
          transcripts.value.push(segment);
          // Auto scroll to bottom
          setTimeout(() => {
            const content = document.querySelector('.transcript-content');
            if (content) content.scrollTop = content.scrollHeight;
          }, 100);
        },
        onError: (error) => {
          ElMessage.error(`错误: ${error}`);
        },
        onDisconnected: () => {
          isConnected.value = false;
          ElMessage.warning('连接已断开');
        }
      }
    );
  } catch (error) {
    ElMessage.error('连接失败');
    console.error(error);
  }
}

function handleAudioData(data: ArrayBuffer) {
  if (wsClient.value && isConnected.value) {
    wsClient.value.sendAudio(data);
  }
}

function handleRecordingState(recording: boolean) {
  isRecording.value = recording;
}

function clearTranscript() {
  transcripts.value = [];
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function goBack() {
  if (isConnected.value) {
    wsClient.value?.stop();
  }
  router.push('/meetings');
}
</script>

<style scoped>
.realtime-transcription {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.main-card {
  margin-top: 20px;
}

.transcription-area {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.controls-card {
  position: sticky;
  top: 20px;
  z-index: 10;
}

.connection-status {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  justify-content: center;
}

.transcript-card {
  min-height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.transcript-content {
  max-height: 500px;
  overflow-y: auto;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.transcript-segment {
  display: flex;
  gap: 12px;
  padding: 12px;
  margin-bottom: 8px;
  background-color: white;
  border-radius: 6px;
  align-items: flex-start;
}

.speaker-label {
  font-weight: 600;
  color: #409eff;
  white-space: nowrap;
}

.transcript-text {
  flex: 1;
  line-height: 1.6;
}

.time-stamp {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
}
</style>
