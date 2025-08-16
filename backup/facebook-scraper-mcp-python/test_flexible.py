#!/usr/bin/env python3

"""
Test script for Facebook Scraper MCP Server - Testing flexible input formats
"""

import asyncio
import json
from server import scrape_facebook_posts, normalize_start_urls

async def test_input_formats():
    """Test different input formats for start_urls"""
    
    print("Testing normalize_start_urls function:")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        # Single string
        "https://www.facebook.com/NationTV/",
        
        # List of strings
        ["https://www.facebook.com/NationTV/", "https://www.facebook.com/ThaiPBS/"],
        
        # List of dicts (original format)
        [{"url": "https://www.facebook.com/NationTV/"}],
        
        # Mixed list
        ["https://www.facebook.com/NationTV/", {"url": "https://www.facebook.com/ThaiPBS/"}]
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {test_input}")
        try:
            result = normalize_start_urls(test_input)
            print(f"Output: {result}")
            print("✅ Success")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Testing actual Facebook scraping with string input:")
    
    # Test actual scraping with simple string input
    try:
        result = await scrape_facebook_posts(
            start_urls="https://www.facebook.com/NationTV/",
            results_limit=2,
            caption_text=False
        )
        print("✅ Scraping with string input successful")
        
        # Parse and display summary
        result_data = json.loads(result)
        if result_data.get("success"):
            print(f"Retrieved {result_data.get('totalResults', 0)} posts")
            print(f"Input URLs processed: {result_data.get('inputUrls', [])}")
        else:
            print(f"❌ Scraping failed: {result_data.get('error')}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_input_formats())
