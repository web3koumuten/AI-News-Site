"""
TechCrunch Japan scraper
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
    print(f"Import error in techcrunch_scraper: {e}")
    raise


class TechCrunchScraper(BaseScraper):
    """Scraper for TechCrunch Japan"""
    
    def __init__(self):
        super().__init__(SOURCES['techcrunch'])
        self.ai_category_url = SOURCES['techcrunch']['ai_category']
    
    def fetch_articles(self) -> List[Dict]:
        """Fetch AI-related articles from TechCrunch Japan"""
        articles = []
        
        try:
            # Fetch AI category page
            soup = self.fetch_page(self.ai_category_url)
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
                            
                            # Get image URL from article page if not already present
                            if not article_data.get('image_url'):
                                article_soup = self.fetch_page(article_data['url'])
                                if article_soup:
                                    image_url = self._extract_image_url(article_soup)
                                    if image_url:
                                        article_data['image_url'] = image_url
                        
                        parsed_article = self.parse_article(article_data)
                        if parsed_article:
                            articles.append(parsed_article)
            
            # Also check the main page for recent AI articles
            main_page_articles = self._fetch_from_main_page()
            articles.extend(main_page_articles)
            
        except Exception as e:
            print(f"Error fetching TechCrunch articles: {e}")
        
        # Remove duplicates
        unique_articles = {}
        for article in articles:
            url = article.get('url', '')
            if url and url not in unique_articles:
                unique_articles[url] = article
        
        return list(unique_articles.values())
    
    def _fetch_from_main_page(self) -> List[Dict]:
        """Fetch AI articles from main page"""
        articles = []
        
        try:
            soup = self.fetch_page(self.base_url)
            if not soup:
                return articles
            
            # Find all articles and filter for AI-related ones
            article_elements = soup.select('article, .post-block')
            
            ai_keywords = ['ai', '人工知能', '機械学習', 'ディープラーニング', '深層学習',
                          'chatgpt', 'gpt', 'llm', '生成ai', 'openai', 'anthropic',
                          'google ai', 'gemini', 'claude']
            
            for elem in article_elements[:20]:  # Check recent articles
                title_elem = elem.select_one('h2 a, h3 a, .post-block__title a')
                if title_elem:
                    title = title_elem.get_text().lower()
                    if any(keyword in title for keyword in ai_keywords):
                        article_data = self._parse_article_element(elem)
                        if article_data:
                            date = parse_date(article_data.get('date', ''), self.source_name)
                            if date and validate_article_date(date, TIME_WINDOW):
                                self.sleep_between_requests()
                                full_content = self.get_article_content(article_data['url'])
                                if full_content:
                                    article_data['content'] = full_content
                                
                                parsed_article = self.parse_article(article_data)
                                if parsed_article:
                                    articles.append(parsed_article)
            
        except Exception as e:
            print(f"Error fetching TechCrunch main page articles: {e}")
        
        return articles
    
    def _find_article_elements(self, soup):
        """Find article elements on the page"""
        # TechCrunch Japan article selectors
        selectors = [
            'article.post-block',
            '.post-block',
            'article',
            '.river-block'
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
            title_elem = elem.select_one('h2 a, h3 a, .post-block__title a')
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
            date_elem = elem.select_one('time, .post-block__time, .river-block__time')
            if date_elem:
                date_str = date_elem.get('datetime', '') or date_elem.get_text()
            
            # Find summary
            summary = ''
            summary_elem = elem.select_one('.post-block__content, .excerpt, p')
            if summary_elem:
                summary = clean_text(summary_elem.get_text())
            
            # Find image
            image_url = None
            img_elem = elem.select_one('img, .post-block__media img')
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src')
                if image_url:
                    image_url = make_absolute_url(image_url, self.base_url)
            
            # Find category/tags
            category = ''
            category_elem = elem.select_one('.post-block__tag, .category')
            if category_elem:
                category = clean_text(category_elem.get_text())
            
            return {
                'title': title,
                'url': url,
                'date': date_str,
                'summary': summary,
                'category': category,
                'image_url': image_url,
                'content': ''  # Will be fetched separately
            }
            
        except Exception as e:
            print(f"Error parsing TechCrunch article element: {e}")
            return None
    
    def get_article_content(self, url: str) -> Optional[str]:
        """Override to handle TechCrunch Japan specific content extraction"""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # TechCrunch Japan specific content selectors
        content_selectors = [
            '.article-content',
            '.entry-content',
            '[itemprop="articleBody"]',
            '.post-content',
            'article .content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove unwanted elements
                for elem in content_elem.select('script, style, .ad, .newsletter-signup, .related-articles'):
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
        # TechCrunch Japan specific image selectors
        selectors = [
            'meta[property="og:image"]',
            '.article-featured-image img',
            '.featured-image img',
            'article img'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                if elem.name == 'meta':
                    img_url = elem.get('content')
                else:
                    img_url = elem.get('src') or elem.get('data-src')
                
                if img_url:
                    return make_absolute_url(img_url, self.base_url)
        
        return None