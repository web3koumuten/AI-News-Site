"""
Nikkei AI scraper - search based
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
    print(f"Import error in nikkei_ai_scraper: {e}")
    raise


class NikkeiAIScraper(BaseScraper):
    """Scraper for Nikkei AI articles"""
    
    def __init__(self):
        super().__init__(SOURCES['nikkei_ai'])
        self.search_url = SOURCES['nikkei_ai']['search_url']
    
    def fetch_articles(self) -> List[Dict]:
        """Fetch articles from Nikkei AI search"""
        articles = []
        
        try:
            # Scrape search results
            search_articles = self._scrape_search_results()
            articles.extend(search_articles)
            
        except Exception as e:
            print(f"Error fetching Nikkei articles: {e}")
        
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
                        
                # Limit for performance and politeness
                if len(articles) >= 5:
                    break
        
        return articles
    
    def _find_search_result_elements(self, soup):
        """Find search result elements"""
        selectors = [
            '.cmn-list_item',
            '.search-result',
            '.result-item',
            '.article-item',
            'li[class*="result"]',
            '.news-list li'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                return elements[:10]  # Limit for performance
        
        # Fallback to article links
        return soup.select('a[href*="/article/"]')[:10]
    
    def _parse_search_result_element(self, elem) -> Optional[Dict]:
        """Parse search result element"""
        try:
            # Find title and URL
            if elem.name == 'a':
                title = clean_text(elem.get_text())
                url = elem.get('href', '')
            else:
                title_elem = elem.select_one('a[href], h1, h2, h3, .title, .headline')
                if not title_elem:
                    return None
                title = clean_text(title_elem.get_text())
                url = title_elem.get('href', '') if title_elem.name == 'a' else ''
                if not url:
                    link_elem = elem.select_one('a[href]')
                    if link_elem:
                        url = link_elem.get('href', '')
            
            if not title or not url:
                return None
            
            # Make URL absolute
            url = make_absolute_url(url, self.base_url)
            
            # Find date
            date_str = ''
            date_elem = elem.select_one('time, .date, .published, .timestamp, .news-date')
            if date_elem:
                date_str = date_elem.get('datetime', '') or date_elem.get_text()
            
            # Find summary
            summary = ''
            summary_elem = elem.select_one('.summary, .excerpt, .description, .lead, p')
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
            print(f"Error parsing Nikkei search result element: {e}")
            return None
    
    def get_article_content(self, url: str) -> Optional[str]:
        """Override to handle Nikkei specific content extraction"""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # Nikkei specific content selectors
        content_selectors = [
            '.article-body',
            '.article-content',
            '.content',
            '.article-text',
            'article',
            '.news-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove unwanted elements
                for elem in content_elem.select('script, style, .ad, .share, .related, .navigation, .recommend'):
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
            '.news-image img',
            '.main-image img'
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