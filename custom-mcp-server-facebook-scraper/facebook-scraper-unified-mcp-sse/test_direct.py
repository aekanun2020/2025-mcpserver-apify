#!/usr/bin/env python3

"""
Direct test script สำหรับทดสอบ Facebook scraper functions โดยตรง
ทดสอบทั้ง posts และ comments scraping
"""

import asyncio
import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import scrape_facebook_posts, scrape_facebook_comments, normalize_start_urls

async def test_normalize_function():
    """ทดสอบ normalize_start_urls function"""
    print("🧪 Testing normalize_start_urls function:")
    print("=" * 50)
    
    test_cases = [
        # Single string
        "https://www.facebook.com/NationTV/",
        
        # List of strings
        ["https://www.facebook.com/NationTV/", "https://www.facebook.com/ThaiPBS/"],
        
        # List of dicts
        [{"url": "https://www.facebook.com/NationTV/"}],
        
        # Mixed list
        ["https://www.facebook.com/NationTV/", {"url": "https://www.facebook.com/ThaiPBS/"}]
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n🔬 Test Case {i}:")
        print(f"Input: {test_input}")
        try:
            result = normalize_start_urls(test_input)
            print(f"Output: {result}")
            print("✅ Success")
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_posts_scraping():
    """ทดสอบการ scrape Facebook posts โดยตรง"""
    print("\n" + "=" * 50)
    print("🧪 Testing Facebook posts scraping function:")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Single page URL",
            "args": {
                "start_urls": "https://www.facebook.com/NationTV/",
                "results_limit": 2,
                "caption_text": False
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 Test {i}: {test_case['name']}")
        print(f"Args: {test_case['args']}")
        print("⏳ Scraping posts...")
        
        try:
            result = await scrape_facebook_posts(**test_case['args'])
            
            # Parse and display summary
            result_data = json.loads(result)
            if result_data.get("success"):
                print("✅ Posts scraping successful!")
                print(f"   Total results: {result_data.get('totalResults', 0)}")
                print(f"   Input URLs: {result_data.get('inputUrls', [])}")
                print(f"   Run status: {result_data.get('runInfo', {}).get('status', 'unknown')}")
            else:
                print(f"❌ Posts scraping failed: {result_data.get('error')}")
                
        except Exception as e:
            print(f"❌ Exception occurred: {e}")

async def test_comments_scraping():
    """ทดสอบการ scrape Facebook comments โดยตรง"""
    print("\n" + "=" * 50)
    print("🧪 Testing Facebook comments scraping function:")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Single post URL",
            "args": {
                "start_urls": "https://www.facebook.com/humansofnewyork/posts/pfbid0BbKbkisExKGSKuhee9a7i86RwRuMKFC8NSkKStB7CsM3uXJuAAfZLrkcJMXxhH4Yl",
                "results_limit": 3,
                "include_nested_comments": False,
                "view_option": "RANKED_UNFILTERED"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 Test {i}: {test_case['name']}")
        print(f"Args: {test_case['args']}")
        print("⏳ Scraping comments...")
        
        try:
            result = await scrape_facebook_comments(**test_case['args'])
            
            # Parse and display summary
            result_data = json.loads(result)
            if result_data.get("success"):
                print("✅ Comments scraping successful!")
                print(f"   Total results: {result_data.get('totalResults', 0)}")
                print(f"   Input URLs: {result_data.get('inputUrls', [])}")
                print(f"   Run status: {result_data.get('runInfo', {}).get('status', 'unknown')}")
            else:
                print(f"❌ Comments scraping failed: {result_data.get('error')}")
                
        except Exception as e:
            print(f"❌ Exception occurred: {e}")

async def main():
    """Main test function"""
    print("""
🧪 Facebook Scraper Unified Direct Function Test
===============================================
ทดสอบ unified functions โดยตรงโดยไม่ผ่าน HTTP/SSE transport
""")
    
    # Test normalize function
    await test_normalize_function()
    
    # Test posts scraping
    await test_posts_scraping()
    
    # Wait between tests
    print("\n⏳ Waiting 5 seconds before comments test...")
    await asyncio.sleep(5)
    
    # Test comments scraping
    await test_comments_scraping()
    
    print("\n" + "=" * 50)
    print("🎉 Direct unified function tests completed!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
