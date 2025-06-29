"""
Utility functions for AI Updates 72 scraper
"""
import re
import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Tuple
import unicodedata
from urllib.parse import urljoin, urlparse
import pytz
from bs4 import BeautifulSoup
import requests
from config import AI_TOOL_KEYWORDS, PRICING_KEYWORDS, CATEGORY_MAPPING

# Japan Standard Time
JST = pytz.timezone('Asia/Tokyo')


def parse_date(date_str: str, source: str = None) -> Optional[datetime]:
    """
    Parse various date formats and convert to JST
    """
    if not date_str:
        return None
    
    # Clean the date string
    date_str = date_str.strip()
    
    # Common patterns
    patterns = [
        # ISO format
        ('%Y-%m-%dT%H:%M:%S%z', None),
        ('%Y-%m-%dT%H:%M:%S', JST),
        ('%Y-%m-%d %H:%M:%S', JST),
        # Japanese formats
        ('%Y年%m月%d日 %H:%M', JST),
        ('%Y年%m月%d日', JST),
        # English formats
        ('%a, %d %b %Y %H:%M:%S %z', None),
        ('%a, %d %b %Y %H:%M:%S GMT', pytz.UTC),
        ('%d %b %Y %H:%M:%S', JST),
        ('%B %d, %Y', JST),
        ('%d %B %Y', JST),
    ]
    
    for pattern, tz in patterns:
        try:
            if tz:
                dt = datetime.strptime(date_str, pattern)
                if not dt.tzinfo:
                    dt = tz.localize(dt)
            else:
                dt = datetime.strptime(date_str, pattern)
            
            # Convert to JST
            if dt.tzinfo:
                return dt.astimezone(JST)
            else:
                return JST.localize(dt)
        except ValueError:
            continue
    
    # Try relative dates (e.g., "2 hours ago", "2時間前")
    relative_patterns = [
        (r'(\d+)\s*分前', 'minutes'),
        (r'(\d+)\s*時間前', 'hours'),
        (r'(\d+)\s*日前', 'days'),
        (r'(\d+)\s*minutes?\s*ago', 'minutes'),
        (r'(\d+)\s*hours?\s*ago', 'hours'),
        (r'(\d+)\s*days?\s*ago', 'days'),
    ]
    
    for pattern, unit in relative_patterns:
        match = re.search(pattern, date_str, re.IGNORECASE)
        if match:
            value = int(match.group(1))
            now = datetime.now(JST)
            if unit == 'minutes':
                return now - timedelta(minutes=value)
            elif unit == 'hours':
                return now - timedelta(hours=value)
            elif unit == 'days':
                return now - timedelta(days=value)
    
    return None


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    """
    if not text:
        return ""
    
    # Normalize unicode
    text = unicodedata.normalize('NFKC', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep Japanese
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_summary(text: str, max_length: int = 200) -> str:
    """
    Extract or generate a summary from text
    """
    if not text:
        return ""
    
    # Clean the text first
    text = clean_text(text)
    
    # If text is already short enough, return it
    if len(text) <= max_length:
        return text
    
    # Try to find a natural break point
    sentences = re.split(r'[。．.!?！？]', text)
    summary = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        if len(summary) + len(sentence) + 1 <= max_length:
            if summary:
                summary += "。"
            summary += sentence
        else:
            if not summary:
                # If first sentence is too long, truncate it
                summary = sentence[:max_length-3] + "..."
            break
    
    if summary and not re.search(r'[。．.!?！？]$', summary):
        summary += "。"
    
    return summary


def generate_id(url: str, title: str = "") -> str:
    """
    Generate a unique ID for an article/tool
    """
    content = f"{url}{title}".encode('utf-8')
    return hashlib.md5(content).hexdigest()[:12]


def detect_duplicates(items: List[Dict]) -> List[Dict]:
    """
    Remove duplicate items based on URL and title similarity
    """
    seen_urls = set()
    seen_titles = set()
    unique_items = []
    
    for item in items:
        url = item.get('url', '').lower().strip('/')
        title = clean_text(item.get('title', '')).lower()
        
        # Check exact URL match
        if url in seen_urls:
            continue
        
        # Check title similarity (for very similar titles)
        is_duplicate = False
        for seen_title in seen_titles:
            similarity = calculate_similarity(title, seen_title)
            if similarity > 0.9:  # 90% similarity threshold
                is_duplicate = True
                break
        
        if not is_duplicate:
            seen_urls.add(url)
            seen_titles.add(title)
            unique_items.append(item)
    
    return unique_items


def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculate string similarity using Jaccard index
    """
    if not str1 or not str2:
        return 0.0
    
    # Tokenize by words
    words1 = set(re.findall(r'\w+', str1.lower()))
    words2 = set(re.findall(r'\w+', str2.lower()))
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)


def is_ai_tool(title: str, content: str = "") -> bool:
    """
    Detect if an article is about an AI tool/service release
    """
    text = f"{title} {content}".lower()
    
    # Strong AI tool indicators
    ai_keywords = [
        'ai', 'artificial intelligence', 'machine learning', 'ml', 'gpt',
        'llm', 'chatbot', 'generative', 'neural', 'openai', 'claude',
        'gemini', 'copilot', 'midjourney', 'stable diffusion', 'dalle'
    ]
    
    # Tool/product release indicators
    tool_release_keywords = [
        'launches', 'releases', 'unveils', 'announces', 'debuts', 'introduces',
        'open sources', 'beta', 'early access', 'new tool', 'new feature',
        'app', 'platform', 'service', 'api', 'extension', 'plugin'
    ]
    
    # Product/tool specific language
    product_keywords = [
        'pricing', 'free tier', 'subscription', 'features', 'capabilities',
        'how to use', 'getting started', 'download', 'sign up', 'try it',
        'demo', 'github', 'documentation', 'sdk', 'cli'
    ]
    
    # Check for AI context
    has_ai_context = any(keyword in text for keyword in ai_keywords)
    
    # Check for tool release indicators
    has_tool_release = any(keyword in text for keyword in tool_release_keywords)
    
    # Check for product language
    has_product_language = any(keyword in text for keyword in product_keywords)
    
    # Score the content
    score = 0
    if has_ai_context:
        score += 2
    if has_tool_release:
        score += 3
    if has_product_language:
        score += 1
    
    # Also check for specific tool announcement patterns in title
    announcement_patterns = [
        r'(launches?|releases?|unveils?|announces?|debuts?)\s+.*\s+(ai|tool|app|platform)',
        r'(new|latest)\s+ai\s+(tool|app|platform|feature)',
        r'show\s+hn:.*\s+(ai|tool|built|created)',
        r'(google|microsoft|openai|anthropic|adobe).*\s+(ai|tool|feature)'
    ]
    
    for pattern in announcement_patterns:
        if re.search(pattern, title, re.IGNORECASE):
            score += 2
            break
    
    # Return true if score suggests it's a tool announcement
    return score >= 4


def detect_pricing_type(content: str) -> Tuple[str, Optional[str]]:
    """
    Detect pricing type and starting price from content
    """
    content_lower = content.lower()
    
    # Check for pricing keywords
    pricing_type = 'paid'  # Default to paid
    starting_price = None
    
    for p_type, keywords in PRICING_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in content_lower:
                pricing_type = p_type
                break
    
    # Try to extract price
    price_patterns = [
        r'(\d{1,3}(?:,\d{3})*)\s*円/月',
        r'¥\s*(\d{1,3}(?:,\d{3})*)/月',
        r'\$(\d+(?:\.\d{2})?)/month',
        r'月額\s*(\d{1,3}(?:,\d{3})*)\s*円',
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            starting_price = match.group(0)
            break
    
    return pricing_type, starting_price


def categorize_content(title: str, content: str = "", source_category: str = "") -> str:
    """
    Categorize content based on keywords with focus on AI tool types
    """
    text = f"{title} {content} {source_category}".lower()
    
    # AI Coding Tools
    coding_keywords = [
        'code', 'coding', 'programming', 'developer', 'copilot', 'ide', 'editor',
        'github', 'vscode', 'compiler', 'debugger', 'api', 'sdk', 'cli',
        'repository', 'git', 'devtools', 'programmer', 'software development'
    ]
    if any(keyword in text for keyword in coding_keywords):
        return 'ai_coding'
    
    # AI Creative Tools (Image/Video)
    creative_keywords = [
        'image', 'photo', 'video', 'visual', 'art', 'design', 'creative',
        'midjourney', 'dalle', 'stable diffusion', 'generate image', 'generate video',
        'photoshop', 'illustrator', 'graphic', 'avatar', 'animation', 'render'
    ]
    if any(keyword in text for keyword in creative_keywords):
        return 'ai_creative'
    
    # AI Writing Tools
    writing_keywords = [
        'writing', 'text', 'content', 'blog', 'article', 'copy', 'writer',
        'document', 'email', 'marketing', 'seo', 'copywriting', 'grammar',
        'translation', 'summary', 'transcription'
    ]
    if any(keyword in text for keyword in writing_keywords):
        return 'ai_writing'
    
    # AI Assistant/Chat Tools
    assistant_keywords = [
        'chat', 'conversation', 'assistant', 'bot', 'chatbot', 'support',
        'customer service', 'help desk', 'virtual assistant', 'ai companion'
    ]
    if any(keyword in text for keyword in assistant_keywords):
        return 'ai_assistant'
    
    # AI Data/Analytics Tools
    data_keywords = [
        'data', 'analytics', 'analysis', 'dashboard', 'report', 'insight',
        'business intelligence', 'metrics', 'visualization', 'chart', 'graph'
    ]
    if any(keyword in text for keyword in data_keywords):
        return 'ai_data'
    
    # AI Productivity Tools
    productivity_keywords = [
        'productivity', 'workflow', 'automation', 'schedule', 'task', 'project',
        'management', 'organization', 'efficiency', 'time tracking'
    ]
    if any(keyword in text for keyword in productivity_keywords):
        return 'productivity'
    
    # Technology News (non-tool specific)
    tech_keywords = [
        'technology', 'tech', 'startup', 'company', 'business', 'industry',
        'market', 'investment', 'funding', 'acquisition', 'partnership'
    ]
    if any(keyword in text for keyword in tech_keywords):
        return 'technology'
    
    # Fallback to legacy category mapping if available
    if hasattr(globals(), 'CATEGORY_MAPPING'):
        for keyword, category in CATEGORY_MAPPING.items():
            if keyword.lower() in text:
                return category
    
    # Default categories based on source
    if source_category:
        return source_category.lower()
    
    return 'ai_general'


def extract_domain(url: str) -> str:
    """
    Extract domain name from URL
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return ''


def make_absolute_url(url: str, base_url: str) -> str:
    """
    Convert relative URL to absolute URL
    """
    if not url:
        return ''
    
    # Already absolute
    if url.startswith(('http://', 'https://')):
        return url
    
    return urljoin(base_url, url)


def extract_image_url(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """
    Extract main image URL from article
    """
    # Common image patterns
    selectors = [
        'meta[property="og:image"]',
        'meta[name="twitter:image"]',
        'article img',
        '.article-image img',
        '.main-image img',
        'figure img'
    ]
    
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            if element.name == 'meta':
                img_url = element.get('content')
            else:
                img_url = element.get('src') or element.get('data-src')
            
            if img_url:
                return make_absolute_url(img_url, base_url)
    
    return None


def extract_tags(title: str, content: str = "") -> List[str]:
    """
    Extract relevant tags from content
    """
    text = f"{title} {content}".lower()
    tags = []
    
    # Common AI-related tags
    tag_patterns = {
        'ChatGPT': r'chatgpt',
        'GPT-4': r'gpt-?4',
        'Claude': r'claude',
        'Gemini': r'gemini',
        'LLM': r'llm|大規模言語モデル',
        'Generative AI': r'generative\s*ai|生成ai|生成型ai',
        'Computer Vision': r'computer\s*vision|コンピュータビジョン|画像認識',
        'NLP': r'nlp|自然言語処理',
        'Machine Learning': r'machine\s*learning|機械学習',
        'Deep Learning': r'deep\s*learning|ディープラーニング|深層学習'
    }
    
    for tag, pattern in tag_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            tags.append(tag)
    
    return tags[:5]  # Limit to 5 tags


def safe_request(url: str, headers: Dict = None, timeout: int = 30, retries: int = 3) -> Optional[requests.Response]:
    """
    Make a safe HTTP request with retries and error handling
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if attempt == retries - 1:
                print(f"Failed to fetch {url}: {e}")
                return None
            time.sleep(1 * (attempt + 1))  # Exponential backoff
    
    return None


def should_translate(title: str, content: str = "") -> bool:
    """
    Determine if content should be translated (for English articles)
    """
    text = f"{title} {content}"
    
    # Check if text contains significant Japanese content
    japanese_pattern = r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]'
    japanese_chars = len(re.findall(japanese_pattern, text))
    total_chars = len(text.replace(' ', ''))
    
    if total_chars == 0:
        return False
    
    # If less than 20% Japanese characters, consider it English
    japanese_ratio = japanese_chars / total_chars
    return japanese_ratio < 0.2


def validate_article_date(date: datetime, time_window: timedelta) -> bool:
    """
    Check if article date is within the specified time window
    """
    if not date:
        return False
    
    now = datetime.now(JST)
    return (now - date) <= time_window


import time
import logging
from functools import lru_cache


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@lru_cache(maxsize=128)
def cached_parse_date(date_str: str, source: str = None) -> Optional[datetime]:
    """Cached version of parse_date for better performance"""
    return parse_date(date_str, source)


def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to maximum length while preserving word boundaries"""
    if not text or len(text) <= max_length:
        return text
    
    # Find the last space within the limit
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # If space is found within 80% of limit
        return text[:last_space] + "..."
    else:
        return text[:max_length-3] + "..."


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text for better categorization"""
    if not text:
        return []
    
    # Common Japanese and English stop words
    stop_words = {
        'の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し', 'れ', 'さ', 'ある', 'いる',
        'する', 'です', 'ます', 'ない', 'この', 'その', 'あの', 'these', 'those', 'that',
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did'
    }
    
    # Extract words
    import re
    words = re.findall(r'\w+', text.lower())
    
    # Filter out stop words and short words
    keywords = [word for word in words if len(word) > 2 and word not in stop_words]
    
    # Count frequency
    from collections import Counter
    word_freq = Counter(keywords)
    
    # Return most common keywords
    return [word for word, count in word_freq.most_common(max_keywords)]


def format_japanese_date(date: datetime) -> str:
    """Format date in Japanese style"""
    return date.strftime('%Y年%m月%d日 %H:%M')


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    import re
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    return filename[:255]