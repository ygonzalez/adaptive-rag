import asyncio
import time
from typing import Any, Dict

from ..chains.generation import generation_chain
from ..state import GraphState
from ...visualization import (
    emit_generation_started,
    emit_generation_completed,
    emit_step_failed,
    ProcessStepType
)


def generate(state: GraphState) -> Dict[str, Any]:
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]
    generation_attempts = state.get("generation_attempts", 0)
    session_id = state.get("session_id", "default")
    
    # Create event loop if needed for async event emission
    loop = None
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    start_time = time.time()
    attempt = generation_attempts + 1
    
    # Emit started event
    if loop:
        loop.create_task(emit_generation_started(session_id, question, attempt))

    try:
        # Format documents properly - extract only page_content
        formatted_docs = "\n\n---\n\n".join([doc.page_content for doc in documents])
        generation = generation_chain.invoke({"context": formatted_docs, "question": question})
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Emit completed event
        if loop:
            loop.create_task(emit_generation_completed(
                session_id, 
                question, 
                attempt,
                generation,
                duration_ms
            ))
        
        return {
            "documents": documents, 
            "question": question, 
            "generation": generation,
            "generation_attempts": attempt
        }
    
    except Exception as e:
        # Emit failed event
        if loop:
            loop.create_task(emit_step_failed(
                session_id, 
                ProcessStepType.GENERATE, 
                question, 
                str(e)
            ))
        raise e