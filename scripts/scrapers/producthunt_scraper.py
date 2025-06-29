"""
Product Hunt AI Tools Scraper for AI Updates 72
Focuses on AI tool launches and updates from Product Hunt
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re
import time
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from utils import (
    safe_request, clean_text, generate_id, categorize_content,
    extract_summary, parse_date, JST, TIME_WINDOW
)


class ProductHuntScraper(BaseScraper):
    """Scraper for Product Hunt AI tools"""
    
    def __init__(self):
        source_config = {
            'name': 'Product Hunt',
            'base_url': 'https://www.producthunt.com',
            'categories': ['ai_tools', 'productivity', 'developer_tools']
        }
        super().__init__(source_config)
        
        # AI-related keywords for filtering
        self.ai_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'ml', 'gpt', 'chatbot',
            'automation', 'generative', 'neural', 'llm', 'openai', 'claude', 'gemini',
            'midjourney', 'stable diffusion', 'dalle', 'copilot', 'code assistant',
            'ai coding', 'ai writing', 'ai image', 'ai video', 'voice ai', 'speech'
        ]
        
        # Tool-specific indicators
        self.tool_indicators = [
            'launch', 'release', 'new tool', 'app', 'platform', 'extension',
            'plugin', 'api', 'beta', 'early access', 'free trial', 'pricing'
        ]
    
    def fetch_articles(self) -> List[Dict]:
        """Fetch AI tool articles from Product Hunt"""
        articles = []
        
        try:
            # Fetch from AI category and trending
            urls_to_scrape = [
                f"{self.base_url}/topics/artificial-intelligence",
                f"{self.base_url}/topics/developer-tools",
                f"{self.base_url}/topics/productivity"
            ]
            
            for url in urls_to_scrape:
                print(f"Scraping {url}...")
                page_articles = self._scrape_category_page(url)
                articles.extend(page_articles)
                time.sleep(2)  # Be respectful
            
            # Filter for AI-related tools
            ai_articles = self._filter_ai_tools(articles)
            print(f"Found {len(ai_articles)} AI tool articles from Product Hunt")
            
            return ai_articles
            
        except Exception as e:
            print(f"Error in Product Hunt scraper: {e}")
            return []
    
    def _scrape_category_page(self, url: str) -> List[Dict]:
        """Scrape a Product Hunt category page"""
        soup = self.fetch_page(url)
        if not soup:
            return []
        
        articles = []
        
        # Find product cards
        product_cards = soup.find_all(['div', 'article'], class_=re.compile(r'.*product.*|.*post.*'))
        
        for card in product_cards:
            try:
                article_data = self._extract_product_data(card)
                if article_data:
                    articles.append(article_data)
            except Exception as e:
                print(f"Error extracting product data: {e}")
                continue
        
        return articles
    
    def _extract_product_data(self, card) -> Optional[Dict]:
        """Extract product data from a Product Hunt card"""
        try:
            # Find title/name
            title_elem = card.find(['h3', 'h2', 'a'], class_=re.compile(r'.*title.*|.*name.*'))
            if not title_elem:
                title_elem = card.find('a')
            
            if not title_elem:
                return None
            
            title = clean_text(title_elem.get_text())
            
            # Get URL
            link_elem = title_elem if title_elem.name == 'a' else title_elem.find('a')
            if not link_elem:
                return None
            
            href = link_elem.get('href', '')
            if href.startswith('/'):
                url = self.base_url + href
            else:
                url = href
            
            # Get description
            desc_elem = card.find(['p', 'div'], class_=re.compile(r'.*description.*|.*tagline.*'))
            description = clean_text(desc_elem.get_text()) if desc_elem else ""
            
            # Get image
            img_elem = card.find('img')
            image_url = img_elem.get('src') if img_elem else None
            
            # Get date (Product Hunt shows launch date)
            date_elem = card.find(['time', 'span'], class_=re.compile(r'.*date.*|.*time.*'))
            date_str = date_elem.get_text() if date_elem else ""
            
            # Check if it's recent enough
            parsed_date = self._parse_product_hunt_date(date_str)
            if not parsed_date or not self._is_within_time_window(parsed_date):
                return None
            
            return {
                'title': title,
                'url': url,
                'content': description,
                'summary': description,
                'date': parsed_date.isoformat(),
                'image_url': image_url
            }
            
        except Exception as e:
            print(f"Error extracting product data: {e}")
            return None
    
    def _parse_product_hunt_date(self, date_str: str) -> Optional[datetime]:
        """Parse Product Hunt date string"""
        if not date_str:
            return datetime.now(JST)  # Default to now if no date
        
        # Product Hunt uses relative dates like "2 days ago"
        now = datetime.now(JST)
        
        if 'today' in date_str.lower():
            return now
        elif 'yesterday' in date_str.lower():
            return now - timedelta(days=1)
        elif 'days ago' in date_str.lower():
            days_match = re.search(r'(\d+)\s+days?\s+ago', date_str.lower())
            if days_match:
                days = int(days_match.group(1))
                return now - timedelta(days=days)
        elif 'hours ago' in date_str.lower():
            hours_match = re.search(r'(\d+)\s+hours?\s+ago', date_str.lower())
            if hours_match:
                hours = int(hours_match.group(1))
                return now - timedelta(hours=hours)
        
        return now  # Default fallback
    
    def _is_within_time_window(self, date: datetime) -> bool:
        """Check if date is within our time window"""
        cutoff = datetime.now(JST) - TIME_WINDOW
        return date >= cutoff
    
    def _filter_ai_tools(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles to only include AI-related tools"""
        ai_articles = []
        
        for article in articles:
            title = article.get('title', '').lower()
            content = article.get('content', '').lower()
            
            # Check for AI keywords
            has_ai_keyword = any(keyword in title or keyword in content 
                               for keyword in self.ai_keywords)
            
            # Check for tool indicators
            has_tool_indicator = any(indicator in title or indicator in content 
                                   for indicator in self.tool_indicators)
            
            if has_ai_keyword and has_tool_indicator:
                # Mark as tool type
                article['type'] = 'tool'
                ai_articles.append(article)
        
        return ai_articles


# Source configuration for main scraper
PRODUCTHUNT_CONFIG = {
    'name': 'Product Hunt',
    'base_url': 'https://www.producthunt.com',
    'categories': ['ai_tools', 'productivity', 'developer_tools']
}