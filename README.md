# AI in Healthcare RAG System

An intelligent Retrieval-Augmented Generation (RAG) system focused on AI in Healthcare, built with FastAPI, LangChain, and LangGraph. The system automatically adapts between document retrieval and web search to provide comprehensive answers about AI applications in medical imaging, clinical decision support, diagnostic AI, and healthcare ethics.

## 🚀 Features

- **Healthcare AI Focus**: Specialized knowledge base covering medical imaging, clinical AI, diagnostic systems, and healthcare ethics
- **Adaptive Question Routing**: Automatically determines whether to use document retrieval or web search
- **Multi-Stage Validation**: Includes hallucination detection and answer quality grading for medical accuracy
- **Semantic Document Chunking**: Uses semantic similarity for intelligent text splitting of medical literature
- **Current Healthcare Developments**: Web search integration for latest FDA approvals, clinical trials, and industry news
- **FastAPI Backend**: RESTful API with automatic OpenAPI documentation
- **Interactive CLI**: Command-line interface for direct healthcare AI queries
- **Comprehensive Testing**: Full test suite with healthcare-specific test cases
- **Docker Support**: Containerized deployment ready

## 🏗️ Architecture

The system implements a sophisticated graph-based workflow:

1. **Question Routing**: Analyzes queries to determine optimal processing path
2. **Document Retrieval**: Searches vector database for relevant documents
3. **Relevance Grading**: Filters documents based on relevance to the query
4. **Answer Generation**: Creates responses from retrieved documents
5. **Quality Validation**: Checks for hallucinations and answer quality
6. **Web Search Fallback**: Falls back to web search if document-based answers are inadequate

### Core Components

- **FastAPI Backend** (`backend/app/`): RESTful API with async endpoints
- **Graph Workflow** (`backend/app/core/graph/`): LangGraph-based processing pipeline
- **Document Ingestion** (`backend/app/core/ingestion/`): Semantic chunking and vector storage
- **Model Management** (`backend/app/core/models/`): Google Gemini integration
- **Testing Suite** (`backend/tests/`): Comprehensive unit and integration tests

## 🛠️ Setup

### Prerequisites

- Python 3.10+
- Google API Key (for Gemini models)
- Tavily API Key (for web search)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd adaptive_rag
   ```

2. **Set up backend environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   # GOOGLE_API_KEY=your_google_api_key
   # TAVILY_API_KEY=your_tavily_api_key
   ```

### Docker Setup (Alternative)

```bash
cd backend
docker-compose up --build
```

## 🚀 Usage

### API Server

Start the FastAPI server:
```bash
cd backend
python run.py
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

### CLI Interface

For interactive chat:
```bash
cd backend
python cli.py
```

### API Endpoints

- `POST /api/v1/chat` - Send questions to the RAG system
- `POST /api/v1/documents/ingest` - Add documents to vector store
- `DELETE /api/v1/documents/clear` - Clear vector store
- `GET /api/v1/health` - Health check
- `GET /docs` - Interactive API documentation

### Example API Usage

```bash
# Healthcare AI queries
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "How does AI improve medical image analysis?"}'

curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the latest FDA approvals for AI medical devices?"}'

# Ingest healthcare documents
curl -X POST "http://localhost:8000/api/v1/documents/ingest" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Clinical AI research content here"]}'
```

## 🧪 Testing

### Run All Tests
```bash
cd backend
pytest
```

### Run Specific Test Types
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Exclude slow tests
pytest -m "not slow"
```

### Test Coverage
```bash
pytest --cov=app tests/
```

## 🛠️ Development

### Code Formatting
```bash
cd backend
black .
isort .
```

### Development Workflow
1. Make changes to the code
2. Run tests: `pytest`
3. Format code: `black . && isort .`
4. Run the application: `python run.py`

### Project Structure

```
adaptive_rag/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # Core RAG functionality
│   │   ├── models/       # Data models and schemas
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utilities
│   ├── tests/            # Test suite
│   ├── cli.py           # CLI interface
│   ├── run.py           # API server
│   └── requirements.txt # Dependencies
├── CLAUDE.md            # Development guide
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Required for Gemini models
- `TAVILY_API_KEY`: Required for web search functionality
- `LOG_LEVEL`: Logging level (default: INFO)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

### Default Healthcare AI Data Sources

The system comes pre-configured with curated healthcare AI literature from:

**Medical Imaging AI:**
- Nature Medicine articles on deep learning in medical imaging
- Research on AI in dermatology and retinal imaging
- Medical imaging overview and analysis techniques

**Clinical AI Systems:**
- NCBI PMC articles on AI in clinical decision making
- Machine learning applications in intensive care
- AI systems for emergency medicine

**Diagnostic AI:**
- Research on AI in diagnostic imaging and pathology
- Laboratory diagnostics and AI integration
- Validation methods for diagnostic AI systems

**Predictive Analytics:**
- Healthcare predictive models and early detection systems
- Patient monitoring and deterioration prediction

**AI Ethics & Validation:**
- Bias and fairness in healthcare AI
- Explainable AI in medical applications
- Regulatory guidelines and compliance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🔗 Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Google Gemini API](https://ai.google.dev/)

## 💡 Healthcare AI Use Cases

- **Medical Research**: Query latest research on AI applications in healthcare
- **Clinical Decision Support**: Get evidence-based answers about AI diagnostic tools
- **Regulatory Compliance**: Access current FDA guidelines and approval processes
- **Educational Resources**: Learn about healthcare AI implementations and best practices
- **Technology Assessment**: Compare different AI solutions for medical applications
- **Ethics and Safety**: Understand bias, fairness, and validation requirements

### Sample Questions the System Can Answer:

**Medical Imaging:**
- "How does deep learning improve medical image analysis?"
- "What are the challenges of AI in radiology?"
- "How accurate is AI for detecting skin cancer in dermoscopy images?"

**Clinical Applications:**
- "How do AI systems assist in clinical decision making?"
- "What role does machine learning play in intensive care units?"
- "How can AI improve emergency department triage?"

**Current Developments:**
- "Latest FDA approvals for AI medical devices 2024"
- "Recent breakthroughs in AI medical imaging"
- "New regulations for AI medical devices"

**Complex Queries:**
- "What AI imaging technologies are currently in FDA clinical trials?"
- "How are current AI ethics guidelines affecting diagnostic AI development?"

## 🎯 Future Enhancements

- Integration with medical databases (PubMed, ClinicalTrials.gov)
- Multi-modal support for medical images and DICOM files
- Real-time regulatory updates and notifications
- Specialized medical terminology processing
- Integration with clinical workflow systems
- Advanced medical literature analysis