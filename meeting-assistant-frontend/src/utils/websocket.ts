/** WebSocket client for real-time transcription */

export class TranscriptionWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3;

  constructor(private baseUrl: string = '') {
    this.url = `${baseUrl.replace('http', 'ws')}/api/v1/ws/transcribe`;
  }

  connect(
    config: { title?: string; language?: string; meeting_id?: string },
    handlers: {
      onConnected: (meetingId: string) => void;
      onTranscript: (segment: any) => void;
      onError: (error: string) => void;
      onDisconnected: () => void;
    }
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          // Send init message
          this.send({
            type: 'init',
            meeting_id: config.meeting_id,
            language: config.language || 'zh',
            title: config.title
          });
          resolve();
        };

        this.ws.onmessage = (event) => {
          const message = JSON.parse(event.data);

          switch (message.type) {
            case 'connected':
              handlers.onConnected(message.meeting_id);
              break;
            case 'transcript':
              handlers.onTranscript(message.data);
              break;
            case 'error':
              handlers.onError(message.message || 'Unknown error');
              break;
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket closed');
          handlers.onDisconnected();
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  sendAudio(audioData: ArrayBuffer): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      // Convert to base64
      const base64 = this.arrayBufferToBase64(audioData);
      this.send({
        type: 'audio',
        data: base64
      });
    }
  }

  stop(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.send({ type: 'stop' });
    }
    this.close();
  }

  private send(data: any): void {
    if (this.ws) {
      this.ws.send(JSON.stringify(data));
    }
  }

  private close(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}
