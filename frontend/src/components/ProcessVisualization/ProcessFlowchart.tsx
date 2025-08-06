import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Chip,
  LinearProgress,
  Collapse,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  useTheme,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Route as RouteIcon,
  Search as SearchIcon,
  Storage as StorageIcon,
  Psychology as GenerateIcon,
  FactCheck as FactCheckIcon,
  Grading as GradeIcon,
  Public as WebIcon,
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
  HourglassEmpty as PendingIcon,
  PlayArrow as ActiveIcon,
  Info as InfoIcon,
  Check as CheckSmallIcon,
  Close as CancelSmallIcon,
} from '@mui/icons-material';

import type { ProcessEvent, ProcessStepType, ProcessStepStatus, DocumentGrade } from '../../types/visualization';

interface ProcessFlowchartProps {
  events: ProcessEvent[];
  sessionId: string;
}

const stepOrder: ProcessStepType[] = [
  'routing',
  'retrieve',
  'grade_documents',
  'websearch',
  'generate',
  'hallucination_check',
  'answer_grading',
];

const stepIcons = {
  routing: RouteIcon,
  retrieve: StorageIcon,
  grade_documents: GradeIcon,
  websearch: WebIcon,
  generate: GenerateIcon,
  hallucination_check: CheckIcon,
  answer_grading: FactCheckIcon,
};

const stepLabels = {
  routing: 'Route Question',
  retrieve: 'Retrieve Documents',
  grade_documents: 'Grade Documents',
  websearch: 'Web Search',
  generate: 'Generate Answer',
  hallucination_check: 'Hallucination Check',
  answer_grading: 'Answer Grading',
};

const statusColors = {
  pending: 'default',
  started: 'primary',
  completed: 'success',
  failed: 'error',
  skipped: 'default',
} as const;

const statusIcons = {
  pending: PendingIcon,
  started: ActiveIcon,
  completed: CheckIcon,
  failed: CancelIcon,
  skipped: CancelIcon,
};

export const ProcessFlowchart: React.FC<ProcessFlowchartProps> = ({ events, sessionId }) => {
  const theme = useTheme();
  const [activeStep, setActiveStep] = useState(-1);
  const [expandedSteps, setExpandedSteps] = useState<Set<ProcessStepType>>(new Set());
  const [selectedEvent, setSelectedEvent] = useState<ProcessEvent | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  // Process events into step states
  const stepStates = React.useMemo(() => {
    const states: Record<ProcessStepType, {
      status: ProcessStepStatus;
      events: ProcessEvent[];
      latestEvent?: ProcessEvent;
    }> = {} as any;

    // Initialize all steps as pending
    stepOrder.forEach(step => {
      states[step] = {
        status: 'pending' as ProcessStepStatus,
        events: [],
      };
    });

    // Process events chronologically
    const sortedEvents = [...events].sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    sortedEvents.forEach(event => {
      if (event.step_type in states) {
        states[event.step_type].events.push(event);
        states[event.step_type].latestEvent = event;
        
        // Update status based on latest event
        if (event.status === 'started') {
          states[event.step_type].status = 'started';
        } else if (event.status === 'completed') {
          states[event.step_type].status = 'completed';
        } else if (event.status === 'failed') {
          states[event.step_type].status = 'failed';
        }
      }
    });

    return states;
  }, [events]);

  // Find current active step
  useEffect(() => {
    const currentlyActive = stepOrder.findIndex(step => 
      stepStates[step]?.status === 'started'
    );
    setActiveStep(currentlyActive >= 0 ? currentlyActive : 
      stepOrder.findLastIndex(step => stepStates[step]?.status === 'completed') + 1
    );
  }, [stepStates]);

  const handleStepToggle = (stepType: ProcessStepType) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(stepType)) {
      newExpanded.delete(stepType);
    } else {
      newExpanded.add(stepType);
    }
    setExpandedSteps(newExpanded);
  };

  const handleEventClick = (event: ProcessEvent) => {
    setSelectedEvent(event);
    setDetailsOpen(true);
  };

  const formatDuration = (ms?: number) => {
    if (!ms) return 'N/A';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const getStepIcon = (stepType: ProcessStepType, status: ProcessStepStatus) => {
    const StatusIcon = statusIcons[status];
    return <StatusIcon />;
  };

  return (
    <Box sx={{ width: '100%', maxHeight: '600px', overflow: 'auto' }}>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            RAG Process Flow - Session: {sessionId}
          </Typography>
          
          <Stepper activeStep={activeStep} orientation="vertical">
            {stepOrder.map((stepType, index) => {
              const stepState = stepStates[stepType];
              const Icon = stepIcons[stepType];
              const isExpanded = expandedSteps.has(stepType);
              const hasEvents = stepState.events.length > 0;

              return (
                <Step key={stepType} completed={stepState.status === 'completed'} expanded={isExpanded}>
                  <StepLabel
                    icon={getStepIcon(stepType, stepState.status)}
                    error={stepState.status === 'failed'}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Icon sx={{ fontSize: '1rem' }} />
                      <Typography variant="subtitle2">
                        {stepLabels[stepType]}
                      </Typography>
                      <Chip
                        size="small"
                        label={stepState.status}
                        color={statusColors[stepState.status]}
                        variant="outlined"
                      />
                      {stepState.latestEvent?.duration_ms && (
                        <Chip
                          size="small"
                          label={formatDuration(stepState.latestEvent.duration_ms)}
                          variant="outlined"
                        />
                      )}
                      {hasEvents && (
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleStepToggle(stepType);
                          }}
                        >
                          {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </IconButton>
                      )}
                    </Box>
                  </StepLabel>
                  
                  <StepContent>
                    {stepState.status === 'started' && (
                      <LinearProgress sx={{ mb: 2 }} />
                    )}
                    
                    <Collapse in={isExpanded || stepState.status === 'started'}>
                      {hasEvents ? (
                        <Box sx={{ ml: 2 }}>
                          {stepState.events.map((event, eventIndex) => (
                            <Card
                              key={event.event_id}
                              variant="outlined"
                              sx={{
                                mb: 1,
                                cursor: 'pointer',
                                '&:hover': { bgcolor: 'action.hover' }
                              }}
                              onClick={() => handleEventClick(event)}
                            >
                              <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                  <Typography variant="caption" color="text.secondary">
                                    {new Date(event.timestamp).toLocaleTimeString()}
                                  </Typography>
                                  <IconButton size="small">
                                    <InfoIcon fontSize="small" />
                                  </IconButton>
                                </Box>
                                
                                {/* Step-specific content preview */}
                                {stepType === 'routing' && event.routing_decision && (
                                  <Box sx={{ mt: 1 }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                      <Chip 
                                        size="small" 
                                        label={event.routing_decision === 'vectorstore' ? 'Vector Store' : 'Web Search'}
                                        color={event.routing_decision === 'vectorstore' ? 'primary' : 'secondary'}
                                        icon={event.routing_decision === 'vectorstore' ? <StorageIcon /> : <WebIcon />}
                                      />
                                      {event.routing_confidence && (
                                        <Chip 
                                          size="small" 
                                          label={`${Math.round(event.routing_confidence * 100)}% confidence`}
                                          variant="outlined"
                                        />
                                      )}
                                    </Box>
                                    {event.routing_reasoning && (
                                      <Typography variant="caption" color="text.secondary" display="block">
                                        Reasoning: {event.routing_reasoning}
                                      </Typography>
                                    )}
                                  </Box>
                                )}
                                
                                {stepType === 'retrieve' && event.documents_found !== undefined && (
                                  <Box sx={{ mt: 1 }}>
                                    <Chip 
                                      size="small" 
                                      label={`${event.documents_found} documents found`}
                                      color={event.documents_found > 0 ? 'success' : 'default'}
                                      variant="outlined"
                                    />
                                  </Box>
                                )}
                                
                                {stepType === 'grade_documents' && event.documents_graded && (
                                  <Box sx={{ mt: 1 }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                      <Chip 
                                        size="small" 
                                        label={`${event.relevant_documents}/${event.documents_graded.length} relevant`}
                                        color={event.relevant_documents > 0 ? 'success' : 'warning'}
                                      />
                                    </Box>
                                    {event.documents_graded.slice(0, 3).map((doc, idx) => (
                                      <Box key={idx} sx={{ 
                                        p: 1, 
                                        mb: 0.5, 
                                        bgcolor: 'action.hover', 
                                        borderRadius: 1,
                                        borderLeft: 3,
                                        borderColor: doc.relevance_score === 'yes' ? 'success.main' : 'error.main'
                                      }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                                          {doc.relevance_score === 'yes' ? 
                                            <CheckSmallIcon fontSize="small" color="success" /> : 
                                            <CancelSmallIcon fontSize="small" color="error" />
                                          }
                                          <Typography variant="caption" fontWeight="bold">
                                            {doc.relevance_score === 'yes' ? 'Relevant' : 'Not Relevant'}
                                          </Typography>
                                          {doc.source && (
                                            <Typography variant="caption" color="text.secondary">
                                              • {doc.source}
                                            </Typography>
                                          )}
                                        </Box>
                                        <Typography variant="caption" color="text.secondary" sx={{ 
                                          display: '-webkit-box',
                                          WebkitLineClamp: 2,
                                          WebkitBoxOrient: 'vertical',
                                          overflow: 'hidden'
                                        }}>
                                          {doc.content_preview}
                                        </Typography>
                                      </Box>
                                    ))}
                                    {event.documents_graded.length > 3 && (
                                      <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                                        +{event.documents_graded.length - 3} more documents...
                                      </Typography>
                                    )}
                                  </Box>
                                )}
                                
                                {stepType === 'websearch' && (
                                  <Box sx={{ mt: 1 }}>
                                    <Chip 
                                      size="small" 
                                      label={`${event.web_sources_found || 0} web sources found`}
                                      color="info"
                                      icon={<WebIcon />}
                                    />
                                    {event.web_search_query && (
                                      <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                                        Query: "{event.web_search_query}"
                                      </Typography>
                                    )}
                                  </Box>
                                )}
                                
                                {stepType === 'generate' && (
                                  <Box sx={{ mt: 1 }}>
                                    <Chip 
                                      size="small" 
                                      label={`Attempt #${event.generation_attempt}`}
                                      variant="outlined"
                                    />
                                    {event.generation_preview && (
                                      <Box sx={{ 
                                        mt: 1, 
                                        p: 1, 
                                        bgcolor: 'action.hover', 
                                        borderRadius: 1,
                                        borderLeft: 3,
                                        borderColor: 'info.main'
                                      }}>
                                        <Typography variant="caption" sx={{ fontStyle: 'italic' }}>
                                          "{event.generation_preview}"
                                        </Typography>
                                      </Box>
                                    )}
                                  </Box>
                                )}
                                
                                {stepType === 'hallucination_check' && (
                                  <Box sx={{ mt: 1 }}>
                                    <Chip 
                                      size="small" 
                                      label={event.hallucination_score === 'yes' ? 'Grounded ✓' : 'Hallucination Detected'}
                                      color={event.hallucination_score === 'yes' ? 'success' : 'error'}
                                      icon={event.hallucination_score === 'yes' ? <CheckIcon /> : <CancelIcon />}
                                    />
                                  </Box>
                                )}
                                
                                {stepType === 'answer_grading' && (
                                  <Box sx={{ mt: 1 }}>
                                    <Chip 
                                      size="small" 
                                      label={event.answer_grade === 'yes' ? 'Answer Addresses Question ✓' : 'Answer Inadequate'}
                                      color={event.answer_grade === 'yes' ? 'success' : 'warning'}
                                      icon={event.answer_grade === 'yes' ? <CheckIcon /> : <CancelIcon />}
                                    />
                                  </Box>
                                )}
                              </CardContent>
                            </Card>
                          ))}
                        </Box>
                      ) : (
                        <Typography variant="body2" color="text.secondary" sx={{ ml: 2, py: 1 }}>
                          No events recorded for this step yet.
                        </Typography>
                      )}
                    </Collapse>
                  </StepContent>
                </Step>
              );
            })}
          </Stepper>
        </CardContent>
      </Card>

      {/* Event Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedEvent && `${stepLabels[selectedEvent.step_type]} Details`}
        </DialogTitle>
        <DialogContent>
          {selectedEvent && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Event Information
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText
                    primary="Timestamp"
                    secondary={new Date(selectedEvent.timestamp).toLocaleString()}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Status"
                    secondary={selectedEvent.status}
                  />
                </ListItem>
                {selectedEvent.duration_ms && (
                  <ListItem>
                    <ListItemText
                      primary="Duration"
                      secondary={formatDuration(selectedEvent.duration_ms)}
                    />
                  </ListItem>
                )}
              </List>

              {/* Step-specific details */}
              {selectedEvent.step_type === 'routing' && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Routing Decision
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemText
                        primary="Decision"
                        secondary={selectedEvent.routing_decision}
                      />
                    </ListItem>
                    {selectedEvent.routing_confidence && (
                      <ListItem>
                        <ListItemText
                          primary="Confidence"
                          secondary={`${Math.round(selectedEvent.routing_confidence * 100)}%`}
                        />
                      </ListItem>
                    )}
                    {selectedEvent.routing_reasoning && (
                      <ListItem>
                        <ListItemText
                          primary="Reasoning"
                          secondary={selectedEvent.routing_reasoning}
                        />
                      </ListItem>
                    )}
                  </List>
                </>
              )}

              {selectedEvent.step_type === 'grade_documents' && selectedEvent.documents_graded && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Document Grades ({selectedEvent.documents_graded.length})
                  </Typography>
                  {selectedEvent.documents_graded.map((doc, idx) => (
                    <Card key={idx} variant="outlined" sx={{ mb: 1 }}>
                      <CardContent sx={{ py: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <Chip
                            size="small"
                            label={doc.relevance_score === 'yes' ? 'Relevant' : 'Not Relevant'}
                            color={doc.relevance_score === 'yes' ? 'success' : 'error'}
                            variant="outlined"
                          />
                          {doc.source && (
                            <Chip size="small" label={doc.source} variant="outlined" />
                          )}
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {doc.content_preview}
                        </Typography>
                      </CardContent>
                    </Card>
                  ))}
                </>
              )}

              {selectedEvent.error_message && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom color="error">
                    Error
                  </Typography>
                  <Typography variant="body2" color="error">
                    {selectedEvent.error_message}
                  </Typography>
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};