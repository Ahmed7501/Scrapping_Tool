import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from tqdm import tqdm
import os
from urllib.parse import urlparse
import logging
import sys

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
    def __init__(self, delay=1):
        self.delay = delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    def extract_emails(self, text):
        """Extract emails from text using regex."""
        return list(set(re.findall(self.email_pattern, text)))

    def get_domain_name(self, url):
        """Extract domain name from URL."""
        try:
            parsed_url = urlparse(url)
            return parsed_url.netloc
        except:
            return url

    def scrape_url(self, url):
        """Scrape emails from a single URL."""
        try:
            print(f"\nProcessing: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get page title for business name
            title = soup.title.string if soup.title else ''
            
            # Extract emails from text content
            text_content = soup.get_text()
            emails = self.extract_emails(text_content)
            
            # Get domain name
            domain = self.get_domain_name(url)
            
            result = {
                'url': url,
                'business': title.strip() if title else domain,
                'emails': ', '.join(emails),
                'domain': domain
            }
            
            print(f"Found {len(emails)} emails")
            return result
            
        except Exception as e:
            logging.error(f"Error scraping {url}: {str(e)}")
            print(f"Error processing {url}: {str(e)}")
            return {
                'url': url,
                'business': self.get_domain_name(url),
                'emails': '',
                'domain': self.get_domain_name(url)
            }

    def process_urls(self, input_file, output_file):
        """Process URLs from input file and save results to CSV."""
        try:
            # Read URLs from file
            with open(input_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]

            results = []
            
            # Process URLs with progress bar
            for url in tqdm(urls, desc="Scraping URLs"):
                result = self.scrape_url(url)
                results.append(result)
                time.sleep(self.delay)  # Rate limiting

            # Create DataFrame and save to CSV
            df = pd.DataFrame(results)
            df.to_csv(output_file, index=False)
            logging.info(f"Results saved to {output_file}")
            print(f"\nResults saved to {output_file}")
            
            return len(results)
            
        except Exception as e:
            logging.error(f"Error processing URLs: {str(e)}")
            print(f"Error: {str(e)}")
            return 0

def main():
    # Create scraper instance
    scraper = EmailScraper(delay=1)  # 1 second delay between requests
    
    # Get input file path from command line or prompt
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("Enter the path to your URLs file: ").strip()
    
    if not os.path.exists(input_file):
        print("Error: Input file not found!")
        return
    
    # Set output file path
    output_file = "scraped_emails.csv"
    
    print(f"\nStarting email scraping from {input_file}")
    print("Results will be saved to:", output_file)
    print("\nPress Ctrl+C to stop the process at any time.\n")
    
    try:
        processed_count = scraper.process_urls(input_file, output_file)
        print(f"\nScraping completed! Processed {processed_count} URLs.")
        print(f"Results saved to: {output_file}")
        
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main() 