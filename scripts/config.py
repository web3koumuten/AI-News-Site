"""
Configuration for AI Updates 72 scraper
"""
from datetime import timedelta

# Source configurations
SOURCES = {
    'itmedia': {
        'name': 'ITmedia AI+',
        'base_url': 'https://www.itmedia.co.jp/aiplus/',
        'rss_url': 'https://rss.itmedia.co.jp/rss/2.0/aiplus.xml',
        'categories': ['ai_news', 'research', 'industry', 'technology']
    },
    'ai_scholar': {
        'name': 'AI-SCHOLAR',
        'base_url': 'https://ai-scholar.tech/',
        'rss_url': 'https://ai-scholar.tech/feed/',
        'categories': ['research', 'paper', 'conference', 'technology']
    },
    'ledge_ai': {
        'name': 'Ledge.ai',
        'base_url': 'https://ledge.ai/',
        'rss_url': 'https://ledge.ai/feed/',
        'categories': ['business', 'case_study', 'product', 'industry']
    },
    'ainow': {
        'name': 'AINOW',
        'base_url': 'https://ainow.ai/',
        'rss_url': 'https://ainow.ai/feed/',
        'categories': ['ai_news', 'machine_learning', 'technology', 'business']
    },
    'ascii_ai': {
        'name': 'ASCII.jp AI',
        'base_url': 'https://ascii.jp/',
        'ai_section': 'https://ascii.jp/elem/000/004/121/',
        'search_url': 'https://ascii.jp/search/?q=AI+%E4%BA%BA%E5%B7%A5%E7%9F%A5%E8%83%BD',
        'categories': ['technology', 'product', 'service']
    },
    'nikkei_ai': {
        'name': '日経 AI',
        'base_url': 'https://www.nikkei.com/',
        'search_url': 'https://www.nikkei.com/search/?sw=%E4%BA%BA%E5%B7%A5%E7%9F%A5%E8%83%BD',
        'categories': ['business', 'economy', 'technology', 'industry']
    }
}

# Time window for fetching articles (72 hours)
TIME_WINDOW = timedelta(hours=72)

# User agent for requests
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AI-Updates-72-Bot/1.0'

# Request headers
DEFAULT_HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Keywords for AI tool detection
AI_TOOL_KEYWORDS = [
    # Japanese
    'ツール', 'サービス', 'プラットフォーム', 'アプリ', 'ソフトウェア',
    'API', 'SDK', 'ライブラリ', 'フレームワーク', '無料', '有料',
    'プラン', '価格', '料金', 'リリース', 'ローンチ', 'β版', 'ベータ版',
    '新機能', '機能追加', 'アップデート',
    # English
    'tool', 'service', 'platform', 'app', 'software', 'application',
    'launch', 'release', 'beta', 'pricing', 'free', 'paid', 'plan',
    'feature', 'update', 'introduces', 'announces'
]

# Category mapping
CATEGORY_MAPPING = {
    # Technology categories
    '技術': 'technology',
    'テクノロジー': 'technology',
    'AI': 'ai_general',
    '人工知能': 'ai_general',
    '機械学習': 'machine_learning',
    'ディープラーニング': 'deep_learning',
    '深層学習': 'deep_learning',
    
    # Business categories
    'ビジネス': 'business',
    '経営': 'business',
    '業界': 'industry',
    '産業': 'industry',
    'スタートアップ': 'startup',
    '資金調達': 'funding',
    
    # Research categories
    '研究': 'research',
    '論文': 'paper',
    '学会': 'conference',
    
    # Product categories
    '製品': 'product',
    'プロダクト': 'product',
    'サービス': 'service',
    '事例': 'case_study',
    'ケーススタディ': 'case_study'
}

# Pricing type detection keywords
PRICING_KEYWORDS = {
    'free': ['無料', 'フリー', 'free', 'complimentary', '0円', '¥0'],
    'freemium': ['フリーミアム', 'freemium', '無料プラン', 'free plan', '基本無料'],
    'paid': ['有料', '有償', 'paid', 'premium', '円/月', '$/month', 'subscription']
}

# Output configuration
OUTPUT_DIR = 'data'
OUTPUT_FILE = 'ai_updates.json'

# Request timeout
REQUEST_TIMEOUT = 30  # seconds

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Concurrent requests limit
MAX_CONCURRENT_REQUESTS = 5

# Cache configuration
ENABLE_CACHE = True
CACHE_DIR = '.cache'
CACHE_EXPIRY = timedelta(hours=6)