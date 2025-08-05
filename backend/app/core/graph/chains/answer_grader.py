from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence, RunnableLambda
from pydantic import BaseModel, Field
from ...models.model import get_chat_model


class GradeAnswer(BaseModel):

    binary_score: bool = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

llm =  get_chat_model()

structured_llm_grader = llm.with_structured_output(GradeAnswer)

system = """You are a grader assessing whether an answer addresses / resolves a question \n 
     Give a binary score 'yes' or 'no'. 'Yes' means that the answer resolves the question.
     Empty or blank answers should always be graded as 'no' (not addressing the question)."""
answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
    ]
)

def preprocess_answer(inputs):
    """Preprocess inputs to handle edge cases."""
    if not inputs.get("generation", "").strip():
        return GradeAnswer(binary_score=False)
    return None

# Create chain with preprocessing
chain_with_llm = answer_prompt | structured_llm_grader

def grade_with_preprocessing(inputs):
    """Grade answer with preprocessing for edge cases."""
    preprocessed = preprocess_answer(inputs)
    if preprocessed:
        return preprocessed
    return chain_with_llm.invoke(inputs)

answer_grader = RunnableLambda(grade_with_preprocessing)