"""
AI Healthcare data sources and sample queries for the RAG system.
"""

# AI Healthcare URLs for ingestion
AI_HEALTHCARE_URLS = [
    # MEDICAL IMAGING AI
    "https://www.nature.com/articles/s41591-018-0107-6",    # AI for medical imaging overview
    "https://www.nature.com/articles/s41591-020-0912-5",    # Deep learning in medical imaging
    "https://www.nature.com/articles/s41591-019-0447-x",    # AI in dermatology imaging
    "https://www.nature.com/articles/s41591-018-0300-7",    # AI in retinal imaging
    
    # CLINICAL AI SYSTEMS  
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7392384/",  # AI in clinical decision making
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8285948/",  # ML in intensive care
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7502282/",  # AI in emergency medicine
    
    # DIAGNOSTIC AI
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8543151/",  # AI in diagnostic imaging
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7861833/",  # AI in lab diagnostics
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8012650/",  # AI in pathology
    
    # PREDICTIVE ANALYTICS
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7308977/",  # Predictive healthcare models
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8234062/",  # AI for early detection
    
    # AI ETHICS & VALIDATION
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8285617/",  # Bias in healthcare AI
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7640852/",  # Fairness in medical AI
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8234721/",  # Explainable AI in medicine
]

# Sample queries for different healthcare AI domains
IMAGING_QUERIES = [
    # Technical implementation questions
    "How does deep learning improve medical image analysis?",
    "What are the challenges of AI in radiology?", 
    "How accurate is AI for detecting skin cancer in dermoscopy images?",
    "What neural network architectures work best for medical imaging?",
    
    # Clinical application questions
    "How is AI being used in retinal disease diagnosis?",
    "What are the benefits of AI-assisted pathology diagnosis?",
    "How does AI help radiologists detect early-stage cancer?",
    
    # Comparison and evaluation
    "How does AI performance compare to human radiologists?",
    "What metrics are used to evaluate medical imaging AI systems?",
]

CLINICAL_AI_QUERIES = [
    # System capabilities  
    "How do AI systems assist in clinical decision making?",
    "What role does machine learning play in intensive care units?",
    "How can AI improve emergency department triage?",
    
    # Implementation challenges
    "What are the barriers to implementing AI in clinical practice?",
    "How do clinicians interact with AI decision support systems?",
    "What training do doctors need for AI-assisted diagnosis?",
    
    # Specific applications
    "How does AI predict patient deterioration in hospitals?",
    "What AI tools are available for drug interaction checking?",
]

DIAGNOSTIC_QUERIES = [
    # Technology and methods
    "How does AI analyze laboratory test results?",
    "What machine learning models are used for medical diagnosis?",
    "How do multimodal AI systems combine different data types?",
    
    # Accuracy and validation
    "How accurate are AI diagnostic systems compared to doctors?",
    "What validation methods are used for diagnostic AI?",
    "How do you ensure AI diagnostic systems are safe for patients?",
    
    # Specific conditions
    "How does AI detect cancer in biopsy images?",
    "What AI systems exist for cardiovascular disease diagnosis?",
]

CURRENT_QUERIES = [
    # Recent approvals and developments
    "Latest FDA approvals for AI medical devices 2024",
    "Recent breakthroughs in AI medical imaging 2024", 
    "New AI diagnostic tools approved this year",
    "Current clinical trials using AI for diagnosis",
    
    # Market and industry
    "Top healthcare AI companies 2024",
    "Recent funding for medical AI startups",
    "New partnerships between hospitals and AI companies",
    
    # Regulatory updates
    "Latest FDA guidance on AI in healthcare 2024",
    "New regulations for AI medical devices",
    "Recent changes in AI healthcare compliance requirements",
]

COMPLEX_QUERIES = [
    # Cross-domain queries
    "What AI imaging technologies are currently in FDA clinical trials?",
    "How do recent regulatory changes affect AI radiology implementations?",
    "Which diagnostic AI systems have been approved since 2023?",
    
    # Technical + current events
    "What new deep learning architectures are being tested for medical imaging?",
    "How are current AI ethics guidelines affecting diagnostic AI development?",
    "What validation challenges exist for recently approved AI medical devices?",
]

# All sample queries combined
ALL_SAMPLE_QUERIES = (
    IMAGING_QUERIES + 
    CLINICAL_AI_QUERIES + 
    DIAGNOSTIC_QUERIES + 
    CURRENT_QUERIES + 
    COMPLEX_QUERIES
)

def get_healthcare_urls():
    """Get the list of AI healthcare URLs for ingestion."""
    return AI_HEALTHCARE_URLS

def get_sample_queries():
    """Get all sample healthcare AI queries."""
    return ALL_SAMPLE_QUERIES

def get_sample_queries_by_category():
    """Get sample queries organized by category."""
    return {
        "Medical Imaging": IMAGING_QUERIES,
        "Clinical AI": CLINICAL_AI_QUERIES,
        "Diagnostic AI": DIAGNOSTIC_QUERIES,
        "Current Developments": CURRENT_QUERIES,
        "Complex Queries": COMPLEX_QUERIES
    }