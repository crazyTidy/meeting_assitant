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
from app.services.whisperx_service import WhisperXTranscriber

logger = logging.getLogger(__name__)

router = APIRouter()

# Track active connections
active_connections: Dict[str, WebSocket] = {}
active_transcribers: Dict[str, WhisperXTranscriber] = {}


def get_db_session():
    """Get database session for WebSocket."""
    from app.core.database import AsyncSessionLocal
    return AsyncSessionLocal()


@router.websocket("/ws/transcribe")
async def transcribe_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time transcription."""
    await websocket.accept()

    meeting_id = None
    transcriber = None
    db = None

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
        db = get_db_session()
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
            if db:
                try:
                    meeting = await db.get(Meeting, meeting_id)
                    if meeting:
                        meeting.ended_at = datetime.utcnow()
                        meeting.status = MeetingStatus.COMPLETED
                        meeting.progress = 100
                        await db.commit()
                except Exception as e:
                    logger.error(f"Error updating meeting status: {e}")

            if db:
                await db.close()


@router.get("/transcribe/active")
async def get_active_sessions():
    """Get list of active transcription sessions."""
    return {
        "active_sessions": list(active_connections.keys()),
        "count": len(active_connections)
    }
