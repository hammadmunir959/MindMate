import json
import logging
from typing import AsyncGenerator, Any
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

class StreamingService:
    @staticmethod
    async def stream_events(graph: Any, state: dict, config: dict = None) -> AsyncGenerator[str, None]:
        """
        Streams only the clinician response tokens as Server-Sent Events (SSE).
        Filters out internal agent reasoning (supervisor, extractor, etc.).
        """
        try:
            async for event in graph.astream_events(state, config=config, version="v2"):
                # Metadata check is the standard way in LangGraph to identify node origin.
                # We only want tokens from the 'call_llm' node which represents the clinician persona.
                node_name = event.get("metadata", {}).get("langgraph_node")
                
                if event["event"] == "on_chat_model_stream" and node_name == "call_llm":
                    chunk = event["data"].get("chunk")
                    content = getattr(chunk, "content", "")
                    if content:
                        yield f"data: {json.dumps({'content': content})}\n\n"
                        
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    @staticmethod
    def create_streaming_response(graph: Any, state: dict, config: dict = None) -> StreamingResponse:
        """
        Returns a FastAPI StreamingResponse configured for SSE event streaming.
        """
        return StreamingResponse(
            StreamingService.stream_events(graph, state, config),
            media_type="text/event-stream"
        )
