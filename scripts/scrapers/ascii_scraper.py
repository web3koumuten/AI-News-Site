"""
ASCII.jp scraper
"""
from datetime import datetime
from typing import List, Dict, Optional
import sys
import os

# Add the parent directory to the Python path to enable imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from scrapers.base_scraper import BaseScraper
    from config import SOURCES, TIME_WINDOW
    from utils import clean_text, parse_date, extract_summary, make_absolute_url, validate_article_date
except ImportError as e:
    print(f"Import error in ascii_scraper: {e}")
    raise


class ASCIIScraper(BaseScraper):
    """Scraper for ASCII.jp"""
    
    def __init__(self):
        super().__init__(SOURCES['ascii'])
        self.search_url = SOURCES['ascii']['search_url']
    
    def fetch_articles(self) -> List[Dict]:
        """Fetch AI-related articles from ASCII.jp"""
        articles = []
        
        try:
            # Search for AI articles
            soup = self.fetch_page(self.search_url)
            if not soup:
                return articles
            
            # Find article listings
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
                            
                            # Get image URL from article page
                            article_soup = self.fetch_page(article_data['url'])
                            if article_soup:
                                image_url = self._extract_image_url(article_soup)
                                if image_url:
                                    article_data['image_url'] = image_url
                        
                        parsed_article = self.parse_article(article_data)
                        if parsed_article:
                            articles.append(parsed_article)
            
        except Exception as e:
            print(f"Error fetching ASCII articles: {e}")
        
        return articles
    
    def _find_article_elements(self, soup):
        """Find article elements on the page"""
        # ASCII.jp article selectors
        selectors = [
            '.searchList li',
            '.articleList li',
            '.content-list article',
            '.search-result-item'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                return elements
        
        return []
    
    def _parse_article_element(self, elem) -> Optional[Dict]:
        """Parse article element"""
        try:
            # Find title and URL
            title_elem = elem.select_one('h3 a, h2 a, .title a')
            if not title_elem:
                return None
            
            title = clean_text(title_elem.get_text())
            url = title_elem.get('href', '')
            
            if not title or not url:
                return None
            
            # Make URL absolute
            url = make_absolute_url(url, self.base_url)
            
            # Find date
            date_str = ''
            date_elem = elem.select_one('.date, .time, time')
            if date_elem:
                date_str = date_elem.get_text()
            
            # Find summary
            summary = ''
            summary_elem = elem.select_one('.summary, .description, .excerpt, p')
            if summary_elem:
                summary = clean_text(summary_elem.get_text())
            
            # Find category
            category = ''
            category_elem = elem.select_one('.category, .tag')
            if category_elem:
                category = clean_text(category_elem.get_text())
            
            return {
                'title': title,
                'url': url,
                'date': date_str,
                'summary': summary,
                'category': category,
                'content': ''  # Will be fetched separately
            }
            
        except Exception as e:
            print(f"Error parsing ASCII article element: {e}")
            return None
    
    def get_article_content(self, url: str) -> Optional[str]:
        """Override to handle ASCII.jp specific content extraction"""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # ASCII.jp specific content selectors
        content_selectors = [
            '#contents',
            '.contents',
            '.article-body',
            '.article-content',
            'article .text'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove unwanted elements
                for elem in content_elem.select('script, style, .ad, .banner, .related'):
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
        # ASCII.jp specific image selectors
        selectors = [
            'meta[property="og:image"]',
            '.article-image img',
            '.main-image img',
            'article img'
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