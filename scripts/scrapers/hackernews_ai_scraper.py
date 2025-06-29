"""
Hacker News AI Tools Scraper for AI Updates 72
Focuses on AI tool launches and Show HN posts from Hacker News
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re
import time
import json
from .base_scraper import BaseScraper
from utils import (
    safe_request, clean_text, generate_id, categorize_content,
    extract_summary, parse_date, JST, TIME_WINDOW
)


class HackerNewsAIScraper(BaseScraper):
    """Scraper for Hacker News AI tool posts"""
    
    def __init__(self):
        source_config = {
            'name': 'Hacker News',
            'base_url': 'https://hacker-news.firebaseio.com/v0',
            'categories': ['ai_tools', 'show_hn', 'technology']
        }
        super().__init__(source_config)
        
        self.hn_web_url = 'https://news.ycombinator.com'
        
        # AI tool keywords for filtering
        self.ai_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'ml', 'gpt',
            'llm', 'chatbot', 'generative', 'neural', 'openai', 'claude',
            'gemini', 'copilot', 'midjourney', 'stable diffusion', 'dalle',
            'ai coding', 'ai assistant', 'ai tool', 'automation'
        ]
        
        # Show HN indicators for tools
        self.show_hn_keywords = [
            'show hn', 'launch', 'built', 'created', 'made', 'new tool',
            'open source', 'side project', 'weekend project', 'beta'
        ]
        
        # Tool/product indicators
        self.tool_indicators = [
            'app', 'tool', 'platform', 'service', 'api', 'extension',
            'plugin', 'library', 'framework', 'sdk', 'cli', 'dashboard'
        ]
    
    def fetch_articles(self) -> List[Dict]:
        """Fetch AI tool articles from Hacker News"""
        articles = []
        
        try:
            # Get recent stories from different endpoints
            story_types = ['topstories', 'newstories', 'showstories']
            
            for story_type in story_types:
                print(f"Fetching {story_type} from Hacker News...")
                stories = self._fetch_stories(story_type, limit=100)
                articles.extend(stories)
                time.sleep(1)
            
            # Filter for AI-related tool posts
            ai_tool_articles = self._filter_ai_tools(articles)
            print(f"Found {len(ai_tool_articles)} AI tool articles from Hacker News")
            
            return ai_tool_articles
            
        except Exception as e:
            print(f"Error in Hacker News AI scraper: {e}")
            return []
    
    def _fetch_stories(self, story_type: str, limit: int = 100) -> List[Dict]:
        """Fetch stories from Hacker News API"""
        try:
            # Get story IDs
            ids_url = f"{self.base_url}/{story_type}.json"
            response = safe_request(ids_url, self.headers)
            
            if not response:
                return []
            
            story_ids = response.json()[:limit]
            stories = []
            
            # Fetch individual stories
            for story_id in story_ids:
                story_data = self._fetch_story_details(story_id)
                if story_data:
                    stories.append(story_data)
                
                # Rate limiting
                time.sleep(0.1)
            
            return stories
            
        except Exception as e:
            print(f"Error fetching {story_type}: {e}")
            return []
    
    def _fetch_story_details(self, story_id: int) -> Optional[Dict]:
        """Fetch individual story details"""
        try:
            story_url = f"{self.base_url}/item/{story_id}.json"
            response = safe_request(story_url, self.headers)
            
            if not response:
                return None
            
            story_data = response.json()
            
            # Check if it's a valid story
            if story_data.get('type') != 'story' or story_data.get('deleted') or story_data.get('dead'):
                return None
            
            title = story_data.get('title', '')
            url = story_data.get('url', '')
            
            # If no URL, it's a text post - use HN link
            if not url:
                url = f"{self.hn_web_url}/item?id={story_id}"
            
            # Parse timestamp
            timestamp = story_data.get('time', 0)
            if timestamp:
                date = datetime.fromtimestamp(timestamp, tz=JST)
            else:
                date = datetime.now(JST)
            
            # Check if within time window
            if not self._is_within_time_window(date):
                return None
            
            # Get story text if available
            text = story_data.get('text', '')
            
            return {
                'id': story_id,
                'title': title,
                'url': url,
                'content': text,
                'summary': text,
                'date': date.isoformat(),
                'score': story_data.get('score', 0),
                'comments': story_data.get('descendants', 0),
                'author': story_data.get('by', ''),
                'hn_url': f"{self.hn_web_url}/item?id={story_id}"
            }
            
        except Exception as e:
            print(f"Error fetching story {story_id}: {e}")
            return None
    
    def _is_within_time_window(self, date: datetime) -> bool:
        """Check if date is within our time window"""
        cutoff = datetime.now(JST) - TIME_WINDOW
        return date >= cutoff
    
    def _filter_ai_tools(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles to only include AI-related tools"""
        ai_tool_articles = []
        
        for article in articles:
            title = article.get('title', '').lower()
            content = article.get('content', '').lower()
            
            # Check for AI keywords
            has_ai_keyword = any(keyword in title or keyword in content 
                               for keyword in self.ai_keywords)
            
            if not has_ai_keyword:
                continue
            
            # Check if it's a Show HN post or tool announcement
            is_show_hn = any(keyword in title for keyword in self.show_hn_keywords)
            has_tool_indicator = any(indicator in title or indicator in content 
                                   for indicator in self.tool_indicators)
            
            # Include if it's AI-related and either Show HN or has tool indicators
            if is_show_hn or has_tool_indicator:
                # Try to get more content from the linked URL if it's not a text post
                if not article.get('content') and article.get('url') != article.get('hn_url'):
                    full_content = self.get_article_content(article['url'])
                    if full_content:
                        article['content'] = full_content
                        article['summary'] = extract_summary(full_content)
                
                # Determine if it's a tool or news
                if self._is_tool_post(article):
                    article['type'] = 'tool'
                else:
                    article['type'] = 'news'
                
                # Add HN-specific metadata
                article['source'] = 'Hacker News'
                article['hn_score'] = article.get('score', 0)
                article['hn_comments'] = article.get('comments', 0)
                
                ai_tool_articles.append(article)
        
        return ai_tool_articles
    
    def _is_tool_post(self, article: Dict) -> bool:
        """Determine if this is a tool post vs news post"""
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        
        # Strong tool indicators
        tool_keywords = [
            'show hn:', 'i built', 'i made', 'i created', 'we built', 'we made',
            'launching', 'released', 'open sourced', 'new tool', 'side project'
        ]
        
        # Check title for tool announcement patterns
        is_tool_announcement = any(keyword in title for keyword in tool_keywords)
        
        # Check for product features/capabilities
        feature_keywords = [
            'features', 'api', 'free tier', 'pricing', 'beta', 'early access',
            'sign up', 'try it', 'demo', 'github', 'documentation'
        ]
        has_product_features = any(keyword in content for keyword in feature_keywords)
        
        return is_tool_announcement or has_product_features
    
    def _categorize_ai_tool(self, article: Dict) -> str:
        """Categorize the AI tool based on content"""
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        
        # Coding tools
        if any(keyword in title or keyword in content for keyword in 
               ['code', 'coding', 'programming', 'developer', 'copilot', 'ide', 'editor']):
            return 'ai_coding'
        
        # Image/video tools
        if any(keyword in title or keyword in content for keyword in 
               ['image', 'photo', 'video', 'visual', 'midjourney', 'dalle', 'stable diffusion']):
            return 'ai_creative'
        
        # Writing tools
        if any(keyword in title or keyword in content for keyword in 
               ['writing', 'text', 'content', 'blog', 'article', 'gpt']):
            return 'ai_writing'
        
        # Chat/conversation tools
        if any(keyword in title or keyword in content for keyword in 
               ['chat', 'conversation', 'assistant', 'bot', 'claude', 'chatgpt']):
            return 'ai_assistant'
        
        return 'ai_general'


# Source configuration for main scraper
HACKERNEWS_AI_CONFIG = {
    'name': 'Hacker News',
    'base_url': 'https://hacker-news.firebaseio.com/v0',
    'categories': ['ai_tools', 'show_hn', 'technology']
}