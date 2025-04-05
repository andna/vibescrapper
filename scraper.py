#!/usr/bin/env python3
"""
Web Scraper for extracting HTML content from divs with data-lyrics-container="true" attribute.
"""

import requests
from bs4 import BeautifulSoup
import argparse
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_element(element):
    """Parse an HTML element into the structured format."""
    # If it's a string (NavigableString), return it as is for further processing
    if isinstance(element, str) or element.name is None:
        text = str(element).strip()
        return text if text else None
    
    # Handle <a> tags
    elif element.name == 'a':
        # Get the href attribute
        href = element.get('href')
        
        # Process the content of the <a> tag
        content = None
        for child in element.children:
            if child.name == 'span':
                # Get the text from the span
                span_text = child.get_text().strip()
                if span_text:
                    content = {"type": "span", "text": span_text}
                break
        
        # Create the structured object for the <a> tag
        if content:
            return {"type": "a", "content": content, "href": href}
    
    # Handle <span> tags
    elif element.name == 'span':
        # Get the text from the span
        span_text = element.get_text().strip()
        if span_text:
            return {"type": "span", "text": span_text}
    
    # For other elements, try to get their text content
    else:
        text = element.get_text().strip()
        if text:
            return {"type": element.name, "text": text}
    
    return None

def scrape_lyrics_containers(url):
    """
    Scrape HTML content from divs with data-lyrics-container="true" attribute.
    
    Args:
        url (str): The URL of the webpage to scrape
        
    Returns:
        list: List of HTML content from matching divs
    """
    try:
        # Send HTTP request to the website
        logger.info(f"Sending request to {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, verify=False)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all divs with data-lyrics-container="true"
        lyrics_containers = soup.find_all('div', attrs={'data-lyrics-container': 'true'})
        
        if not lyrics_containers:
            logger.warning("No divs with data-lyrics-container='true' found on the page.")
            return []
        
        logger.info(f"Found {len(lyrics_containers)} lyrics containers.")
        
        # Extract the HTML content from each container
        results = []
        for i, container in enumerate(lyrics_containers, 1):
            # Find and remove divs with data-exclude-from-selection="true"
            exclude_divs = container.find_all('div', attrs={'data-exclude-from-selection': 'true'})
            for div in exclude_divs:
                div.decompose()
            
            # Only process non-empty containers
            if container.contents:
                # Parse the container and convert to structured format
                structured_content = []
                
                # Split content by <br/> tags and process each part
                current_content = []
                for child in container.children:
                    if child.name == 'br':
                        # Process accumulated content before the <br>
                        if current_content:
                            for item in current_content:
                                if isinstance(item, str) and item.strip():
                                    structured_content.append({"text": item.strip()})
                                elif item:
                                    structured_content.append(item)
                            current_content = []
                    else:
                        # Process this element
                        parsed = parse_element(child)
                        if parsed:
                            current_content.append(parsed)
                
                # Add any remaining content after the last <br>
                for item in current_content:
                    if isinstance(item, str) and item.strip():
                        structured_content.append({"text": item.strip()})
                    elif item:
                        structured_content.append(item)
                
                # Only add if we have structured content
                if structured_content:
                    results.extend(structured_content)
            
        return results
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error during request: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return []

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Scrape HTML content from divs with data-lyrics-container="true" attribute.')
    parser.add_argument('url', help='The URL of the webpage to scrape')
    parser.add_argument('--output', '-o', help='Output file to save the results (optional)')
    parser.add_argument('--format', '-f', choices=['json', 'text', 'html'], default='text',
                        help='Output format (default: text)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Scrape the webpage
    results = scrape_lyrics_containers(args.url)
    
    if not results:
        logger.error("No results found.")
        sys.exit(1)
    
    # Output the results
    if args.output:
        import json
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"Results saved to {args.output}")
    else:
        # Print results to console
        if args.format == 'json':
            import json
            print(json.dumps(results, ensure_ascii=False, indent=2))
        elif args.format == 'html':
            for result in results:
                print(result['html_content'])
        else:  # text format
            for result in results:
                print(f"HTML Content:\n{result['html_content']}")

if __name__ == "__main__":
    main()
