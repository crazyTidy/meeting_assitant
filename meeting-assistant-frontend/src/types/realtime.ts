/** Real-time transcription types */

export interface TranscriptSegment {
  segment_id: string;
  speaker: string;
  text: string;
  start_time: number;
  end_time: number;
}

export interface WebSocketMessage {
  type: 'connected' | 'transcript' | 'error';
  meeting_id?: string;
  message?: string;
  data?: TranscriptSegment;
}

export interface RealtimeMeeting {
  id: string;
  title: string;
  status: string;
  started_at: string;
  segments: TranscriptSegment[];
}
