import asyncio
import time
from dotenv import load_dotenv
from langgraph.graph import END, StateGraph

from .chains.answer_grader import answer_grader
from .chains.hallucination_grader import hallucination_grader
from .chains.router import RouteQuery, question_router
from .consts import GENERATE, GRADE_DOCUMENTS, RETRIEVE, WEBSEARCH
from .nodes.generate import generate
from .nodes.grade_documents import grade_documents
from .nodes.retrieve import retrieve
from .nodes.web_search import web_search
from .state import GraphState
from ..visualization import (
    emit_routing_started,
    emit_routing_completed,
    emit_hallucination_check,
    emit_answer_grading
)

load_dotenv()

def decide_to_generate(state):
    print("---ASSESS GRADED DOCUMENTS---")

    if state["web_search"]:
        print(
            "---DECISION: NOT ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, INCLUDE WEB SEARCH---"
        )
        return WEBSEARCH
    else:
        print("---DECISION: GENERATE---")
        return GENERATE

def grade_generation_grounded_in_documents_and_question(state: GraphState) -> str:
    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]
    generation_attempts = state.get("generation_attempts", 0)
    web_search_attempts = state.get("web_search_attempts", 0)
    session_id = state.get("session_id", "default")
    
    # Create event loop if needed for async event emission
    loop = None
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Check if we've hit max retries
    MAX_GENERATION_ATTEMPTS = 3
    MAX_WEB_SEARCH_ATTEMPTS = 2
    
    if generation_attempts >= MAX_GENERATION_ATTEMPTS:
        print(f"---MAX GENERATION ATTEMPTS ({MAX_GENERATION_ATTEMPTS}) REACHED, ENDING---")
        return "max_retries"
    
    start_time = time.time()
    # Format documents for hallucination checking - extract only page_content
    formatted_docs = "\n\n---\n\n".join([doc.page_content for doc in documents])
    score = hallucination_grader.invoke(
        {"documents": formatted_docs, "generation": generation}
    )
    duration_ms = int((time.time() - start_time) * 1000)

    # Emit hallucination check event
    if loop:
        loop.create_task(emit_hallucination_check(
            session_id, question, "yes" if score.binary_score else "no", duration_ms
        ))

    if hallucination_grade := score.binary_score:
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        print("---GRADE GENERATION vs QUESTION---")
        
        start_time = time.time()
        score = answer_grader.invoke({"question": question, "generation": generation})
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Emit answer grading event
        if loop:
            loop.create_task(emit_answer_grading(
                session_id, question, "yes" if score.binary_score else "no", duration_ms
            ))
        
        if answer_grade := score.binary_score:
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            if web_search_attempts >= MAX_WEB_SEARCH_ATTEMPTS:
                print(f"---MAX WEB SEARCH ATTEMPTS ({MAX_WEB_SEARCH_ATTEMPTS}) REACHED, ENDING---")
                return "max_retries"
            return "not useful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"


def route_question(state: GraphState) -> str:
    """
    Route question to web search or RAG.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE QUESTION---")
    question = state["question"]
    session_id = state.get("session_id", "default")
    
    # Create event loop if needed for async event emission
    loop = None
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Emit routing started event
    if loop:
        loop.create_task(emit_routing_started(session_id, question))
    
    start_time = time.time()
    source: RouteQuery = question_router.invoke({"question": question})
    duration_ms = int((time.time() - start_time) * 1000)
    
    decision = source.datasource
    confidence = 0.85 if decision == WEBSEARCH else 0.95  # Mock confidence scores
    reasoning = f"Question contains {'general/web' if decision == WEBSEARCH else 'AI/ML'} keywords"
    
    # Emit routing completed event
    if loop:
        loop.create_task(emit_routing_completed(
            session_id, question, decision, confidence, reasoning, duration_ms
        ))

    if source.datasource == WEBSEARCH:
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return WEBSEARCH
    elif source.datasource == "vectorstore":
        print("---ROUTE QUESTION TO RAG---")
        return RETRIEVE


workflow = StateGraph(GraphState)

workflow.add_node(RETRIEVE, retrieve)
workflow.add_node(GRADE_DOCUMENTS, grade_documents)
workflow.add_node(GENERATE, generate)
workflow.add_node(WEBSEARCH, web_search)

workflow.set_conditional_entry_point(
    route_question,
    {
        WEBSEARCH: WEBSEARCH,
        RETRIEVE: RETRIEVE,
    },
)

# workflow.set_entry_point(RETRIEVE)

workflow.add_edge(RETRIEVE, GRADE_DOCUMENTS)
workflow.add_conditional_edges(
    GRADE_DOCUMENTS,
    decide_to_generate,
    {
        WEBSEARCH: WEBSEARCH,
        GENERATE: GENERATE,
    },
)

workflow.add_conditional_edges(
    GENERATE,
    grade_generation_grounded_in_documents_and_question,
    {
        "not supported": GENERATE,
        "useful": END,
        "not useful": WEBSEARCH,
        "max_retries": END,
    },
)
workflow.add_edge(WEBSEARCH, GENERATE)
workflow.add_edge(GENERATE, END)

app = workflow.compile()

# Set recursion limit to prevent infinite loops
app.recursion_limit = 15

app.get_graph().draw_mermaid_png(output_file_path="graph.png")