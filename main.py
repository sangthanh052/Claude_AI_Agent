"""
File khởi động chính cho Claude Agent API.

File này khởi động FastAPI server và cấu hình Logfire.
"""

import uvicorn
from src.api.app import app
from src.utils.logger import Logger
from src.config.settings import API_HOST, API_PORT

if __name__ == "__main__":
    # Cấu hình Logfire
    Logger.setup()
    
    # Khởi động ứng dụng FastAPI
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT
    )
