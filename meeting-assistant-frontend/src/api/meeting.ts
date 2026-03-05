import axios from 'axios'
import type {
  Meeting,
  MeetingDetail,
  MeetingListResponse,
  MeetingStatusResponse,
  Participant,
  ParticipantUpdateRequest
} from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    const message = error.response?.data?.detail?.error?.message
      || error.response?.data?.message
      || error.message
      || '请求失败'
    return Promise.reject(new Error(message))
  }
)

export const meetingApi = {
  // Create meeting with audio upload
  async create(title: string, audioFile: File): Promise<Meeting> {
    const formData = new FormData()
    formData.append('title', title)
    formData.append('audio', audioFile)

    const response = await api.post<Meeting>('/meetings/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  // Get meeting list
  async getList(params: {
    search?: string
    page?: number
    size?: number
  } = {}): Promise<MeetingListResponse> {
    const response = await api.get<MeetingListResponse>('/meetings/', { params })
    return response.data
  },

  // Get meeting detail
  async getDetail(meetingId: string): Promise<MeetingDetail> {
    const response = await api.get<MeetingDetail>(`/meetings/${meetingId}`)
    return response.data
  },

  // Get meeting status
  async getStatus(meetingId: string): Promise<MeetingStatusResponse> {
    const response = await api.get<MeetingStatusResponse>(`/meetings/${meetingId}/status`)
    return response.data
  },

  // Delete meeting
  async delete(meetingId: string): Promise<void> {
    await api.delete(`/meetings/${meetingId}`)
  },

  // Update participant name
  async updateParticipant(
    meetingId: string,
    participantId: string,
    data: ParticipantUpdateRequest
  ): Promise<Participant> {
    const response = await api.patch<Participant>(
      `/meetings/${meetingId}/participants/${participantId}`,
      data
    )
    return response.data
  },

  // Update speaker name by speaker_id (updates all participants with same speaker_id)
  async updateSpeakerName(
    meetingId: string,
    speakerId: string,
    data: ParticipantUpdateRequest
  ): Promise<{ updated_count: number; speaker_id: string }> {
    const response = await api.patch<{ updated_count: number; speaker_id: string }>(
      `/meetings/${meetingId}/speakers/${speakerId}/name`,
      data
    )
    return response.data
  },

  // Download audio file
  async downloadAudio(meetingId: string, filename: string): Promise<void> {
    const response = await api.get(`/meetings/${meetingId}/audio`, {
      responseType: 'blob'
    })

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  },

  // Update summary content
  async updateSummary(meetingId: string, content: string): Promise<{ id: string; content: string; generated_at: string }> {
    console.log('API: Sending PATCH request', `/meetings/${meetingId}/summary`, { content: content.substring(0, 50) + '...' })
    const response = await api.patch(`/meetings/${meetingId}/summary`, {
      content
    })
    console.log('API: Response received', response.status, response.data)
    return response.data
  },

  // Regenerate summary
  async regenerateSummary(meetingId: string): Promise<{
    id: string
    status: string
    progress: number
    stage?: string
    message: string
    stage_description?: string
  }> {
    const response = await api.post(`/meetings/${meetingId}/regenerate-summary`)
    return response.data
  }
}

export default api
