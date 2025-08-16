#!/usr/bin/env python3

"""
Test script for Facebook Scraper MCP Server
"""

import asyncio
import json
from server_original import scrape_facebook_posts

async def test_facebook_scraper():
    """Test the Facebook scraper function"""
    
    # Test input
    test_input = {
        "start_urls": [
            {"url": "https://www.facebook.com/NationTV/"}
        ],
        "results_limit": 5,
        "caption_text": False
    }
    
    print("Testing Facebook Scraper...")
    print(f"Input: {json.dumps(test_input, indent=2)}")
    print("-" * 50)
    
    try:
        result = await scrape_facebook_posts(**test_input)
        print("Result:")
        print(result)
        
        # Parse and display summary
        result_data = json.loads(result)
        if result_data.get("success"):
            print(f"\n✅ Success! Retrieved {result_data.get('totalResults', 0)} posts")
        else:
            print(f"\n❌ Error: {result_data.get('error')}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_facebook_scraper())
