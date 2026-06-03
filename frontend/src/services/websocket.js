const WS_URL = 'ws://127.0.0.1:8000'

class WebSocketService {
  constructor() {
    this.ws = null
    this.listeners = []
  }

  connect(channelId, token) {
    this.disconnect()
    this.ws = new WebSocket(`${WS_URL}/ws/channel/${channelId}?token=${token}`)

    this.ws.onmessage = (e) => {
      const data = JSON.parse(e.data)
      this.listeners.forEach((listener) => listener(data))
    }

    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
    }

    this.ws.onerror = (e) => {
      console.error('WebSocket error:', e)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  sendMessage(content) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ event: 'message', content }))
    }
  }

  sendTyping(isTyping) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ event: 'typing', is_typing: isTyping }))
    }
  }

  addListener(listener) {
    this.listeners.push(listener)
  }

  removeListener(listener) {
    this.listeners = this.listeners.filter((l) => l !== listener)
  }
}

export default new WebSocketService()