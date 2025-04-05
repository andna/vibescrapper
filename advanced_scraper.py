#!/usr/bin/env python3
"""
Advanced Web Scraper for extracting HTML content from divs with data-lyrics-container="true" attribute.
Supports multiple output formats and additional configuration options.
"""

import requests
from bs4 import BeautifulSoup
import argparse
import sys
import logging
import json
import csv
import time
import os
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LyricsScraper:
    def __init__(self, user_agent=None, timeout=30, delay=0):
        """
        Initialize the scraper with configuration options.
        
        Args:
            user_agent (str): Custom User-Agent string
            timeout (int): Request timeout in seconds
            delay (float): Delay between requests in seconds
        """
        self.timeout = timeout
        self.delay = delay
        
        # Default User-Agent if none provided
        if user_agent is None:
            self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        else:
            self.user_agent = user_agent
            
        self.headers = {
            'User-Agent': self.user_agent
        }
    
    def scrape_url(self, url):
        """
        Scrape a single URL for lyrics containers.
        
        Args:
            url (str): URL to scrape
            
        Returns:
            list: List of container data dictionaries
        """
        try:
            logger.info(f"Sending request to {url}")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all divs with data-lyrics-container="true"
            lyrics_containers = soup.find_all('div', attrs={'data-lyrics-container': 'true'})
            
            if not lyrics_containers:
                logger.warning("No divs with data-lyrics-container='true' found on the page.")
                return []
            
            logger.info(f"Found {len(lyrics_containers)} lyrics containers.")
            
            # Extract data from each container
            results = []
            for i, container in enumerate(lyrics_containers, 1):
                results.append({
                    'url': url,
                    'container_number': i,
                    'html_content': str(container),
                    'text_content': container.get_text(strip=True)
                })
                
            # Apply delay if specified
            if self.delay > 0:
                time.sleep(self.delay)
                
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error during request to {url}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error while scraping {url}: {e}")
            return []
    
    def scrape_multiple_urls(self, urls):
        """
        Scrape multiple URLs for lyrics containers.
        
        Args:
            urls (list): List of URLs to scrape
            
        Returns:
            list: Combined results from all URLs
        """
        all_results = []
        for url in urls:
            results = self.scrape_url(url)
            all_results.extend(results)
        return all_results
    
    @staticmethod
    def save_results(results, output_file, format='json'):
        """
        Save results to a file in the specified format.
        
        Args:
            results (list): Scraping results
            output_file (str): Output file path
            format (str): Output format (json, csv, html, txt)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            if format.lower() == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            
            elif format.lower() == 'csv':
                with open(output_file, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    # Write header
                    writer.writerow(['URL', 'Container Number', 'Text Content'])
                    # Write data
                    for item in results:
                        writer.writerow([
                            item['url'],
                            item['container_number'],
                            item['text_content']
                        ])
            
            elif format.lower() == 'html':
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write('<!DOCTYPE html>\n<html>\n<head>\n')
                    f.write('<meta charset="UTF-8">\n')
                    f.write('<title>Lyrics Scraping Results</title>\n')
                    f.write('<style>body{font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px}')
                    f.write('.container{border:1px solid #ddd;margin:20px 0;padding:15px;border-radius:5px}')
                    f.write('h2{color:#333}pre{white-space:pre-wrap;background:#f5f5f5;padding:10px;border-radius:3px}</style>\n')
                    f.write('</head>\n<body>\n')
                    f.write('<h1>Lyrics Scraping Results</h1>\n')
                    
                    for item in results:
                        f.write(f'<div class="container">\n')
                        f.write(f'<h2>Container {item["container_number"]} from {item["url"]}</h2>\n')
                        f.write(f'<h3>HTML Content:</h3>\n<pre>{item["html_content"]}</pre>\n')
                        f.write(f'<h3>Text Content:</h3>\n<p>{item["text_content"]}</p>\n')
                        f.write('</div>\n')
                    
                    f.write('</body>\n</html>')
            
            elif format.lower() == 'txt':
                with open(output_file, 'w', encoding='utf-8') as f:
                    for item in results:
                        f.write(f'=== Container {item["container_number"]} from {item["url"]} ===\n\n')
                        f.write('--- HTML Content ---\n')
                        f.write(f'{item["html_content"]}\n\n')
                        f.write('--- Text Content ---\n')
                        f.write(f'{item["text_content"]}\n\n')
                        f.write('=' * 50 + '\n\n')
            
            else:
                logger.error(f"Unsupported output format: {format}")
                return False
            
            logger.info(f"Results saved to {output_file} in {format} format")
            return True
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return False

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Advanced scraper for lyrics containers')
    
    # Required arguments
    parser.add_argument('urls', nargs='+', help='URLs to scrape')
    
    # Output options
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['json', 'csv', 'html', 'txt'], default='json',
                        help='Output format (default: json)')
    
    # Request options
    parser.add_argument('--user-agent', help='Custom User-Agent string')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds (default: 30)')
    parser.add_argument('--delay', type=float, default=0, help='Delay between requests in seconds (default: 0)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = LyricsScraper(
        user_agent=args.user_agent,
        timeout=args.timeout,
        delay=args.delay
    )
    
    # Scrape URLs
    results = scraper.scrape_multiple_urls(args.urls)
    
    if not results:
        logger.error("No results found.")
        sys.exit(1)
    
    # Output the results
    if args.output:
        scraper.save_results(results, args.output, args.format)
    else:
        # Print results to console
        for result in results:
            print(f"\n--- Container {result['container_number']} from {result['url']} ---")
            print(f"HTML Content:\n{result['html_content']}")
            print(f"\nText Content:\n{result['text_content']}")
            print("-" * 50)

if __name__ == "__main__":
    main()
