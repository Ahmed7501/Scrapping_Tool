#!/usr/bin/env python3
"""
Debug email extraction issue
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_scraper.scraper import EmailScraper
import re

def debug_email_extraction():
    """Debug the email extraction issue"""
    
    print("Debugging email extraction...")
    print("=" * 40)
    
    # Create scraper
    scraper = EmailScraper()
    
    # Test text
    test_text = "Contact us at test@example.com"
    print(f"Test text: {test_text}")
    
    # Check regex pattern
    print(f"Regex pattern: {scraper.email_pattern}")
    
    # Test regex directly
    emails = re.findall(scraper.email_pattern, test_text, re.IGNORECASE)
    print(f"Raw regex result: {emails}")
    
    # Test the extract_emails method
    extracted_emails = scraper.extract_emails(test_text)
    print(f"Extracted emails: {extracted_emails}")
    
    # Test with more complex text
    complex_text = """
    Contact us at info@company.com
    Support: support@company.com
    Sales: sales@company.com
    """
    print(f"\nComplex text: {complex_text}")
    complex_emails = scraper.extract_emails(complex_text)
    print(f"Complex extracted emails: {complex_emails}")

if __name__ == "__main__":
    debug_email_extraction() 