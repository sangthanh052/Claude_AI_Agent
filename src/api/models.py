"""
Các mô hình dữ liệu cho API Claude Agent.

File này định nghĩa các lớp Pydantic được sử dụng để xác thực
và chuyển đổi dữ liệu trong API.
"""

from typing import List, Optional
from pydantic import BaseModel

class Message(BaseModel):
    """Đại diện cho một tin nhắn trong cuộc trò chuyện."""
    role: str  # 'user' hoặc 'assistant'
    content: str  # Nội dung tin nhắn

class ChatRequest(BaseModel):
    """Yêu cầu chat từ người dùng."""
    messages: List[Message] = []
    session_id: Optional[str] = None  # ID phiên làm việc, tùy chọn
    system_prompt: Optional[str] = None  # System prompt tùy chọn
    prompt_type: Optional[str] = None  # Loại prompt từ file prompts.py

class ChatResponse(BaseModel):
    """Phản hồi chat từ Claude."""
    response: str
    session_id: str  # ID phiên làm việc

class SessionConfig(BaseModel):
    """Cấu hình cho một phiên làm việc."""
    system_prompt: str
