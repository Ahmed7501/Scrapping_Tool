#!/usr/bin/env python3
"""
Test with a real website that contains contact information
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_scraper.scraper import EmailScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def test_contact_page():
    """Test with a website that has contact information"""
    
    scraper = EmailScraper(delay=0.5, max_concurrent=1)
    
    # Test with websites that might have contact info
    test_urls = [
        "https://httpbin.org/",
        "https://www.python.org/",
        "https://www.wikipedia.org/"
    ]
    
    print("Testing with real websites...")
    print("=" * 50)
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        try:
            result = await scraper.scrape_url(url)
            print(f"Status: {result['status']}")
            print(f"Business: {result['business']}")
            print(f"Emails found: {result['email_count']}")
            if result['emails']:
                print(f"Emails: {result['emails']}")
            else:
                print("No emails found")
        except Exception as e:
            print(f"Error: {e}")
    
    await scraper.close_session()

if __name__ == "__main__":
    print("Real Website Email Scraping Test")
    print("=" * 50)
    
    asyncio.run(test_contact_page())
    
    print("\nTest completed!") 