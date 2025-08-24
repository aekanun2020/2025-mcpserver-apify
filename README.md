# 2025-mcpserver-apify

## คอมพิวเตอร์ที่จะนำมาใช้ทำ lab

1. CPU ไม่น้อยกว่า 2 core และ RAM ไม่น้อยกว่า 8 GB

2. มี disk เหลืออยู่ไม่น้อยกว่า 200 GB

3. มีซอฟต์แวร์ Docker Desktop ที่พร้อมใช้งานได้ (เหมาะที่สุดกับการเรียนคือ version 4.44.x)

4. มีซอฟต์แวร์ conda ที่พร้อมใช้งานได้ (เหมาะที่สุดกับการเรียนคือ version 24.9.x)

5. ไม่มีการปิดกั้นการใช้งานเครื่องและเครือข่ายใดๆ เลย (เครื่องสำนักงาน ไม่ควรนำมาใช้เรียน เพราะอาจมีการปิดกั้นต่างๆ ไว้)

6. ควรเตรียม internet ที่แชร์ hotspot ผ่านมือถือ มาสำรองไว้ เผื่อเกิดปัญหาเน็ตช้าหรืออื่นๆ

7. อาจมีการแจ้งเพิ่มอีกครั้งก่อนวันเรียน 3 วันครับผม

## การเตรียม lab (ทำใน class เรียน)

### 1. รันคำสั่ง Docker

```bash
docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n -e N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true docker.n8n.io/n8nio/n8n:1.90.2
```

### 2. สร้าง credential ใน n8n

#### 2.1 MCP Client (STDIO) for native mcp server apify
- **ชื่อ:** MCP Client (STDIO) for native mcp server apify
- **Command:** `npx`
- **Arguments:** `-y @apify/actors-mcp-server --actors apify/facebook-posts-scraper,apify/facebook-comments-scraper`
- **Environments:** `APIFY_TOKEN=xxxxxxx`
- **ดูวีดีโอการทำ:** https://video.aekanun.com/FhrF8NGF

#### 2.2 OpenAI account
- **ชื่อ:** OpenAi account
- **API Key:** `xxxxxxx`
- **Base URL:** `https://openrouter.ai/api/v1`
- **ดูวีดีโอการทำ:** https://video.aekanun.com/XcTf47pX

#### 2.3 MongoDB with local container

**รันคำสั่งสร้าง MongoDB container:**

```bash
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password123 \
  mongo:latest
```

**Connection String:**
```
mongodb://admin:password123@host.docker.internal:27017/admin?authSource=admin
```

**Configuration:**
- **Configuration Type:** Connection String
- **Connection String:** (ตามด้านบน)
- **Database:** admin
- **Use TLS:** ปิด

#### 2.4 Airtable Personal Access Token account
- **ชื่อ:** Airtable Personal Access Token account
- **Access Token:** `xxxxxxx`
- **หมายเหตุ:** Make sure you enabled the following scopes for your token:
  - `data.records:read`
  - `data.records:write`
  - `schema.bases:read`