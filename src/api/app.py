"""
API Server sử dụng Claude 3.7 với FastAPI.

Ứng dụng này tạo ra một API server có khả năng xử lý yêu cầu từ người dùng,
sử dụng mô hình Claude 3.7 của Anthropic và framework FastAPI để phục vụ
các endpoints API.
"""

import os
import asyncio
from typing import List, Optional, Dict, Any
import uuid
import json

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware

# Import từ các module trong dự án
from src.api.models import Message, ChatRequest, ChatResponse, SessionConfig
from src.api.agent import ClaudeAgent
from src.prompts.prompts import (
    DEFAULT_SYSTEM_PROMPT, 
    PROGRAMMING_ASSISTANT_PROMPT, 
    WRITING_ASSISTANT_PROMPT, 
    EDUCATION_ASSISTANT_PROMPT
)
from src.utils.logger import Logger
from src.config.settings import (
    API_HOST, 
    API_PORT, 
    API_TITLE, 
    API_DESCRIPTION, 
    API_VERSION,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS
)

# Tạo ứng dụng FastAPI
# (Create FastAPI application)
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Thêm CORS middleware để cho phép yêu cầu từ các nguồn khác
# (Add CORS middleware to allow requests from other origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

# Middleware để ghi log tất cả các yêu cầu
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware để ghi log tất cả các yêu cầu và phản hồi."""
    # Ghi log yêu cầu
    request_path = request.url.path
    request_method = request.method
    
    # Lấy body của yêu cầu nếu có thể
    request_body = None
    if request_method in ["POST", "PUT"]:
        try:
            body_bytes = await request.body()
            if body_bytes:
                request_body = body_bytes.decode()
        except Exception:
            request_body = None
    
    # Ghi log yêu cầu
    Logger.info(
        "API request",
        method=request_method,
        path=request_path,
        body=request_body
    )
    
    # Xử lý yêu cầu
    response = await call_next(request)
    
    # Ghi log phản hồi
    Logger.info(
        "API response",
        method=request_method,
        path=request_path,
        status_code=response.status_code
    )
    
    return response

# Lưu trữ lịch sử hội thoại theo phiên làm việc
# (Store conversation history by session)
conversation_history: Dict[str, List[Message]] = {}

# Lưu trữ cấu hình cho mỗi phiên làm việc
# (Store configuration for each session)
session_configs: Dict[str, SessionConfig] = {}

# Dictionary ánh xạ tên prompt đến giá trị prompt
# (Dictionary mapping prompt names to prompt values)
PROMPT_TYPES = {
    "default": DEFAULT_SYSTEM_PROMPT,
    "programming": PROGRAMMING_ASSISTANT_PROMPT,
    "writing": WRITING_ASSISTANT_PROMPT,
    "education": EDUCATION_ASSISTANT_PROMPT
}

# Hàm để lấy hoặc tạo phiên làm việc mới
# (Function to get or create a new session)
def get_or_create_session(session_id: Optional[str] = None) -> str:
    """
    Lấy phiên làm việc hiện có hoặc tạo phiên mới nếu không tồn tại.
    
    Args:
        session_id: ID phiên làm việc tùy chọn
        
    Returns:
        ID phiên làm việc
    """
    # Nếu không cung cấp session_id, tạo mới
    if not session_id:
        session_id = str(uuid.uuid4())
        conversation_history[session_id] = []
        session_configs[session_id] = SessionConfig(system_prompt=DEFAULT_SYSTEM_PROMPT)
        
        # Ghi log tạo phiên mới
        Logger.info("Session created", session_id=session_id)
    
    # Nếu session_id không tồn tại, tạo mới
    elif session_id not in conversation_history:
        conversation_history[session_id] = []
        session_configs[session_id] = SessionConfig(system_prompt=DEFAULT_SYSTEM_PROMPT)
        
        # Ghi log tạo phiên mới
        Logger.info("Session created", session_id=session_id)
    
    return session_id

# Định nghĩa endpoint API
# (Define API endpoints)

@app.get("/")
async def root():
    """Endpoint chính để kiểm tra trạng thái máy chủ."""
    return {"status": "online", "message": "Claude Agent API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint để xử lý yêu cầu chat.
    
    Nhận danh sách tin nhắn và trả về phản hồi từ Claude.
    Nếu cung cấp session_id, sẽ tiếp tục hội thoại hiện có.
    Nếu không, sẽ tạo phiên mới.
    """
    try:
        # Lấy hoặc tạo phiên làm việc
        session_id = get_or_create_session(request.session_id)
        
        # Xác định system prompt
        system_prompt = DEFAULT_SYSTEM_PROMPT
        
        # Nếu có prompt_type, sử dụng prompt tương ứng
        if request.prompt_type and request.prompt_type in PROMPT_TYPES:
            system_prompt = PROMPT_TYPES[request.prompt_type]
            # Cập nhật cấu hình phiên
            session_configs[session_id].system_prompt = system_prompt
            
            # Ghi log cập nhật system prompt
            Logger.info(
                "System prompt updated from type",
                session_id=session_id,
                prompt_type=request.prompt_type
            )
        
        # Nếu có system_prompt tùy chỉnh, sử dụng nó
        elif request.system_prompt:
            system_prompt = request.system_prompt
            # Cập nhật cấu hình phiên
            session_configs[session_id].system_prompt = system_prompt
            
            # Ghi log cập nhật system prompt
            Logger.info(
                "System prompt updated from custom",
                session_id=session_id,
                prompt_length=len(system_prompt)
            )
        # Nếu không, sử dụng system prompt từ cấu hình phiên
        else:
            system_prompt = session_configs[session_id].system_prompt
        
        # Lấy lịch sử hội thoại
        history = conversation_history[session_id]
        
        # Thêm tin nhắn mới vào lịch sử
        for message in request.messages:
            if message not in history:
                history.append(message)
        
        # Ghi log yêu cầu chat
        Logger.info(
            "Chat request",
            session_id=session_id,
            message_count=len(request.messages)
        )
        
        # Tạo phản hồi từ Claude
        response = await ClaudeAgent.generate_response(history, system_prompt)
        
        # Thêm phản hồi vào lịch sử
        history.append(Message(role="assistant", content=response))
        
        # Ghi log phản hồi chat
        Logger.info(
            "Chat response",
            session_id=session_id,
            response_length=len(response)
        )
        
        return ChatResponse(response=response, session_id=session_id)
    
    except Exception as e:
        error_msg = f"Error processing chat request: {e}"
        
        # Ghi log lỗi
        Logger.error(
            "Chat error",
            error=str(e)
        )
        
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Lấy lịch sử hội thoại cho một phiên làm việc cụ thể."""
    if session_id not in conversation_history:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    return {"session_id": session_id, "messages": conversation_history[session_id]}

@app.get("/prompts")
async def get_available_prompts():
    """Lấy danh sách các loại prompt có sẵn."""
    return {
        "prompt_types": list(PROMPT_TYPES.keys())
    }

@app.put("/sessions/{session_id}/system-prompt")
async def update_system_prompt(session_id: str, config: SessionConfig):
    """Cập nhật system prompt cho một phiên làm việc."""
    if session_id not in session_configs:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    # Cập nhật system prompt
    session_configs[session_id].system_prompt = config.system_prompt
    
    # Ghi log cập nhật system prompt
    Logger.info(
        "System prompt updated via API",
        session_id=session_id,
        prompt_length=len(config.system_prompt)
    )
    
    return {
        "status": "success",
        "message": "System prompt updated",
        "session_id": session_id
    }

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Xóa một phiên làm việc."""
    if session_id not in conversation_history:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    # Xóa phiên làm việc
    del conversation_history[session_id]
    
    # Xóa cấu hình phiên
    if session_id in session_configs:
        del session_configs[session_id]
    
    # Ghi log xóa phiên
    Logger.info(
        "Session deleted",
        session_id=session_id
    )
    
    return {
        "status": "success",
        "message": f"Session {session_id} deleted"
    }

@app.get("/health")
async def health_check():
    """Endpoint để kiểm tra sức khỏe của máy chủ."""
    return {"status": "healthy"}

# Điểm vào chương trình
# (Program entry point)
if __name__ == "__main__":
    # Chạy máy chủ Uvicorn
    # (Run Uvicorn server)
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
