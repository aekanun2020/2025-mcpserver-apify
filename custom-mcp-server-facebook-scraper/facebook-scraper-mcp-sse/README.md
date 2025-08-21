# Facebook Scraper MCP Server (HTTP with SSE) 

MCP Server สำหรับ scrape โพสต์จาก Facebook โดยใช้ Apify Actor `facebook-posts-scraper` ผ่าน HTTP with Server-Sent Events (SSE) transport

## คุณสมบัติ

- MCP Server แบบ HTTP with SSE transport
- รองรับ multiple client connections
- Scrape โพสต์จาก Facebook pages
- รองรับการกรองตามวันที่
- สามารถกำหนดจำนวนผลลัพธ์ที่ต้องการ
- รองรับ caption text
- ใช้ Apify API สำหรับการ scraping
- รองรับ input หลายรูปแบบ
- Security features ตาม MCP spec

## Transport Architecture

### SSE Endpoints
- **SSE Endpoint**: `/sse` - สำหรับรับ messages จาก server
- **POST Endpoint**: `/message/{client_id}` - สำหรับส่ง messages ไป server
- **Health Check**: `/health` - ตรวจสอบสถานะ server

### Security Features
- Origin header validation
- Localhost binding (127.0.0.1)
- Client authentication support
- CORS configuration

## การติดตั้ง

### วิธีที่ 1: ใช้ Conda (แนะนำ)

```bash
# สร้าง environment ใหม่
conda env create -f environment.yml

# Activate environment
conda activate facebook-scraper-mcp-sse

# รัน server
python server.py
```

### วิธีที่ 2: ใช้ Virtual Environment

```bash
# สร้าง virtual environment
python -m venv facebook-scraper-sse-env

# Activate environment
source facebook-scraper-sse-env/bin/activate  # macOS/Linux
# หรือ facebook-scraper-sse-env\Scripts\activate  # Windows

# ติดตั้ง dependencies
pip install -r requirements.txt

# รัน server
python server.py
```

## การใช้งาน

### รัน Server

```bash
# Default: localhost:8000
python server.py

# Custom host/port
python server.py --host 127.0.0.1 --port 8080
```

### ทดสอบ Server

```bash
# ทดสอบ health check
curl http://localhost:8000/health

# ทดสอบ SSE connection
curl -N -H "Accept: text/event-stream" http://localhost:8000/sse
```

### การเชื่อมต่อกับ MCP Client

Server จะรันที่ `http://localhost:8000` และรองรับ MCP over HTTP with SSE

#### MCP Client Configuration Example:
```json
{
  "mcpServers": {
    "facebook-scraper-sse": {
      "transport": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## Tool ที่มีให้ใช้

### scrape_facebook_posts

Scrape โพสต์จาก Facebook pages

**Parameters:**
- `start_urls`: Facebook page URLs รองรับหลายรูปแบบ:
  - Single string: `"https://www.facebook.com/page"`
  - List of strings: `["https://www.facebook.com/page1", "https://www.facebook.com/page2"]`
  - List of dicts: `[{"url": "https://www.facebook.com/page"}]`
  - Mixed format: `["https://www.facebook.com/page1", {"url": "https://www.facebook.com/page2"}]`
- `results_limit`: จำนวนโพสต์สูงสุด (1-1000, default: 20)
- `caption_text`: รวม caption text หรือไม่ (default: False)
- `only_posts_newer_than`: กรองโพสต์ใหม่กว่าวันที่นี้ (ISO format)
- `only_posts_older_than`: กรองโพสต์เก่ากว่าวันที่นี้ (ISO format)

## Server Configuration

### Environment Variables
```bash
HOST=127.0.0.1          # Server host (default: 127.0.0.1)
PORT=8000               # Server port (default: 8000)
ALLOWED_ORIGINS=*       # Allowed origins for CORS
LOG_LEVEL=info          # Logging level
```

### Security Settings
- Server binds only to localhost (127.0.0.1) by default
- Origin header validation enabled
- CORS configured for security
- Client authentication ready (can be extended)

## API Endpoints

### SSE Endpoint
```
GET /sse
Headers: Accept: text/event-stream
```

เมื่อเชื่อมต่อสำเร็จ server จะส่ง `endpoint` event:
```
event: endpoint
data: {"uri": "/message/{client_id}"}
```

### Message Endpoint
```
POST /message/{client_id}
Content-Type: application/json
Body: MCP JSON-RPC message
```

### Health Check
```
GET /health
Response: {"status": "healthy", "transport": "sse"}
```

## Message Flow

1. Client เชื่อมต่อไปที่ SSE endpoint (`/sse`)
2. Server ส่ง `endpoint` event พร้อม message URI
3. Client ส่ง MCP messages ผ่าน HTTP POST ไปที่ message URI
4. Server ส่ง responses กลับผ่าน SSE `message` events

## ข้อมูลที่ได้กลับมา

```json
{
  "success": true,
  "totalResults": 15,
  "data": [
    {
      "media": [...],
      "id": "...",
      "owner": {...},
      "...": "..."
    }
  ],
  "runInfo": {
    "actorRunId": "...",
    "status": "SUCCEEDED",
    "startedAt": "2025-01-15T10:00:00Z",
    "finishedAt": "2025-01-15T10:02:30Z"
  },
  "inputUrls": ["https://www.facebook.com/NationTV/"]
}
```

## การแก้ปัญหา

### Connection Issues
- ตรวจสอบว่า server รันอยู่ที่ port ที่ถูกต้อง
- เช็ค firewall settings
- ตรวจสอบ CORS configuration

### SSE Connection Problems
- ตรวจสอบ `Accept: text/event-stream` header
- เช็ค Origin header ถ้าเปิด validation

### Tool ไม่ทำงาน
- ตรวจสอบ Apify API token
- เช็ค network connectivity
- ดู server logs สำหรับ error details

## Dependencies

- Python 3.10+
- mcp >= 1.2.0
- apify-client >= 1.8.0
- httpx >= 0.24.0
- fastapi >= 0.104.0
- uvicorn >= 0.24.0
- sse-starlette >= 1.6.0

## ไฟล์ในโปรเจ็กต์

```
facebook-scraper-mcp-sse/
├── server.py              # MCP Server แบบ HTTP with SSE
├── client_test.py         # ทดสอบ client connection
├── environment.yml        # Conda environment config
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # คู่มือนี้
```

---

**Transport**: HTTP with Server-Sent Events (SSE)
**Protocol**: MCP 2024-11-05
**เวอร์ชัน**: 1.0.0
**อัปเดต**: 2025-08-19
**รองรับ**: Multiple MCP clients, Web browsers, HTTP tools
**ทดสอบแล้ว**: ✅ Local connections ✅ Multiple clients
