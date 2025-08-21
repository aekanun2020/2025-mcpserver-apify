# Facebook Scraper MCP Server (Python) - Final Version

MCP Server สำหรับ scrape โพสต์จาก Facebook โดยใช้ Apify Actor `facebook-posts-scraper`

## คุณสมบัติ

- Scrape โพสต์จาก Facebook pages
- รองรับการกรองตามวันที่
- สามารถกำหนดจำนวนผลลัพธ์ที่ต้องการ
- รองรับ caption text
- ใช้ Apify API สำหรับการ scraping
- ใช้ FastMCP สำหรับความง่ายในการพัฒนา
- **รองรับ input หลายรูปแบบ** - ใช้งานได้ทั้งใน Claude Desktop และ Langflow

## การติดตั้ง

### วิธีที่ 1: ใช้ Conda (แนะนำ)

```bash
# สร้าง environment ใหม่
conda env create -f environment.yml

# Activate environment
conda activate facebook-scraper-mcp

# ทดสอบการทำงาน
python test_flexible.py
```

### วิธีที่ 2: ใช้ Virtual Environment

```bash
# สร้าง virtual environment
python -m venv facebook-scraper-env

# Activate environment
source facebook-scraper-env/bin/activate  # macOS/Linux
# หรือ facebook-scraper-env\Scripts\activate  # Windows

# ติดตั้ง dependencies
pip install -r requirements.txt

# ทดสอบการทำงาน
python test_flexible.py
```

## การใช้งาน

### ทดสอบ server
```bash
python server.py
```

### ใช้กับ Claude Desktop

**สำหรับ Conda environment:**
```json
{
  "mcpServers": {
    "facebook-scraper": {
      "command": "/path/to/conda/envs/facebook-scraper-mcp/bin/python",
      "args": ["/path/to/facebook-scraper-mcp-final/server.py"]
    }
  }
}
```

**สำหรับ Virtual environment:**
```json
{
  "mcpServers": {
    "facebook-scraper": {
      "command": "/path/to/facebook-scraper-env/bin/python",
      "args": ["/path/to/facebook-scraper-mcp-final/server.py"]
    }
  }
}
```

**เช็ค path ของ Python:**
```bash
# สำหรับ conda
conda activate facebook-scraper-mcp
which python

# สำหรับ venv  
source facebook-scraper-env/bin/activate
which python
```

### ใช้กับ Langflow

MCP Tool ใน Langflow สามารถใช้ได้โดยการส่ง string URL ธรรมดา เช่น:
```
"https://www.facebook.com/nationtv"
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

**ตัวอย่างการใช้ (Claude Desktop):**
```json
{
  "start_urls": [
    {
      "url": "https://www.facebook.com/NationTV/"
    }
  ],
  "results_limit": 20,
  "caption_text": false
}
```

**ตัวอย่างการใช้ (Langflow):**
```
start_urls: "https://www.facebook.com/NationTV/"
results_limit: 20
caption_text: false
```

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

## การตรวจสอบผลลัพธ์

### เช็คว่าได้ครบตามที่ขอหรือไม่
- `totalResults` vs `results_limit` ที่ส่งไป
- ถ้าได้น้อยกว่า อาจเป็นเพราะ:
  - Page มีโพสต์น้อยกว่าที่ขอ
  - Rate limiting จาก Facebook
  - Date filters ที่กำหนด
  - Posts visibility/privacy settings

### Status Codes
- `success: true` = scraping สำเร็จ
- `success: false` = มี error เกิดขึ้น
- `runInfo.status: "SUCCEEDED"` = Apify Actor ทำงานสำเร็จ

## ไฟล์ในโปรเจ็กต์

```
facebook-scraper-mcp-final/
├── server.py              # MCP Server หลัก (flexible input)
├── server_original.py     # MCP Server เดิม (backup)
├── environment.yml         # Conda environment config
├── requirements.txt        # Python dependencies
├── test_server.py         # ทดสอบแบบเดิม
├── test_flexible.py       # ทดสอบ input หลายรูปแบบ
└── README.md              # คู่มือนี้
```

## การแก้ปัญหา

### Langflow Validation Error
ถ้าเจอ error `Input should be a valid string` หรือ `Input should be a valid dictionary`:
- ตรวจสอบว่าใช้ `server.py` (ไม่ใช่ `server_original.py`)
- Parameter type เป็น `Any` แล้วควรทำงานได้

### Claude Desktop ไม่แสดง Tool
- ตรวจสอบ path ใน config ให้ถูกต้อง
- Restart Claude Desktop หลังแก้ config
- เช็ค logs: `tail -f ~/Library/Logs/Claude/mcp*.log`

### Results ไม่ครบ
- เช็ค `totalResults` ใน response
- ลองเพิ่ม `results_limit`
- ตรวจสอบ date filters
- บาง Facebook pages อาจมีโพสต์น้อย

## การติดตั้งและใช้งาน

### วิธีที่ 1: ใช้ Conda (แนะนำ)

1. **สร้าง Conda Environment:**
   ```bash
   cd /Users/grizzlymacbookpro/Desktop/test/2025-08-14/facebook-scraper-mcp-final
   conda env create -f environment.yml
   conda activate facebook-scraper-mcp
   ```

2. **ทดสอบ:**
   ```bash
   python test_flexible.py
   ```

3. **เช็ค Python path สำหรับ Claude Desktop:**
   ```bash
   which python
   # คัดลอก path นี้ไปใส่ใน config
   ```

### วิธีที่ 2: ใช้ Virtual Environment

1. **สร้าง Virtual Environment:**
   ```bash
   cd /Users/grizzlymacbookpro/Desktop/test/2025-08-14/facebook-scraper-mcp-final
   python -m venv facebook-scraper-env
   source facebook-scraper-env/bin/activate
   pip install -r requirements.txt
   ```

2. **ทดสอบ:**
   ```bash
   python test_flexible.py
   ```

## API Configuration

```python
APIFY_TOKEN = "apify_api_xZVA6BjhUebdeKplts2cPb7zvmpGXU1oA4rb"
FACEBOOK_SCRAPER_ACTOR = "apify/facebook-posts-scraper"
```

## Dependencies

- Python 3.10+
- mcp >= 1.2.0
- apify-client >= 1.8.0
- httpx >= 0.24.0

---

**เวอร์ชัน:** Final (Flexible Input Support)
**อัปเดต:** 2025-01-15
**รองรับ:** Claude Desktop, Langflow, และ MCP clients อื่นๆ
**ทดสอบแล้ว:** ✅ Claude Desktop ✅ Langflow
