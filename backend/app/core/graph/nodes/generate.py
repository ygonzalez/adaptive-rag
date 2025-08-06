from typing import Any, Dict

from ..chains.generation import generation_chain
from ..state import GraphState


def generate(state: GraphState) -> Dict[str, Any]:
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]
    generation_attempts = state.get("generation_attempts", 0)

    generation = generation_chain.invoke({"context": documents, "question": question})
    return {
        "documents": documents, 
        "question": question, 
        "generation": generation,
        "generation_attempts": generation_attempts + 1
    }