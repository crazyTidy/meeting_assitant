#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
"""LLM service for generating meeting summaries using ZhipuAI."""
import logging
import requests
from typing import List, Optional
from dataclasses import dataclass

from ..settings import environment_config
from .separation_service import SpeakerInfo, SpeakerSegment

logger = logging.getLogger(__name__)


@dataclass
class SummaryResult:
    """Result from summary generation."""
    content: str  # Markdown formatted summary
    raw_response: Optional[str] = None


class LLMService:
    """Service for generating meeting summaries using Zhipu GLM."""

    def __init__(self):
        self.api_key = environment_config.ZHIPU_API_KEY

    def _build_prompt_from_timeline(
        self,
        meeting_title: str,
        speakers: List[SpeakerInfo],
        timeline: List[SpeakerSegment],
        speaker_name_map: Optional[dict] = None
    ) -> str:
        """Build prompt for meeting summary generation from timeline segments with transcripts."""

        # Build speaker info with speaking time
        speaker_list = "\n".join([
            f"- {s.display_name} ({s.speaker_id}) - 发言时长: {int(s.total_duration/60)}分{int(s.total_duration%60)}秒"
            for s in speakers
        ])

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
            f"- [{self._format_timestamp(seg.start_time)}-{self._format_timestamp(seg.end_time)}] {get_speaker_display_name(seg.speaker_id)} ({seg.speaker_id}): {seg.transcript if seg.transcript else '(暂无转写文本)'}"
            for seg in timeline
        ])

        prompt = f"""请根据以下会议信息和完整发言记录生成一份会议纪要。

会议标题：{meeting_title}

参会人员：
{speaker_list}

发言记录（按时间顺序）：
{timeline_text}

请按照以下格式生成会议纪要（使用Markdown格式）：

## 会议主题
[从讨论内容提炼会议主题]

## 参会人员
{speaker_list}

## 主要议题
[基于发言内容识别的主要议题，按重要性排序]

## 讨论要点
[按议题分类整理，引用关键发言]

### 议题1：[标题]
- [说话人A]：[观点或发言摘要]
- [说话人B]：[回应或补充]

### 议题2：[标题]
- [说话人A]：[关键观点]
- [说话人B]：[补充说明]

## 决议事项
- [基于讨论内容总结的决议]
- [达成的共识]

## 待办事项
- [ ] [负责人]：[具体任务] - [截止日期（如提到）]

## 下次会议安排
[如提到下次会议，请列出时间和议题]

请确保：
1. 完全基于提供的发言记录内容生成纪要
2. 准确引用和归纳发言人的观点
3. 保持客观、简洁、重点突出
4. 如果某些部分（如待办事项）没有明确提到，标注"未明确讨论"
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
