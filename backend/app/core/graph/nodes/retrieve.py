import asyncio
import time
from typing import Any, Dict

from ..state import GraphState
from ...ingestion.ingestion import get_retriever
from ...visualization import (
    emit_retrieve_started,
    emit_retrieve_completed,
    emit_step_failed,
    ProcessStepType
)


def retrieve(state: GraphState) -> Dict[str, Any]:
    print("---RETRIEVE---")
    question = state["question"]
    session_id = state.get("session_id", "default")
    
    # Create event loop if needed for async event emission
    loop = None
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    start_time = time.time()
    
    # Emit started event
    if loop:
        loop.create_task(emit_retrieve_started(session_id, question))

    try:
        retriever = get_retriever()
        documents = retriever.invoke(question)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Emit completed event
        if loop:
            loop.create_task(emit_retrieve_completed(
                session_id, 
                question, 
                len(documents), 
                duration_ms
            ))
        
        return {"documents": documents, "question": question}
    
    except Exception as e:
        # Emit failed event
        if loop:
            loop.create_task(emit_step_failed(
                session_id, 
                ProcessStepType.RETRIEVE, 
                question, 
                str(e)
            ))
        raise e