"""Repository for real-time segment operations."""
import logging
from typing import List
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
