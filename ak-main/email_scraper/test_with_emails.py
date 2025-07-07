#!/usr/bin/env python3
"""
Test script with HTML content that contains emails
"""

import asyncio
import sys
import os
from bs4 import BeautifulSoup

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_scraper.scraper import EmailScraper
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)

def test_email_extraction_from_html():
    """Test email extraction from HTML content"""
    
    # HTML content with emails
    html_content = """
    <html>
    <head>
        <title>Test Company</title>
        <meta name="contact" content="contact@testcompany.com">
    </head>
    <body>
        <h1>Contact Us</h1>
        <p>Email us at: info@testcompany.com</p>
        <p>Support: support@testcompany.com</p>
        <p>Sales: sales@testcompany.com</p>
        <a href="mailto:admin@testcompany.com">Email Admin</a>
        <div data-email="hr@testcompany.com">HR Department</div>
        <script>
            var contactEmail = "dev@testcompany.com";
            var supportEmail = "help@testcompany.com";
        </script>
    </body>
    </html>
    """
    
    scraper = EmailScraper()
    soup = BeautifulSoup(html_content, 'html.parser')
    
    print("Testing email extraction from HTML...")
    print("=" * 50)
    
    # Test text extraction
    text_content = soup.get_text()
    print(f"Text content length: {len(text_content)}")
    text_emails = scraper.extract_emails(text_content)
    print(f"Emails from text: {text_emails}")
    
    # Test HTML extraction
    html_emails = scraper.extract_emails_from_html(soup)
    print(f"Emails from HTML: {html_emails}")
    
    # Combine
    all_emails = list(set(text_emails + list(html_emails)))
    print(f"All emails: {all_emails}")
    print(f"Total unique emails: {len(all_emails)}")

async def test_real_website():
    """Test with a real website that has contact information"""
    
    scraper = EmailScraper(delay=0.1, max_concurrent=1)
    
    # Test with a website that likely has contact info
    test_urls = [
        "https://httpbin.org/",
        "https://www.google.com/",
        "https://www.github.com/"
    ]
    
    print("\nTesting with real websites...")
    print("=" * 50)
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        try:
            result = await scraper.scrape_url(url)
            print(f"Status: {result['status']}")
            print(f"Emails found: {result['email_count']}")
            if result['emails']:
                print(f"Emails: {result['emails']}")
            else:
                print("No emails found")
        except Exception as e:
            print(f"Error: {e}")
    
    await scraper.close_session()

if __name__ == "__main__":
    print("Email Extraction Test with Sample HTML")
    print("=" * 50)
    
    # Test with sample HTML first
    test_email_extraction_from_html()
    
    # Test with real websites
    asyncio.run(test_real_website())
    
    print("\nTest completed!") 