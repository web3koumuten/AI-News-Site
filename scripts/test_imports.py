#!/usr/bin/env python3
"""
Test script to verify that all imports work correctly after fixing the import issues.
This script tests the import fixes applied to the AI Updates 72 scraper system.
"""

def test_imports():
    """Test all imports work correctly"""
    print('=== AI Updates 72 Scraper Import Test ===')
    print()

    # Test 1: Import main scraper
    try:
        from main_scraper import MainScraper
        print('✓ main_scraper module imported successfully')
    except ImportError as e:
        print(f'❌ Failed to import main_scraper: {e}')
        return False

    # Test 2: Import individual scrapers
    try:
        from scrapers.itmedia_scraper import ITMediaScraper
        from scrapers.ascii_scraper import ASCIIScraper
        from scrapers.cnet_scraper import CNETScraper
        from scrapers.techcrunch_scraper import TechCrunchScraper
        from scrapers.ai_scholar_scraper import AIScholarScraper
        from scrapers.ledge_ai_scraper import LedgeAIScraper
        print('✓ All individual scrapers imported successfully')
    except ImportError as e:
        print(f'❌ Failed to import individual scrapers: {e}')
        return False

    # Test 3: Import base scraper
    try:
        from scrapers.base_scraper import BaseScraper
        print('✓ Base scraper imported successfully')
    except ImportError as e:
        print(f'❌ Failed to import base scraper: {e}')
        return False

    # Test 4: Import utilities and config
    try:
        import config
        import utils
        print('✓ Config and utils imported successfully')
    except ImportError as e:
        print(f'❌ Failed to import config/utils: {e}')
        return False

    # Test 5: Instantiate main scraper
    try:
        scraper = MainScraper()
        print(f'✓ MainScraper instantiated with {len(scraper.scrapers)} scrapers')
    except Exception as e:
        print(f'❌ Failed to instantiate MainScraper: {e}')
        return False

    # Test 6: Test scraper creation
    try:
        for name, scraper_instance in scraper.scrapers.items():
            print(f'  - {name}: {type(scraper_instance).__name__}')
        print('✓ All scrapers created successfully')
    except Exception as e:
        print(f'❌ Failed to create scrapers: {e}')
        return False

    print()
    print('🎉 All import tests passed! The scraper system is ready to use.')
    print()
    print('To run the scraper:')
    print('  python3 main_scraper.py')
    print()
    
    return True


if __name__ == '__main__':
    success = test_imports()
    exit(0 if success else 1)