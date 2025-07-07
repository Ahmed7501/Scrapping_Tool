#!/usr/bin/env python3
"""
Simple test for email extraction
"""

import re
from bs4 import BeautifulSoup

def extract_emails(text):
    """Extract emails from text using regex."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text, re.IGNORECASE)
    
    # Filter emails
    unique_emails = []
    for email in emails:
        email = email.lower().strip()
        if (email and 
            not email.startswith('example@') and 
            not email.startswith('test@') and
            not email.startswith('noreply@') and
            not email.startswith('no-reply@') and
            not email.startswith('donotreply@') and
            not email.startswith('mailto:') and
            len(email) > 5 and
            '@' in email and
            '.' in email.split('@')[1]):
            unique_emails.append(email)
    
    return list(set(unique_emails))

# Test with sample text
test_text = """
Contact us at info@company.com
Support: support@company.com
Sales: sales@company.com
Email: contact@example.org
"""

print("Testing email extraction...")
print("=" * 40)
print(f"Test text: {test_text}")
emails = extract_emails(test_text)
print(f"Found emails: {emails}")
print(f"Count: {len(emails)}")

# Test with HTML
html_content = """
<html>
<body>
    <p>Contact: info@test.com</p>
    <a href="mailto:support@test.com">Support</a>
    <div data-email="sales@test.com">Sales</div>
</body>
</html>
"""

soup = BeautifulSoup(html_content, 'html.parser')
text_content = soup.get_text()
print(f"\nHTML text content: {text_content}")
html_emails = extract_emails(text_content)
print(f"Emails from HTML: {html_emails}")

print("\nTest completed!") 