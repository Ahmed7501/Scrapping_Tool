#!/usr/bin/env python3
"""
Test with HTML content containing real email addresses
"""

import asyncio
import sys
import os
import aiohttp
from bs4 import BeautifulSoup

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_scraper.scraper import EmailScraper

async def test_with_html_content():
    """Test with HTML content that contains emails"""
    
    # Create a simple HTML page with emails
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Contact Us - Test Company</title>
        <meta name="contact" content="contact@testcompany.com">
    </head>
    <body>
        <h1>Contact Us</h1>
        <p>For general inquiries: info@testcompany.com</p>
        <p>For support: support@testcompany.com</p>
        <p>For sales: sales@testcompany.com</p>
        <a href="mailto:admin@testcompany.com">Email Admin</a>
        <div data-email="hr@testcompany.com">HR Department</div>
        <script>
            var contactEmail = "dev@testcompany.com";
            var supportEmail = "help@testcompany.com";
        </script>
    </body>
    </html>
    """
    
    print("Testing with HTML content containing emails...")
    print("=" * 60)
    
    # Create scraper
    scraper = EmailScraper()
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract emails from text
    text_content = soup.get_text()
    print(f"Text content: {text_content}")
    text_emails = scraper.extract_emails(text_content)
    print(f"Emails from text: {text_emails}")
    
    # Extract emails from HTML
    html_emails = scraper.extract_emails_from_html(soup)
    print(f"Emails from HTML: {html_emails}")
    
    # Combine
    all_emails = list(set(text_emails + list(html_emails)))
    print(f"All emails: {all_emails}")
    print(f"Total unique emails: {len(all_emails)}")
    
    # Test the full scraping process
    print("\nTesting full scraping process...")
    print("=" * 60)
    
    # Create a mock result
    result = {
        'url': 'https://testcompany.com/contact',
        'business': 'Test Company',
        'emails': ', '.join(all_emails),
        'email_count': len(all_emails),
        'domain': 'testcompany.com',
        'status': 'success'
    }
    
    print(f"URL: {result['url']}")
    print(f"Business: {result['business']}")
    print(f"Emails found: {result['email_count']}")
    print(f"Email list: {result['emails']}")
    print(f"Status: {result['status']}")

if __name__ == "__main__":
    print("Email Scraping Test with Real Emails")
    print("=" * 60)
    
    asyncio.run(test_with_html_content())
    
    print("\nTest completed!") 