#!/usr/bin/env python3
"""
Example usage of AI Updates 72 scraper
Demonstrates how to use individual scrapers and the main scraper
"""
import sys
from pathlib import Path
import json

# Add scripts directory to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from scrapers import ITMediaScraper
from main_scraper import MainScraper
from utils import parse_date, clean_text, is_ai_tool


def demo_individual_scraper():
    """Demo using an individual scraper"""
    print("🔍 Demo: Using ITmedia scraper individually")
    print("-" * 50)
    
    # Create scraper instance
    scraper = ITMediaScraper()
    
    # Fetch articles
    print("Fetching articles from ITmedia AI+...")
    articles = scraper.fetch_articles()
    
    print(f"Found {len(articles)} articles")
    
    if articles:
        # Show first article
        article = articles[0]
        print(f"\nSample article:")
        print(f"  Type: {article.get('type', 'unknown')}")
        print(f"  Title: {article.get('title', article.get('name', 'N/A'))}")
        print(f"  URL: {article.get('url', 'N/A')}")
        print(f"  Category: {article.get('category', 'N/A')}")
        
        if article.get('type') == 'tool':
            print(f"  Pricing: {article.get('pricing', {}).get('type', 'N/A')}")
        else:
            print(f"  Source: {article.get('source', 'N/A')}")
    
    print()


def demo_main_scraper():
    """Demo using the main scraper"""
    print("🚀 Demo: Using main scraper (all sources)")
    print("-" * 50)
    
    # Create main scraper
    scraper = MainScraper()
    
    # For demo, limit to faster scrapers
    limited_scrapers = {
        'itmedia': scraper.scrapers['itmedia'],
        'cnet': scraper.scrapers['cnet']
    }
    scraper.scrapers = limited_scrapers
    
    print("Running limited scraper (ITmedia + CNET)...")
    
    # Run scraper
    output_data = scraper.run()
    
    # Show summary
    print(f"\n📊 Results Summary:")
    print(f"  Total articles: {output_data['metadata']['totalArticles']}")
    print(f"  Tools: {output_data['metadata']['toolsCount']}")
    print(f"  News: {output_data['metadata']['newsCount']}")
    print(f"  Sources: {', '.join(output_data['metadata']['sources'])}")
    
    # Show sample items
    if output_data['tools']:
        print(f"\n🛠️ Sample Tool:")
        tool = output_data['tools'][0]
        print(f"  Name: {tool['name']}")
        print(f"  Category: {tool['category']}")
        print(f"  Pricing: {tool['pricing']['type']}")
    
    if output_data['news']:
        print(f"\n📰 Sample News:")
        news = output_data['news'][0]
        print(f"  Title: {news['title']}")
        print(f"  Source: {news['source']}")
        print(f"  Category: {news['category']}")
        print(f"  Tags: {', '.join(news.get('tags', [])[:3])}")


def demo_utilities():
    """Demo utility functions"""
    print("🔧 Demo: Utility functions")
    print("-" * 50)
    
    # Date parsing
    test_dates = [
        "2024年1月1日 12:00",
        "2024-01-01T12:00:00+09:00",
        "1時間前",
        "2 hours ago"
    ]
    
    print("Date parsing examples:")
    for date_str in test_dates:
        parsed = parse_date(date_str)
        print(f"  '{date_str}' -> {parsed}")
    
    # Text cleaning
    print("\nText cleaning examples:")
    dirty_text = "  これは　　テスト　です。\n\n  "
    clean = clean_text(dirty_text)
    print(f"  Original: '{dirty_text}'")
    print(f"  Cleaned:  '{clean}'")
    
    # AI tool detection
    print("\nAI tool detection examples:")
    test_texts = [
        "新しいAIツールがリリースされました",
        "ChatGPTの最新ニュースです",
        "機械学習の研究論文が発表"
    ]
    
    for text in test_texts:
        is_tool = is_ai_tool(text)
        print(f"  '{text}' -> {'Tool' if is_tool else 'News'}")


def main():
    """Run all demos"""
    print("=" * 60)
    print("AI Updates 72 Scraper - Example Usage")
    print("=" * 60)
    
    try:
        # Demo individual scraper
        demo_individual_scraper()
        
        # Demo utilities
        demo_utilities()
        
        print("\n" + "=" * 60)
        
        # Ask user if they want to run the full demo
        response = input("Run main scraper demo? (fetches real data) [y/N]: ")
        if response.lower() in ['y', 'yes']:
            demo_main_scraper()
        else:
            print("Skipping main scraper demo.")
        
        print("\n" + "=" * 60)
        print("🎉 Demo completed!")
        print("To run the full scraper: python run_scraper.py")
        print("To test all scrapers: python test_scrapers.py")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")


if __name__ == '__main__':
    main()