# Facebook Scraper Unified MCP Server (HTTP with SSE)

MCP Server รวมสำหรับ scrape ทั้งโพสต์และคอมเมนต์จาก Facebook โดยใช้ Apify Actors ผ่าน HTTP with Server-Sent Events (SSE) transport

## คุณสมบัติ

- **Unified MCP Server** แบบ HTTP with SSE transport
- รองรับ **multiple client connections**
- **2 Tools ใน 1 Server**:
  - `scrape_facebook_posts` - Scrape โพสต์จาก Facebook pages
  - `scrape_facebook_comments` - Scrape คอมเมนต์จาก Facebook posts
- รองรับการกรองตามวันที่และ view options
- รองรับ input หลายรูปแบบ
- ใช้ Apify API สำหรับการ scraping
- Security features ตาม MCP spec

## Transport Architecture

### SSE Endpoints
- **SSE Endpoint**: `/sse` - สำหรับรับ messages จาก server
- **POST Endpoint**: `/messages?session_id={client_id}` - สำหรับส่ง messages ไป server
- **Health Check**: `/health` - ตรวจสอบสถานะ server
- **Root**: `/` - ข้อมูล server

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
conda activate facebook-scraper-unified-mcp-sse

# รัน server
python server.py
```

### วิธีที่ 2: ใช้ Virtual Environment

```bash
# สร้าง virtual environment
python -m venv facebook-scraper-unified-env

# Activate environment
source facebook-scraper-unified-env/bin/activate  # macOS/Linux
# หรือ facebook-scraper-unified-env\Scripts\activate  # Windows

# ติดตั้ง dependencies
pip install -r requirements.txt

# รัน server
python server.py
```

## การใช้งาน

### รัน Server

```bash
# Default: localhost:4000
python server.py

# Custom host/port
python server.py --host 127.0.0.1 --port 4000
```

### ทดสอบ Server

```bash
# ทดสอบ health check
curl http://localhost:4000/health

# ทดสอบ SSE connection
curl -N -H "Accept: text/event-stream" http://localhost:4000/sse
```

### การเชื่อมต่อกับ MCP Client

Server จะรันที่ `http://localhost:4000` และรองรับ MCP over HTTP with SSE

#### MCP Client Configuration Example:
```json
{
  "mcpServers": {
    "facebook-scraper-unified": {
      "transport": "sse", 
      "url": "http://localhost:4000/sse"
    }
  }
}
```

## Tools ที่มีให้ใช้

### 1. scrape_facebook_posts

Scrape โพสต์จาก Facebook pages

**Parameters:**
- `start_urls`: Facebook page URLs รองรับหลายรูปแบบ:
  - Single string: `"https://www.facebook.com/page"`
  - List of strings: `["https://www.facebook.com/page1", "https://www.facebook.com/page2"]`
  - List of dicts: `[{"url": "https://www.facebook.com/page"}]`
- `results_limit`: จำนวนโพสต์สูงสุด (1-1000, default: 20)
- `caption_text`: รวม caption text หรือไม่ (default: False)
- `only_posts_newer_than`: กรองโพสต์ใหม่กว่าวันที่นี้ (ISO format)
- `only_posts_older_than`: กรองโพสต์เก่ากว่าวันที่นี้ (ISO format)

### 2. scrape_facebook_comments

Scrape คอมเมนต์จาก Facebook posts

**Parameters:**
- `start_urls`: Facebook post URLs รองรับหลายรูปแบบ:
  - Single string: `"https://www.facebook.com/page/posts/id"`
  - List of strings: `["https://www.facebook.com/page/posts/id1", "https://www.facebook.com/page/posts/id2"]`
  - List of dicts: `[{"url": "https://www.facebook.com/page/posts/id"}]`
- `results_limit`: จำนวนคอมเมนต์สูงสุด (1-1000, default: 50)
- `include_nested_comments`: รวม nested comments หรือไม่ (default: False)
- `view_option`: รูปแบบการดูคอมเมนต์ (default: "RANKED_UNFILTERED")
  - `"RANKED_UNFILTERED"`: แสดงทุกคอมเมนต์ตามลำดับความสำคัญ
  - `"TOP"`: แสดงเฉพาะคอมเมนต์ยอดนิยม
  - `"MOST_RECENT"`: แสดงตามลำดับเวลาล่าสุด

## Server Configuration

### Environment Variables
```bash
HOST=127.0.0.1          # Server host (default: 127.0.0.1)
PORT=4000               # Server port (default: 4000)
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

### Message Endpoint
```
POST /messages?session_id={client_id}
Content-Type: application/json
Body: MCP JSON-RPC message
```

### Health Check
```
GET /health
Response: {
  "status": "healthy",
  "transport": "sse", 
  "tools": ["scrape_facebook_posts", "scrape_facebook_comments"]
}
```

## Message Flow

1. Client เชื่อมต่อไปที่ SSE endpoint (`/sse`)
2. Server ส่ง `endpoint` event พร้อม message URI
3. Client ส่ง MCP messages ผ่าน HTTP POST ไปที่ message URI
4. Server ส่ง responses กลับผ่าน SSE `message` events

## ข้อมูลที่ได้กลับมา

### Posts Response
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
    "status": "SUCCEEDED"
  },
  "inputUrls": ["https://www.facebook.com/NationTV/"]
}
```

### Comments Response
```json
{
  "success": true,
  "totalResults": 25,
  "data": [
    {
      "id": "...",
      "author": {...},
      "text": "...",
      "reactions": {...},
      "replies": [...]
    }
  ],
  "runInfo": {
    "actorRunId": "...",
    "status": "SUCCEEDED"
  },
  "inputUrls": ["https://www.facebook.com/page/posts/id"]
}
```

## การทดสอบ

### ทดสอบ MCP Client
```bash
python client_test.py
```

### ทดสอบ Functions โดยตรง
```bash
python test_direct.py
```

## การแก้ปัญหา

### Connection Issues
- ตรวจสอบว่า server รันอยู่ที่ port 4000
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
facebook-scraper-unified-mcp-sse/
├── server.py              # Unified MCP Server แบบ HTTP with SSE
├── client_test.py         # ทดสอบ client connection
├── test_direct.py         # ทดสอบ functions โดยตรง
├── environment.yml        # Conda environment config
├── requirements.txt       # Python dependencies
└── README.md             # คู่มือนี้
```

## Workflow Example

```python
# 1. Scrape posts from a page
posts_result = await client.call_tool("scrape_facebook_posts", {
    "start_urls": "https://www.facebook.com/NationTV/",
    "results_limit": 10
})

# 2. Extract post URLs from results
post_urls = [post['url'] for post in posts_result['data']]

# 3. Scrape comments from those posts
comments_result = await client.call_tool("scrape_facebook_comments", {
    "start_urls": post_urls,
    "results_limit": 50,
    "include_nested_comments": True
})
```

---

**Transport**: HTTP with Server-Sent Events (SSE)  
**Protocol**: MCP 2024-11-05  
**เวอร์ชัน**: 1.0.0  
**Port**: 4000 (default)  
**รองรับ**: Multiple MCP clients, Web browsers, HTTP tools  
**ทดสอบแล้ว**: ✅ Local connections ✅ Multiple clients ✅ Unified tools

## ข้อจำกัดและการปรับแก้สำหรับ n8n Compatibility

### ปัญหาที่พบ: n8n MCP Client Schema Limitations

**ปัญหาหลัก**: n8n MCP Client ตัด JSON schema fields สำคัญออกก่อนส่งให้ Agent

**Fields ที่หายไป**:
- `"required": ["start_urls"]` - Agent ไม่รู้ว่า parameter ไหนจำเป็น
- `"default"` values - Agent ไม่รู้ค่า default ของแต่ละ parameter
- `"minimum"`, `"maximum"` constraints - ไม่มีการ validate ขอบเขต
- `"enum"` arrays - Agent ไม่รู้ valid options สำหรับ `view_option`
- `"anyOf"` complex schemas - รองรับแค่ simple types
- `"format"` specifications - ไม่มี date-time validation

### การแก้ไขที่ทำไปแล้ว

#### 1. Schema Simplification
```diff
- "anyOf": [{"type": "string"}, {"type": "array"}]  # ซับซ้อน
+ "type": "string"                                    # เรียบง่าย
```

#### 2. Description Enhancement
```diff
- "description": "Facebook page URLs"
+ "description": "Facebook page URLs (REQUIRED) - Example: https://www.facebook.com/pagename"
```

#### 3. Embedded Schema Information
```diff
- "description": "Maximum posts (1-1000)"
+ "description": "Maximum posts (1-1000), default: 20"

- "description": "Comment sort option"
+ "description": "Comment sort option: RANKED_UNFILTERED, TOP, or MOST_RECENT (default: RANKED_UNFILTERED)"
```

#### 4. Response Size Optimization
**เหตุผล**: n8n Agent ไม่สามารถ parse large JSON responses ได้

**Posts Response** - จำกัดขนาด:
```diff
- "data": [full_post_objects]           # 100KB+ per post
+ "posts": [essential_fields_only]      # <10KB total
```

**Comments Response** - จำกัดขนาด:
```diff
- "data": [full_comment_objects]        # 50KB+ per comment  
+ "comments": [essential_fields_only]   # <5KB total
```

**Truncated Fields**:
- `text`: จำกัด 200 chars สำหรับ posts, 100 chars สำหรับ comments
- `posts`: จำกัดสูงสุด 5 posts ใน response
- `comments`: จำกัดสูงสุด 10 comments ใน response

### ข้อจำกัดที่ยังคงมีอยู่

#### 1. Schema Validation
- **ไม่มี automatic validation** สำหรับ parameter types
- **ไม่มี enum enforcement** - Agent อาจส่ง invalid `view_option`
- **ไม่มี required field validation** - ต้องพึ่งพา description hints

#### 2. Response Data Limitations
- **ข้อมูลถูกตัดทอน** - เหลือแค่ fields สำคัญ
- **จำนวน items จำกัด** - ไม่ได้ข้อมูลครบทั้งหมดจาก Apify
- **Text truncation** - เนื้อหายาวๆ จะถูกตัด

#### 3. Error Handling
- **Limited error details** - error messages อาจไม่ละเอียด
- **No parameter suggestions** - ไม่มี auto-complete หรือ hints

### วิธีใช้งานที่แนะนำ

#### สำหรับ Full Data Access:
```bash
# ใช้ client_test.py เพื่อดูข้อมูลครบถ้วน
python client_test.py
```

#### สำหรับ Production Use:
- ใช้ **individual MCP servers** (facebook-scraper-mcp-sse, facebook-comments-scraper-mcp-sse)
- หรือใช้ **Claude Desktop** ที่รองรับ full MCP schema

#### Parameter Best Practices:
```javascript
// ✅ ใช้ complete URLs
"start_urls": "https://www.facebook.com/pagename"

// ✅ ระบุ view_option อย่างชัดเจน
"view_option": "RANKED_UNFILTERED"  // หรือ "TOP", "MOST_RECENT"

// ✅ จำกัด results_limit ให้เหมาะสม
"results_limit": 20  // สำหรับ posts
"results_limit": 50  // สำหรับ comments
```

### การทดสอบ Compatibility

#### n8n Testing:
1. ทดสอบใน n8n workflow ด้วย Agent node
2. ตรวจสอบว่า tools ถูกเรียกได้
3. ตรวจสอบ response parsing

#### Direct Testing:
```bash
# ทดสอบ full schema (ไม่ผ่าน n8n)
python client_test.py

# เปรียบเทียบ responses
curl -X POST http://localhost:4000/... # manual test
```

### Migration Path

**จาก Individual Servers → Unified Server**:
- ✅ Schema compatibility maintained
- ⚠️ Response format เปลี่ยน (truncated)
- ⚠️ n8n limitations ใหม่

**กลับไป Individual Servers**:
- หาก n8n compatibility ไม่สำคัญ
- หากต้องการ full data access
- หากต้องการ complete schema validation

---

**หมายเหตุ**: ข้อจำกัดเหล่านี้เป็นผลมาจาก n8n MCP Client implementation ไม่ใช่ MCP Server เรา ใน MCP clients อื่นๆ (เช่น Claude Desktop) จะได้ schema และ data แบบครบถ้วน
