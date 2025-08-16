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

@mcp.tool()
async def scrape_facebook_posts(
    start_urls: List[Dict[str, str]],
    results_limit: int = 20,
    caption_text: bool = False,
    only_posts_newer_than: Optional[str] = None,
    only_posts_older_than: Optional[str] = None
) -> str:
    """
    Scrape posts from Facebook pages using Apify Actor.
    
    Args:
        start_urls: List of dictionaries with 'url' key containing Facebook page URLs
        results_limit: Maximum number of posts to retrieve (1-1000)
        caption_text: Whether to include caption text in results
        only_posts_newer_than: Filter posts newer than this date (ISO format)
        only_posts_older_than: Filter posts older than this date (ISO format)
    
    Returns:
        JSON string containing scraped Facebook posts data
    """
    try:
        # Validate input
        if not start_urls or not isinstance(start_urls, list):
            raise ValueError("start_urls must be a non-empty list")
        
        for url_item in start_urls:
            if not isinstance(url_item, dict) or 'url' not in url_item:
                raise ValueError("Each item in start_urls must be a dictionary with 'url' key")
        
        if not 1 <= results_limit <= 1000:
            raise ValueError("results_limit must be between 1 and 1000")
        
        # Prepare input for Apify actor
        actor_input = {
            "startUrls": start_urls,
            "resultsLimit": results_limit,
            "captionText": caption_text
        }
        
        # Add optional date filters if provided
        if only_posts_newer_than:
            actor_input["onlyPostsNewerThan"] = only_posts_newer_than
        
        if only_posts_older_than:
            actor_input["onlyPostsOlderThan"] = only_posts_older_than
        
        logger.info(f"Starting Facebook scraping for {len(start_urls)} URL(s)...")
        
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
            "runInfo": cleaned_run_info
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
