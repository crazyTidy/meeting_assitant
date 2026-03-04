# 实时语音转录功能实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为会议助手增加实时语音转录模式，支持会议进行中的边说边录、实时话者分离、WebSocket实时推送

**架构:** 前端通过WebSocket上传音频流 → 后端WhisperX模型识别+话者分离 → 结果实时推送给前端并保存数据库

**Tech Stack:**
- 后端: FastAPI WebSocket, WhisperX (ASR+Diarization)
- 前端: Vue 3, WebSocket API, Web Audio API
- 数据库: SQLite (扩展现有schema)

---

## 概览

本计划将实时转录功能集成到现有会议助手中，新增实时模式与现有文件上传模式并行。

### 实现任务清单

| 任务 | 描述 | 预估时间 |
|------|------|---------|
| Task 1 | 扩展数据模型 (Meetings, RealTimeSegments) | 30min |
| Task 2 | 创建 WhisperX 转录服务 | 45min |
| Task 3 | 实现 WebSocket 端点 | 40min |
| Task 4 | 创建 Repository 层 | 20min |
| Task 5 | 前端 WebSocket 客户端 | 35min |
| Task 6 | 前端录音组件 | 30min |
| Task 7 | 前端实时转录页面 | 25min |
| Task 8 | 集成测试 | 20min |

---

## Task 1: 扩展数据模型

**Files:**
- Modify: `meeting-assistant-backend/app/models/meeting.py`
- Create: `meeting-assistant-backend/app/models/real_time_segment.py`
- Modify: `meeting-assistant-backend/app/core/database.py`

### Step 1: 添加 MeetingMode 枚举到 meeting.py

在 `meeting.py` 文件顶部添加新的枚举：

```python
class MeetingMode(str, enum.Enum):
    """会议处理模式"""
    FILE_UPLOAD = "file_upload"      # 原有：文件上传模式
    REAL_TIME = "real_time"          # 新增：实时转录模式
```

编辑位置: 在 `ProcessingStage` 枚举之后, `Meeting` 类之前

### Step 2: 扩展 Meeting 模型

在 `Meeting` 类中添加新字段：

```python
class Meeting(Base):
    # ... 现有字段 ...

    # 新增字段
    mode = Column(
        Enum(MeetingMode),
        default=MeetingMode.FILE_UPLOAD,
        nullable=False
    )
    websocket_id = Column(String(100), nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
```

编辑位置: 在 `duration` 字段之后

### Step 3: 创建 RealTimeSegment 模型

创建新文件 `real_time_segment.py`:

```python
"""Real-time transcription segment model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class RealTimeSegment(Base):
    """Real-time transcription segment."""

    __tablename__ = "real_time_segments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String(36), ForeignKey("meetings.id"), nullable=False)
    speaker_id = Column(String(50), nullable=False)
    text = Column(Text, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    is_final = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    meeting = relationship("Meeting", back_populates="real_time_segments")
```

### Step 4: 更新 Meeting 关系

在 `meeting.py` 的 `Meeting` 类中添加关系：

```python
# 在 relationship 部分添加
real_time_segments = relationship(
    "RealTimeSegment",
    back_populates="meeting",
    cascade="all, delete-orphan",
    order_by="RealTimeSegment.start_time"
)
```

### Step 5: 导入新模型到 database.py

在 `app/core/database.py` 中添加导入：

```python
from app.models.real_time_segment import RealTimeSegment
```

### Step 6: 创建数据库迁移脚本

创建新文件 `meeting-assistant-backend/migrations/add_realtime_mode.py`:

```python
"""Add real-time transcription mode to meetings table."""
from sqlalchemy import text
from app.core.database import engine

async def upgrade():
    async with engine.begin() as conn:
        # Add mode column
        await conn.execute(text(
            "ALTER TABLE meetings ADD COLUMN mode VARCHAR(20) DEFAULT 'file_upload' NOT NULL"
        ))
        # Add websocket_id column
        await conn.execute(text(
            "ALTER TABLE meetings ADD COLUMN websocket_id VARCHAR(100)"
        ))
        # Add started_at column
        await conn.execute(text(
            "ALTER TABLE meetings ADD COLUMN started_at TIMESTAMP"
        ))
        # Add ended_at column
        await conn.execute(text(
            "ALTER TABLE meetings ADD COLUMN ended_at TIMESTAMP"
        ))

async def downgrade():
    async with engine.begin() as conn:
        # SQLite doesn't support DROP COLUMN easily, so recreate table
        await conn.execute(text(
            "CREATE TABLE meetings_backup AS SELECT id, title, audio_path, status, progress, stage, error_message, duration, created_at, updated_at FROM meetings"
        ))
        await conn.execute(text("DROP TABLE meetings"))
        await conn.execute(text("ALTER TABLE meetings_backup RENAME TO meetings"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(upgrade())
```

### Step 7: 创建 real_time_segments 表

创建新文件 `meeting-assistant-backend/migrations/create_realtime_segments.py`:

```python
"""Create real_time_segments table."""
from sqlalchemy import text
from app.core.database import engine

async def upgrade():
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS real_time_segments (
                id VARCHAR(36) PRIMARY KEY,
                meeting_id VARCHAR(36) NOT NULL,
                speaker_id VARCHAR(50) NOT NULL,
                text TEXT NOT NULL,
                start_time FLOAT NOT NULL,
                end_time FLOAT NOT NULL,
                is_final BOOLEAN DEFAULT 0,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
            )
        """))
        # Create index for faster queries
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_realtime_meeting ON real_time_segments(meeting_id)"
        ))

if __name__ == "__main__":
    import asyncio
    asyncio.run(upgrade())
```

### Step 8: 运行迁移

```bash
cd meeting-assistant-backend
python migrations/add_realtime_mode.py
python migrations/create_realtime_segments.py
```

预期输出: 表结构更新成功, 无错误

### Step 9: 提交

```bash
git add meeting-assistant-backend/app/models/meeting.py
git add meeting-assistant-backend/app/models/real_time_segment.py
git add meeting-assistant-backend/app/core/database.py
git add meeting-assistant-backend/migrations/add_realtime_mode.py
git add meeting-assistant-backend/migrations/create_realtime_segments.py
git commit -m "feat: add realtime transcription data models"
```

---

## Task 2: 创建 WhisperX 转录服务

**Files:**
- Create: `meeting-assistant-backend/app/services/whisperx_service.py`
- Modify: `meeting-assistant-backend/requirements.txt`

### Step 1: 添加依赖到 requirements.txt

```bash
echo "whisperx>=3.0.0" >> meeting-assistant-backend/requirements.txt
```

### Step 2: 安装依赖

```bash
cd meeting-assistant-backend
pip install whisperx>=3.0.0
```

预期输出: 安装成功, 无错误

### Step 3: 创建 WhisperX 转录服务

创建 `whisperx_service.py`:

```python
"""WhisperX real-time transcription service."""
import logging
import time
import asyncio
from typing import Optional, Dict, Any
from collections import deque
import numpy as np
import torch

logger = logging.getLogger(__name__)


class WhisperXTranscriber:
    """WhisperX real-time transcription with speaker diarization."""

    def __init__(self, meeting_id: str, language: str = "zh", sample_rate: int = 16000):
        self.meeting_id = meeting_id
        self.language = language
        self.sample_rate = sample_rate
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Models (lazy loaded)
        self.model = None
        self.align_model = None
        self.align_metadata = None
        self.diarize_model = None

        # Audio buffer for chunking
        self.audio_buffer = deque()
        self.buffer_duration = 3.0  # Process 3 seconds at a time
        self.start_time = time.time()
        self.is_initialized = False

    async def initialize(self):
        """Initialize WhisperX models."""
        if self.is_initialized:
            return

        logger.info(f"Initializing WhisperX for meeting {self.meeting_id}")

        try:
            import whisperx

            # Load transcription model
            compute_type = "float16" if self.device == "cuda" else "int8"
            self.model = whisperx.load_model(
                "base",
                self.device,
                compute_type=compute_type
            )

            # Load alignment model for word-level timestamps
            self.align_model, self.align_metadata = whisperx.load_align_model(
                language_code=self.language,
                device=self.device
            )

            # Load diarization model
            self.diarize_model = whisperx.DiarizationPipeline(
                device=self.device,
                use_auth_token=None
            )

            self.is_initialized = True
            logger.info(f"WhisperX initialized successfully for meeting {self.meeting_id}")

        except Exception as e:
            logger.error(f"Failed to initialize WhisperX: {e}")
            raise

    async def process_audio(self, audio_data: bytes) -> Optional[Dict[str, Any]]:
        """Process audio chunk and return transcription result.

        Args:
            audio_data: Raw audio bytes (float32, 16kHz)

        Returns:
            Dict with speaker, text, start_time, end_time or None
        """
        if not self.is_initialized:
            await self.initialize()

        # Decode audio
        audio = np.frombuffer(audio_data, dtype=np.float32)

        # Skip if too short
        if len(audio) < self.sample_rate * 0.5:  # Less than 0.5 seconds
            return None

        # Add to buffer
        chunk_duration = len(audio) / self.sample_rate
        self.audio_buffer.append({
            "audio": audio,
            "duration": chunk_duration
        })

        # Check if buffer is full enough
        total_duration = sum(item["duration"] for item in self.audio_buffer)
        if total_duration < self.buffer_duration:
            return None

        # Combine audio chunks
        audio_chunks = [item["audio"] for item in self.audio_buffer]
        combined_audio = np.concatenate(audio_chunks)

        # Transcribe with WhisperX
        try:
            result = await self._transcribe_with_diarization(combined_audio)

            # Clear buffer after processing
            self.audio_buffer.clear()

            return result

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None

    async def _transcribe_with_diarization(self, audio: np.ndarray) -> Optional[Dict[str, Any]]:
        """Transcribe audio with speaker diarization."""
        import whisperx

        # Step 1: Transcribe
        result = self.model.transcribe(
            audio,
            language=self.language,
            batch_size=1
        )

        # Step 2: Align for word-level timestamps
        result = whisperx.align(
            result,
            self.align_model,
            self.align_metadata,
            self.device,
            audio
        )

        # Step 3: Assign speakers
        diarize_segments = self.diarize_model(audio)
        result = whisperx.assign_word_speakers(diarize_segments, result)

        # Extract the last segment (new content)
        if result.get("segments"):
            segments = result["segments"]

            # Return all segments from this chunk
            results = []
            for seg in segments:
                if seg["text"].strip():
                    results.append({
                        "speaker": seg.get("speaker", "SPEAKER_00"),
                        "text": seg["text"].strip(),
                        "start_time": round(seg["start"], 2),
                        "end_time": round(seg["end"], 2)
                    })

            # Return the last result if any
            return results[-1] if results else None

        return None

    async def finalize(self) -> list:
        """Finalize transcription and return all remaining segments."""
        # Process any remaining audio in buffer
        results = []
        if self.audio_buffer:
            audio_chunks = [item["audio"] for item in self.audio_buffer]
            if audio_chunks:
                combined_audio = np.concatenate(audio_chunks)
                result = await self._transcribe_with_diarization(combined_audio)
                if result:
                    results.append(result)

        self.audio_buffer.clear()
        return results

    async def cleanup(self):
        """Cleanup resources."""
        self.audio_buffer.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info(f"WhisperX cleaned up for meeting {self.meeting_id}")
```

### Step 4: 提交

```bash
git add meeting-assistant-backend/app/services/whisperx_service.py
git add meeting-assistant-backend/requirements.txt
git commit -m "feat: add WhisperX transcription service"
```

---

## Task 3: 实现 WebSocket 端点

**Files:**
- Create: `meeting-assistant-backend/app/api/v1/endpoints/realtime.py`
- Modify: `meeting-assistant-backend/app/api/v1/router.py`

### Step 1: 创建 WebSocket 端点

创建 `realtime.py`:

```python
"""Real-time transcription WebSocket endpoint."""
import json
import base64
import logging
import uuid
from datetime import datetime
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.meeting import Meeting, MeetingMode, MeetingStatus
from app.models.real_time_segment import RealTimeSegment
from app.repositories.meeting_repository import meeting_repository
from app.services.whisperx_service import WhisperXTranscriber

logger = logging.getLogger(__name__)

router = APIRouter()

# Track active connections
active_connections: Dict[str, WebSocket] = {}
active_transcribers: Dict[str, WhisperXTranscriber] = {}


@router.websocket("/ws/transcribe")
async def transcribe_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time transcription."""
    await websocket.accept()

    meeting_id = None
    transcriber = None

    try:
        # Step 1: Receive initial handshake
        init_data = await websocket.receive_json()

        if init_data.get("type") != "init":
            await websocket.send_json({
                "type": "error",
                "message": "First message must be init"
            })
            await websocket.close()
            return

        meeting_id = init_data.get("meeting_id") or str(uuid.uuid4())
        language = init_data.get("language", "zh")
        title = init_data.get("title") or f"实时会议 {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        logger.info(f"Initializing real-time transcription for meeting: {meeting_id}")

        # Step 2: Create meeting record
        async with get_db() as db:
            meeting = Meeting(
                id=meeting_id,
                title=title,
                audio_path="",  # No file for real-time
                mode=MeetingMode.REAL_TIME,
                status=MeetingStatus.PROCESSING,
                progress=0,
                started_at=datetime.utcnow()
            )
            db.add(meeting)
            await db.commit()

        # Step 3: Initialize transcriber
        transcriber = WhisperXTranscriber(meeting_id, language)
        await transcriber.initialize()

        active_connections[meeting_id] = websocket
        active_transcribers[meeting_id] = transcriber

        # Step 4: Send connected message
        await websocket.send_json({
            "type": "connected",
            "meeting_id": meeting_id,
            "message": "转录服务已就绪"
        })

        # Step 5: Process audio stream
        async for message in websocket.iter_json():
            msg_type = message.get("type")

            if msg_type == "audio":
                # Decode and process audio
                audio_data = base64.b64decode(message.get("data", ""))
                result = await transcriber.process_audio(audio_data)

                if result:
                    # Save to database
                    async with get_db() as db:
                        segment = RealTimeSegment(
                            meeting_id=meeting_id,
                            speaker_id=result["speaker"],
                            text=result["text"],
                            start_time=result["start_time"],
                            end_time=result["end_time"],
                            is_final=True
                        )
                        db.add(segment)
                        await db.commit()

                        # Send to frontend
                        await websocket.send_json({
                            "type": "transcript",
                            "data": {
                                "segment_id": segment.id,
                                "speaker": result["speaker"],
                                "text": result["text"],
                                "start_time": result["start_time"],
                                "end_time": result["end_time"]
                            }
                        })

            elif msg_type == "stop":
                logger.info(f"Stopping transcription for meeting: {meeting_id}")
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {meeting_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
    finally:
        # Cleanup
        if transcriber:
            await transcriber.cleanup()

        if meeting_id:
            active_connections.pop(meeting_id, None)
            active_transcribers.pop(meeting_id, None)

            # Update meeting status
            async with get_db() as db:
                meeting = await db.get(Meeting, meeting_id)
                if meeting:
                    meeting.ended_at = datetime.utcnow()
                    meeting.status = MeetingStatus.COMPLETED
                    meeting.progress = 100
                    await db.commit()


@router.get("/transcribe/active")
async def get_active_sessions():
    """Get list of active transcription sessions."""
    return {
        "active_sessions": list(active_connections.keys()),
        "count": len(active_connections)
    }
```

### Step 2: 更新路由

在 `router.py` 中添加新路由：

```python
from app.api.v1.endpoints import realtime

api_router.include_router(realtime.router, tags=["realtime"])
```

### Step 3: 提交

```bash
git add meeting-assistant-backend/app/api/v1/endpoints/realtime.py
git add meeting-assistant-backend/app/api/v1/router.py
git commit -m "feat: add WebSocket endpoint for real-time transcription"
```

---

## Task 4: 创建 Repository 层

**Files:**
- Create: `meeting-assistant-backend/app/repositories/realtime_segment_repository.py`

### Step 1: 创建 RealTimeSegment Repository

创建 `realtime_segment_repository.py`:

```python
"""Repository for real-time segment operations."""
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.real_time_segment import RealTimeSegment

logger = logging.getLogger(__name__)


class RealTimeSegmentRepository:
    """Repository for RealTimeSegment model."""

    async def create(
        self,
        db: AsyncSession,
        meeting_id: str,
        speaker_id: str,
        text: str,
        start_time: float,
        end_time: float,
        is_final: bool = True
    ) -> RealTimeSegment:
        """Create a new real-time segment."""
        segment = RealTimeSegment(
            meeting_id=meeting_id,
            speaker_id=speaker_id,
            text=text,
            start_time=start_time,
            end_time=end_time,
            is_final=is_final
        )
        db.add(segment)
        await db.commit()
        await db.refresh(segment)
        return segment

    async def get_by_meeting(
        self,
        db: AsyncSession,
        meeting_id: str
    ) -> List[RealTimeSegment]:
        """Get all segments for a meeting, ordered by time."""
        result = await db.execute(
            select(RealTimeSegment)
            .where(RealTimeSegment.meeting_id == meeting_id)
            .order_by(RealTimeSegment.start_time)
        )
        return list(result.scalars().all())

    async def get_by_speaker(
        self,
        db: AsyncSession,
        meeting_id: str,
        speaker_id: str
    ) -> List[RealTimeSegment]:
        """Get all segments for a specific speaker."""
        result = await db.execute(
            select(RealTimeSegment)
            .where(
                RealTimeSegment.meeting_id == meeting_id,
                RealTimeSegment.speaker_id == speaker_id
            )
            .order_by(RealTimeSegment.start_time)
        )
        return list(result.scalars().all())


realtime_segment_repository = RealTimeSegmentRepository()
```

### Step 2: 更新 repositories/__init__.py

```python
from app.repositories.realtime_segment_repository import realtime_segment_repository
```

### Step 3: 提交

```bash
git add meeting-assistant-backend/app/repositories/realtime_segment_repository.py
git commit -m "feat: add RealTimeSegment repository"
```

---

## Task 5: 前端 WebSocket 客户端

**Files:**
- Create: `meeting-assistant-frontend/src/utils/websocket.ts`
- Create: `meeting-assistant-frontend/src/types/realtime.ts`

### Step 1: 创建类型定义

创建 `realtime.ts`:

```typescript
/** Real-time transcription types */

export interface TranscriptSegment {
  segment_id: string;
  speaker: string;
  text: string;
  start_time: number;
  end_time: number;
}

export interface WebSocketMessage {
  type: 'connected' | 'transcript' | 'error';
  meeting_id?: string;
  message?: string;
  data?: TranscriptSegment;
}

export interface RealtimeMeeting {
  id: string;
  title: string;
  status: string;
  started_at: string;
  segments: TranscriptSegment[];
}
```

### Step 2: 创建 WebSocket 工具类

创建 `websocket.ts`:

```typescript
/** WebSocket client for real-time transcription */

export class TranscriptionWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3;

  constructor(private baseUrl: string = '') {
    this.url = `${baseUrl.replace('http', 'ws')}/api/v1/ws/transcribe`;
  }

  connect(
    config: { title?: string; language?: string; meeting_id?: string },
    handlers: {
      onConnected: (meetingId: string) => void;
      onTranscript: (segment: any) => void;
      onError: (error: string) => void;
      onDisconnected: () => void;
    }
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          // Send init message
          this.send({
            type: 'init',
            meeting_id: config.meeting_id,
            language: config.language || 'zh',
            title: config.title
          });
          resolve();
        };

        this.ws.onmessage = (event) => {
          const message = JSON.parse(event.data);

          switch (message.type) {
            case 'connected':
              handlers.onConnected(message.meeting_id);
              break;
            case 'transcript':
              handlers.onTranscript(message.data);
              break;
            case 'error':
              handlers.onError(message.message || 'Unknown error');
              break;
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket closed');
          handlers.onDisconnected();
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  sendAudio(audioData: ArrayBuffer): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      // Convert to base64
      const base64 = this.arrayBufferToBase64(audioData);
      this.send({
        type: 'audio',
        data: base64
      });
    }
  }

  stop(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.send({ type: 'stop' });
    }
    this.close();
  }

  private send(data: any): void {
    if (this.ws) {
      this.ws.send(JSON.stringify(data));
    }
  }

  private close(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}
```

### Step 3: 提交

```bash
git add meeting-assistant-frontend/src/utils/websocket.ts
git add meeting-assistant-frontend/src/types/realtime.ts
git commit -m "feat: add WebSocket client for real-time transcription"
```

---

## Task 6: 前端录音组件

**Files:**
- Create: `meeting-assistant-frontend/src/components/AudioRecorder.vue`

### Step 1: 创建录音组件

创建 `AudioRecorder.vue`:

```vue
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
        v-if="isRecording"
        type="warning"
        icon="VideoStop"
        @click="stopRecording"
        size="large"
      >
        结束转录
      </el-button>
    </div>

    <div v-if="isRecording" class="recording-status">
      <el-badge :value="formatDuration(recordingTime)" class="recording-badge">
        <div class="recording-indicator"></div>
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
const recordingTime = ref(0);
let mediaRecorder: MediaRecorder | null = null;
let audioContext: AudioContext | null = null;
let processor: ScriptProcessorNode | null = null;
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
    const source = audioContext.createMediaStreamSource(stream);

    processor = audioContext.createScriptProcessor(4096, 1, 1);

    processor.onaudioprocess = (e) => {
      if (isRecording.value) {
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
    isRecording.value = false;
    emit('recordingState', false);
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

  if (audioContext) {
    audioContext.close();
  }

  if (timer) clearInterval(timer);

  isRecording.value = false;
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

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
```

### Step 2: 提交

```bash
git add meeting-assistant-frontend/src/components/AudioRecorder.vue
git commit -m "feat: add AudioRecorder component"
```

---

## Task 7: 前端实时转录页面

**Files:**
- Create: `meeting-assistant-frontend/src/views/RealtimeTranscriptionView.vue`
- Modify: `meeting-assistant-frontend/src/router/index.ts`

### Step 1: 创建实时转录页面

创建 `RealtimeTranscriptionView.vue`:

```vue
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

  wsClient.value = new TranscriptionWebSocket(import.meta.env.VITE_API_BASE_URL);

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
```

### Step 2: 更新路由配置

在 `router/index.ts` 中添加:

```typescript
{
  path: '/realtime',
  name: 'RealtimeTranscription',
  component: () => import('@/views/RealtimeTranscriptionView.vue')
}
```

### Step 3: 添加入口链接

在 `MeetingListView.vue` 中添加按钮:

```vue
<el-button type="success" @click="$router.push('/realtime')">
  实时转录
</el-button>
```

### Step 4: 提交

```bash
git add meeting-assistant-frontend/src/views/RealtimeTranscriptionView.vue
git add meeting-assistant-frontend/src/router/index.ts
git commit -m "feat: add real-time transcription page"
```

---

## Task 8: 集成测试

**Files:**
- Create: `meeting-assistant-backend/tests/test_realtime.py`

### Step 1: 创建测试文件

创建 `test_realtime.py`:

```python
"""Tests for real-time transcription feature."""
import pytest
import asyncio
from httpx import AsyncClient
from fastapi import WebSocketDisconnect


@pytest.mark.asyncio
async def test_realtime_meeting_creation(async_client: AsyncClient, db_session):
    """Test creating a real-time meeting record."""
    from app.models.meeting import Meeting, MeetingMode

    meeting = Meeting(
        title="Test Real-time Meeting",
        audio_path="",
        mode=MeetingMode.REAL_TIME
    )
    db_session.add(meeting)
    await db_session.commit()
    await db_session.refresh(meeting)

    assert meeting.id is not None
    assert meeting.mode == MeetingMode.REAL_TIME
    assert meeting.started_at is not None


@pytest.mark.asyncio
async def test_realtime_segment_creation(async_client: AsyncClient, db_session):
    """Test creating a real-time segment."""
    from app.models.meeting import Meeting, MeetingMode
    from app.models.real_time_segment import RealTimeSegment
    from app.repositories.realtime_segment_repository import realtime_segment_repository

    # Create meeting
    meeting = Meeting(
        title="Test Meeting",
        audio_path="",
        mode=MeetingMode.REAL_TIME
    )
    db_session.add(meeting)
    await db_session.commit()

    # Create segment
    segment = await realtime_segment_repository.create(
        db=db_session,
        meeting_id=meeting.id,
        speaker_id="SPEAKER_00",
        text="Hello world",
        start_time=0.0,
        end_time=2.5
    )

    assert segment.id is not None
    assert segment.text == "Hello world"
    assert segment.speaker_id == "SPEAKER_00"


@pytest.mark.asyncio
async def test_get_active_sessions(async_client: AsyncClient):
    """Test getting active transcription sessions."""
    response = await async_client.get("/api/v1/transcribe/active")

    assert response.status_code == 200
    assert "active_sessions" in response.json()
    assert "count" in response.json()


@pytest.mark.asyncio
async def test_realtime_segments_by_meeting(async_client: AsyncClient, db_session):
    """Test getting segments by meeting ID."""
    from app.models.meeting import Meeting, MeetingMode
    from app.models.real_time_segment import RealTimeSegment
    from app.repositories.realtime_segment_repository import realtime_segment_repository

    # Create meeting
    meeting = Meeting(
        title="Test Meeting",
        audio_path="",
        mode=MeetingMode.REAL_TIME
    )
    db_session.add(meeting)
    await db_session.commit()

    # Create segments
    await realtime_segment_repository.create(
        db=db_session,
        meeting_id=meeting.id,
        speaker_id="SPEAKER_00",
        text="First segment",
        start_time=0.0,
        end_time=2.0
    )

    await realtime_segment_repository.create(
        db=db_session,
        meeting_id=meeting.id,
        speaker_id="SPEAKER_01",
        text="Second segment",
        start_time=2.0,
        end_time=4.0
    )

    # Get segments
    segments = await realtime_segment_repository.get_by_meeting(db_session, meeting.id)

    assert len(segments) == 2
    assert segments[0].text == "First segment"
    assert segments[1].text == "Second segment"
```

### Step 2: 运行测试

```bash
cd meeting-assistant-backend
pytest tests/test_realtime.py -v
```

预期输出: 所有测试通过

### Step 3: 提交

```bash
git add meeting-assistant-backend/tests/test_realtime.py
git commit -m "test: add real-time transcription tests"
```

---

## 完成清单

- [ ] Task 1: 数据模型扩展完成
- [ ] Task 2: WhisperX 服务完成
- [ ] Task 3: WebSocket 端点完成
- [ ] Task 4: Repository 层完成
- [ ] Task 5: 前端 WebSocket 客户端完成
- [ ] Task 6: 前端录音组件完成
- [ ] Task 7: 前端实时转录页面完成
- [ ] Task 8: 集成测试通过

---

## 注意事项

1. **WhisperX 依赖**: 需要确保服务器有足够资源运行 WhisperX，建议使用 GPU
2. **音频格式**: 前端录音采样率需设置为 16kHz 以匹配 WhisperX 要求
3. **网络延迟**: WebSocket 连接可能受网络影响，需要添加错误重连机制
4. **资源清理**: 确保 WebSocket 断开时正确释放模型资源

## 后续优化建议

1. 添加说话人名称编辑功能（类似文件上传模式）
2. 支持实时转录结束后生成会议纪要
3. 添加音频可视化波形显示
4. 支持导出实时转录结果为文档
