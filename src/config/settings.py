"""
Cấu hình cho ứng dụng Claude Agent.

File này chứa các cài đặt và cấu hình cho ứng dụng,
bao gồm các biến môi trường và cài đặt mặc định.
"""

import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
# (Load environment variables from .env file)
load_dotenv()

# API Keys và tokens
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LOGFIRE_TOKEN = os.getenv("LOGFIRE_TOKEN")

# Cấu hình Claude
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "anthropic:claude-3-7-sonnet-20250219")

# Cấu hình API Server
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_TITLE = "Claude Agent API"
API_DESCRIPTION = "API server for Claude 3.7 agent"
API_VERSION = "1.0.0"

# Cấu hình CORS
CORS_ORIGINS = ["*"]  # Trong môi trường sản xuất, hãy giới hạn điều này
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# Cấu hình Logfire
LOGFIRE_SERVICE_NAME = "claude-agent-api"
