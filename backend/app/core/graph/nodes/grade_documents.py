import asyncio
import time
from typing import Any, Dict

from ..chains.retrieval_grader import retrieval_grader
from ..state import GraphState
from ...visualization import (
    DocumentGrade,
    emit_grading_started,
    emit_grading_completed,
    emit_step_failed,
    ProcessStepType
)


def grade_documents(state: GraphState) -> Dict[str, Any]:
    """
    Determines whether the retrieved documents are relevant to the question
    If any document is not relevant, we will set a flag to run web search

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Filtered out irrelevant documents and updated web_search state
    """

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]
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
        loop.create_task(emit_grading_started(session_id, question))

    try:
        filtered_docs = []
        web_search = False
        document_grades = []
        
        for d in documents:
            score = retrieval_grader.invoke(
                {"question": question, "document": d.page_content}
            )
            grade = score.binary_score
            
            # Create document grade info for visualization
            doc_grade = DocumentGrade(
                content_preview=d.page_content[:150] + "..." if len(d.page_content) > 150 else d.page_content,
                relevance_score=grade,
                source=getattr(d, 'metadata', {}).get('source', 'Unknown') if hasattr(d, 'metadata') else 'Unknown'
            )
            document_grades.append(doc_grade)
            
            if grade.lower() == "yes":
                print("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(d)
            else:
                print("---GRADE: DOCUMENT NOT RELEVANT---")
                web_search = True
                continue
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Emit completed event
        if loop:
            loop.create_task(emit_grading_completed(
                session_id,
                question,
                document_grades,
                len(filtered_docs),
                duration_ms
            ))
        
        return {"documents": filtered_docs, "question": question, "web_search": web_search}
    
    except Exception as e:
        # Emit failed event
        if loop:
            loop.create_task(emit_step_failed(
                session_id, 
                ProcessStepType.GRADE_DOCUMENTS, 
                question, 
                str(e)
            ))
        raise e