# Advanced Process Visualization for Adaptive RAG

This document describes the implementation of Advanced Process Visualization that shows users exactly what the AI is doing during the RAG workflow and why.

## 🎯 Overview

The Advanced Process Visualization transforms the hidden RAG process into an interactive, real-time visualization that shows:

- **Real-time decision flow**: See each step as it happens
- **Decision explanations**: Understand why the AI chose each path
- **Document relevance scores**: View which documents were found and how they were graded
- **Performance metrics**: Track timing and attempts for each step
- **Interactive exploration**: Click on any step to see detailed information

## 🏗️ Architecture

### Backend Components

#### 1. Event System (`backend/app/core/visualization/`)
- **`events.py`**: Core event data structures and emission functions
- **Process Event Types**: routing, retrieve, grade_documents, websearch, generate, hallucination_check, answer_grading
- **Event Manager**: Manages WebSocket connections and event broadcasting

#### 2. Graph Integration
Modified existing graph nodes to emit detailed events:
- **Routing**: Captures decision (vectorstore vs websearch), confidence scores, reasoning
- **Retrieval**: Tracks documents found and timing
- **Document Grading**: Shows relevance scores for each document with previews
- **Generation**: Captures attempt numbers and response previews
- **Quality Checks**: Shows hallucination and answer grading results

#### 3. WebSocket API (`backend/app/api/v1/visualization.py`)
- **Real-time events**: `/api/v1/visualization/ws/{session_id}`
- **Event history**: `/api/v1/visualization/events/{session_id}`
- **Session management**: Clear events, get active sessions

### Frontend Components

#### 1. Process Flowchart (`frontend/src/components/ProcessVisualization/ProcessFlowchart.tsx`)
Interactive stepper component that shows:
- **Step status**: pending, started, completed, failed
- **Progress visualization**: Linear progress bars for active steps
- **Expandable details**: Click to see step-specific information
- **Event timeline**: Multiple events per step with timestamps

#### 2. Process Visualization Container (`frontend/src/components/ProcessVisualization/ProcessVisualization.tsx`)
Manages WebSocket connections and provides:
- **Connection management**: Auto-reconnect with backoff
- **Event aggregation**: Sorts and deduplicates events
- **Controls**: Enable/disable, refresh, clear events
- **Status indicators**: Connection state, event counts, last activity

#### 3. Chat Interface Integration
Enhanced the main chat interface with:
- **Tabbed interface**: Chat + Process Visualization
- **Real-time updates**: Events stream in as chat processes
- **Session persistence**: Events tied to chat session IDs

## 🚀 Key Features

### Real-Time Decision Tree
Shows the exact flow:
```
User Question → Route Decision → Retrieve OR Web Search → Grade Documents → Generate Answer → Quality Check → Final Response
```

### Interactive Explanations
Each step provides detailed information:
- **Routing**: Decision confidence (95% for vectorstore, 85% for websearch)
- **Document Grading**: Relevance scores with document previews
- **Generation**: Attempt numbers and response previews
- **Quality Checks**: Pass/fail results with reasoning

### Document Relevance Visualization
```
✅ Doc 1: "Agent Memory Systems" (Relevance: 95%)
✅ Doc 2: "LLM Context Windows" (Relevance: 78%) 
❌ Doc 3: "Pizza Recipe Methods" (Relevance: 12%)
```

### Performance Metrics
- **Step duration**: Millisecond timing for each operation
- **Retry tracking**: Generation and web search attempt counters
- **Connection status**: Real-time WebSocket health

## 📊 Event Flow Example

### Question: "What is agent memory?"

1. **ROUTING** (120ms, 95% confidence)
   - Decision: vectorstore
   - Reasoning: "Question contains AI/ML keywords"

2. **RETRIEVE** (200ms)
   - Documents found: 4
   - Sources: agent_memory.md, llm_agents.pdf, etc.

3. **GRADE_DOCUMENTS** (300ms)
   - Relevant: 3/4 documents
   - Filtered out irrelevant content

4. **GENERATE** (600ms, attempt #1)
   - Context: 3 relevant documents
   - Preview: "Agent memory refers to..."

5. **HALLUCINATION_CHECK** (150ms)
   - Result: ✅ Grounded in documents

6. **ANSWER_GRADING** (100ms)
   - Result: ✅ Addresses question

### Question: "How to make pizza?"

1. **ROUTING** (150ms, 85% confidence)
   - Decision: websearch
   - Reasoning: "Question contains general/web keywords"

2. **WEBSEARCH** (1200ms)
   - Query: "how to make pizza"
   - Sources found: 3 websites

3. **GENERATE** (800ms, attempt #1)
   - Context: Web search results
   - Preview: "Here's how to make pizza..."

## 🔧 Implementation Details

### WebSocket Protocol
```typescript
// Client → Server
{ "type": "ping" }
{ "type": "get_events" }

// Server → Client
{ "type": "pong" }
{ "type": "session_events", "events": [...] }
// Individual events as they happen
```

### Event Data Structure
```python
class ProcessEvent(BaseModel):
    session_id: str
    event_id: str
    step_type: ProcessStepType
    status: ProcessStepStatus
    timestamp: datetime
    
    # Step-specific data
    routing_decision?: str
    documents_found?: int
    generation_attempt?: int
    # ... and more
```

### Connection Management
- **Auto-reconnect**: Up to 5 attempts with exponential backoff
- **Heartbeat**: 30-second ping/pong to maintain connections  
- **Error handling**: Graceful degradation with status indicators

## 🎨 UI/UX Features

### Visual Design
- **Material-UI components**: Professional, consistent design
- **Color coding**: Success (green), error (red), pending (grey)
- **Icons**: Intuitive step representation (route, storage, search, etc.)
- **Responsive**: Works on all screen sizes

### Interactive Elements
- **Expandable steps**: Click to see detailed information
- **Event details**: Modal dialogs with comprehensive data
- **Control panel**: Toggle, refresh, clear events
- **Status chips**: Connection state, timing, counts

### Real-time Updates
- **Live indicators**: Progress bars for active steps
- **Event streaming**: New events appear immediately
- **Timestamp tracking**: Last activity indicators
- **Connection status**: Visual connection health

## 📋 Usage

### For Users
1. **Enable visualization**: Toggle the switch in the Process Visualization tab
2. **Ask questions**: Send messages in the Chat tab  
3. **Watch the flow**: Switch to Process Visualization to see real-time progress
4. **Explore details**: Click on any step to understand the reasoning

### For Developers
1. **Event emission**: All graph nodes automatically emit events
2. **WebSocket monitoring**: Use browser dev tools to see real-time events
3. **REST API**: Query `/api/v1/visualization/events/{session_id}` for debugging
4. **Session management**: Events are automatically tied to chat sessions

## 🔮 Benefits

### User Understanding
- **Transparency**: See exactly how the AI makes decisions
- **Trust**: Understand the reasoning behind each choice
- **Learning**: Observe how different questions are handled
- **Debugging**: Identify when and why processes fail

### Developer Insights
- **Performance monitoring**: Track step durations and bottlenecks
- **Error diagnosis**: See exactly where failures occur
- **Process optimization**: Identify redundant or slow operations
- **Quality assurance**: Monitor hallucination and answer grading

### Educational Value
- **AI literacy**: Help users understand RAG systems
- **Decision making**: Show the complexity of AI reasoning
- **System design**: Demonstrate graph-based workflows
- **Real-time systems**: Showcase WebSocket implementations

## 🎯 Technical Achievements

1. **Zero-latency visualization**: Events stream in real-time via WebSockets
2. **Comprehensive coverage**: Every graph node emits detailed events
3. **Interactive exploration**: Click any step for detailed information
4. **Robust connections**: Auto-reconnect with intelligent backoff
5. **Session persistence**: Events tied to chat sessions
6. **Performance optimized**: Minimal overhead on RAG processing
7. **Production ready**: Error handling, logging, connection management

This implementation transforms the "AI is thinking..." black box into a transparent, educational, and debugging-friendly visualization that shows users exactly what their advanced RAG system is doing and why.