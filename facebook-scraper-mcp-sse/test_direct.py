#!/usr/bin/env python3

"""
Quick test script สำหรับทดสอบ Facebook scraper function โดยตรง
ไม่ผ่าน HTTP/SSE transport
"""

import asyncio
import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import scrape_facebook_posts, normalize_start_urls

async def test_normalize_function():
    """ทดสอบ normalize_start_urls function"""
    print("🧪 Testing normalize_start_urls function:")
    print("=" * 50)
    
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
        print(f"\n🔬 Test Case {i}:")
        print(f"Input: {test_input}")
        try:
            result = normalize_start_urls(test_input)
            print(f"Output: {result}")
            print("✅ Success")
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_facebook_scraping():
    """ทดสอบการ scrape Facebook โดยตรง"""
    print("\n" + "=" * 50)
    print("🧪 Testing Facebook scraping function:")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Single string URL",
            "args": {
                "start_urls": "https://www.facebook.com/NationTV/",
                "results_limit": 2,
                "caption_text": False
            }
        },
        {
            "name": "List format",
            "args": {
                "start_urls": [{"url": "https://www.facebook.com/ThaiPBS/"}],
                "results_limit": 1,
                "caption_text": False
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 Test {i}: {test_case['name']}")
        print(f"Args: {test_case['args']}")
        print("⏳ Scraping...")
        
        try:
            result = await scrape_facebook_posts(**test_case['args'])
            
            # Parse and display summary
            result_data = json.loads(result)
            if result_data.get("success"):
                print("✅ Scraping successful!")
                print(f"   Total results: {result_data.get('totalResults', 0)}")
                print(f"   Input URLs: {result_data.get('inputUrls', [])}")
                print(f"   Run status: {result_data.get('runInfo', {}).get('status', 'unknown')}")
                
                # Show first post summary if available
                data = result_data.get('data', [])
                if data:
                    first_post = data[0]
                    print(f"   First post ID: {first_post.get('id', 'N/A')}")
                    if 'owner' in first_post:
                        print(f"   Page: {first_post['owner'].get('name', 'N/A')}")
            else:
                print(f"❌ Scraping failed: {result_data.get('error')}")
                
        except Exception as e:
            print(f"❌ Exception occurred: {e}")
        
        # พักระหว่างการทดสอบ
        if i < len(test_cases):
            print("⏳ Waiting 3 seconds...")
            await asyncio.sleep(3)

async def main():
    """Main test function"""
    print("""
🧪 Facebook Scraper Direct Function Test
=========================================
ทดสอบ function โดยตรงโดยไม่ผ่าน HTTP/SSE transport
""")
    
    # Test normalize function
    await test_normalize_function()
    
    # Test actual scraping
    await test_facebook_scraping()
    
    print("\n" + "=" * 50)
    print("🎉 Direct function tests completed!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
