import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  Alert,
  IconButton,
  Tooltip,
  Chip,
  Button,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Clear as ClearIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from '@mui/icons-material';

import { ProcessFlowchart } from './ProcessFlowchart';
import type { ProcessEvent } from '../../types/visualization';

interface ProcessVisualizationProps {
  sessionId: string;
  enabled: boolean;
  onToggle: (enabled: boolean) => void;
}

export const ProcessVisualization: React.FC<ProcessVisualizationProps> = ({
  sessionId,
  enabled,
  onToggle,
}) => {
  const [events, setEvents] = useState<ProcessEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [lastEventTime, setLastEventTime] = useState<Date | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_DELAY = 2000;

  // WebSocket connection management
  const connectWebSocket = useCallback(() => {
    if (!enabled || !sessionId) return;

    try {
      const wsUrl = `ws://localhost:8000/api/v1/visualization/ws/${sessionId}`;
      console.log('Connecting to WebSocket:', wsUrl);
      
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setConnectionError(null);
        reconnectAttemptsRef.current = 0;
        
        // Request existing events
        wsRef.current?.send(JSON.stringify({ type: 'get_events' }));
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket message:', data);
          
          if (data.type === 'pong') {
            // Heartbeat response
            return;
          } else if (data.type === 'session_events') {
            // Bulk events response
            setEvents(data.events);
          } else {
            // Single event
            const processEvent = data as ProcessEvent;
            setEvents(prev => {
              // Check if event already exists
              const exists = prev.some(e => e.event_id === processEvent.event_id);
              if (exists) return prev;
              
              // Add new event and sort by timestamp
              const newEvents = [...prev, processEvent];
              return newEvents.sort((a, b) => 
                new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
              );
            });
            setLastEventTime(new Date());
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setIsConnected(false);
        
        // Attempt to reconnect if enabled and not too many attempts
        if (enabled && reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttemptsRef.current += 1;
          setConnectionError(`Disconnected. Reconnect attempt ${reconnectAttemptsRef.current}/${MAX_RECONNECT_ATTEMPTS}...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connectWebSocket();
          }, RECONNECT_DELAY * reconnectAttemptsRef.current);
        } else {
          setConnectionError('Connection lost. Click refresh to reconnect.');
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionError('WebSocket connection error');
      };

      // Send periodic heartbeat
      const heartbeat = setInterval(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000);

      return () => clearInterval(heartbeat);
      
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setConnectionError('Failed to create WebSocket connection');
    }
  }, [enabled, sessionId]);

  const disconnectWebSocket = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
    reconnectAttemptsRef.current = 0;
  }, []);

  // Connect/disconnect based on enabled state
  useEffect(() => {
    if (enabled) {
      connectWebSocket();
    } else {
      disconnectWebSocket();
    }

    return () => {
      disconnectWebSocket();
    };
  }, [enabled, connectWebSocket, disconnectWebSocket]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnectWebSocket();
    };
  }, [disconnectWebSocket]);

  const handleRefresh = () => {
    setConnectionError(null);
    reconnectAttemptsRef.current = 0;
    disconnectWebSocket();
    if (enabled) {
      setTimeout(connectWebSocket, 100);
    }
  };

  const handleClearEvents = async () => {
    try {
      const response = await fetch(`/api/v1/visualization/events/${sessionId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        setEvents([]);
        setLastEventTime(null);
      } else {
        console.error('Failed to clear events:', response.statusText);
      }
    } catch (error) {
      console.error('Error clearing events:', error);
    }
  };

  const getConnectionStatusColor = () => {
    if (!enabled) return 'default';
    if (connectionError) return 'error';
    if (isConnected) return 'success';
    return 'warning';
  };

  const getConnectionStatusText = () => {
    if (!enabled) return 'Disabled';
    if (connectionError) return 'Error';
    if (isConnected) return 'Connected';
    return 'Connecting...';
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">
              Process Visualization
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Chip
                size="small"
                label={getConnectionStatusText()}
                color={getConnectionStatusColor()}
                variant="outlined"
              />
              
              {events.length > 0 && (
                <Chip
                  size="small"
                  label={`${events.length} events`}
                  variant="outlined"
                />
              )}
              
              {lastEventTime && (
                <Typography variant="caption" color="text.secondary">
                  Last: {lastEventTime.toLocaleTimeString()}
                </Typography>
              )}
              
              <Tooltip title="Refresh connection">
                <IconButton size="small" onClick={handleRefresh}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
              
              <Tooltip title="Clear events">
                <IconButton size="small" onClick={handleClearEvents} disabled={events.length === 0}>
                  <ClearIcon />
                </IconButton>
              </Tooltip>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={enabled}
                    onChange={(e) => onToggle(e.target.checked)}
                    icon={<VisibilityOffIcon />}
                    checkedIcon={<VisibilityIcon />}
                  />
                }
                label="Enable"
              />
            </Box>
          </Box>

          {connectionError && (
            <Alert 
              severity="warning" 
              sx={{ mb: 2 }}
              action={
                <Button size="small" onClick={handleRefresh}>
                  Retry
                </Button>
              }
            >
              {connectionError}
            </Alert>
          )}

          {!enabled && (
            <Alert severity="info" sx={{ mb: 2 }}>
              Process visualization is disabled. Enable it to see real-time RAG workflow details.
            </Alert>
          )}

          {enabled && events.length === 0 && !connectionError && (
            <Alert severity="info" sx={{ mb: 2 }}>
              Waiting for RAG process events. Send a message to see the workflow visualization.
            </Alert>
          )}
        </CardContent>
      </Card>

      {enabled && events.length > 0 && (
        <ProcessFlowchart events={events} sessionId={sessionId} />
      )}
    </Box>
  );
};