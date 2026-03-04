"""Mock real-time transcription service for testing."""
import logging
import time
import random
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class WhisperXTranscriber:
    """Mock transcriber for simulating real-time transcription."""

    # 模拟转录文本库
    MOCK_TEXTS = {
        "zh": [
            "大家好，今天我们来讨论一下新产品的设计方案",
            "我认为这个功能非常重要，需要优先实现",
            "关于技术实现方面，我有几个建议",
            "这个问题需要进一步讨论",
            "我们可以在下周的会议上再详细说明",
            "好的，我同意你的观点",
            "那我们就这样定了，大家还有其他意见吗",
            "这部分我负责跟进",
            "请问大家还有什么问题吗",
            "今天的会议就到这里，谢谢大家参与"
        ],
        "en": [
            "Hello everyone, let's discuss the new product design today",
            "I think this feature is very important and should be implemented first",
            "I have some suggestions regarding the technical implementation",
            "This issue needs further discussion",
            "We can discuss this in more detail at next week's meeting",
            "Okay, I agree with your point",
            "Then it's settled, does anyone have any other opinions",
            "I'll follow up on this part",
            "Does anyone have any questions",
            "That's all for today's meeting, thank you all for participating"
        ]
    }

    def __init__(self, meeting_id: str, language: str = "zh", sample_rate: int = 16000):
        self.meeting_id = meeting_id
        self.language = language
        self.sample_rate = sample_rate

        # 状态追踪
        self.start_time = time.time()
        self.is_initialized = False
        self.segment_count = 0
        self.current_speaker = 0

        # 模拟处理延迟
        self.processing_delay = 2.0  # 秒

    async def initialize(self):
        """Initialize mock transcriber."""
        if self.is_initialized:
            return

        logger.info(f"Initializing mock transcriber for meeting {self.meeting_id}")
        # 模拟初始化延迟
        await asyncio_sleep(0.1)
        self.is_initialized = True
        logger.info(f"Mock transcriber initialized for meeting {self.meeting_id}")

    async def process_audio(self, audio_data: bytes) -> Optional[Dict[str, Any]]:
        """Process audio chunk and return mock transcription result.

        Args:
            audio_data: Raw audio bytes (ignored in mock mode)

        Returns:
            Dict with speaker, text, start_time, end_time or None
        """
        if not self.is_initialized:
            await self.initialize()

        # 模拟处理时间
        await asyncio_sleep(0.1)

        # 每处理几次音频返回一个模拟转录结果
        self.segment_count += 1

        # 每5次音频处理返回一个转录结果（模拟累积时间）
        if self.segment_count % 5 == 0:
            elapsed_time = time.time() - self.start_time

            # 随机选择说话人（每3次切换一次）
            if self.segment_count % 15 == 0:
                self.current_speaker = (self.current_speaker + 1) % 3

            # 随机选择文本
            texts = self.MOCK_TEXTS.get(self.language, self.MOCK_TEXTS["zh"])
            text = random.choice(texts)

            return {
                "speaker": f"SPEAKER_0{self.current_speaker}",
                "text": text,
                "start_time": round(elapsed_time - 3, 2),
                "end_time": round(elapsed_time, 2)
            }

        return None

    async def finalize(self) -> list:
        """Finalize transcription and return any remaining segments."""
        logger.info(f"Finalizing mock transcription for meeting {self.meeting_id}")
        return []

    async def cleanup(self):
        """Cleanup resources."""
        self.segment_count = 0
        self.current_speaker = 0
        logger.info(f"Mock transcriber cleaned up for meeting {self.meeting_id}")


# Helper function for async sleep
async def asyncio_sleep(seconds: float):
    """Async sleep helper."""
    import asyncio
    await asyncio.sleep(seconds)
