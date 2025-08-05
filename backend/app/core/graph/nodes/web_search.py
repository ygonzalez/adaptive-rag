from typing import Any, Dict
import asyncio
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_tavily import TavilySearch
from ..state import GraphState

load_dotenv()

def get_web_search_tool():
    """Get web search tool with proper event loop handling"""
    try:
        return TavilySearch(max_results=3)
    except Exception as e:
        print(f"Warning: Could not initialize TavilySearch: {e}")
        return None

def web_search(state: GraphState) -> Dict[str, Any]:
    print("---WEB SEARCH---")
    question = state["question"]
    documents = state.get("documents", [])

    try:
        # Ensure we have an event loop for async operations
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Event loop is closed")
        except RuntimeError:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Get the search tool
        web_search_tool = get_web_search_tool()
        if web_search_tool is None:
            # Fallback: create a mock result if web search fails
            web_results = Document(
                page_content=f"I apologize, but I cannot perform a web search for '{question}' at the moment due to a configuration issue. Please check your TAVILY_API_KEY environment variable."
            )
        else:
            # Perform the web search
            tavily_results = web_search_tool.invoke({"query": question})["results"]
            joined_tavily_result = "\n".join(
                [tavily_result["content"] for tavily_result in tavily_results]
            )
            web_results = Document(page_content=joined_tavily_result)

        if documents:
            documents.append(web_results)
        else:
            documents = [web_results]

        return {"documents": documents, "question": question}

    except Exception as e:
        print(f"Error in web search: {e}")
        # Return a fallback response
        fallback_doc = Document(
            page_content=f"I encountered an error while searching for information about '{question}'. Please try again or rephrase your question."
        )
        if documents:
            documents.append(fallback_doc)
        else:
            documents = [fallback_doc]
        
        return {"documents": documents, "question": question}

if __name__ == "__main__":
    web_search(state={"question": "agent memory", "documents": None})