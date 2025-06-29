"""
Main scraper for AI Updates 72
Orchestrates all individual scrapers and outputs clean JSON data
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import concurrent.futures
from pathlib import Path
import hashlib

# Import scrapers
from scrapers.itmedia_scraper import ITMediaScraper
from scrapers.ai_scholar_scraper import AIScholarScraper
from scrapers.ledge_ai_scraper import LedgeAIScraper
from scrapers.ainow_scraper import AINOWScraper
from scrapers.ascii_ai_scraper import ASCIIAIScraper
from scrapers.nikkei_ai_scraper import NikkeiAIScraper
from scrapers.producthunt_scraper import ProductHuntScraper
from scrapers.techcrunch_ai_scraper import TechCrunchAIScraper
from scrapers.hackernews_ai_scraper import HackerNewsAIScraper

# Import utilities
from config import OUTPUT_DIR, OUTPUT_FILE, TIME_WINDOW, MAX_CONCURRENT_REQUESTS
from utils import detect_duplicates, clean_text, JST


class MainScraper:
    """Main scraper class that orchestrates all individual scrapers"""
    
    def __init__(self):
        self.scrapers = {
            'itmedia': ITMediaScraper(),
            'ai_scholar': AIScholarScraper(),
            'ledge_ai': LedgeAIScraper(),
            'ainow': AINOWScraper(),
            'ascii_ai': ASCIIAIScraper(),
            'nikkei_ai': NikkeiAIScraper(),
            'producthunt': ProductHuntScraper(),
            'techcrunch_ai': TechCrunchAIScraper(),
            'hackernews_ai': HackerNewsAIScraper()
        }
        
        self.output_dir = Path(OUTPUT_DIR)
        self.output_file = OUTPUT_FILE
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
    
    def run(self) -> Dict:
        """Run all scrapers and collect articles"""
        print("Starting AI Updates 72 scraper...")
        print(f"Fetching articles from the last {TIME_WINDOW.total_seconds() / 3600:.0f} hours")
        
        all_articles = []
        
        # Run scrapers concurrently with limited concurrency
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
            # Submit all scraper tasks
            future_to_scraper = {
                executor.submit(self._run_scraper, name, scraper): name 
                for name, scraper in self.scrapers.items()
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_scraper):
                scraper_name = future_to_scraper[future]
                try:
                    articles = future.result()
                    print(f"✓ {scraper_name}: {len(articles)} articles")
                    all_articles.extend(articles)
                except Exception as e:
                    print(f"✗ {scraper_name}: Error - {e}")
        
        print(f"\nTotal articles before deduplication: {len(all_articles)}")
        
        # Deduplicate articles
        unique_articles = detect_duplicates(all_articles)
        print(f"Total articles after deduplication: {len(unique_articles)}")
        
        # Separate tools and news
        tools, news = self._separate_tools_and_news(unique_articles)
        print(f"Tools: {len(tools)}, News: {len(news)}")
        
        # Create output data
        output_data = {
            'tools': tools,
            'news': news,
            'lastUpdated': datetime.now(JST).isoformat(),
            'metadata': {
                'totalArticles': len(unique_articles),
                'toolsCount': len(tools),
                'newsCount': len(news),
                'sources': list(self.scrapers.keys()),
                'timeWindow': f"{TIME_WINDOW.total_seconds() / 3600:.0f}h",
                'generatedAt': datetime.now(JST).isoformat()
            }
        }
        
        # Save to file
        output_path = self.output_dir / self.output_file
        self._save_output(output_data, output_path)
        
        print(f"\n✓ Output saved to: {output_path}")
        print(f"✓ Generated {len(tools)} tools and {len(news)} news items")
        
        return output_data
    
    def _run_scraper(self, name: str, scraper) -> List[Dict]:
        """Run individual scraper with error handling"""
        try:
            print(f"Running {name} scraper...")
            articles = scraper.fetch_articles()
            return articles
        except Exception as e:
            print(f"Error in {name} scraper: {e}")
            return []
    
    def _separate_tools_and_news(self, articles: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Separate articles into tools and news"""
        tools = []
        news = []
        
        for article in articles:
            if article.get('type') == 'tool':
                tools.append(self._format_tool(article))
            else:
                news.append(self._format_news(article))
        
        # Sort by date (newest first)
        tools.sort(key=lambda x: x['updatedAt'], reverse=True)
        news.sort(key=lambda x: x['publishedAt'], reverse=True)
        
        return tools, news
    
    def _format_tool(self, article: Dict) -> Dict:
        """Format tool data to match TypeScript interface"""
        return {
            'id': article['id'],
            'name': article['name'],
            'description': article['description'],
            'category': article['category'],
            'url': article['url'],
            'logo': article.get('logo'),
            'features': article.get('features', []),
            'pricing': {
                'type': article['pricing']['type'],
                'startingPrice': article['pricing'].get('startingPrice')
            },
            'updatedAt': article['updatedAt'],
            'content': article.get('content', article['description']),
            'slug': self._generate_slug(article['name'])
        }
    
    def _format_news(self, article: Dict) -> Dict:
        """Format news data to match TypeScript interface"""
        return {
            'id': article['id'],
            'title': article['title'],
            'summary': article['summary'],
            'source': article['source'],
            'url': article['url'],
            'publishedAt': article['publishedAt'],
            'category': article['category'],
            'imageUrl': article.get('imageUrl'),
            'tags': article.get('tags', []),
            'content': article.get('content', article['summary']),
            'slug': self._generate_slug(article['title'])
        }
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        import re
        
        # Convert to lowercase and normalize unicode
        slug = title.lower()
        
        # Replace Japanese characters and symbols with hyphens
        slug = re.sub(r'[^\w\s-]', '-', slug)
        
        # Replace whitespace with hyphens
        slug = re.sub(r'\s+', '-', slug)
        
        # Remove duplicate hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        # Limit length
        if len(slug) > 100:
            slug = slug[:100].rstrip('-')
        
        return slug or 'article'
    
    def _save_output(self, data: Dict, output_path: Path):
        """Save output data to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving output: {e}")
            # Try saving to backup location
            backup_path = output_path.with_suffix('.backup.json')
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Saved to backup location: {backup_path}")
    
    def validate_output(self) -> bool:
        """Validate the generated output"""
        output_path = self.output_dir / self.output_file
        
        if not output_path.exists():
            print("❌ Output file does not exist")
            return False
        
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check required fields
            required_fields = ['tools', 'news', 'lastUpdated']
            for field in required_fields:
                if field not in data:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            # Check data types
            if not isinstance(data['tools'], list):
                print("❌ 'tools' should be a list")
                return False
            
            if not isinstance(data['news'], list):
                print("❌ 'news' should be a list")
                return False
            
            # Validate tool structure
            for i, tool in enumerate(data['tools'][:5]):  # Check first 5 tools
                required_tool_fields = ['id', 'name', 'description', 'category', 'url', 'pricing', 'updatedAt']
                for field in required_tool_fields:
                    if field not in tool:
                        print(f"❌ Tool {i}: Missing field '{field}'")
                        return False
            
            # Validate news structure
            for i, news_item in enumerate(data['news'][:5]):  # Check first 5 news
                required_news_fields = ['id', 'title', 'summary', 'source', 'url', 'publishedAt', 'category']
                for field in required_news_fields:
                    if field not in news_item:
                        print(f"❌ News {i}: Missing field '{field}'")
                        return False
            
            print("✅ Output validation passed")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return False
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False


def main():
    """Main entry point"""
    scraper = MainScraper()
    
    try:
        # Run scraper
        output_data = scraper.run()
        
        # Validate output
        if scraper.validate_output():
            print("\n🎉 Scraping completed successfully!")
            print(f"📊 Summary:")
            print(f"   • Total articles: {output_data['metadata']['totalArticles']}")
            print(f"   • Tools: {output_data['metadata']['toolsCount']}")
            print(f"   • News: {output_data['metadata']['newsCount']}")
            print(f"   • Sources: {', '.join(output_data['metadata']['sources'])}")
        else:
            print("\n❌ Output validation failed")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Scraping failed: {e}")
        exit(1)


if __name__ == '__main__':
    main()