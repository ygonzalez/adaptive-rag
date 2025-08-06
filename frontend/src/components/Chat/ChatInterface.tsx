import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  useTheme,
  Tabs,
  Tab,
  Container,
} from '@mui/material';
import {
  Send as SendIcon,
  Person as PersonIcon,
  Psychology as AIIcon,
  Web as WebIcon,
  Storage as DatabaseIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { ChatMessage, AppState } from '@/types/api';
import { apiService } from '@/services/api';
import { ProcessVisualization } from '../ProcessVisualization';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div role="tabpanel" hidden={value !== index} style={{ height: '100%' }}>
      {value === index && <Box sx={{ p: 0, height: '100%' }}>{children}</Box>}
    </div>
  );
};

const ChatInterface: React.FC = () => {
  const theme = useTheme();
  const [state, setState] = useState<AppState>({
    messages: [],
    isLoading: false,
    error: null,
    sessionId: `session-${Date.now()}`,
  });
  const [inputValue, setInputValue] = useState('');
  const [currentTab, setCurrentTab] = useState(0);
  const [visualizationEnabled, setVisualizationEnabled] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [state.messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || state.isLoading) return;

    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
      error: null,
    }));

    setInputValue('');

    try {
      const response = await apiService.chat({
        question: userMessage.content,
        session_id: state.sessionId,
      });

      const assistantMessage: ChatMessage = {
        id: `msg-${Date.now()}-ai`,
        type: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources,
        usedWebSearch: response.used_web_search,
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false,
      }));
    } catch (error) {
      console.error('Chat error:', error);
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: 'Failed to get response. Please try again.',
      }));
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <Container maxWidth="xl" sx={{ py: 2, height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h5" gutterBottom>
          AI in Healthcare Research Assistant
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Ask questions about AI applications in healthcare, medical imaging, clinical decision support, 
          diagnostic AI, and current developments. The system intelligently routes to medical literature or web search.
        </Typography>
        
        {/* Tabs */}
        <Tabs 
          value={currentTab} 
          onChange={(_, newValue) => setCurrentTab(newValue)}
          sx={{ mt: 2 }}
        >
          <Tab label="Chat" />
          <Tab label="Process Visualization" />
        </Tabs>
      </Paper>

      <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden' }}>
        {/* Tab Content */}
        <TabPanel value={currentTab} index={0}>
          <Box sx={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 280px)' }}>
            {/* Messages Area */}
            <Paper
              sx={{
                flex: 1,
                overflow: 'auto',
                p: 1,
                bgcolor: theme.palette.mode === 'dark' ? 'grey.900' : 'grey.50',
                mb: 2,
              }}
            >
              <Box sx={{ minHeight: '100%', display: 'flex', flexDirection: 'column' }}>
                {state.messages.length === 0 && (
                  <Box
                    sx={{
                      flex: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexDirection: 'column',
                      gap: 2,
                    }}
                  >
                    <Typography variant="h6" color="text.secondary">
                      Explore AI in Healthcare!
                    </Typography>
                    <Box sx={{ maxWidth: '600px', textAlign: 'center' }}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Sample questions to get you started:
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mt: 2 }}>
                        {[
                          "How does AI improve medical image analysis?",
                          "What are the challenges of AI in radiology?", 
                          "How do AI systems assist in clinical decision making?",
                          "Latest FDA approvals for AI medical devices 2024",
                          "How accurate is AI for detecting skin cancer?"
                        ].map((question, index) => (
                          <Chip
                            key={index}
                            label={question}
                            variant="outlined"
                            onClick={() => setInputValue(question)}
                            sx={{ 
                              cursor: 'pointer',
                              '&:hover': { bgcolor: 'action.hover' }
                            }}
                          />
                        ))}
                      </Box>
                    </Box>
                  </Box>
                )}

                {state.messages.map((message) => (
                  <Box
                    key={message.id}
                    sx={{
                      display: 'flex',
                      flexDirection: message.type === 'user' ? 'row-reverse' : 'row',
                      mb: 2,
                      alignItems: 'flex-start',
                    }}
                  >
                    <Box
                      sx={{
                        bgcolor: message.type === 'user' ? 'primary.main' : 'background.paper',
                        color: message.type === 'user' ? 'primary.contrastText' : 'text.primary',
                        maxWidth: '70%',
                        borderRadius: 2,
                        p: 2,
                        boxShadow: 1,
                      }}
                    >
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  {message.type === 'user' ? (
                    <PersonIcon sx={{ mr: 1, fontSize: '1rem' }} />
                  ) : (
                    <AIIcon sx={{ mr: 1, fontSize: '1rem' }} />
                  )}
                  <Typography variant="caption">
                    {message.type === 'user' ? 'You' : 'AI Assistant'}
                  </Typography>
                  <Typography variant="caption" sx={{ ml: 'auto', opacity: 0.7 }}>
                    {formatTimestamp(message.timestamp)}
                  </Typography>
                </Box>

                {message.type === 'user' ? (
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {message.content}
                  </Typography>
                ) : (
                  <Box sx={{ 
                    '& p': { margin: '0.5em 0' },
                    '& ul, & ol': { pl: 3, my: 1 },
                    '& li': { mb: 0.5 },
                    '& code': { 
                      bgcolor: 'rgba(0, 0, 0, 0.05)',
                      p: 0.5,
                      borderRadius: 0.5,
                      fontFamily: 'monospace',
                      fontSize: '0.9em'
                    },
                    '& pre': { 
                      bgcolor: 'rgba(0, 0, 0, 0.05)',
                      p: 2,
                      borderRadius: 1,
                      overflow: 'auto'
                    },
                    '& strong': { fontWeight: 600 },
                    '& em': { fontStyle: 'italic' }
                  }}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>
                  </Box>
                )}

                {/* Show sources and metadata for AI responses */}
                {message.type === 'assistant' && (
                  <Box sx={{ mt: 2 }}>
                    {/* Processing indicators */}
                    <Box sx={{ display: 'flex', gap: 1, mb: 1, flexWrap: 'wrap' }}>
                      {message.usedWebSearch && (
                        <Chip
                          icon={<WebIcon />}
                          label="Web Search"
                          size="small"
                          color="info"
                          variant="outlined"
                        />
                      )}
                      {message.sources && message.sources.length > 0 && (
                        <Chip
                          icon={<DatabaseIcon />}
                          label={`${message.sources.length} Sources`}
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                      )}
                    </Box>

                    {/* Sources details */}
                    {message.sources && message.sources.length > 0 && (
                      <Card variant="outlined" sx={{ mt: 1 }}>
                        <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Sources:
                          </Typography>
                          <List dense>
                            {message.sources.map((source, index) => (
                              <ListItem key={index} sx={{ py: 0.5 }}>
                                <ListItemText
                                  primary={source.content}
                                  secondary={
                                    source.metadata.source &&
                                    `Source: ${source.metadata.source}`
                                  }
                                  primaryTypographyProps={{ variant: 'body2' }}
                                  secondaryTypographyProps={{ variant: 'caption' }}
                                />
                              </ListItem>
                            ))}
                          </List>
                        </CardContent>
                      </Card>
                    )}
                      </Box>
                    )}
                    </Box>
                  </Box>
                ))}

                {/* Loading indicator */}
                {state.isLoading && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2 }}>
                    <CircularProgress size={20} />
                    <Typography variant="body2" color="text.secondary">
                      AI is thinking...
                    </Typography>
                  </Box>
                )}

                <div ref={messagesEndRef} />
              </Box>
            </Paper>

            {/* Error display */}
            {state.error && (
              <Alert
                severity="error"
                sx={{ mb: 2 }}
                onClose={() => setState(prev => ({ ...prev, error: null }))}
              >
                {state.error}
              </Alert>
            )}

            {/* Input area */}
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  multiline
                  maxRows={4}
                  placeholder="Ask about AI in healthcare, medical imaging, clinical AI, diagnostics..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={state.isLoading}
                  variant="outlined"
                  size="small"
                />
                <IconButton
                  color="primary"
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || state.isLoading}
                  sx={{ alignSelf: 'flex-end' }}
                >
                  <SendIcon />
                </IconButton>
              </Box>
            </Paper>
          </Box>
        </TabPanel>

        {/* Process Visualization Tab */}
        <TabPanel value={currentTab} index={1}>
          <Box sx={{ height: 'calc(100vh - 280px)', overflow: 'auto' }}>
            <ProcessVisualization
              sessionId={state.sessionId}
              enabled={visualizationEnabled}
              onToggle={setVisualizationEnabled}
            />
          </Box>
        </TabPanel>
      </Box>
    </Container>
  );
};

export default ChatInterface;