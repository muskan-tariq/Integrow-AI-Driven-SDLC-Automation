/**
 * WebSocket client for real-time requirements chat
 */

export interface ChatMessage {
  type: 'chunk' | 'complete' | 'error' | 'connected' | 'chat_cleared';
  content?: string;
  session_id?: string;
  timestamp: string;
}

export interface WebSocketClientOptions {
  sessionId: string;
  token: string;
  onMessage?: (message: ChatMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Error) => void;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private options: WebSocketClientOptions;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private messageBuffer: string = '';

  constructor(options: WebSocketClientOptions) {
    this.options = options;
  }

  connect(): void {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const wsUrl = baseUrl.replace('http', 'ws');
    const url = `${wsUrl}/api/requirements/chat/${this.options.sessionId}?token=${this.options.token}`;

    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        // console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.options.onConnect?.();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: ChatMessage = JSON.parse(event.data);

          if (message.type === 'chunk') {
            // Accumulate chunks for streaming
            this.messageBuffer += message.content || '';
          } else if (message.type === 'complete') {
            // Clear buffer on completion
            this.messageBuffer = '';
          }

          this.options.onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        this.options.onError?.(new Error('WebSocket connection error'));
      };

      this.ws.onclose = () => {
        //console.log('WebSocket disconnected');
        this.options.onDisconnect?.();

        // Attempt to reconnect
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          setTimeout(() => {
            // console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);
            this.connect();
          }, this.reconnectDelay * this.reconnectAttempts);
        }
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.options.onError?.(error as Error);
    }
  }

  sendMessage(content: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'message',
        content
      }));
    } else {
      console.error('WebSocket is not connected');
      this.options.onError?.(new Error('WebSocket is not connected'));
    }
  }

  newChat(requirementId?: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'new_chat',
        requirement_id: requirementId
      }));
      this.messageBuffer = '';
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  getMessageBuffer(): string {
    return this.messageBuffer;
  }
}
