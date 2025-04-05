#!/usr/bin/env python3
"""
Web UI for the lyrics scraper using Flask
"""

from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import json
import os

app = Flask(__name__)

# Ensure templates directory exists
os.makedirs('templates', exist_ok=True)

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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all divs with data-lyrics-container="true"
        lyrics_containers = soup.find_all('div', attrs={'data-lyrics-container': 'true'})
        
        # Extract the HTML content from each container
        results = []
        for i, container in enumerate(lyrics_containers, 1):
            results.append({
                'container_number': i,
                'html_content': str(container),
                'text_content': container.get_text(strip=True)
            })
            
        return results, None
        
    except requests.exceptions.RequestException as e:
        return [], f"Error during request: {e}"
    except Exception as e:
        return [], f"Unexpected error: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'})
    
    results, error = scrape_lyrics_containers(url)
    
    if error:
        return jsonify({'error': error})
    
    if not results:
        return jsonify({'error': 'No divs with data-lyrics-container="true" found on the page'})
    
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True)
