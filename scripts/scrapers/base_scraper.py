"""
Base scraper class for AI Updates 72
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re
import sys
import os

# Add the parent directory to the Python path to enable imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import DEFAULT_HEADERS, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY
    from utils import (
        safe_request, clean_text, extract_summary, generate_id,
        parse_date, is_ai_tool, detect_pricing_type, categorize_content,
        extract_image_url, extract_tags, make_absolute_url, validate_article_date
    )
except ImportError as e:
    print(f"Import error in base_scraper: {e}")
    raise


class BaseScraper(ABC):
    """Base class for all scrapers"""
    
    def __init__(self, source_config: Dict):
        self.source_name = source_config['name']
        self.base_url = source_config['base_url']
        self.categories = source_config.get('categories', [])
        self.headers = DEFAULT_HEADERS.copy()
        
    @abstractmethod
    def fetch_articles(self) -> List[Dict]:
        """Fetch articles from the source"""
        pass
    
    def parse_article(self, article_data: Dict) -> Optional[Dict]:
        """
        Parse article data into standardized format
        """
        try:
            # Basic required fields
            title = clean_text(article_data.get('title', ''))
            url = article_data.get('url', '')
            
            if not title or not url:
                return None
            
            # Parse date
            date = parse_date(article_data.get('date', ''), self.source_name)
            if not date:
                return None
            
            # Get content for analysis
            content = article_data.get('content', '')
            summary = article_data.get('summary') or extract_summary(content)
            
            # Determine if it's a tool or news
            if is_ai_tool(title, content):
                return self._create_tool_item(article_data, title, url, summary, date)
            else:
                return self._create_news_item(article_data, title, url, summary, date)
                
        except Exception as e:
            print(f"Error parsing article: {e}")
            return None
    
    def _create_tool_item(self, article_data: Dict, title: str, url: str, 
                         summary: str, date: datetime) -> Dict:
        """Create a tool item"""
        content = article_data.get('content', '')
        pricing_type, starting_price = detect_pricing_type(content)
        
        return {
            'type': 'tool',
            'id': generate_id(url, title),
            'name': title,
            'description': summary,
            'category': categorize_content(title, content),
            'url': url,
            'logo': article_data.get('image_url'),
            'features': self._extract_features(content),
            'pricing': {
                'type': pricing_type,
                'startingPrice': starting_price
            },
            'updatedAt': date.isoformat()
        }
    
    def _create_news_item(self, article_data: Dict, title: str, url: str,
                         summary: str, date: datetime) -> Dict:
        """Create a news item"""
        content = article_data.get('content', '')
        
        return {
            'type': 'news',
            'id': generate_id(url, title),
            'title': title,
            'summary': summary,
            'source': self.source_name,
            'url': url,
            'publishedAt': date.isoformat(),
            'category': categorize_content(title, content),
            'imageUrl': article_data.get('image_url'),
            'tags': extract_tags(title, content)
        }
    
    def _extract_features(self, content: str) -> List[str]:
        """Extract feature list from content"""
        features = []
        
        # Look for bullet points or feature lists
        feature_patterns = [
            r'[・•]\s*(.+?)(?=[・•\n]|$)',
            r'[-*]\s*(.+?)(?=[-*\n]|$)',
            r'\d+[.)]\s*(.+?)(?=\d+[.)]|\n|$)'
        ]
        
        for pattern in feature_patterns:
            matches = re.findall(pattern, content)
            for match in matches[:5]:  # Limit to 5 features
                feature = clean_text(match)
                if len(feature) > 10 and len(feature) < 100:
                    features.append(feature)
        
        return features
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page"""
        response = safe_request(url, self.headers, REQUEST_TIMEOUT, MAX_RETRIES)
        if response:
            return BeautifulSoup(response.content, 'html.parser')
        return None
    
    def get_article_content(self, url: str) -> Optional[str]:
        """Fetch full article content"""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # Common article content selectors
        content_selectors = [
            'article',
            '[role="main"]',
            '.article-body',
            '.article-content',
            '.entry-content',
            '.post-content',
            '.content-main',
            'main'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove script and style elements
                for elem in content_elem.select('script, style'):
                    elem.decompose()
                
                return clean_text(content_elem.get_text())
        
        return None
    
    def sleep_between_requests(self):
        """Add delay between requests to be respectful"""
        time.sleep(1)