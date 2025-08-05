from typing import Any, Dict

from ..state import GraphState
from ...ingestion.ingestion import get_retriever


def retrieve(state: GraphState) -> Dict[str, Any]:
    print("---RETRIEVE---")
    question = state["question"]

    retriever = get_retriever()
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}