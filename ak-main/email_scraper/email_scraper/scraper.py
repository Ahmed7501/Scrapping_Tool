import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from tqdm import tqdm
import os
from urllib.parse import urlparse
import logging
from concurrent.futures import ThreadPoolExecutor
import aiofiles
from typing import Optional, List, Set

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class EmailScraper:
    def __init__(self, delay=0.5, max_concurrent=10):
        self.delay = delay
        self.max_concurrent = max_concurrent
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Enhanced email pattern to catch more email formats but avoid false positives
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        self.session: Optional[aiohttp.ClientSession] = None

    async def init_session(self):
        """Initialize aiohttp session."""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

    async def close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None

    def extract_emails(self, text: str) -> List[str]:
        """Extract emails from text using enhanced regex."""
        emails = re.findall(self.email_pattern, text, re.IGNORECASE)
        # Remove duplicates and filter out common false positives
        unique_emails = []
        for email in emails:
            email = email.lower().strip()
            # More specific filtering to avoid false positives
            if (email and 
                not email.startswith('example@') and 
                not email.startswith('test@') and
                not email.startswith('noreply@') and
                not email.startswith('no-reply@') and
                not email.startswith('donotreply@') and
                not email.startswith('mailto:') and
                not email.endswith('.png') and
                not email.endswith('.jpg') and
                not email.endswith('.jpeg') and
                not email.endswith('.gif') and
                not email.endswith('.svg') and
                not email.endswith('.ico') and
                not email.endswith('.webp') and
                len(email) > 5 and
                '@' in email and
                '.' in email.split('@')[1] and  # Ensure domain has a TLD
                len(email.split('@')[1].split('.')[0]) > 0):  # Ensure domain name exists
                unique_emails.append(email)
        
        # Log found emails for debugging
        if unique_emails:
            logging.info(f"Found emails: {unique_emails}")
        
        return list(set(unique_emails))

    def extract_emails_from_html(self, soup: BeautifulSoup) -> Set[str]:
        """Extract emails from HTML attributes and content."""
        emails = set()
        
        try:
            # Extract from href attributes (mailto links)
            mailto_links = soup.find_all('a', href=True)
            for link in mailto_links:
                href = link.get('href', '')
                if href and href.startswith('mailto:'):
                    email = href.replace('mailto:', '').split('?')[0].split('#')[0]
                    if email and '@' in email:
                        emails.add(email.lower().strip())
            
            # Extract from all attributes that might contain emails
            for tag in soup.find_all():
                for attr_name, attr_value in tag.attrs.items():
                    if isinstance(attr_value, str) and '@' in attr_value:
                        found_emails = self.extract_emails(attr_value)
                        emails.update(found_emails)
            
            # Extract from script tags (JavaScript)
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    found_emails = self.extract_emails(script.string)
                    emails.update(found_emails)
            
            # Extract from meta tags
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                content = meta.get('content', '')
                if content and '@' in content:
                    found_emails = self.extract_emails(content)
                    emails.update(found_emails)
                    
        except Exception as e:
            logging.error(f"Error extracting emails from HTML: {e}")
        
        return emails

    def get_domain_name(self, url):
        """Extract domain name from URL."""
        try:
            parsed_url = urlparse(url)
            return parsed_url.netloc
        except:
            return url

    async def scrape_url(self, url):
        """Scrape emails from a single URL using enhanced extraction."""
        try:
            await self.init_session()
            timeout = aiohttp.ClientTimeout(total=15)  # Increased timeout
            assert self.session is not None, "Session was not initialized!"
            
            async with self.session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Get page title for business name
                    title = soup.title.string if soup.title else ''
                    
                    # Extract emails from text content
                    text_content = soup.get_text()
                    text_emails = self.extract_emails(text_content)
                    
                    # Extract emails from HTML attributes and JavaScript
                    html_emails = self.extract_emails_from_html(soup)
                    
                    # Combine all emails
                    all_emails = list(set(text_emails + list(html_emails)))
                    
                    # Get domain name
                    domain = self.get_domain_name(url)
                    
                    # Debug logging
                    logging.info(f"URL: {url}")
                    logging.info(f"Text emails found: {len(text_emails)}")
                    logging.info(f"HTML emails found: {len(html_emails)}")
                    logging.info(f"Total emails found: {len(all_emails)}")
                    if all_emails:
                        logging.info(f"Email list: {all_emails}")
                    
                    return {
                        'url': url,
                        'business': title.strip() if title else domain,
                        'emails': ', '.join(all_emails),
                        'email_count': len(all_emails),
                        'domain': domain,
                        'status': 'success'
                    }
                else:
                    raise Exception(f"HTTP {response.status}")
                    
        except Exception as e:
            logging.error(f"Error scraping {url}: {str(e)}")
            return {
                'url': url,
                'business': self.get_domain_name(url),
                'emails': '',
                'email_count': 0,
                'domain': self.get_domain_name(url),
                'status': f'error: {str(e)}'
            }

    async def process_urls_async(self, urls):
        """Process URLs concurrently using asyncio with better rate limiting."""
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def scrape_with_semaphore(url):
            async with semaphore:
                result = await self.scrape_url(url)
                await asyncio.sleep(self.delay)  # Rate limiting
                return result
        
        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logging.error(f"Exception processing {urls[i]}: {result}")
                processed_results.append({
                    'url': urls[i],
                    'business': self.get_domain_name(urls[i]),
                    'emails': '',
                    'email_count': 0,
                    'domain': self.get_domain_name(urls[i]),
                    'status': f'error: {str(result)}'
                })
            else:
                processed_results.append(result)
        
        return processed_results

    def process_urls(self, input_file, output_file):
        """Process URLs from input file and save results to CSV."""
        try:
            # Read URLs from file
            with open(input_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]

            logging.info(f"Processing {len(urls)} URLs...")

            # Create event loop and run async processing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                results = loop.run_until_complete(self.process_urls_async(urls))
            finally:
                loop.run_until_complete(self.close_session())
                loop.close()

            # Create DataFrame and save to CSV
            df = pd.DataFrame(results)
            
            # Add summary statistics
            total_emails = df['email_count'].sum()
            successful_scrapes = len(df[df['status'] == 'success'])
            
            logging.info(f"Scraping completed: {successful_scrapes}/{len(urls)} URLs successful")
            logging.info(f"Total emails found: {total_emails}")
            
            df.to_csv(output_file, index=False)
            logging.info(f"Results saved to {output_file}")
            
            return len(results)
            
        except Exception as e:
            logging.error(f"Error processing URLs: {str(e)}")
            return 0 