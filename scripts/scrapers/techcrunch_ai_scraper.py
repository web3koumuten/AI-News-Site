"""
TechCrunch AI Scraper for AI Updates 72
Focuses on AI tool launches, updates, and releases from TechCrunch
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


class TechCrunchAIScraper(BaseScraper):
    """Scraper for TechCrunch AI articles"""
    
    def __init__(self):
        source_config = {
            'name': 'TechCrunch',
            'base_url': 'https://techcrunch.com',
            'categories': ['ai_tools', 'startups', 'technology']
        }
        super().__init__(source_config)
        
        # AI tool release keywords
        self.ai_tool_keywords = [
            'launches', 'releases', 'unveils', 'announces', 'debuts', 'introduces',
            'open sources', 'beta', 'early access', 'new ai', 'ai tool', 'ai platform',
            'generative ai', 'chatgpt', 'claude', 'gemini', 'copilot', 'midjourney',
            'ai coding', 'ai assistant', 'ai model', 'llm', 'machine learning tool'
        ]
        
        # Company/product keywords for AI tools
        self.ai_companies = [
            'openai', 'anthropic', 'google', 'microsoft', 'adobe', 'nvidia',
            'stability ai', 'hugging face', 'cohere', 'ai21', 'replicate',
            'github', 'figma', 'notion', 'discord', 'slack'
        ]
    
    def fetch_articles(self) -> List[Dict]:
        """Fetch AI tool articles from TechCrunch"""
        articles = []
        
        try:
            # Search for AI-related articles
            search_terms = ['ai tool', 'artificial intelligence', 'generative ai', 'machine learning']
            
            for term in search_terms:
                print(f"Searching TechCrunch for: {term}")
                search_articles = self._search_articles(term)
                articles.extend(search_articles)
                time.sleep(2)
            
            # Also scrape AI category page
            ai_category_url = f"{self.base_url}/category/artificial-intelligence/"
            print(f"Scraping TechCrunch AI category...")
            category_articles = self._scrape_category_page(ai_category_url)
            articles.extend(category_articles)
            
            # Filter for actual tool releases
            tool_articles = self._filter_tool_releases(articles)
            print(f"Found {len(tool_articles)} AI tool release articles from TechCrunch")
            
            return tool_articles
            
        except Exception as e:
            print(f"Error in TechCrunch AI scraper: {e}")
            return []
    
    def _search_articles(self, search_term: str) -> List[Dict]:
        """Search TechCrunch for articles"""
        search_url = f"{self.base_url}/wp-json/tc/v1/search"
        params = {
            'query': search_term,
            'limit': 20,
            'page': 1
        }
        
        try:
            response = safe_request(search_url, self.headers, params=params)
            if not response:
                return []
            
            data = response.json()
            articles = []
            
            for item in data.get('posts', []):
                article_data = self._extract_search_result(item)
                if article_data:
                    articles.append(article_data)
            
            return articles
            
        except Exception as e:
            print(f"Error searching TechCrunch: {e}")
            return []
    
    def _scrape_category_page(self, url: str) -> List[Dict]:
        """Scrape TechCrunch category page"""
        soup = self.fetch_page(url)
        if not soup:
            return []
        
        articles = []
        
        # Find article elements
        article_elements = soup.find_all(['article', 'div'], class_=re.compile(r'.*post.*|.*article.*'))
        
        for element in article_elements:
            try:
                article_data = self._extract_article_data(element)
                if article_data:
                    articles.append(article_data)
            except Exception as e:
                continue
        
        return articles
    
    def _extract_search_result(self, item: Dict) -> Optional[Dict]:
        """Extract article data from search API result"""
        try:
            title = clean_text(item.get('title', ''))
            url = item.get('permalink', '')
            excerpt = clean_text(item.get('excerpt', ''))
            
            if not title or not url:
                return None
            
            # Parse date
            date_str = item.get('date', '')
            parsed_date = parse_date(date_str, 'TechCrunch')
            
            if not parsed_date or not self._is_within_time_window(parsed_date):
                return None
            
            # Get featured image
            image_url = None
            if 'featured_image' in item and item['featured_image']:
                image_url = item['featured_image'].get('src')
            
            return {
                'title': title,
                'url': url,
                'content': excerpt,
                'summary': excerpt,
                'date': parsed_date.isoformat(),
                'image_url': image_url
            }
            
        except Exception as e:
            print(f"Error extracting search result: {e}")
            return None
    
    def _extract_article_data(self, element) -> Optional[Dict]:
        """Extract article data from HTML element"""
        try:
            # Find title
            title_elem = element.find(['h1', 'h2', 'h3'], class_=re.compile(r'.*title.*|.*headline.*'))
            if not title_elem:
                title_elem = element.find('a')
            
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
            
            # Get excerpt/summary
            excerpt_elem = element.find(['p', 'div'], class_=re.compile(r'.*excerpt.*|.*summary.*'))
            excerpt = clean_text(excerpt_elem.get_text()) if excerpt_elem else ""
            
            # Get image
            img_elem = element.find('img')
            image_url = img_elem.get('src') if img_elem else None
            
            # Get date
            date_elem = element.find(['time', 'span'], class_=re.compile(r'.*date.*|.*time.*'))
            if date_elem:
                date_str = date_elem.get('datetime') or date_elem.get_text()
                parsed_date = parse_date(date_str, 'TechCrunch')
            else:
                parsed_date = datetime.now(JST)
            
            if not self._is_within_time_window(parsed_date):
                return None
            
            return {
                'title': title,
                'url': url,
                'content': excerpt,
                'summary': excerpt,
                'date': parsed_date.isoformat(),
                'image_url': image_url
            }
            
        except Exception as e:
            print(f"Error extracting article data: {e}")
            return None
    
    def _is_within_time_window(self, date: datetime) -> bool:
        """Check if date is within our time window"""
        cutoff = datetime.now(JST) - TIME_WINDOW
        return date >= cutoff
    
    def _filter_tool_releases(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles to focus on AI tool releases"""
        tool_articles = []
        
        for article in articles:
            title = article.get('title', '').lower()
            content = article.get('content', '').lower()
            
            # Check for tool release keywords
            has_release_keyword = any(keyword in title or keyword in content 
                                    for keyword in self.ai_tool_keywords)
            
            # Check for AI company mentions
            has_ai_company = any(company in title or company in content 
                               for company in self.ai_companies)
            
            # Check for specific tool indicators
            tool_indicators = [
                'new feature', 'update', 'version', 'api', 'beta', 'plugin',
                'extension', 'integration', 'platform', 'service', 'tool'
            ]
            has_tool_indicator = any(indicator in title or indicator in content 
                                   for indicator in tool_indicators)
            
            if (has_release_keyword or has_ai_company) and has_tool_indicator:
                # Fetch full article content for better analysis
                full_content = self.get_article_content(article['url'])
                if full_content:
                    article['content'] = full_content
                    article['summary'] = extract_summary(full_content)
                
                # Mark as tool if it looks like a tool announcement
                if self._is_tool_announcement(article):
                    article['type'] = 'tool'
                else:
                    article['type'] = 'news'
                
                tool_articles.append(article)
        
        return tool_articles
    
    def _is_tool_announcement(self, article: Dict) -> bool:
        """Determine if article is about a tool announcement vs just news"""
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        
        # Strong indicators it's a tool announcement
        tool_announcement_keywords = [
            'launches', 'releases', 'unveils', 'announces', 'debuts',
            'introduces', 'open sources', 'now available', 'beta launch'
        ]
        
        # Check if it's announcing a specific tool/product
        has_announcement = any(keyword in title for keyword in tool_announcement_keywords)
        
        # Check for product-specific language
        product_language = [
            'pricing', 'free tier', 'subscription', 'api access', 'features',
            'capabilities', 'how to use', 'getting started', 'download'
        ]
        has_product_info = any(lang in content for lang in product_language)
        
        return has_announcement or has_product_info


# Source configuration for main scraper
TECHCRUNCH_AI_CONFIG = {
    'name': 'TechCrunch AI',
    'base_url': 'https://techcrunch.com',
    'categories': ['ai_tools', 'startups', 'technology']
}