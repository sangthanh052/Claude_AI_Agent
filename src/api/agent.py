"""
Lớp ClaudeAgent để tương tác với Claude 3.7.

File này định nghĩa lớp ClaudeAgent, cung cấp các phương thức
để tạo phản hồi từ Claude 3.7 sử dụng PydanticAI.
"""

from typing import List
from pydantic_ai import Agent
from fastapi import HTTPException

from src.api.models import Message
from src.config.settings import CLAUDE_MODEL
from src.utils.logger import Logger

class ClaudeAgent:
    """Agent AI được hỗ trợ bởi Claude 3.7."""
    
    @staticmethod
    async def generate_response(messages: List[Message], system_prompt: str) -> str:
        """Tạo phản hồi sử dụng Claude 3.7 với PydanticAI."""
        try:
            # Tạo agent sử dụng Claude model từ biến môi trường
            # (Create an agent using Claude model from environment variable)
            agent = Agent(CLAUDE_MODEL)
            
            # Định dạng tin nhắn thành chuỗi hội thoại với system prompt
            # (Format messages as a conversation string with system prompt)
            conversation = f"\nSystem: {system_prompt}"
            for msg in messages:
                conversation += f"\n{msg.role.capitalize()}: {msg.content}"
            
            # Ghi log yêu cầu
            # (Log the request)
            print(f"Sending to Claude: {conversation}")
            
            # Ghi log yêu cầu với Logfire
            Logger.info(
                "Claude request",
                model=CLAUDE_MODEL,
                message_count=len(messages),
                system_prompt_length=len(system_prompt)
            )
            
            # Chạy agent với chuỗi hội thoại
            # (Run the agent with the conversation string)
            result = await agent.run(conversation)
            
            # Ghi log phản hồi với Logfire
            Logger.info(
                "Claude response",
                model=CLAUDE_MODEL,
                response_length=len(result.data)
            )
            
            return result.data
        except Exception as e:
            error_msg = f"Error communicating with Claude: {e}"
            print(f"Error details: {e}")
            
            # Ghi log lỗi với Logfire
            Logger.error(
                "Claude error",
                error=str(e)
            )
            
            raise HTTPException(status_code=500, detail=error_msg)
