#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
"""Meeting API endpoints."""
from typing import Optional
from pathlib import Path
from urllib.parse import quote
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import get_db
from ..settings import environment_config
from ..items.meeting_item import (
    MeetingResponseItem,
    MeetingDetailResponseItem,
    MeetingListResponseItem,
    MeetingStatusResponseItem,
    ErrorResponseItem
)
from ..services.meeting_service import meeting_service, summary_service, regenerate_service

router = APIRouter(prefix="/meetings", tags=["meetings"])


class SummaryUpdateRequest(BaseModel):
    """Request model for updating summary."""
    content: str


@router.post(
    "/",
    response_model=MeetingResponseItem,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponseItem, "description": "Invalid input"},
        413: {"model": ErrorResponseItem, "description": "File too large"}
    }
)
async def create_meeting(
    background_tasks: BackgroundTasks,
    title: str = Form(..., min_length=1, max_length=255),
    audio: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload audio and create a new meeting.

    - **title**: Meeting title (required)
    - **audio**: Audio file (mp3, wav, m4a supported)

    Returns the created meeting with pending status.
    Processing starts automatically in the background.
    """
    try:
        meeting = await meeting_service.create_meeting(
            db=db,
            title=title,
            audio_file=audio,
            background_tasks=background_tasks
        )
        return meeting
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_INPUT", "message": str(e)}}
        )


@router.get(
    "/",
    response_model=MeetingListResponseItem
)
async def list_meetings(
    search: Optional[str] = None,
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of meetings.

    - **search**: Search by meeting title (optional)
    - **page**: Page number (default: 1)
    - **size**: Items per page (default: 10, max: 100)
    """
    if page < 1:
        page = 1
    if size < 1:
        size = 1
    if size > 100:
        size = 100

    return await meeting_service.get_meeting_list(
        db=db,
        search=search,
        page=page,
        size=size
    )


@router.get(
    "/{meeting_id}",
    response_model=MeetingDetailResponseItem,
    responses={404: {"model": ErrorResponseItem}}
)
async def get_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get meeting details including participants and summary.

    - **meeting_id**: Meeting UUID
    """
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "会议不存在"}}
        )
    return meeting


@router.get(
    "/{meeting_id}/status",
    response_model=MeetingStatusResponseItem,
    responses={404: {"model": ErrorResponseItem}}
)
async def get_meeting_status(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get meeting processing status.

    Use this endpoint to poll for processing progress.
    Recommended polling interval: 3 seconds.

    - **meeting_id**: Meeting UUID
    """
    status_response = await meeting_service.get_meeting_status(db, meeting_id)
    if not status_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "会议不存在"}}
        )
    return status_response


@router.delete(
    "/{meeting_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponseItem}}
)
async def delete_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a meeting and all associated data.

    - **meeting_id**: Meeting UUID
    """
    deleted = await meeting_service.delete_meeting(db, meeting_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "会议不存在"}}
        )


@router.get(
    "/{meeting_id}/audio",
    responses={404: {"model": ErrorResponseItem}}
)
async def download_audio(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Download the original audio file for a meeting.

    - **meeting_id**: Meeting UUID
    """
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "会议不存在"}}
        )

    audio_path = Path(meeting.audio_path)
    if not audio_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "FILE_NOT_FOUND", "message": "音频文件不存在"}}
        )

    # Determine media type based on file extension
    media_type = "audio/mpeg"
    if audio_path.suffix == ".wav":
        media_type = "audio/wav"
    elif audio_path.suffix == ".m4a":
        media_type = "audio/mp4"
    elif audio_path.suffix == ".flac":
        media_type = "audio/flac"
    elif audio_path.suffix == ".ogg":
        media_type = "audio/ogg"

    # Create filename from title
    safe_title = "".join(c for c in meeting.title if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"{safe_title}{audio_path.suffix}"

    # Use RFC 5987 encoding for non-ASCII filenames
    encoded_filename = quote(filename)

    return FileResponse(
        path=str(audio_path),
        media_type=media_type,
        filename=filename,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )


@router.patch(
    "/{meeting_id}/summary",
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponseItem}}
)
async def update_summary(
    meeting_id: str,
    request: SummaryUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update meeting summary content.

    - **meeting_id**: Meeting UUID
    - **content**: New summary content in Markdown format
    """
    # Verify meeting exists
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "会议不存在"}}
        )

    # Update summary
    updated = await summary_service.update_summary(
        db=db,
        meeting_id=meeting_id,
        content=request.content
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "SUMMARY_NOT_FOUND", "message": "会议纪要不存在"}}
        )

    await db.commit()

    return updated


@router.post(
    "/{meeting_id}/regenerate-summary",
    response_model=MeetingStatusResponseItem,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ErrorResponseItem, "description": "Cannot regenerate summary"},
        404: {"model": ErrorResponseItem, "description": "Meeting not found"}
    }
)
async def regenerate_summary(
    meeting_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Regenerate meeting summary using existing speaker segments.

    This endpoint triggers a background task to regenerate the AI summary
    based on the existing speaker timeline data. Useful when you want to
    improve the summary quality or the original generation failed.

    - **meeting_id**: Meeting UUID

    Returns the processing status. The actual generation happens in background.
    """
    result = await regenerate_service.regenerate_summary(
        db=db,
        meeting_id=meeting_id,
        background_tasks=background_tasks
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "会议不存在"}}
        )

    return result
