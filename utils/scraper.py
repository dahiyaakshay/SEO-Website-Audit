import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urlparse, urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebScraper:
    """Utility for scraping website content"""
    
    def __init__(self, url, headers=None, timeout=10):
        """
        Initialize the web scraper
        
        Args:
            url (str): The URL to scrape
            headers (dict, optional): Custom headers for the request
            timeout (int, optional): Request timeout in seconds
        """
        self.url = url
        self.timeout = timeout
        
        # Set default headers to mimic a browser
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Parse the URL
        self.parsed_url = urlparse(url)
        self.domain = self.parsed_url.netloc
        self.scheme = self.parsed_url.scheme
        self.base_url = f"{self.scheme}://{self.domain}"
    
    def scrape(self):
        """
        Scrape the webpage content
        
        Returns:
            BeautifulSoup: Parsed HTML content
        """
        try:
            logger.info(f"Scraping URL: {self.url}")
            start_time = time.time()
            
            # Send HTTP request
            response = requests.get(
                self.url, 
                headers=self.headers, 
                timeout=self.timeout
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Log request time
            request_time = time.time() - start_time
            logger.info(f"Request completed in {request_time:.2f} seconds")
            
            # Get content type
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type.lower():
                logger.warning(f"URL is not HTML content (Content-Type: {content_type})")
            
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Add base URL to make relative links absolute
            base_tag = soup.find('base')
            base_href = base_tag.get('href') if base_tag else self.base_url
            
            # Update all relative links to absolute
            for tag in soup.find_all(['a', 'img', 'link', 'script']):
                if tag.has_attr('href'):
                    tag['href'] = urljoin(base_href, tag['href'])
                elif tag.has_attr('src'):
                    tag['src'] = urljoin(base_href, tag['src'])
            
            return soup
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping URL: {str(e)}")
            raise
    
    def get_all_links(self, soup=None):
        """
        Extract all links from the page
        
        Args:
            soup (BeautifulSoup, optional): Already parsed content
            
        Returns:
            dict: Dictionary of internal and external links
        """
        if not soup:
            soup = self.scrape()
        
        internal_links = []
        external_links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            
            # Skip empty, javascript, and anchor links
            if not href or href.startswith(('#', 'javascript:', 'mailto:')):
                continue
            
            # Make URL absolute if it's relative
            absolute_url = urljoin(self.url, href)
            
            # Parse the URL
            parsed_href = urlparse(absolute_url)
            
            # Check if internal or external
            if parsed_href.netloc == self.domain:
                internal_links.append({
                    'url': absolute_url,
                    'text': a_tag.get_text(strip=True) or '[No Text]',
                    'nofollow': 'nofollow' in a_tag.get('rel', [])
                })
            else:
                external_links.append({
                    'url': absolute_url,
                    'text': a_tag.get_text(strip=True) or '[No Text]',
                    'nofollow': 'nofollow' in a_tag.get('rel', [])
                })
        
        return {
            'internal': internal_links,
            'external': external_links
        }
    
    def get_images(self, soup=None):
        """
        Extract all images from the page
        
        Args:
            soup (BeautifulSoup, optional): Already parsed content
            
        Returns:
            list: List of image info dictionaries
        """
        if not soup:
            soup = self.scrape()
        
        images = []
        
        for img_tag in soup.find_all('img'):
            # Get image source (handle both src and data-src)
            src = img_tag.get('src') or img_tag.get('data-src')
            if not src:
                continue
            
            # Make relative URLs absolute
            absolute_url = urljoin(self.url, src)
            
            # Get alt text and dimensions if available
            alt_text = img_tag.get('alt', '')
            width = img_tag.get('width', '')
            height = img_tag.get('height', '')
            
            images.append({
                'url': absolute_url,
                'alt_text': alt_text,
                'width': width,
                'height': height
            })
        
        return images
    
    def get_meta_tags(self, soup=None):
        """
        Extract meta tags from the page
        
        Args:
            soup (BeautifulSoup, optional): Already parsed content
            
        Returns:
            dict: Dictionary of meta tags by category
        """
        if not soup:
            soup = self.scrape()
        
        meta_tags = {
            'general': [],
            'opengraph': [],
            'twitter': []
        }
        
        # Get all meta tags
        for meta in soup.find_all('meta'):
            if meta.get('property') and meta['property'].startswith('og:'):
                # OpenGraph meta tags
                meta_tags['opengraph'].append({
                    'property': meta['property'],
                    'content': meta.get('content', '')
                })
            elif meta.get('name') and meta['name'].startswith('twitter:'):
                # Twitter meta tags
                meta_tags['twitter'].append({
                    'name': meta['name'],
                    'content': meta.get('content', '')
                })
            elif meta.get('name'):
                # General meta tags
                meta_tags['general'].append({
                    'name': meta['name'],
                    'content': meta.get('content', '')
                })
        
        return meta_tags
    
    def get_headers(self, soup=None):
        """
        Extract heading structure from the page
        
        Args:
            soup (BeautifulSoup, optional): Already parsed content
            
        Returns:
            dict: Dictionary of headings by level
        """
        if not soup:
            soup = self.scrape()
        
        headings = {
            'h1': [],
            'h2': [],
            'h3': [],
            'h4': [],
            'h5': [],
            'h6': []
        }
        
        for level in range(1, 7):
            tag = f'h{level}'
            for heading in soup.find_all(tag):
                headings[tag].append(heading.get_text(strip=True))
        
        return headings
    
    def take_screenshot(self):
        """
        Take a screenshot of the webpage (placeholder - would require headless browser)
        
        Returns:
            str: Message that this feature requires browser integration
        """
        return "Screenshot functionality requires browser integration (Selenium/Playwright)"
