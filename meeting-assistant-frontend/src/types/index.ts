// Meeting status enum
export type MeetingStatus = 'pending' | 'processing' | 'completed' | 'failed'

// Processing stage enum
export type ProcessingStage =
  | 'initializing'
  | 'separating'
  | 'separation_completed'
  | 'summarizing'
  | 'completed'

// Participant
export interface Participant {
  id: string
  speaker_id: string
  display_name: string
  voice_segment_path?: string
}

// Speaker Segment
export interface SpeakerSegment {
  id: string
  participant_id?: string
  speaker_id: string
  start_time: number
  end_time: number
  duration: number
  transcript?: string
  segment_index?: number
}

// Merged Segment
export interface MergedSegment {
  id: string
  participant_id?: string
  speaker_id: string
  start_time: number
  end_time: number
  duration: number
  transcript?: string
  segment_count: number
  segment_index: number
}

// Summary
export interface Summary {
  id: string
  content: string
  generated_at: string
}

// Meeting base
export interface Meeting {
  id: string
  title: string
  status: MeetingStatus
  progress: number
  stage?: ProcessingStage
  duration?: number
  created_at: string
  updated_at: string
}

// Meeting detail with participants and summary
export interface MeetingDetail extends Meeting {
  participants: Participant[]
  speaker_segments: SpeakerSegment[]
  merged_segments: MergedSegment[]
  summary?: Summary
  error_message?: string
}

// Meeting status response
export interface MeetingStatusResponse {
  id: string
  status: MeetingStatus
  progress: number
  stage?: ProcessingStage
  message: string
  stage_description?: string
}

// Paginated meeting list
export interface MeetingListResponse {
  items: Meeting[]
  total: number
  page: number
  size: number
  pages: number
}

// API Error
export interface ApiError {
  error: {
    code: string
    message: string
  }
}

// Participant update request
export interface ParticipantUpdateRequest {
  display_name: string
}
