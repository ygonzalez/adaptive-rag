# State Management System

from typing import List, TypedDict


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        web_search: whether to add search
        documents: list of documents
        generation_attempts: number of generation attempts
        web_search_attempts: number of web search attempts
        session_id: session identifier for process visualization
    """

    question: str
    generation: str
    web_search: bool
    documents: List[str]
    generation_attempts: int
    web_search_attempts: int
    session_id: str