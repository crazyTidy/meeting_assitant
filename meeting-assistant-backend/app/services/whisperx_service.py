"""WhisperX real-time transcription service."""
import logging
import time
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
