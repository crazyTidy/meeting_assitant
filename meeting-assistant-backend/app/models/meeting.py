"""Meeting database model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum,Float
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


# Import SpeakerSegment to avoid circular imports
class SpeakerSegment:
    """Placeholder for SpeakerSegment to avoid circular import."""
    pass


class MeetingStatus(str, enum.Enum):
    """Meeting processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStage(str, enum.Enum):
    """Processing stage for progress tracking."""
    INITIALIZING = "initializing"       # 0-10%
    SEPARATING = "separating"           # 10-50% - 人声分离阶段
    SEPARATION_COMPLETED = "separation_completed"  # 50% - 人声分离完成
    SUMMARIZING = "summarizing"         # 50-90% - 总结生成阶段
    COMPLETED = "completed"             # 100% - 全部完成


class MeetingMode(str, enum.Enum):
    """Meeting processing mode."""
    FILE_UPLOAD = "file_upload"      # 原有：文件上传模式
    REAL_TIME = "real_time"          # 新增：实时转录模式

    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum lookup for legacy data."""
        if isinstance(value, str):
            # 尝试匹配不区分大小写
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        # 返回默认值
        return cls.FILE_UPLOAD


class Meeting(Base):
    """Meeting model."""

    __tablename__ = "meetings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    audio_path = Column(String(512), nullable=False)
    status = Column(
        Enum(MeetingStatus),
        default=MeetingStatus.PENDING,
        nullable=False
    )
    progress = Column(Integer, default=0)
    stage = Column(
        String(50),
        default=ProcessingStage.INITIALIZING,
        nullable=True
    )
    error_message = Column(Text, nullable=True)
    duration = Column(Float, nullable=True)  # in seconds (can be fractional)

    # 实时转录模式字段
    mode = Column(
        Enum(MeetingMode),
        default=MeetingMode.FILE_UPLOAD,
        nullable=False
    )
    websocket_id = Column(String(100), nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    participants = relationship(
        "Participant",
        back_populates="meeting",
        cascade="all, delete-orphan"
    )
    summary = relationship(
        "Summary",
        back_populates="meeting",
        uselist=False,
        cascade="all, delete-orphan"
    )
    speaker_segments = relationship(
        "SpeakerSegment",
        back_populates="meeting",
        cascade="all, delete-orphan",
        order_by="SpeakerSegment.start_time"
    )
    merged_segments = relationship(
        "MergedSegment",
        back_populates="meeting",
        cascade="all, delete-orphan",
        order_by="MergedSegment.start_time"
    )
    real_time_segments = relationship(
        "RealTimeSegment",
        back_populates="meeting",
        cascade="all, delete-orphan",
        order_by="RealTimeSegment.start_time"
    )

    def __repr__(self):
        return f"<Meeting(id={self.id}, title={self.title}, status={self.status})>"
