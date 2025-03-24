"""
Tiện ích ghi log cho ứng dụng Claude Agent.

File này cung cấp các hàm và lớp để ghi log sử dụng Logfire,
giúp theo dõi và gỡ lỗi ứng dụng.
"""

import logfire
from src.config.settings import LOGFIRE_TOKEN, LOGFIRE_SERVICE_NAME

class Logger:
    """Lớp Logger để ghi log với Logfire."""
    
    @staticmethod
    def setup():
        """Cấu hình Logfire."""
        if LOGFIRE_TOKEN:
            try:
                logfire.configure(token=LOGFIRE_TOKEN)
                print(f"Logfire configured with token: {LOGFIRE_TOKEN[:5]}...{LOGFIRE_TOKEN[-5:]}")
                
                # Kiểm tra kết nối Logfire
                logfire.info("Application started", service=LOGFIRE_SERVICE_NAME)
                return True
            except Exception as e:
                print(f"Error configuring Logfire: {e}")
                print("Logging will be disabled")
                return False
        else:
            print("Warning: LOGFIRE_TOKEN not found in environment variables")
            return False
    
    @staticmethod
    def info(message, **kwargs):
        """Ghi log thông tin."""
        if LOGFIRE_TOKEN:
            try:
                logfire.info(message, service=LOGFIRE_SERVICE_NAME, **kwargs)
            except Exception as e:
                print(f"Error logging to Logfire: {e}")
    
    @staticmethod
    def error(message, **kwargs):
        """Ghi log lỗi."""
        if LOGFIRE_TOKEN:
            try:
                logfire.error(message, service=LOGFIRE_SERVICE_NAME, **kwargs)
            except Exception as e:
                print(f"Error logging to Logfire: {e}")
    
    @staticmethod
    def warning(message, **kwargs):
        """Ghi log cảnh báo."""
        if LOGFIRE_TOKEN:
            try:
                logfire.warning(message, service=LOGFIRE_SERVICE_NAME, **kwargs)
            except Exception as e:
                print(f"Error logging to Logfire: {e}")
    
    @staticmethod
    def debug(message, **kwargs):
        """Ghi log gỡ lỗi."""
        if LOGFIRE_TOKEN:
            try:
                logfire.debug(message, service=LOGFIRE_SERVICE_NAME, **kwargs)
            except Exception as e:
                print(f"Error logging to Logfire: {e}")
