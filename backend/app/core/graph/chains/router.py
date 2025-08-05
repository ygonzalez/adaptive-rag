from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from pydantic import BaseModel, Field
from ...models.model import get_chat_model

class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: Literal["vectorstore", "websearch"] = Field(
        ...,
        description="Given a user question choose to route it to web search or a vectorstore.",
    )

llm = get_chat_model()

structured_llm_router = llm.with_structured_output(RouteQuery)

system = """You are an expert at routing a user question to a vectorstore or web search.
The vectorstore contains documents related to agents, prompt engineering, adversarial attacks, and general AI/ML concepts.
Use the vectorstore for questions about AI, machine learning, agents, prompt engineering, LLMs, or adversarial attacks.
For all other topics (weather, news, recipes, non-AI topics), use web-search."""
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

question_router: RunnableSequence = route_prompt | structured_llm_router