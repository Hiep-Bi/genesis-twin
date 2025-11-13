import { io } from 'socket.io-client';

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = {};
  }

  connect(token) {
    if (this.socket?.connected) {
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      this.socket = io(WS_URL, {
        auth: { token },
        transports: ['websocket'],
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: 5,
      });

      this.socket.on('connect', () => {
        console.log('✅ WebSocket connected');
        resolve();
      });

      this.socket.on('disconnect', () => {
        console.log('❌ WebSocket disconnected');
      });

      this.socket.on('connect_error', (error) => {
        console.error('WebSocket connection error:', error);
        reject(error);
      });

      this.socket.on('error', (error) => {
        console.error('WebSocket error:', error);
      });
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  subscribe(channel) {
    if (!this.socket) return;

    this.socket.emit('message', {
      type: 'subscribe',
      channel: channel,
    });
  }

  unsubscribe(channel) {
    if (!this.socket) return;

    this.socket.emit('message', {
      type: 'unsubscribe',
      channel: channel,
    });
  }

  on(event, callback) {
    if (!this.socket) return;

    this.socket.on(event, callback);
    
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  off(event, callback) {
    if (!this.socket) return;

    this.socket.off(event, callback);
    
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  }

  emit(event, data) {
    if (!this.socket) return;

    this.socket.emit(event, data);
  }

  isConnected() {
    return this.socket?.connected || false;
  }
}

export const websocket = new WebSocketService();
export default websocket;

