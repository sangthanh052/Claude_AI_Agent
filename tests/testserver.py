import requests
import json

# URL của API server
API_URL = "http://localhost:8000"

# Gửi tin nhắn và nhận phản hồi
def chat_with_claude(message, session_id=None):
    url = f"{API_URL}/chat"
    
    # Chuẩn bị dữ liệu yêu cầu
    payload = {
        "messages": [{"role": "user", "content": message}]
    }
    
    # Thêm session_id nếu có
    if session_id:
        payload["session_id"] = session_id
    
    # Gửi yêu cầu POST
    response = requests.post(url, json=payload)
    
    # Kiểm tra phản hồi
    if response.status_code == 200:
        result = response.json()
        return result["response"], result["session_id"]
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None, None

# Sử dụng hàm
message = "Xin chào, bạn là ai?"
print("YOU: ", message)
response, session_id = chat_with_claude(message)
print(f"Claude: {response}")

# Tiếp tục hội thoại với cùng một session_id
follow_up = "Bạn có thể giúp tôi viết một đoạn mã Python để tính giai thừa không?"
print("YOU: ", follow_up)
response, _ = chat_with_claude(follow_up, session_id)
print(f"Claude: {response}")