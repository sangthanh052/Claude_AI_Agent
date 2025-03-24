# Claude 3.7 AI Agent API

## Giới thiệu (Introduction)

Dự án này tạo ra một API Server sử dụng Claude 3.7, PydanticAI, LangGraph, FastAPI và Logfire. API Server có khả năng xử lý yêu cầu chat từ người dùng, quản lý phiên hội thoại, và tạo ra phản hồi thông minh từ Claude 3.7.

This project creates an API Server using Claude 3.7, PydanticAI, FastAPI, and Logfire. The API server can process chat requests from users, manage conversation sessions, and generate intelligent responses from Claude 3.7.

## Cấu trúc dự án (Project Structure)

```
agent/
├── docs/                   # Tài liệu dự án
├── src/                    # Mã nguồn chính
│   ├── api/                # API server
│   │   ├── app.py          # Ứng dụng FastAPI chính
│   │   ├── agent.py        # Lớp ClaudeAgent để tương tác với Claude
│   │   └── models.py       # Các mô hình dữ liệu Pydantic
│   ├── agent/              # Các triển khai agent
│   │   ├── agent_core.py   # Triển khai nâng cao với LangGraph
│   │   └── simple_chat.py  # Triển khai đơn giản với PydanticAI
│   ├── config/             # Cấu hình ứng dụng
│   │   └── settings.py     # Cài đặt và biến môi trường
│   ├── prompts/            # System prompts
│   │   └── prompts.py      # Các system prompt khác nhau
│   └── utils/              # Tiện ích
│       └── logger.py       # Tiện ích ghi log với Logfire
├── tests/                  # Kiểm thử
├── .env                    # Biến môi trường (API keys)
├── main.py                 # Điểm vào chính của ứng dụng
└── requirements.txt        # Danh sách các thư viện cần thiết
```

## Cài đặt (Installation)

1. Clone dự án:

```bash
git clone https://github.com/cnguyen14/Claude_AI_Agent.git
cd agent
```

2. Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

3. Tạo file `.env` từ mẫu `.env.example`:

```bash
cp .env.example .env
```

4. Cập nhật các API key trong file `.env`:

```
# API key của Anthropic (Claude)
# Đăng ký tại: https://console.anthropic.com/
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# API token của Logfire
# Đăng ký tại: https://pydantic.dev/logfire
LOGFIRE_TOKEN=your_logfire_token_here

# Mô hình Claude (mặc định: claude-3-7-sonnet)
CLAUDE_MODEL=anthropic:claude-3-7-sonnet-20250219
```

5. (Tùy chọn) Cài đặt dự án như một package Python:

```bash
pip install -e .
```

## Sử dụng (Usage)

### Khởi động API Server

```bash
python main.py
```

Hoặc sử dụng Uvicorn trực tiếp:

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```

### Các Endpoint API

#### 1. Root Endpoint

- **URL**: `/`
- **Method**: `GET`
- **Mô tả**: Kiểm tra trạng thái của server
- **Response**: 
  ```json
  {
    "status": "online", 
    "message": "Claude Agent API is running"
  }
  ```

#### 2. Chat Endpoint

- **URL**: `/chat`
- **Method**: `POST`
- **Mô tả**: Gửi tin nhắn và nhận phản hồi từ Claude
- **Request Body**:
  ```json
  {
    "messages": [
      {
        "role": "user",
        "content": "Xin chào, bạn là ai?"
      }
    ]
  }
  ```
- **Response**:
  ```json
  {
    "response": "Xin chào! Tôi là Claude, một trợ lý AI...",
    "session_id": "session-uuid"
  }
  ```

#### 3. Health Check

- **URL**: `/health`
- **Method**: `GET`
- **Mô tả**: Kiểm tra sức khỏe của server
- **Response**:
  ```json
  {
    "status": "healthy"
  }
  ```

#### 4. Get Session

- **URL**: `/sessions/{session_id}`
- **Method**: `GET`
- **Mô tả**: Lấy lịch sử hội thoại cho một phiên làm việc
- **Response**:
  ```json
  {
    "session_id": "session-uuid",
    "messages": [
      {
        "role": "user",
        "content": "Xin chào"
      },
      {
        "role": "assistant",
        "content": "Xin chào! Tôi có thể giúp gì cho bạn?"
      }
    ]
  }
  ```

#### 5. Delete Session

- **URL**: `/sessions/{session_id}`
- **Method**: `DELETE`
- **Mô tả**: Xóa một phiên làm việc
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Session deleted"
  }
  ```

#### 6. Get Available Prompts

- **URL**: `/prompts`
- **Method**: `GET`
- **Mô tả**: Lấy danh sách các loại prompt có sẵn
- **Response**:
  ```json
  {
    "prompt_types": [
      "default",
      "programming",
      "writing",
      "education"
    ]
  }
  ```

### Ví dụ sử dụng API

#### Sử dụng với Python và requests (sử dụng trong folder tests)

```python
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
```

#### Sử dụng với cURL

```bash
# Kiểm tra trạng thái server
curl http://localhost:8000/

# Gửi yêu cầu chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Xin chào, bạn là ai?"}]
  }'

# Lấy danh sách các loại prompt có sẵn
curl http://localhost:8000/prompts

# Kiểm tra sức khỏe server
curl http://localhost:8000/health
```

#### Sử dụng với JavaScript/Fetch

```javascript
// URL của API server
const API_URL = "http://localhost:8000";

// Hàm gửi tin nhắn và nhận phản hồi
async function chatWithClaude(message, sessionId = null) {
  try {
    const payload = {
      messages: [{ role: 'user', content: message }]
    };
    
    // Thêm session_id nếu có
    if (sessionId) {
      payload.session_id = sessionId;
    }
    
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return {
      response: result.response,
      sessionId: result.session_id
    };
  } catch (error) {
    console.error('Error:', error);
    return { response: null, sessionId: null };
  }
}

// Sử dụng hàm
(async () => {
  const { response, sessionId } = await chatWithClaude('Xin chào, bạn là ai?');
  console.log(`Claude: ${response}`);
  
  // Tiếp tục hội thoại với cùng một session_id
  const followUp = await chatWithClaude('Bạn có thể giúp tôi viết một đoạn mã JavaScript để tính giai thừa không?', sessionId);
  console.log(`Claude: ${followUp.response}`);
})();
```

## Tính năng (Features)

- **API Server với FastAPI**: Cung cấp các endpoint RESTful để tương tác với Claude 3.7
- **Quản lý phiên hội thoại**: Lưu trữ và quản lý lịch sử hội thoại theo phiên
- **System prompts tùy chỉnh**: Hỗ trợ nhiều loại system prompt khác nhau
- **Ghi log với Logfire**: Ghi log tất cả các yêu cầu, phản hồi và lỗi
- **Xử lý lỗi**: Xử lý các trường hợp ngoại lệ để đảm bảo trải nghiệm người dùng mượt mà
- **CORS**: Hỗ trợ Cross-Origin Resource Sharing cho các ứng dụng web

## Giải thích kỹ thuật (Technical Explanation)

### FastAPI

FastAPI là một framework web hiện đại, nhanh chóng (dựa trên Starlette) cho việc xây dựng API với Python. Nó cung cấp:
- Xác thực và chuyển đổi dữ liệu tự động với Pydantic
- Tạo tài liệu API tự động (OpenAPI)
- Hiệu suất cao nhờ Starlette và Uvicorn

### PydanticAI

PydanticAI cung cấp một cách đơn giản để tương tác với các mô hình ngôn ngữ lớn như Claude. Nó cho phép chúng ta tạo ra các agent có thể gửi tin nhắn và nhận phản hồi từ mô hình.

### LangGraph

LangGraph là một framework cho phép xây dựng các ứng dụng AI phức tạp bằng cách định nghĩa các node và edge trong một đồ thị. Trong dự án này, chúng ta sử dụng LangGraph để quản lý trạng thái hội thoại.

### Logfire

Logfire được sử dụng để ghi log các cuộc hội thoại và API calls, giúp theo dõi và gỡ lỗi ứng dụng. Nó cung cấp một giao diện web để xem và phân tích log.

#### Cài đặt Logfire

Để sử dụng Logfire, bạn cần:

1. Tạo tài khoản tại [Pydantic Logfire](https://pydantic.dev/logfire)
2. Tạo một project mới và lấy API token
3. Thêm token vào file `.env` của bạn:
   ```
   LOGFIRE_TOKEN=your_logfire_token_here
   ```

Sau khi cấu hình, bạn có thể truy cập dashboard Logfire để xem tất cả log của ứng dụng tại URL được hiển thị khi khởi động server (thường là `https://logfire-us.pydantic.dev/your-username/your-project`).

## Phát triển (Development)

### Thêm System Prompt mới

Để thêm một system prompt mới:

1. Mở file `src/prompts/prompts.py`
2. Thêm biến mới với nội dung prompt
3. Cập nhật dictionary `PROMPT_TYPES` trong `src/api/app.py`

### Thêm Endpoint API mới

Để thêm một endpoint API mới:

1. Mở file `src/api/app.py`
2. Định nghĩa endpoint mới với decorator `@app.route()`
3. Cập nhật tài liệu API nếu cần

## Lưu ý (Notes)

- Đảm bảo rằng bạn có API key hợp lệ cho Anthropic và Logfire
  - API key của Anthropic có thể lấy từ [Console Anthropic](https://console.anthropic.com/)
  - API token của Logfire có thể lấy từ [Pydantic Logfire](https://pydantic.dev/logfire)
- Mô hình Claude 3.7 yêu cầu kết nối internet để hoạt động
- Các cuộc hội thoại hiện tại được lưu trữ trong bộ nhớ, không phải cơ sở dữ liệu
- Trong môi trường sản xuất, bạn nên giới hạn CORS và thêm xác thực
- File `.env` chứa API key nhạy cảm và đã được thêm vào `.gitignore` để không bị đẩy lên Git
- Luôn sử dụng `.env.example` làm mẫu và không bao giờ commit API key thật lên repository

## Đóng góp (Contributing)

Đóng góp và báo cáo lỗi luôn được chào đón. Vui lòng tạo issue hoặc pull request trên repository.
