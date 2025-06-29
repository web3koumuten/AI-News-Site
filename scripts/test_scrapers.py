#!/usr/bin/env python3
"""
Test script for AI Updates 72 scrapers
"""
import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from scrapers import *
from utils import validate_article_date
from config import TIME_WINDOW
from datetime import datetime
import json


def test_scraper(scraper_class, name):
    """Test individual scraper"""
    print(f"\n🧪 Testing {name} scraper...")
    
    try:
        scraper = scraper_class()
        articles = scraper.fetch_articles()
        
        print(f"   ✓ Fetched {len(articles)} articles")
        
        if articles:
            # Test first article structure
            article = articles[0]
            required_fields = ['id', 'url', 'type']
            
            for field in required_fields:
                if field not in article:
                    print(f"   ❌ Missing field: {field}")
                    return False
            
            # Check article type specific fields
            if article['type'] == 'tool':
                tool_fields = ['name', 'description', 'category', 'pricing', 'updatedAt']
                for field in tool_fields:
                    if field not in article:
                        print(f"   ❌ Missing tool field: {field}")
                        return False
            else:
                news_fields = ['title', 'summary', 'source', 'publishedAt', 'category']
                for field in news_fields:
                    if field not in article:
                        print(f"   ❌ Missing news field: {field}")
                        return False
            
            print(f"   ✓ Article structure is valid")
            print(f"   ✓ Sample: {article.get('title', article.get('name', 'N/A'))[:50]}...")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_all_scrapers():
    """Test all scrapers"""
    print("🚀 Testing AI Updates 72 scrapers...")
    
    scrapers_to_test = [
        (ITMediaScraper, "ITmedia"),
        (ASCIIScraper, "ASCII.jp"),
        (CNETScraper, "CNET Japan"),
        (TechCrunchScraper, "TechCrunch Japan"),
        (AIScholarScraper, "AI-SCHOLAR"),
        (LedgeAIScraper, "Ledge.ai")
    ]
    
    results = []
    
    for scraper_class, name in scrapers_to_test:
        success = test_scraper(scraper_class, name)
        results.append((name, success))
    
    # Summary
    print(f"\n📊 Test Results:")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {name}")
    
    print(f"\n🎯 Overall: {passed}/{total} scrapers passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️ Some tests failed")
        return False


def test_main_scraper():
    """Test main scraper"""
    print("\n🧪 Testing main scraper...")
    
    try:
        from main_scraper import MainScraper
        
        scraper = MainScraper()
        
        # Test with limited scrapers to avoid long wait
        test_scrapers = {
            'itmedia': scraper.scrapers['itmedia']
        }
        scraper.scrapers = test_scrapers
        
        output_data = scraper.run()
        
        # Validate output
        if scraper.validate_output():
            print("   ✅ Main scraper test passed")
            return True
        else:
            print("   ❌ Main scraper validation failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Main scraper test failed: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("AI Updates 72 Scraper Test Suite")
    print("=" * 60)
    
    # Test individual scrapers
    individual_tests_passed = test_all_scrapers()
    
    # Test main scraper if individual tests pass
    if individual_tests_passed:
        main_test_passed = test_main_scraper()
    else:
        main_test_passed = False
        print("\n⚠️ Skipping main scraper test due to individual test failures")
    
    print("\n" + "=" * 60)
    if individual_tests_passed and main_test_passed:
        print("🎉 ALL TESTS PASSED! The scraper is ready to use.")
    else:
        print("❌ SOME TESTS FAILED. Please check the errors above.")
        sys.exit(1)
    print("=" * 60)