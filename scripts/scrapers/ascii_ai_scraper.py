"""
ASCII.jp AI scraper - search based
"""
from datetime import datetime
from typing import List, Dict, Optional
import sys
import os
import urllib.parse

# Add the parent directory to the Python path to enable imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from scrapers.base_scraper import BaseScraper
    from config import SOURCES, TIME_WINDOW
    from utils import clean_text, parse_date, extract_summary, make_absolute_url, validate_article_date
except ImportError as e:
    print(f"Import error in ascii_ai_scraper: {e}")
    raise


class ASCIIAIScraper(BaseScraper):
    """Scraper for ASCII.jp AI articles"""
    
    def __init__(self):
        super().__init__(SOURCES['ascii_ai'])
        self.search_url = SOURCES['ascii_ai']['search_url']
        self.ai_section = SOURCES['ascii_ai'].get('ai_section')
    
    def fetch_articles(self) -> List[Dict]:
        """Fetch articles from ASCII.jp AI section and search"""
        articles = []
        
        try:
            # First try AI section if available
            if self.ai_section:
                section_articles = self._scrape_ai_section()
                articles.extend(section_articles)
            
            # Then try search results
            search_articles = self._scrape_search_results()
            articles.extend(search_articles)
            
        except Exception as e:
            print(f"Error fetching ASCII.jp articles: {e}")
        
        return articles
    
    def _scrape_ai_section(self) -> List[Dict]:
        """Scrape articles from AI section"""
        articles = []
        
        soup = self.fetch_page(self.ai_section)
        if not soup:
            return articles
        
        # Find article elements
        article_elements = self._find_article_elements(soup)
        
        for elem in article_elements:
            article_data = self._parse_article_element(elem)
            if article_data:
                # Check if article is within time window
                date = parse_date(article_data.get('date', ''), self.source_name)
                if date and validate_article_date(date, TIME_WINDOW):
                    # Fetch full article content
                    self.sleep_between_requests()
                    full_content = self.get_article_content(article_data['url'])
                    if full_content:
                        article_data['content'] = full_content
                    
                    parsed_article = self.parse_article(article_data)
                    if parsed_article:
                        articles.append(parsed_article)
        
        return articles
    
    def _scrape_search_results(self) -> List[Dict]:
        """Scrape articles from search results"""
        articles = []
        
        soup = self.fetch_page(self.search_url)
        if not soup:
            return articles
        
        # Find search result elements
        result_elements = self._find_search_result_elements(soup)
        
        for elem in result_elements:
            article_data = self._parse_search_result_element(elem)
            if article_data:
                # Check if article is within time window
                date = parse_date(article_data.get('date', ''), self.source_name)
                if date and validate_article_date(date, TIME_WINDOW):
                    # Fetch full article content
                    self.sleep_between_requests()
                    full_content = self.get_article_content(article_data['url'])
                    if full_content:
                        article_data['content'] = full_content
                    
                    parsed_article = self.parse_article(article_data)
                    if parsed_article:
                        articles.append(parsed_article)
        
        return articles
    
    def _find_article_elements(self, soup):
        """Find article elements on the page"""
        selectors = [
            'article',
            '.article-item',
            '.news-item',
            '.content-item',
            '.post'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                return elements
        
        # Fallback to links with article-like patterns
        return soup.select('a[href*="/elem/"]')[:20]  # Limit for performance
    
    def _find_search_result_elements(self, soup):
        """Find search result elements"""
        selectors = [
            '.search-result',
            '.result-item',
            '.search-item',
            'li[class*="result"]',
            '.article-list li'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                return elements
        
        # Fallback to links
        return soup.select('a[href*="/elem/"]')[:20]
    
    def _parse_article_element(self, elem) -> Optional[Dict]:
        """Parse article element"""
        try:
            # Find title and URL
            if elem.name == 'a':
                title = clean_text(elem.get_text())
                url = elem.get('href', '')
            else:
                title_elem = elem.select_one('a[href], h1, h2, h3, .title')
                if not title_elem:
                    return None
                title = clean_text(title_elem.get_text())
                url = title_elem.get('href', '') if title_elem.name == 'a' else elem.select_one('a')
                if hasattr(url, 'get'):
                    url = url.get('href', '')
            
            if not title or not url:
                return None
            
            # Make URL absolute
            url = make_absolute_url(url, self.base_url)
            
            # Find date
            date_str = ''
            date_elem = elem.select_one('time, .date, .published, .timestamp')
            if date_elem:
                date_str = date_elem.get('datetime', '') or date_elem.get_text()
            
            # Find summary
            summary = ''
            summary_elem = elem.select_one('.summary, .excerpt, .description, p')
            if summary_elem:
                summary = clean_text(summary_elem.get_text())
            
            return {
                'title': title,
                'url': url,
                'date': date_str,
                'summary': summary,
                'content': ''  # Will be fetched separately
            }
            
        except Exception as e:
            print(f"Error parsing ASCII.jp article element: {e}")
            return None
    
    def _parse_search_result_element(self, elem) -> Optional[Dict]:
        """Parse search result element"""
        return self._parse_article_element(elem)  # Same logic for now
    
    def get_article_content(self, url: str) -> Optional[str]:
        """Override to handle ASCII.jp specific content extraction"""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # ASCII.jp specific content selectors
        content_selectors = [
            '#newsText',
            '.articleText',
            '.article-body',
            '.content',
            'article',
            '#article'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove unwanted elements
                for elem in content_elem.select('script, style, .ad, .share, .related, .navigation'):
                    elem.decompose()
                
                # Extract text
                text = content_elem.get_text()
                cleaned = clean_text(text)
                
                if len(cleaned) > 100:  # Ensure we have substantial content
                    return cleaned
        
        # Fallback to base implementation
        return super().get_article_content(url)
    
    def _extract_image_url(self, soup) -> Optional[str]:
        """Extract article image URL"""
        selectors = [
            'meta[property="og:image"]',
            'meta[name="twitter:image"]',
            '.article-image img',
            '#newsText img',
            '.articleText img'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                if elem.name == 'meta':
                    img_url = elem.get('content')
                else:
                    img_url = elem.get('src')
                
                if img_url:
                    return make_absolute_url(img_url, self.base_url)
        
        return None