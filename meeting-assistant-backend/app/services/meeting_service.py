"""Meeting service for business logic."""
import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional, Tuple, List
from fastapi import UploadFile, BackgroundTasks

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.meeting import Meeting, MeetingStatus, ProcessingStage
from app.repositories.meeting_repository import (
    meeting_repository,
    participant_repository,
    summary_repository
)
from app.schemas.meeting import MeetingListResponse, MeetingStatusResponse
from app.tasks.processor import process_meeting_task
from app.utils.audio import get_audio_duration


class MeetingService:
    """Business logic for meetings."""

    def __init__(self):
        self.repository = meeting_repository

    def _get_status_message(self, status: MeetingStatus, progress: int, stage: Optional[ProcessingStage] = None) -> str:
        """Get human-readable status message."""
        if status == MeetingStatus.PENDING:
            return "等待处理..."
        elif status == MeetingStatus.COMPLETED:
            return "处理完成"
        elif status == MeetingStatus.FAILED:
            if stage == ProcessingStage.SEPARATION_COMPLETED:
                return f"部分完成 (人声分离完成 {progress}%, 总结生成失败)"
            return "处理失败"
        elif status == MeetingStatus.PROCESSING:
            # 根据阶段返回不同的消息
            stage_messages = {
                ProcessingStage.INITIALIZING: f"初始化中... ({progress}%)",
                ProcessingStage.SEPARATING: f"人声分离中... ({progress}%)",
                ProcessingStage.SEPARATION_COMPLETED: f"人声分离完成 ✅ ({progress}%)",
                ProcessingStage.SUMMARIZING: f"AI 总结生成中... ({progress}%)",
                ProcessingStage.COMPLETED: f"处理完成 ✅ ({progress}%)",
            }
            return stage_messages.get(stage, f"正在处理... ({progress}%)")
        return "未知状态"

    def _get_stage_description(self, stage: Optional[ProcessingStage]) -> Optional[str]:
        """Get human-readable stage description."""
        if not stage:
            return None
        descriptions = {
            ProcessingStage.INITIALIZING: "初始化处理",
            ProcessingStage.SEPARATING: "人声分离进行中",
            ProcessingStage.SEPARATION_COMPLETED: "人声分离完成",
            ProcessingStage.SUMMARIZING: "AI 总结生成中",
            ProcessingStage.COMPLETED: "全部完成",
        }
        return descriptions.get(stage)

    async def create_meeting(
        self,
        db: AsyncSession,
        title: str,
        audio_file: UploadFile,
        background_tasks: BackgroundTasks
    ) -> Meeting:
        """Create a meeting and start processing."""
        # Validate file extension
        file_ext = Path(audio_file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_AUDIO_EXTENSIONS:
            raise ValueError(
                f"不支持的音频格式。支持的格式: {', '.join(settings.ALLOWED_AUDIO_EXTENSIONS)}"
            )

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = Path(settings.UPLOAD_DIR) / unique_filename

        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await audio_file.read()
            if len(content) > settings.MAX_UPLOAD_SIZE:
                raise ValueError(
                    f"文件过大。最大允许: {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB"
                )
            await f.write(content)

        # Get audio duration using ffmpeg
        duration = await get_audio_duration(str(file_path))

        # Create meeting record
        meeting = await self.repository.create(
            db=db,
            title=title,
            audio_path=str(file_path),
            duration=duration
        )

        # Commit immediately so background task can find the meeting
        await db.commit()
        await db.refresh(meeting)

        # Start background processing
        background_tasks.add_task(
            process_meeting_task,
            meeting_id=meeting.id
        )

        return meeting

    async def get_meeting(
        self,
        db: AsyncSession,
        meeting_id: str
    ) -> Optional[Meeting]:
        """Get meeting with details."""
        return await self.repository.get_with_details(db, meeting_id)

    async def get_meeting_list(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 10
    ) -> MeetingListResponse:
        """Get paginated meeting list."""
        meetings, total = await self.repository.get_list(
            db=db,
            search=search,
            page=page,
            size=size
        )

        pages = (total + size - 1) // size if total > 0 else 0

        return MeetingListResponse(
            items=meetings,
            total=total,
            page=page,
            size=size,
            pages=pages
        )

    async def get_meeting_status(
        self,
        db: AsyncSession,
        meeting_id: str
    ) -> Optional[MeetingStatusResponse]:
        """Get meeting processing status."""
        meeting = await self.repository.get(db, meeting_id)
        if not meeting:
            return None

        return MeetingStatusResponse(
            id=meeting.id,
            status=meeting.status,
            progress=meeting.progress,
            stage=meeting.stage,
            message=self._get_status_message(meeting.status, meeting.progress, meeting.stage),
            stage_description=self._get_stage_description(meeting.stage)
        )

    async def delete_meeting(
        self,
        db: AsyncSession,
        meeting_id: str
    ) -> bool:
        """Delete meeting and associated files."""
        meeting = await self.repository.get(db, meeting_id)
        if not meeting:
            return False

        # Delete audio file
        try:
            if os.path.exists(meeting.audio_path):
                os.remove(meeting.audio_path)
        except Exception:
            pass  # Ignore file deletion errors

        # Delete from database
        return await self.repository.delete(db, meeting_id)


class ParticipantService:
    """Business logic for participants."""

    def __init__(self):
        self.repository = participant_repository

    async def update_participant_name(
        self,
        db: AsyncSession,
        meeting_id: str,
        participant_id: str,
        display_name: str
    ) -> Optional[dict]:
        """Update participant display name."""
        # Verify participant belongs to meeting
        participant = await self.repository.get(db, participant_id)
        if not participant or participant.meeting_id != meeting_id:
            return None

        updated = await self.repository.update_name(
            db=db,
            participant_id=participant_id,
            display_name=display_name
        )

        if updated:
            return {
                "id": updated.id,
                "speaker_id": updated.speaker_id,
                "display_name": updated.display_name
            }
        return None

    async def update_participant_name_by_speaker_id(
        self,
        db: AsyncSession,
        speaker_id: str,
        display_name: str
    ) -> Optional[int]:
        """
        Update display name for all participants with the given speaker_id.

        This updates all participants (across all meetings) that have the given speaker_id.

        Args:
            db: Database session
            speaker_id: Speaker identifier (e.g., "speaker_1")
            display_name: New display name

        Returns:
            Number of participants updated, or None if speaker_id not found
        """
        from sqlalchemy import select, update
        from app.models.participant import Participant

        # First check if any participants exist with this speaker_id
        result = await db.execute(
            select(Participant).where(Participant.speaker_id == speaker_id)
        )
        participants = result.scalars().all()

        if not participants:
            return None

        # Update all participants with this speaker_id
        await db.execute(
            update(Participant)
            .where(Participant.speaker_id == speaker_id)
            .values(display_name=display_name)
        )

        await db.commit()

        return len(participants)


# Singleton instances
meeting_service = MeetingService()
participant_service = ParticipantService()
