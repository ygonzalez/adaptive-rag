from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence, RunnableLambda
from pydantic import BaseModel, Field
from ...models.model import get_chat_model

llm = get_chat_model()

class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


structured_llm_grader = llm.with_structured_output(GradeDocuments)

system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
    If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant. \n
    Empty or blank documents should always be graded as 'no'. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""

grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
    ]
)

def preprocess_grading(inputs):
    """Preprocess inputs to handle edge cases."""
    if not inputs.get("document", "").strip():
        return GradeDocuments(binary_score="no")
    return None

# Create chain with preprocessing
chain_with_preprocessing = RunnableLambda(preprocess_grading)
chain_with_llm = grade_prompt | structured_llm_grader

def grade_with_preprocessing(inputs):
    """Grade documents with preprocessing for edge cases."""
    preprocessed = preprocess_grading(inputs)
    if preprocessed:
        return preprocessed
    return chain_with_llm.invoke(inputs)

retrieval_grader = RunnableLambda(grade_with_preprocessing)