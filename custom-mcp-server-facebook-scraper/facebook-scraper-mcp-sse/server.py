#!/usr/bin/env python3

import asyncio
import json
import uuid
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from apify_client import ApifyClient

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Apify configuration
APIFY_TOKEN = "apify_api_4fJpN0XFkUXbhKdd3khd6vqFxHJkiH3wLpRI"
FACEBOOK_SCRAPER_ACTOR = "apify/facebook-posts-scraper"

# Global state
connected_clients: Dict[str, asyncio.Queue] = {}
apify_client = ApifyClient(APIFY_TOKEN)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Facebook Scraper MCP Server (SSE) starting up...")
    yield
    logger.info("Facebook Scraper MCP Server (SSE) shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Facebook Scraper MCP Server",
    description="MCP Server for Facebook post scraping via HTTP with SSE",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "http://127.0.0.1:*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

def datetime_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def clean_data_for_json(data):
    """Recursively clean data to make it JSON serializable"""
    if isinstance(data, dict):
        return {key: clean_data_for_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [clean_data_for_json(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    elif hasattr(data, '__dict__'):
        # For objects with attributes, convert to dict
        return clean_data_for_json(data.__dict__)
    else:
        return data

def normalize_start_urls(start_urls: Any) -> List[Dict[str, str]]:
    """
    Normalize start_urls to the expected format: List[Dict[str, str]]
    
    Accepts:
    - Single string URL: "https://facebook.com/page"
    - List of strings: ["https://facebook.com/page1", "https://facebook.com/page2"]
    - List of dicts: [{"url": "https://facebook.com/page1"}, {"url": "https://facebook.com/page2"}]
    - Mixed list: ["https://facebook.com/page1", {"url": "https://facebook.com/page2"}]
    """
    if isinstance(start_urls, str):
        # Single string URL
        return [{"url": start_urls}]
    
    if not isinstance(start_urls, list):
        raise ValueError("start_urls must be a string or list")
    
    if not start_urls:
        raise ValueError("start_urls cannot be empty")
    
    result = []
    for item in start_urls:
        if isinstance(item, str):
            # String URL
            result.append({"url": item})
        elif isinstance(item, dict) and "url" in item:
            # Already in correct format
            result.append(item)
        else:
            raise ValueError(f"Invalid start_urls item: {item}. Must be string or dict with 'url' key")
    
    return result

async def scrape_facebook_posts(
    startUrls: Any = None,
    start_urls: Any = None,
    resultsLimit: int = None,
    results_limit: int = 20,
    captionText: bool = None,
    caption_text: bool = False,
    onlyPostsNewerThan: Optional[str] = None,
    only_posts_newer_than: Optional[str] = None,
    onlyPostsOlderThan: Optional[str] = None,
    only_posts_older_than: Optional[str] = None,
    **kwargs  # รับ parameters อื่นๆ ที่อาจส่งมา
) -> str:
    """
    Scrape posts from Facebook pages using Apify Actor.
    
    Args:
        start_urls: Facebook page URLs. Can be:
                   - Single string: "https://www.facebook.com/page"
                   - List of strings: ["https://www.facebook.com/page1", "https://www.facebook.com/page2"]
                   - List of dicts: [{"url": "https://www.facebook.com/page"}]
        results_limit: Maximum number of posts to retrieve (1-1000)
        caption_text: Whether to include caption text in results
        only_posts_newer_than: Filter posts newer than this date (ISO format)
        only_posts_older_than: Filter posts older than this date (ISO format)
    
    Returns:
        JSON string containing scraped Facebook posts data
    """
    try:
        # Handle both camelCase and snake_case inputs
        urls = startUrls or start_urls
        limit = resultsLimit or results_limit or 20
        caption = captionText if captionText is not None else caption_text
        newer_than = onlyPostsNewerThan or only_posts_newer_than
        older_than = onlyPostsOlderThan or only_posts_older_than
        
        if not urls:
            raise ValueError("start_urls or startUrls is required")
        
        # Normalize input to expected format
        normalized_urls = normalize_start_urls(urls)
        
        if not 1 <= limit <= 1000:
            raise ValueError("results_limit must be between 1 and 1000")
        
        # Prepare input for Apify actor
        actor_input = {
            "startUrls": normalized_urls,
            "resultsLimit": limit,
            "captionText": caption
        }
        
        # Add optional date filters if provided
        if newer_than:
            actor_input["onlyPostsNewerThan"] = newer_than
        
        if older_than:
            actor_input["onlyPostsOlderThan"] = older_than
        
        logger.info(f"Starting Facebook scraping for {len(normalized_urls)} URL(s)...")
        logger.info(f"URLs: {[url['url'] for url in normalized_urls]}")
        
        # Run the Apify actor
        run = apify_client.actor(FACEBOOK_SCRAPER_ACTOR).call(run_input=actor_input)
        
        logger.info(f"Actor run completed with status: {run['status']}")
        
        if run['status'] != "SUCCEEDED":
            raise Exception(f"Actor run failed with status: {run['status']}")
        
        # Get the results from dataset
        dataset_client = apify_client.dataset(run['defaultDatasetId'])
        items = dataset_client.list_items()
        
        # Convert generator to list if needed
        if hasattr(items, 'items'):
            items_list = list(items.items)
        else:
            items_list = list(items)
        
        logger.info(f"Retrieved {len(items_list)} posts")
        
        # Clean data for JSON serialization
        cleaned_items = clean_data_for_json(items_list)
        cleaned_run_info = clean_data_for_json({
            "actorRunId": run['id'],
            "status": run['status'],
            "startedAt": run.get('startedAt'),
            "finishedAt": run.get('finishedAt')
        })
        
        # Prepare response
        response_data = {
            "success": True,
            "totalResults": len(cleaned_items),
            "data": cleaned_items,
            "runInfo": cleaned_run_info,
            "inputUrls": [url['url'] for url in normalized_urls]
        }
        
        return json.dumps(response_data, indent=2, ensure_ascii=False, default=datetime_serializer)
        
    except Exception as error:
        logger.error(f"Error in Facebook scraping: {error}")
        
        error_response = {
            "success": False,
            "error": str(error),
            "details": type(error).__name__
        }
        
        return json.dumps(error_response, indent=2, ensure_ascii=False)

async def handle_mcp_request(client_id: str, message: dict) -> dict:
    """Handle MCP JSON-RPC requests"""
    try:
        method = message.get("method")
        params = message.get("params", {})
        request_id = message.get("id")
        
        logger.info(f"Client {client_id} called method: {method}")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "facebook-scraper-mcp-sse",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "scrape_facebook_posts",
                            "description": "Scrape posts from Facebook pages using Apify Actor",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "start_urls": {
                                        "description": "Facebook page URLs (flexible format)",
                                        "anyOf": [
                                            {"type": "string"},
                                            {"type": "array", "items": {"type": "string"}},
                                            {"type": "array", "items": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}
                                        ]
                                    },
                                    "results_limit": {
                                        "type": "integer",
                                        "description": "Maximum number of posts to retrieve (1-1000)",
                                        "default": 20,
                                        "minimum": 1,
                                        "maximum": 1000
                                    },
                                    "caption_text": {
                                        "type": "boolean",
                                        "description": "Whether to include caption text in results",
                                        "default": False
                                    },
                                    "only_posts_newer_than": {
                                        "type": "string",
                                        "description": "Filter posts newer than this date (ISO format)",
                                        "format": "date-time"
                                    },
                                    "only_posts_older_than": {
                                        "type": "string",
                                        "description": "Filter posts older than this date (ISO format)",
                                        "format": "date-time"
                                    }
                                },
                                "required": ["start_urls"]
                            }
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "scrape_facebook_posts":
                result = await scrape_facebook_posts(**arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                }
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    except Exception as e:
        logger.error(f"Error handling MCP request: {e}")
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": str(e)
            }
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "transport": "sse",
        "connected_clients": len(connected_clients),
        "server_info": {
            "name": "facebook-scraper-mcp-sse",
            "version": "1.0.0"
        }
    }

@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP clients"""
    
    # Security: Validate Origin header for DNS rebinding protection
    origin = request.headers.get("origin")
    if origin and not any(allowed in origin for allowed in ["localhost", "127.0.0.1"]):
        logger.warning(f"Rejected connection from origin: {origin}")
        raise HTTPException(status_code=403, detail="Forbidden origin")
    
    client_id = str(uuid.uuid4())
    client_queue: asyncio.Queue = asyncio.Queue()
    connected_clients[client_id] = client_queue
    
    logger.info(f"New SSE client connected: {client_id}")
    
    async def event_stream():
        try:
            # Send endpoint event as per MCP spec - using n8n compatible format
            endpoint_uri = f"/messages?session_id={client_id}"
            yield f"event: endpoint\ndata: {endpoint_uri}\n\n"
            
            # Listen for messages to send to client
            while True:
                try:
                    # Wait for messages with timeout to send heartbeat
                    message = await asyncio.wait_for(client_queue.get(), timeout=30.0)
                    yield f"event: message\ndata: {json.dumps(message)}\n\n"
                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    yield f": heartbeat {datetime.now().isoformat()}\n\n"
                
        except asyncio.CancelledError:
            logger.info(f"SSE client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error in SSE stream for client {client_id}: {e}")
        finally:
            # Cleanup
            if client_id in connected_clients:
                del connected_clients[client_id]
                logger.info(f"Cleaned up client {client_id}")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

@app.post("/messages")
async def message_endpoint(request: Request, background_tasks: BackgroundTasks):
    """HTTP POST endpoint for clients to send MCP messages"""
    
    # Get session ID from query parameters
    session_id = request.query_params.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing session_id parameter")
    
    if session_id not in connected_clients:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Parse JSON-RPC message
    message = await request.json()
    
    logger.info(f"Received message from session {session_id}: {message.get('method', 'unknown')}")
    
    # Handle MCP request
    response = await handle_mcp_request(session_id, message)
    
    # Send response back to client via SSE
    client_queue = connected_clients[session_id]
    try:
        await client_queue.put(response)
    except Exception as e:
        logger.error(f"Error queuing response for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to queue response")
    
    return {"status": "message_queued"}

@app.get("/")
async def root():
    """Root endpoint with server info"""
    return {
        "name": "Facebook Scraper MCP Server",
        "transport": "HTTP with Server-Sent Events (SSE)",
        "version": "1.0.0",
        "protocol": "MCP 2024-11-05",
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages",
            "health": "/health"
        },
        "connected_clients": len(connected_clients)
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Facebook Scraper MCP Server (SSE)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--log-level", default="info", help="Log level")
    
    args = parser.parse_args()
    
    print(f"""
🚀 Facebook Scraper MCP Server (SSE) starting...
📡 Transport: HTTP with Server-Sent Events
🌐 Address: http://{args.host}:{args.port}
🔧 SSE Endpoint: http://{args.host}:{args.port}/sse
❤️  Health Check: http://{args.host}:{args.port}/health
""")
    
    uvicorn.run(
        "server:app",
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        reload=False
    )
