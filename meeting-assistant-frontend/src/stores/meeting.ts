import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Meeting, MeetingDetail, MeetingStatusResponse } from '@/types'
import { meetingApi } from '@/api/meeting'

export const useMeetingStore = defineStore('meeting', () => {
  // State
  const meetings = ref<Meeting[]>([])
  const currentMeeting = ref<MeetingDetail | null>(null)
  const total = ref(0)
  const page = ref(1)
  const size = ref(10)
  const pages = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const searchQuery = ref('')

  // Computed
  const isEmpty = computed(() => meetings.value.length === 0 && !loading.value)
  const hasMore = computed(() => page.value < pages.value)

  // Actions
  async function fetchMeetings(resetPage = false) {
    if (resetPage) {
      page.value = 1
    }

    loading.value = true
    error.value = null

    try {
      const response = await meetingApi.getList({
        search: searchQuery.value || undefined,
        page: page.value,
        size: size.value
      })

      meetings.value = response.items
      total.value = response.total
      pages.value = response.pages
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function fetchMeetingDetail(meetingId: string) {
    loading.value = true
    error.value = null

    try {
      currentMeeting.value = await meetingApi.getDetail(meetingId)
    } catch (e: any) {
      error.value = e.message
      currentMeeting.value = null
    } finally {
      loading.value = false
    }
  }

  async function createMeeting(title: string, audioFile: File): Promise<Meeting> {
    loading.value = true
    error.value = null

    try {
      const meeting = await meetingApi.create(title, audioFile)
      // Add to the beginning of the list
      meetings.value.unshift(meeting)
      total.value++
      return meeting
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteMeeting(meetingId: string) {
    try {
      await meetingApi.delete(meetingId)
      meetings.value = meetings.value.filter(m => m.id !== meetingId)
      total.value--
      if (currentMeeting.value?.id === meetingId) {
        currentMeeting.value = null
      }
    } catch (e: any) {
      error.value = e.message
      throw e
    }
  }

  async function updateParticipantName(
    meetingId: string,
    participantId: string,
    displayName: string
  ) {
    try {
      const updated = await meetingApi.updateParticipant(meetingId, participantId, {
        display_name: displayName
      })

      // Update local state
      if (currentMeeting.value?.id === meetingId) {
        const participant = currentMeeting.value.participants.find(p => p.id === participantId)
        if (participant) {
          participant.display_name = updated.display_name
        }
      }

      return updated
    } catch (e: any) {
      error.value = e.message
      throw e
    }
  }

  async function updateSpeakerName(
    meetingId: string,
    speakerId: string,
    displayName: string
  ) {
    try {
      const result = await meetingApi.updateSpeakerName(meetingId, speakerId, {
        display_name: displayName
      })

      // Update local state - update all participants with this speaker_id
      if (currentMeeting.value?.id === meetingId) {
        currentMeeting.value.participants.forEach(p => {
          if (p.speaker_id === speakerId) {
            p.display_name = displayName
          }
        })
      }

      return result
    } catch (e: any) {
      error.value = e.message
      throw e
    }
  }

  async function pollStatus(meetingId: string): Promise<MeetingStatusResponse> {
    const status = await meetingApi.getStatus(meetingId)

    // Update local meeting status
    const meeting = meetings.value.find(m => m.id === meetingId)
    if (meeting) {
      meeting.status = status.status
      meeting.progress = status.progress
      meeting.stage = status.stage
    }

    if (currentMeeting.value?.id === meetingId) {
      currentMeeting.value.status = status.status
      currentMeeting.value.progress = status.progress
      currentMeeting.value.stage = status.stage
    }

    return status
  }

  async function downloadAudio(meetingId: string, title: string) {
    try {
      // Create safe filename from title
      const safeTitle = title.replace(/[^a-zA-Z0-9\u4e00-\u9fa5\s\-_]/g, '').trim()
      await meetingApi.downloadAudio(meetingId, `${safeTitle}.mp3`)
    } catch (e: any) {
      error.value = e.message
      throw e
    }
  }

  async function updateSummary(meetingId: string, content: string) {
    try {
      console.log('Store: Calling updateSummary API', meetingId)
      const updated = await meetingApi.updateSummary(meetingId, content)
      console.log('Store: API response', updated)

      // Update local state
      if (currentMeeting.value?.id === meetingId && currentMeeting.value.summary) {
        currentMeeting.value.summary.content = updated.content
        console.log('Store: Local state updated')
      }

      return updated
    } catch (e: any) {
      console.error('Store: updateSummary error', e)
      error.value = e.message
      throw e
    }
  }

  async function regenerateSummary(meetingId: string) {
    try {
      loading.value = true
      error.value = null

      const status = await meetingApi.regenerateSummary(meetingId)

      // Update local meeting status
      if (currentMeeting.value?.id === meetingId) {
        currentMeeting.value.status = status.status as any
        currentMeeting.value.progress = status.progress
        currentMeeting.value.stage = status.stage as any
      }

      // Also update meeting in list
      const meeting = meetings.value.find(m => m.id === meetingId)
      if (meeting) {
        meeting.status = status.status as any
        meeting.progress = status.progress
        meeting.stage = status.stage as any
      }

      return status
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  function setPage(newPage: number) {
    page.value = newPage
    fetchMeetings()
  }

  function setSearch(query: string) {
    searchQuery.value = query
    fetchMeetings(true)
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    meetings,
    currentMeeting,
    total,
    page,
    size,
    pages,
    loading,
    error,
    searchQuery,
    // Computed
    isEmpty,
    hasMore,
    // Actions
    fetchMeetings,
    fetchMeetingDetail,
    createMeeting,
    deleteMeeting,
    updateParticipantName,
    updateSpeakerName,
    pollStatus,
    downloadAudio,
    updateSummary,
    regenerateSummary,
    setPage,
    setSearch,
    clearError
  }
})
