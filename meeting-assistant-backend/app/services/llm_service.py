"""LLM service for generating meeting summaries using ZhipuAI."""
import logging
import requests
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

from app.core.config import settings
from app.services.separation_service import SpeakerInfo, SpeakerSegment
from app.services.asr_service import TranscriptResult

logger = logging.getLogger(__name__)


@dataclass
class SummaryResult:
    """Result from summary generation."""
    content: str  # Markdown formatted summary
    raw_response: Optional[str] = None


class LLMService:
    """Service for generating meeting summaries using Zhipu GLM."""

    def __init__(self):
        self.api_key = settings.ZHIPU_API_KEY
        self.api_key = "dc27759f5b5a4107b6af67aaf60e4a23.DmhTXSW9nk0eL74y"

    def _build_prompt(
        self,
        meeting_title: str,
        speakers: List[SpeakerInfo],
        transcript: TranscriptResult
    ) -> str:
        """Build prompt for meeting summary generation with full transcript."""

        # Build speaker info with speaking time
        speaker_list = "、".join([s.display_name for s in speakers])

        prompt = f"""你是专业的公文写作助手。请根据以下会议转录内容生成一份公文标准格式的会议纪要。

【会议信息】
会议标题：{meeting_title}
参会人员：{speaker_list}

【会议转录内容】
{transcript.full_text}

【写作要求】
1. **内容提炼**：不要逐字逐句罗列转录内容，要对讨论进行提炼、归纳、总结
2. **按议题组织**：根据讨论内容归纳出若干主要议题，每个议题下概括核心观点和讨论要点
3. **引用发言**：重要观点可引用发言人并标注，如"张三指出：..."
4. **公文格式**：使用"一、二、三"作为大标题编号，使用"**标题**"加粗格式
5. **语言风格**：语言严谨、简洁、专业，避免口语化表达
6. **实事求是**：完全基于转录文本，不要虚构信息；未明确的信息填写"未明确提及"

【输出格式】
**会议时间**：[根据转录推断或填写"未明确提及"]
**会议地点**：[如转录中提到，请列出；否则写"未明确提及"]
**参会人员**：{speaker_list}
**记录人**：AI助手

---

**会议议题**：[一句话概括会议核心议题]

---

**会议内容**：

本次会议主要讨论了以下事项：

**一、[议题标题]**

[概括该议题的核心内容和讨论要点，提炼主要观点，如有重要发言请注明发言人]

**二、[议题标题]**

[概括该议题的核心内容和讨论要点]

**三、[议题标题]**

[概括该议题的核心内容和讨论要点]

---

**会议决议**：

一、[决议事项1]

二、[决议事项2]

三、[决议事项3]

[如无明确决议，可写"本次会议未形成明确决议"]

---

**会议要求**：（仅当会议中有明确的待办事项、任务分配时才输出此部分，否则删除）

一、[负责人/责任方]负责[具体事项]，于[时限]前完成。

二、[负责人/责任方]负责[具体事项]，于[时限]前完成。

---
"""

        return prompt

    async def generate_summary(
        self,
        audio_path: str,
        speakers: List[SpeakerInfo],
        meeting_title: str,
        transcript: TranscriptResult
    ) -> SummaryResult:
        """
        Generate meeting summary using Zhipu GLM based on transcript.

        This calls the Zhipu AI API to generate meeting summaries.

        Args:
            audio_path: Path to audio file (for reference)
            speakers: List of speakers with metadata
            meeting_title: Title of the meeting
            transcript: Complete transcript with timeline

        Returns:
            SummaryResult with generated summary
        """
        logger.info(f"[LLM_SUMMARY] Generating summary for meeting: {meeting_title}")
        logger.info(f"[LLM_SUMMARY] API Key configured: {self.api_key}")
        logger.info(f"[LLM_SUMMARY] Number of speakers: {len(speakers)}")
        logger.info(f"[LLM_SUMMARY] Transcript segments: {len(transcript.segments)}")
        logger.info(f"[LLM_SUMMARY] Full text length: {len(transcript.full_text)} characters")

        try:
            # Build prompt for LLM
            prompt = self._build_prompt(meeting_title, speakers, transcript)

            # Print the full prompt for debugging
            logger.info(f"[LLM_SUMMARY] === PROMPT START ===")
            logger.info(f"[LLM_SUMMARY] {prompt}")
            logger.info(f"[LLM_SUMMARY] === PROMPT END ===")
            logger.info(f"[LLM_SUMMARY] Prompt length: {len(prompt)} characters")

            # Real API call to Zhipu AI (智谱 GLM) using requests
            logger.info(f"[LLM_SUMMARY] Calling Zhipu AI API...")

            api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "glm-4-flash",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的会议纪要助手，擅长从会议转录中提炼关键信息。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }

            response = requests.post(api_url, headers=headers, json=payload, timeout=600)
            response.raise_for_status()
            response_data = response.json()

            logger.info(f"[LLM_SUMMARY] API response received, id: {response_data.get('id')}")
            logger.debug(f"[LLM_SUMMARY] Response model: {response_data.get('model')}")
            logger.debug(f"[LLM_SUMMARY] Usage: {response_data.get('usage')}")

            content = response_data['choices'][0]['message']['content']
            raw_response = str(response_data)

            logger.info(f"[LLM_SUMMARY] Summary generated successfully")
            logger.info(f"[LLM_SUMMARY] Summary length: {len(content)} characters")

            return SummaryResult(
                content=content,
                raw_response=raw_response
            )

        except requests.RequestException as e:
            logger.error(f"[LLM_SUMMARY] API request failed: {e}")
            raise
        except KeyError as e:
            logger.error(f"[LLM_SUMMARY] Invalid API response format: {e}")
            raise
        except Exception as e:
            logger.exception(f"[LLM_SUMMARY] Error generating summary: {e}")
            raise

    def _build_prompt_from_timeline(
        self,
        meeting_title: str,
        speakers: List[SpeakerInfo],
        timeline: List[SpeakerSegment],
        speaker_name_map: Optional[dict] = None
    ) -> str:
        """Build prompt for meeting summary generation from timeline segments with transcripts."""

        # Build speaker info with speaking time
        speaker_list = "、".join([s.display_name for s in speakers])

        # Use display_name from map if available, otherwise use speaker_id
        def get_speaker_display_name(speaker_id: str) -> str:
            if speaker_name_map and speaker_id in speaker_name_map:
                return speaker_name_map[speaker_id]
            # Find in speakers list
            for s in speakers:
                if s.speaker_id == speaker_id:
                    return s.display_name
            return speaker_id

        # Build timeline as text with actual transcripts
        # Format: [timestamp] 显示名称 (speaker_id): 发言内容
        timeline_text = "\n".join([
            f"- [{self._format_timestamp(seg.start_time)}-{self._format_timestamp(seg.end_time)}] {get_speaker_display_name(seg.speaker_id)}: {seg.transcript if seg.transcript else '(暂无转写文本)'}"
            for seg in timeline
        ])

        prompt = f"""你是专业的公文写作助手。请根据以下会议发言记录生成一份公文标准格式的会议纪要。

【会议信息】
会议标题：{meeting_title}
参会人员：{speaker_list}

【发言记录（按时间顺序）】
{timeline_text}

【写作要求】
1. **内容提炼**：不要逐字逐句罗列发言记录，要对讨论进行提炼、归纳、总结
2. **按议题组织**：根据讨论内容归纳出若干主要议题，每个议题下概括核心观点和讨论要点
3. **引用发言**：重要观点可引用发言人并标注，如"张三指出：..."
4. **公文格式**：使用"一、二、三"作为大标题编号，使用"**标题**"加粗格式
5. **语言风格**：语言严谨、简洁、专业，避免口语化表达
6. **实事求是**：完全基于发言记录，不要虚构信息；未明确的信息填写"未明确提及"

【输出格式】
**会议时间**：[根据发言记录推断或填写"未明确提及"]
**会议地点**：[如发言中提到，请列出；否则写"未明确提及"]
**参会人员**：{speaker_list}
**记录人**：AI助手

---

**会议议题**：[一句话概括会议核心议题]

---

**会议内容**：

本次会议主要讨论了以下事项：

**一、[议题标题]**

[概括该议题的核心内容和讨论要点，提炼主要观点，如有重要发言请注明发言人]

**二、[议题标题]**

[概括该议题的核心内容和讨论要点]

**三、[议题标题]**

[概括该议题的核心内容和讨论要点]

---

**会议决议**：

一、[决议事项1]

二、[决议事项2]

三、[决议事项3]

[如无明确决议，可写"本次会议未形成明确决议"]

---

**会议要求**：（仅当会议中有明确的待办事项、任务分配时才输出此部分，否则删除）

一、[负责人/责任方]负责[具体事项]，于[时限]前完成。

二、[负责人/责任方]负责[具体事项]，于[时限]前完成。

---
"""

        return prompt

    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp as MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    async def generate_summary_from_timeline(
        self,
        audio_path: str,
        speakers: List[SpeakerInfo],
        meeting_title: str,
        timeline: List[SpeakerSegment],
        speaker_name_map: Optional[dict] = None
    ) -> SummaryResult:
        """
        Generate meeting summary using Zhipu GLM based on timeline segments.

        This generates a summary structure based on speaker timeline without transcription.

        Args:
            audio_path: Path to audio file (for reference)
            speakers: List of speakers with metadata
            meeting_title: Title of the meeting
            timeline: List of speaker segments with timestamps
            speaker_name_map: Optional mapping from speaker_id to display_name

        Returns:
            SummaryResult with generated summary structure
        """
        logger.info(f"[LLM_SUMMARY] Generating summary from timeline for meeting: {meeting_title}")
        logger.info(f"[LLM_SUMMARY] API Key configured: {bool(self.api_key)}")
        logger.info(f"[LLM_SUMMARY] Number of speakers: {len(speakers)}")
        logger.info(f"[LLM_SUMMARY] Timeline segments: {len(timeline)}")

        try:
            # Build prompt for LLM
            prompt = self._build_prompt_from_timeline(meeting_title, speakers, timeline, speaker_name_map)

            # Print the full prompt for debugging
            logger.info(f"[LLM_SUMMARY] === TIMELINE PROMPT START ===")
            logger.info(f"[LLM_SUMMARY] {prompt}")
            logger.info(f"[LLM_SUMMARY] === TIMELINE PROMPT END ===")
            logger.info(f"[LLM_SUMMARY] Prompt length: {len(prompt)} characters")

            # Real API call to Zhipu AI (智谱 GLM) using requests
            logger.info(f"[LLM_SUMMARY] Calling Zhipu AI API...")

            api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "glm-4-flash",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的会议纪要助手，擅长根据会议时间轴生成结构化纪要。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }

            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            response_data = response.json()

            logger.info(f"[LLM_SUMMARY] API response received, id: {response_data.get('id')}")
            logger.debug(f"[LLM_SUMMARY] Response model: {response_data.get('model')}")
            logger.debug(f"[LLM_SUMMARY] Usage: {response_data.get('usage')}")

            content = response_data['choices'][0]['message']['content']
            raw_response = str(response_data)

            logger.info(f"[LLM_SUMMARY] Summary generated successfully from timeline")
            logger.info(f"[LLM_SUMMARY] Summary length: {len(content)} characters")

            return SummaryResult(
                content=content,
                raw_response=raw_response
            )

        except requests.RequestException as e:
            logger.error(f"[LLM_SUMMARY] API request failed: {e}")
            raise
        except KeyError as e:
            logger.error(f"[LLM_SUMMARY] Invalid API response format: {e}")
            raise
        except Exception as e:
            logger.exception(f"[LLM_SUMMARY] Error generating summary from timeline: {e}")
            raise


# Singleton instance
llm_service = LLMService()

