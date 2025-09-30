from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.conversation_answering import ConversationAnswering
from services.preprocessing import Preprocessing
from models.schemas import ChatRequest, ChatResponse
from utils.logger import logger
import uuid
import json
import asyncio

router = APIRouter(prefix="/api/ws")

@router.websocket("/chat")
async def chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat interactions.
    """
    await websocket.accept()
    
    session_id = str(uuid.uuid4())
    logger.info(f"WebSocket connection accepted. session_id={session_id}")

    # Load vector store
    try:
        preprocessor = Preprocessing(file_path=None)
        vector_store = preprocessor.load_embeddings_pinecone()
        index = preprocessor.pc.Index(preprocessor.index_name)
        stats = index.describe_index_stats()
        vector_count = stats["total_vector_count"]
        logger.info(f"{vector_count} vectors in the store.") 
        logger.info("Vector store loaded for chat.")
    except Exception as e:
        logger.error(f"Error loading vector store: {e}")
        await websocket.close()
        return
     
    # Answer using RAG
    conversation = ConversationAnswering(
        vector_store=vector_store,
        session_id=session_id
    )
    logger.info("ConversationAnswering instance created.")
    try:
        while True:
            try:
                try:
                    try:
                    # Receive message (assuming client sends JSON)
                        data = await websocket.receive_text()
                    except WebSocketDisconnect:
                        logger.info(f"WebSocket disconnected while receiving. session_id={session_id}")
                        break
                    
                    data_json = json.loads(data)

                    request = ChatRequest(**data_json)
                    logger.info(f"Received question: {request.message}")
                except Exception as e:
                    logger.error(f"Error parsing message: {e}", exc_info=True)
                    await websocket.send_json({"error": "Invalid message format."})
                    continue

                try:
                    answer = await asyncio.to_thread(conversation.conversation_answer, request.message)
                    logger.info(f"Generated answer")
                except Exception as e:
                    logger.error(f"Error while generating answer in worker thread: {e}", exc_info=True)
                    try:
                        await websocket.send_json({"error": "Error generating answer."})
                    except Exception:
                        pass
                    continue
                try:
                    response = ChatResponse(
                        reply=answer.get("answer", "No answer generated."),
                        session_id=session_id
                    )
                    try:
                        await websocket.send_json(response.model_dump())
                        logger.info("Sent response to client.")
                    except Exception:
                        pass
                except Exception as e:
                    logger.error(f"Error sending response: {e}", exc_info=True)
                    await websocket.send_json({"error": "Error sending response."})

            except Exception as e:
                logger.error(f"Error during chat: {e}")
                await websocket.send_json({"error": "An error occurred during chat."})
                break
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected. session_id={session_id}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        
    finally:
        ConversationAnswering.sessions.pop(session_id, None)
        logger.info(f"Disconnected session. session_id={session_id}")
        try:
            await websocket.close()
        except Exception as e:
            pass