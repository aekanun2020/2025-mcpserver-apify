# Facebook Scraper MCP Server (Python)

MCP Server สำหรับ scrape โพสต์จาก Facebook โดยใช้ Apify Actor `facebook-posts-scraper`

## คุณสมบัติ

- Scrape โพสต์จาก Facebook pages
- รองรับการกรองตามวันที่
- สามารถกำหนดจำนวนผลลัพธ์ที่ต้องการ
- รองรับ caption text
- ใช้ Apify API สำหรับการ scraping
- ใช้ FastMCP สำหรับความง่ายในการพัฒนา

## การติดตั้งด้วย Conda

### สร้าง environment ใหม่
```bash
conda env create -f environment.yml
conda activate facebook-scraper-mcp
```

### หรือติดตั้งใน environment ที่มีอยู่
```bash
conda activate your-env
pip install -r requirements.txt
```

## การใช้งาน

### ทดสอบ server
```bash
python server.py
```

### ใช้กับ Claude Desktop

เพิ่มใน `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "facebook-scraper": {
      "command": "python",
      "args": ["/Users/grizzlystudio/apify-mcp/facebook-scraper-mcp-python/server.py"],
      "env": {
        "CONDA_DEFAULT_ENV": "facebook-scraper-mcp"
      }
    }
  }
}
```

หรือใช้ conda environment โดยตรง:
```json
{
  "mcpServers": {
    "facebook-scraper": {
      "command": "/path/to/conda/envs/facebook-scraper-mcp/bin/python",
      "args": ["/Users/grizzlystudio/apify-mcp/facebook-scraper-mcp-python/server.py"]
    }
  }
}
```

## Tool ที่มีให้ใช้

### scrape_facebook_posts

Scrape โพสต์จาก Facebook pages

**Parameters:**
- `start_urls`: List ของ dictionaries ที่มี 'url' key สำหรับ Facebook page URLs
- `results_limit`: จำนวนโพสต์สูงสุด (1-1000, default: 20)
- `caption_text`: รวม caption text หรือไม่ (default: False)
- `only_posts_newer_than`: กรองโพสต์ใหม่กว่าวันที่นี้ (ISO format)
- `only_posts_older_than`: กรองโพสต์เก่ากว่าวันที่นี้ (ISO format)

**ตัวอย่างการใช้:**
```python
{
  "start_urls": [
    {
      "url": "https://www.facebook.com/NationTV/"
    }
  ],
  "results_limit": 20,
  "caption_text": False
}
```

## การตั้งค่า

API Token ถูกตั้งค่าไว้ในโค้ดแล้ว สำหรับการใช้งานจริงควรใช้ environment variable:

```bash
export APIFY_TOKEN="your_token_here"
```

## Dependencies

- Python 3.11+
- mcp >= 1.2.0
- apify-client >= 1.8.0
- httpx >= 0.24.0

## โครงสร้างโปรเจ็กต์

```
facebook-scraper-mcp-python/
├── server.py              # MCP Server หลัก
├── environment.yml         # Conda environment config
├── requirements.txt        # Python dependencies
└── README.md              # คู่มือนี้
```
