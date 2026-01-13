"""
WebSocket service for real-time requirements chat refinement.
Handles streaming responses from Groq API and conversation state management.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import WebSocket, WebSocketDisconnect
from groq import AsyncGroq
import redis.asyncio as redis

from config import get_settings
from services.llm_service import LLMService

settings = get_settings()


class ConversationManager:
    """Manages conversation state in Redis."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.ttl = 86400  # 24 hours
        
    async def connect(self):
        """Connect to Redis."""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
    
    async def get_conversation(self, session_id: str) -> Optional[Dict]:
        """Retrieve conversation state from Redis."""
        await self.connect()
        data = await self.redis_client.get(f"conversation:{session_id}")
        if data:
            return json.loads(data)
        return None
    
    async def save_conversation(self, session_id: str, conversation: Dict):
        """Save conversation state to Redis with TTL."""
        await self.connect()
        await self.redis_client.setex(
            f"conversation:{session_id}",
            self.ttl,
            json.dumps(conversation)
        )
    
    async def add_message(self, session_id: str, role: str, content: str):
        """Add a message to conversation history."""
        conversation = await self.get_conversation(session_id)
        if not conversation:
            conversation = {
                "session_id": session_id,
                "requirement_id": None,
                "messages": [],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        
        conversation["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        conversation["updated_at"] = datetime.utcnow().isoformat()
        
        await self.save_conversation(session_id, conversation)
    
    async def get_context_window(self, session_id: str, max_messages: int = 10) -> List[Dict]:
        """Get recent messages for context window."""
        conversation = await self.get_conversation(session_id)
        if not conversation:
            return []
        
        messages = conversation.get("messages", [])
        # Return last N messages for context
        return messages[-max_messages:]


class WebSocketService:
    """Handles WebSocket connections for requirements chat."""
    
    def __init__(self):
        self.conversation_manager = ConversationManager()
        self.llm_service = LLMService()
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept WebSocket connection."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        await self.conversation_manager.connect()
    
    async def disconnect(self, session_id: str):
        """Remove WebSocket connection."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, session_id: str, message: Dict):
        """Send message to specific WebSocket."""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)
    
    async def handle_chat(self, websocket: WebSocket, session_id: str):
        """Handle chat messages with streaming responses."""
        try:
            await self.connect(websocket, session_id)
            
            # Send connection confirmation
            await self.send_message(session_id, {
                "type": "connected",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            while True:
                # Receive message from client
                data = await websocket.receive_json()
                
                message_type = data.get("type")
                content = data.get("content", "")
                
                if message_type == "message":
                    # Save user message
                    await self.conversation_manager.add_message(
                        session_id, "user", content
                    )
                    
                    # Get conversation context
                    context = await self.conversation_manager.get_context_window(session_id)
                    
                    # Stream AI response
                    await self.stream_ai_response(session_id, content, context)
                
                elif message_type == "new_chat":
                    # Clear conversation
                    await self.conversation_manager.save_conversation(session_id, {
                        "session_id": session_id,
                        "requirement_id": data.get("requirement_id"),
                        "messages": [],
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
                    })
                    await self.send_message(session_id, {
                        "type": "chat_cleared",
                        "timestamp": datetime.utcnow().isoformat()
                    })
        
        except WebSocketDisconnect:
            await self.disconnect(session_id)
        except Exception as e:
            await self.send_message(session_id, {
                "type": "error",
                "content": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            await self.disconnect(session_id)
    
    async def stream_ai_response(self, session_id: str, user_message: str, context: List[Dict]):
        """Stream AI response using Groq API."""
        try:
            # Build conversation history for Groq
            messages = [
                {
                    "role": "system",
                    "content": """You are an AI assistant helping refine software requirements.
Your goal is to:
1. Identify ambiguous terms and suggest specific alternatives
2. Find missing edge cases, error handling, and constraints
3. Detect potential biases or ethical concerns
4. Provide actionable, specific suggestions

Be concise and practical. Format suggestions as numbered lists when appropriate."""
                }
            ]
            
            # Add recent context
            for msg in context[-5:]:  # Last 5 messages
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add current user message if not already in context
            if not context or context[-1]["content"] != user_message:
                messages.append({
                    "role": "user",
                    "content": user_message
                })
            
            # Stream response from Groq
            client = AsyncGroq(api_key=settings.GROQ_API_KEY)
            
            stream = await client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                stream=True
            )
            
            full_response = ""
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    
                    # Send chunk to client
                    await self.send_message(session_id, {
                        "type": "chunk",
                        "content": content,
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            # Save assistant response
            await self.conversation_manager.add_message(
                session_id, "assistant", full_response
            )
            
            # Send completion signal
            await self.send_message(session_id, {
                "type": "complete",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        except Exception as e:
            await self.send_message(session_id, {
                "type": "error",
                "content": f"Failed to generate response: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            })


# Singleton instance
websocket_service = WebSocketService()
