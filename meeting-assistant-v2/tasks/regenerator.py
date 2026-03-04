#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
"""Background task for regenerating meeting summaries."""
import logging

from ..models.database import AsyncSessionLocal
from ..models.meeting_model import MeetingStatus, ProcessingStage
from ..repositories.meeting_repository import meeting_repository, summary_repository
from ..services.llm_service import llm_service
from ..services.separation_service import SpeakerSegment

logger = logging.getLogger(__name__)


async def regenerate_summary_task(meeting_id: str):
    """
    Background task to regenerate meeting summary.

    This task regenerates the summary using existing merged segments data.
    """
    logger.info(f"[{meeting_id}] Starting summary regeneration task...")

    async with AsyncSessionLocal() as db:
        try:
            # Get meeting with details
            meeting = await meeting_repository.get_with_details(db, meeting_id)
            if not meeting:
                logger.error(f"[{meeting_id}] Meeting not found")
                return

            logger.info(f"[{meeting_id}] Regenerating summary for: {meeting.title}")

            # Build merged segments with transcripts for LLM
            merged_for_llm = []
            speaker_names_map = {}

            for participant in meeting.participants:
                speaker_names_map[participant.speaker_id] = participant.display_name

            for merged_seg in meeting.merged_segments:
                merged_for_llm.append(
                    SpeakerSegment(
                        speaker_id=merged_seg.speaker_id,
                        start_time=merged_seg.start_time,
                        end_time=merged_seg.end_time,
                        transcript=merged_seg.transcript
                    )
                )

            # Build speaker info list
            from ..services.separation_service import SpeakerInfo
            speakers_map = {}
            for participant in meeting.participants:
                if participant.speaker_id not in speakers_map:
                    speakers_map[participant.speaker_id] = {
                        'speaker_id': participant.speaker_id,
                        'display_name': participant.display_name,
                        'segments': [],
                        'total_duration': 0.0
                    }

            # Calculate total duration per speaker
            for merged_seg in meeting.merged_segments:
                if merged_seg.speaker_id in speakers_map:
                    speakers_map[merged_seg.speaker_id]['total_duration'] += merged_seg.duration

            speakers = [
                SpeakerInfo(
                    speaker_id=v['speaker_id'],
                    display_name=v['display_name'],
                    segments=[],
                    total_duration=v['total_duration']
                )
                for v in speakers_map.values()
            ]

            # Generate new summary
            summary_content = await llm_service.generate_summary_from_timeline(
                audio_path=meeting.audio_path,
                speakers=speakers,
                meeting_title=meeting.title,
                timeline=merged_for_llm,
                speaker_name_map=speaker_names_map
            )

            logger.info(f"[{meeting_id}] New summary generated: {len(summary_content.content)} chars")

            # Update or create summary
            existing_summary = await summary_repository.get_by_meeting(db, meeting_id)
            if existing_summary:
                existing_summary.content = summary_content.content
                existing_summary.raw_response = summary_content.raw_response
            else:
                await summary_repository.create(
                    db=db,
                    meeting_id=meeting_id,
                    content=summary_content.content,
                    raw_response=summary_content.raw_response
                )

            await db.commit()

            # Update meeting status to completed
            await meeting_repository.update_stage(
                db=db,
                meeting_id=meeting_id,
                status=MeetingStatus.COMPLETED,
                stage=ProcessingStage.COMPLETED,
                progress=100,
                error_message=None
            )
            await db.commit()

            logger.info(f"[{meeting_id}] ✅ Summary regeneration completed successfully")

        except Exception as e:
            logger.exception(f"[{meeting_id}] ERROR during summary regeneration: {e}")

            # Mark as failed but keep separation data
            async with AsyncSessionLocal() as error_db:
                await meeting_repository.update_stage(
                    db=error_db,
                    meeting_id=meeting_id,
                    status=MeetingStatus.FAILED,
                    stage=ProcessingStage.SEPARATION_COMPLETED,
                    progress=50,
                    error_message=f"总结生成失败: {str(e)}"
                )
                await error_db.commit()

            logger.error(f"[{meeting_id}] Summary regeneration FAILED")
