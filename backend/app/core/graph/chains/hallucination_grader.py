from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence, RunnableLambda
from pydantic import BaseModel, Field
from ...models.model import get_chat_model

llm =  get_chat_model()

class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: bool = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )


structured_llm_grader = llm.with_structured_output(GradeHallucinations)

system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 
     Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts.
     Empty or blank generations should always be graded as 'no' (not grounded)."""

hallucination_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
    ]
)

def preprocess_hallucination(inputs):
    """Preprocess inputs to handle edge cases."""
    if not inputs.get("generation", "").strip():
        return GradeHallucinations(binary_score=False)
    return None

# Create chain with preprocessing
chain_with_llm = hallucination_prompt | structured_llm_grader

def grade_with_preprocessing(inputs):
    """Grade hallucinations with preprocessing for edge cases."""
    preprocessed = preprocess_hallucination(inputs)
    if preprocessed:
        return preprocessed
    return chain_with_llm.invoke(inputs)

hallucination_grader = RunnableLambda(grade_with_preprocessing)