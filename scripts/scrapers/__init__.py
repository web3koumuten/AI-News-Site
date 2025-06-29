"""
AI Updates 72 scrapers package
"""
import sys
import os

# Add the parent directory to the Python path to enable imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from scrapers.itmedia_scraper import ITMediaScraper
    from scrapers.ascii_scraper import ASCIIScraper
    from scrapers.cnet_scraper import CNETScraper
    from scrapers.techcrunch_scraper import TechCrunchScraper
    from scrapers.ai_scholar_scraper import AIScholarScraper
    from scrapers.ledge_ai_scraper import LedgeAIScraper
except ImportError as e:
    print(f"Import error in scrapers __init__: {e}")
    raise

__all__ = [
    'ITMediaScraper',
    'ASCIIScraper',
    'CNETScraper',
    'TechCrunchScraper',
    'AIScholarScraper',
    'LedgeAIScraper'
]