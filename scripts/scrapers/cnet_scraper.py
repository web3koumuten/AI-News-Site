"""
CNET Japan scraper
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
    print(f"Import error in cnet_scraper: {e}")
    raise


class CNETScraper(BaseScraper):
    """Scraper for CNET Japan"""
    
    def __init__(self):
        super().__init__(SOURCES['cnet'])
        self.ai_section = SOURCES['cnet']['ai_section']
        self.rss_url = SOURCES['cnet']['rss_url']
    
    def fetch_articles(self) -> List[Dict]:
        """Fetch AI-related articles from CNET Japan"""
        articles = []
        
        # Try RSS feed first
        rss_articles = self._fetch_from_rss()
        articles.extend(rss_articles)
        
        # Also scrape AI section
        section_articles = self._fetch_from_ai_section()
        articles.extend(section_articles)
        
        # Remove duplicates based on URL
        unique_articles = {}
        for article in articles:
            url = article.get('url', '')
            if url and url not in unique_articles:
                unique_articles[url] = article
        
        return list(unique_articles.values())
    
    def _fetch_from_rss(self) -> List[Dict]:
        """Fetch articles from RSS feed"""
        articles = []
        
        try:
            feed = feedparser.parse(self.rss_url)
            
            if not feed.entries:
                return articles
            
            for entry in feed.entries:
                # Check if it's AI-related
                title = entry.get('title', '').lower()
                summary = entry.get('summary', '').lower()
                
                ai_keywords = ['ai', '人工知能', '機械学習', 'ディープラーニング', '深層学習', 
                             'chatgpt', 'gpt', 'llm', '生成ai']
                
                if not any(keyword in title + summary for keyword in ai_keywords):
                    continue
                
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
            print(f"Error fetching CNET RSS articles: {e}")
        
        return articles
    
    def _fetch_from_ai_section(self) -> List[Dict]:
        """Fetch articles from AI section"""
        articles = []
        
        try:
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
            print(f"Error fetching CNET AI section articles: {e}")
        
        return articles
    
    def _parse_rss_entry(self, entry) -> Optional[Dict]:
        """Parse RSS feed entry"""
        try:
            title = clean_text(entry.get('title', ''))
            url = entry.get('link', '')
            
            if not title or not url:
                return None
            
            date_str = entry.get('published', '') or entry.get('updated', '')
            summary = clean_text(entry.get('summary', ''))
            
            return {
                'title': title,
                'url': url,
                'date': date_str,
                'summary': summary,
                'content': ''  # Will be fetched separately
            }
            
        except Exception as e:
            print(f"Error parsing CNET RSS entry: {e}")
            return None
    
    def _find_article_elements(self, soup):
        """Find article elements on the page"""
        # CNET Japan article selectors
        selectors = [
            '.c-articleList__item',
            '.article-list li',
            '.content-list article',
            '.news-list li'
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
            date_elem = elem.select_one('.date, time, .timestamp')
            if date_elem:
                date_str = date_elem.get_text()
            
            # Find summary
            summary = ''
            summary_elem = elem.select_one('.summary, .description, p')
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
            print(f"Error parsing CNET article element: {e}")
            return None
    
    def get_article_content(self, url: str) -> Optional[str]:
        """Override to handle CNET Japan specific content extraction"""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # CNET Japan specific content selectors
        content_selectors = [
            '.article-body',
            '.article-content',
            '.content-main',
            '[itemprop="articleBody"]',
            '.entry-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove unwanted elements
                for elem in content_elem.select('script, style, .ad, .banner, .related-articles'):
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
        # CNET Japan specific image selectors
        selectors = [
            'meta[property="og:image"]',
            '.article-image img',
            '.main-visual img',
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