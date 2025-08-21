#!/usr/bin/env python3

"""
Test client for Facebook Scraper Unified MCP Server (SSE)
ทดสอบการเชื่อมต่อและการทำงานของ unified MCP server
"""

import asyncio
import json
import logging
from typing import Optional
import httpx
import time

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPSSEClient:
    """MCP Client for HTTP with SSE transport"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:4000"):
        self.base_url = base_url
        self.sse_url = f"{base_url}/sse"
        self.client_id: Optional[str] = None
        self.message_url: Optional[str] = None
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.sse_task: Optional[asyncio.Task] = None
        self.current_event = None
        self.response_queue: asyncio.Queue = asyncio.Queue()
        
    async def connect(self):
        """เชื่อมต่อกับ SSE endpoint และเริ่ม listening loop"""
        logger.info(f"Connecting to SSE endpoint: {self.sse_url}")
        
        try:
            # Start SSE listener task
            self.sse_task = asyncio.create_task(self._sse_listener())
            
            # Wait for endpoint event
            await asyncio.sleep(0.5)
            
            if not self.message_url:
                raise Exception("Failed to receive endpoint event")
                
            logger.info(f"✅ Connected successfully")
            logger.info(f"🆔 Client ID: {self.client_id}")
            logger.info(f"📡 Message URL: {self.message_url}")
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            raise
    
    async def _sse_listener(self):
        """ฟัง SSE events จาก server"""
        try:
            headers = {"Accept": "text/event-stream", "Cache-Control": "no-cache"}
            
            async with self.http_client.stream("GET", self.sse_url, headers=headers) as response:
                if response.status_code != 200:
                    raise Exception(f"SSE connection failed: {response.status_code}")
                
                logger.info("✅ SSE connection established")
                
                buffer = ""
                async for chunk in response.aiter_text():
                    buffer += chunk
                    # Process complete lines
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        await self._process_sse_line(line)
                    
        except asyncio.CancelledError:
            logger.info("SSE listener cancelled")
        except Exception as e:
            logger.error(f"❌ SSE listener error: {e}")
    
    async def _process_sse_line(self, line: str):
        """ประมวลผล SSE event lines"""
        line = line.strip()
        if not line:
            return
            
        if line.startswith("event: "):
            self.current_event = line[7:]
        elif line.startswith("data: "):
            data_content = line[6:]
            await self._handle_event_data(data_content)
        elif line.startswith(": "):
            # Comment line (heartbeat)
            logger.debug("💓 Heartbeat received")
    
    async def _handle_event_data(self, data_content: str):
        """จัดการ event data ตาม event type"""
        try:
            if self.current_event == "endpoint":
                # data_content is the URI string directly
                self.message_url = f"{self.base_url}{data_content}"
                self.client_id = data_content.split('=')[-1]
                logger.info(f"📨 Received endpoint: {self.message_url}")
                    
            elif self.current_event == "message":
                # Handle MCP response
                data = json.loads(data_content)
                if "jsonrpc" in data:
                    logger.info(f"📨 Received MCP response: {data.get('id')}")
                    await self.response_queue.put(data)
                    
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse event data: {data_content[:100]}...")
    
    async def send_message(self, message: dict) -> dict:
        """ส่ง MCP message ไปยัง server และรอ response"""
        if not self.message_url:
            raise Exception("Not connected - call connect() first")
        
        logger.info(f"📤 Sending message: {message.get('method', 'unknown')}")
        
        try:
            # Send HTTP POST
            response = await self.http_client.post(
                self.message_url,
                json=message,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to send message: {response.status_code} - {response.text}")
            
            logger.info("✅ Message sent successfully")
            
            # Wait for response via SSE
            try:
                mcp_response = await asyncio.wait_for(self.response_queue.get(), timeout=120.0)
                return mcp_response
            except asyncio.TimeoutError:
                logger.error("⏰ Timeout waiting for response (120s)")
                return None
            
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            raise
    
    async def initialize(self) -> dict:
        """ส่ง initialize request"""
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "mcp-unified-test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        return await self.send_message(message)
    
    async def list_tools(self) -> dict:
        """ขอรายการ tools ที่มี"""
        message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        return await self.send_message(message)
    
    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """เรียกใช้ tool"""
        message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        logger.info(f"📤 Sending {tool_name} request (this may take up to 2 minutes...)")
        
        try:
            response = await self.http_client.post(
                self.message_url,
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=180.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to send message: {response.status_code} - {response.text}")
            
            logger.info("✅ Message sent successfully")
            
            try:
                mcp_response = await asyncio.wait_for(self.response_queue.get(), timeout=150.0)
                return mcp_response
            except asyncio.TimeoutError:
                logger.error("⏰ Timeout waiting for tool response (150s)")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to call tool: {e}")
            raise
    
    async def close(self):
        """ปิดการเชื่อมต่อ"""
        if self.sse_task:
            self.sse_task.cancel()
            try:
                await self.sse_task
            except asyncio.CancelledError:
                pass
        
        await self.http_client.aclose()
        logger.info("🔌 Connection closed")

async def test_health_check():
    """ทดสอบ health check endpoint"""
    logger.info("🏥 Testing health check...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://127.0.0.1:4000/health")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Health check passed: {data}")
                return True
            else:
                logger.error(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return False

async def test_unified_workflow():
    """ทดสอบ unified MCP workflow"""
    client = MCPSSEClient()
    
    try:
        # 1. เชื่อมต่อ
        logger.info("🔗 Step 1: Connecting...")
        await client.connect()
        
        # 2. Initialize
        logger.info("🚀 Step 2: Initializing...")
        init_response = await client.initialize()
        if init_response:
            server_info = init_response.get('result', {}).get('serverInfo', {})
            logger.info(f"✅ Initialize successful: {server_info}")
        else:
            logger.error("❌ Initialize failed - no response")
            return
        
        # 3. List tools
        logger.info("🔧 Step 3: Listing tools...")
        tools_response = await client.list_tools()
        if tools_response and tools_response.get("result"):
            tools = tools_response["result"].get("tools", [])
            logger.info(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                logger.info(f"  - {tool['name']}: {tool['description']}")
        else:
            logger.error("❌ List tools failed")
            return
        
        # 4. Test Facebook posts scraper
        logger.info("📱 Step 4: Testing Facebook posts scraper...")
        posts_args = {
            "start_urls": "https://www.facebook.com/NationTV/",
            "results_limit": 2,
            "caption_text": False
        }
        
        posts_response = await client.call_tool("scrape_facebook_posts", posts_args)
        
        if posts_response and posts_response.get("result"):
            content = posts_response["result"].get("content", [])
            if content:
                result_text = content[0].get("text", "")
                try:
                    result_data = json.loads(result_text)
                    if result_data.get("success"):
                        logger.info(f"✅ Posts scraping successful!")
                        logger.info(f"   Total results: {result_data.get('totalResults', 0)}")
                    else:
                        logger.error(f"❌ Posts scraping failed: {result_data.get('error')}")
                except json.JSONDecodeError:
                    logger.error("❌ Invalid JSON response from posts scraper")
        
        # 5. Test Facebook comments scraper
        logger.info("💬 Step 5: Testing Facebook comments scraper...")
        comments_args = {
            "start_urls": "https://www.facebook.com/humansofnewyork/posts/pfbid0BbKbkisExKGSKuhee9a7i86RwRuMKFC8NSkKStB7CsM3uXJuAAfZLrkcJMXxhH4Yl",
            "results_limit": 3,
            "include_nested_comments": False
        }
        
        comments_response = await client.call_tool("scrape_facebook_comments", comments_args)
        
        if comments_response and comments_response.get("result"):
            content = comments_response["result"].get("content", [])
            if content:
                result_text = content[0].get("text", "")
                try:
                    result_data = json.loads(result_text)
                    if result_data.get("success"):
                        logger.info(f"✅ Comments scraping successful!")
                        logger.info(f"   Total results: {result_data.get('totalResults', 0)}")
                    else:
                        logger.error(f"❌ Comments scraping failed: {result_data.get('error')}")
                except json.JSONDecodeError:
                    logger.error("❌ Invalid JSON response from comments scraper")
        
        logger.info("🎉 Unified test completed!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
    finally:
        await client.close()

async def main():
    """Main test function"""
    print("""
🧪 Facebook Scraper Unified MCP Server (SSE) Test Client
========================================================
ทดสอบ unified server ที่รวม posts และ comments scraping
""")
    
    # 1. Test health check first
    if not await test_health_check():
        logger.error("❌ Server is not healthy - please start the server first")
        logger.info("💡 Run: python server.py")
        return
    
    print("\n" + "="*50)
    logger.info("Starting unified MCP workflow test...")
    await test_unified_workflow()
    
    print("\n" + "="*50)
    logger.info("All unified tests completed! 🎉")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️  Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
