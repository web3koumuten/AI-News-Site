"""
AI-SCHOLAR scraper - RSS based
"""
import feedparser
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
    print(f"Import error in ai_scholar_scraper: {e}")
    raise


class AIScholarScraper(BaseScraper):
    """Scraper for AI-SCHOLAR RSS feed"""
    
    def __init__(self):
        super().__init__(SOURCES['ai_scholar'])
        self.rss_url = SOURCES['ai_scholar']['rss_url']
    
    def fetch_articles(self) -> List[Dict]:
        """Fetch articles from AI-SCHOLAR RSS feed"""
        articles = []
        
        try:
            # Parse RSS feed
            feed = feedparser.parse(self.rss_url)
            
            if not feed.entries:
                print(f"No entries found in AI-SCHOLAR RSS feed")
                return articles
            
            for entry in feed.entries:
                article_data = self._parse_rss_entry(entry)
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
                
        except Exception as e:
            print(f"Error fetching AI-SCHOLAR articles: {e}")
        
        return articles
    
    def _parse_rss_entry(self, entry) -> Optional[Dict]:
        """Parse RSS feed entry"""
        try:
            # Extract basic info
            title = clean_text(entry.get('title', ''))
            url = entry.get('link', '')
            
            if not title or not url:
                return None
            
            # Extract date
            date_str = entry.get('published', '') or entry.get('updated', '')
            
            # Extract summary
            summary = ''
            if hasattr(entry, 'summary'):
                summary = clean_text(entry.summary)
            elif hasattr(entry, 'description'):
                summary = clean_text(entry.description)
            
            # Extract category
            categories = []
            if hasattr(entry, 'tags'):
                categories = [tag.term for tag in entry.tags]
            
            return {
                'title': title,
                'url': url,
                'date': date_str,
                'summary': summary,
                'categories': categories,
                'content': ''  # Will be fetched separately
            }
            
        except Exception as e:
            print(f"Error parsing RSS entry: {e}")
            return None
    
    def get_article_content(self, url: str) -> Optional[str]:
        """Override to handle AI-SCHOLAR specific content extraction"""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # AI-SCHOLAR specific content selectors
        content_selectors = [
            '.entry-content',
            '.post-content',
            '.article-body',
            'article',
            '.content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove unwanted elements
                for elem in content_elem.select('script, style, .related-articles, .ads, .social-share'):
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
        # AI-SCHOLAR specific image selectors
        selectors = [
            'meta[property="og:image"]',
            'meta[name="twitter:image"]',
            '.entry-content img',
            '.post-thumbnail img',
            '.featured-image img'
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