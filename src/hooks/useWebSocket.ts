import { useState, useEffect, useRef, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import { APP_CONFIG } from '@/lib/constants';
import { WSMessage } from '@/types';

interface UseWebSocketReturn {
  socket: Socket | null;
  isConnected: boolean;
  error: string | null;
  sendMessage: (message: any) => void;
  subscribe: (event: string, callback: (data: any) => void) => () => void;
}

export function useWebSocket(namespace = '/'): UseWebSocketReturn {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const subscriptionsRef = useRef<Map<string, (data: any) => void>>(new Map());

  const connect = useCallback(() => {
    if (socket?.connected) return;

    const newSocket = io(`${APP_CONFIG.WS_URL}${namespace}`, {
      transports: ['websocket'],
      autoConnect: true,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    });

    newSocket.on('connect', () => {
      setIsConnected(true);
      setError(null);
      console.log('WebSocket connected');
    });

    newSocket.on('disconnect', (reason) => {
      setIsConnected(false);
      console.log('WebSocket disconnected:', reason);
    });

    newSocket.on('connect_error', (err) => {
      setError(err.message);
      console.error('WebSocket connection error:', err);
    });

    // Re-subscribe to events
    subscriptionsRef.current.forEach((callback, event) => {
      newSocket.on(event, callback);
    });

    setSocket(newSocket);
  }, [namespace]);

  const disconnect = useCallback(() => {
    if (socket) {
      socket.disconnect();
      setSocket(null);
      setIsConnected(false);
    }
  }, [socket]);

  const sendMessage = useCallback((message: any) => {
    if (socket && isConnected) {
      socket.emit('message', message);
    }
  }, [socket, isConnected]);

  const subscribe = useCallback((event: string, callback: (data: any) => void) => {
    subscriptionsRef.current.set(event, callback);
    
    if (socket) {
      socket.on(event, callback);
    }

    // Return unsubscribe function
    return () => {
      subscriptionsRef.current.delete(event);
      if (socket) {
        socket.off(event, callback);
      }
    };
  }, [socket]);

  useEffect(() => {
    connect();

    return () => {
      disconnect();
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect, disconnect]);

  return {
    socket,
    isConnected,
    error,
    sendMessage,
    subscribe,
  };
}