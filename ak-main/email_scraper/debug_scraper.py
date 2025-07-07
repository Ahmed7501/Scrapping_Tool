#!/usr/bin/env python3
"""
Debug script to test email scraping with detailed output
"""

import asyncio
import sys
import os
import aiohttp
from bs4 import BeautifulSoup

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_scraper.scraper import EmailScraper

async def debug_scrape():
    """Debug scraping with detailed output"""
    
    url = "https://httpbin.org/html"
    
    print(f"Testing URL: {url}")
    print("=" * 50)
    
    # Create scraper
    scraper = EmailScraper()
    await scraper.init_session()
    
    try:
        # Make request
        timeout = aiohttp.ClientTimeout(total=15)
        async with scraper.session.get(url, timeout=timeout) as response:
            print(f"Response status: {response.status}")
            
            if response.status == 200:
                html = await response.text()
                print(f"HTML length: {len(html)}")
                
                # Parse HTML
                soup = BeautifulSoup(html, 'html.parser')
                
                # Get text content
                text_content = soup.get_text()
                print(f"Text content length: {len(text_content)}")
                print(f"Text content preview: {text_content[:200]}...")
                
                # Extract emails from text
                text_emails = scraper.extract_emails(text_content)
                print(f"Emails from text: {text_emails}")
                
                # Extract emails from HTML
                html_emails = scraper.extract_emails_from_html(soup)
                print(f"Emails from HTML: {html_emails}")
                
                # Combine
                all_emails = list(set(text_emails + list(html_emails)))
                print(f"All emails: {all_emails}")
                print(f"Total emails: {len(all_emails)}")
                
                # Show page title
                title = soup.title.string if soup.title else 'No title'
                print(f"Page title: {title}")
                
            else:
                print(f"HTTP Error: {response.status}")
                
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await scraper.close_session()

if __name__ == "__main__":
    print("Debug Email Scraping")
    print("=" * 50)
    
    asyncio.run(debug_scrape())
    
    print("\nDebug completed!") 