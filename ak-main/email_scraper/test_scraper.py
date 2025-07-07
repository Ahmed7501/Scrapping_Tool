#!/usr/bin/env python3
"""
Test script to debug email extraction functionality
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_scraper.scraper import EmailScraper
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)

async def test_email_extraction():
    """Test email extraction with sample URLs"""
    
    # Sample URLs that should contain emails
    test_urls = [
        "https://example.com/contact",
        "https://httpbin.org/html",
        "https://jsonplaceholder.typicode.com/posts/1"
    ]
    
    scraper = EmailScraper(delay=0.1, max_concurrent=3)
    
    print("Testing email extraction...")
    print("=" * 50)
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        try:
            result = await scraper.scrape_url(url)
            print(f"Status: {result['status']}")
            print(f"Emails found: {result['email_count']}")
            print(f"Email list: {result['emails']}")
            print(f"Business: {result['business']}")
        except Exception as e:
            print(f"Error: {e}")
    
    await scraper.close_session()

def test_regex_pattern():
    """Test the email regex pattern with various email formats"""
    
    scraper = EmailScraper()
    
    test_texts = [
        "Contact us at info@example.com",
        "Email: support@test.com or sales@test.com",
        "Our team: john.doe@company.org, jane@company.org",
        "No emails here",
        "Multiple emails: admin@site.com, user@site.com, contact@site.com",
        "mailto:contact@example.com",
        "Email: test@example.com and another@test.org",
        "Complex: user+tag@domain.co.uk",
        "With spaces: user @ domain.com",
        "Invalid: user@domain",
        "Valid: user@domain.com"
    ]
    
    print("\nTesting regex pattern...")
    print("=" * 50)
    
    for text in test_texts:
        emails = scraper.extract_emails(text)
        print(f"Text: {text}")
        print(f"Found emails: {emails}")
        print("-" * 30)

if __name__ == "__main__":
    print("Email Scraper Debug Test")
    print("=" * 50)
    
    # Test regex pattern first
    test_regex_pattern()
    
    # Test actual scraping
    asyncio.run(test_email_extraction())
    
    print("\nDebug test completed!") 