#!/usr/bin/env python3

import asyncio
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from apify_client import ApifyClient
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Apify configuration
APIFY_TOKEN = "apify_api_xZVA6BjhUebdeKplts2cPb7zvmpGXU1oA4rb"
FACEBOOK_SCRAPER_ACTOR = "apify/facebook-posts-scraper"

# Initialize FastMCP server
mcp = FastMCP("facebook-scraper-mcp")

# Initialize Apify client
apify_client = ApifyClient(APIFY_TOKEN)

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

@mcp.tool()
async def scrape_facebook_posts(
    start_urls: Any,
    results_limit: int = 20,
    caption_text: bool = False,
    only_posts_newer_than: Optional[str] = None,
    only_posts_older_than: Optional[str] = None
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
        # Normalize input to expected format
        normalized_urls = normalize_start_urls(start_urls)
        
        if not 1 <= results_limit <= 1000:
            raise ValueError("results_limit must be between 1 and 1000")
        
        # Prepare input for Apify actor
        actor_input = {
            "startUrls": normalized_urls,
            "resultsLimit": results_limit,
            "captionText": caption_text
        }
        
        # Add optional date filters if provided
        if only_posts_newer_than:
            actor_input["onlyPostsNewerThan"] = only_posts_newer_than
        
        if only_posts_older_than:
            actor_input["onlyPostsOlderThan"] = only_posts_older_than
        
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

if __name__ == "__main__":
    # Run the server
    mcp.run(transport='stdio')
