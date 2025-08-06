from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from typing import List
import logging
import json

from app.core.visualization import process_manager, ProcessEvent
from app.utils.dependencies import get_chat_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/visualization/ws/{session_id}")
async def visualization_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time process visualization events
    """
    await websocket.accept()
    logger.info(f"WebSocket connection opened for session: {session_id}")
    
    # Add this connection to the process manager
    process_manager.add_websocket_connection(session_id, websocket)
    
    try:
        # Send any existing events for this session
        existing_events = process_manager.get_session_events(session_id)
        for event in existing_events:
            try:
                await websocket.send_text(event.model_dump_json())
            except Exception as e:
                logger.error(f"Error sending existing event: {e}")
        
        # Keep the connection alive and handle incoming messages
        while True:
            try:
                # We expect the frontend to send ping messages to keep alive
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif message.get("type") == "get_events":
                    # Send all events for this session
                    events = process_manager.get_session_events(session_id)
                    response = {
                        "type": "session_events",
                        "events": [event.model_dump() for event in events]
                    }
                    await websocket.send_text(json.dumps(response, default=str))
                    
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from WebSocket: {data}")
            except Exception as e:
                logger.error(f"Error in WebSocket message handling: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
    finally:
        # Remove the connection from the process manager
        process_manager.remove_websocket_connection(session_id, websocket)


@router.get("/visualization/events/{session_id}")
async def get_session_events(session_id: str) -> List[ProcessEvent]:
    """
    Get all process events for a specific session (REST endpoint fallback)
    """
    try:
        events = process_manager.get_session_events(session_id)
        return events
    except Exception as e:
        logger.error(f"Error retrieving events for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/visualization/events/{session_id}")
async def clear_session_events(session_id: str):
    """
    Clear all process events for a specific session
    """
    try:
        process_manager.clear_session_events(session_id)
        return {"message": f"Events cleared for session {session_id}"}
    except Exception as e:
        logger.error(f"Error clearing events for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visualization/sessions")
async def get_active_sessions():
    """
    Get all active sessions with process events
    """
    try:
        sessions = list(process_manager.active_sessions.keys())
        return {"active_sessions": sessions}
    except Exception as e:
        logger.error(f"Error retrieving active sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))