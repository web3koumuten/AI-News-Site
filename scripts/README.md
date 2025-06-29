# AI Updates 72 Scraper

A comprehensive Python scraping system for gathering AI-related news and tools from Japanese tech websites.

## Features

- **Multi-source scraping**: Fetches content from 6 major Japanese tech sources
- **AI tool detection**: Automatically identifies and categorizes AI tools vs news
- **Deduplication**: Removes duplicate content across sources
- **Time filtering**: Only fetches articles from the last 72 hours
- **Respectful scraping**: Follows robots.txt and implements rate limiting
- **Clean output**: Generates TypeScript-compatible JSON data

## Sources

1. **ITmedia AI+** - RSS feed parsing
2. **ASCII.jp** - Search-based scraping
3. **CNET Japan** - RSS + AI section scraping
4. **TechCrunch Japan** - Category and main page scraping
5. **AI-SCHOLAR** - Research-focused content
6. **Ledge.ai** - Business and case studies

## Installation

1. Install Python dependencies:
```bash
cd scripts
pip install -r requirements.txt
```

2. Create data directory (if not exists):
```bash
mkdir -p data
```

## Usage

### Quick Start
```bash
# Run the scraper
python run_scraper.py

# Or run directly
python main_scraper.py
```

### Test the scrapers
```bash
python test_scrapers.py
```

## Output Format

The scraper generates a JSON file (`data/ai_updates.json`) with the following structure:

```json
{
  "tools": [
    {
      "id": "unique_id",
      "name": "Tool Name",
      "description": "Tool description",
      "category": "ai_general",
      "url": "https://example.com",
      "logo": "https://example.com/logo.png",
      "features": ["feature1", "feature2"],
      "pricing": {
        "type": "freemium",
        "startingPrice": "¥1,000/月"
      },
      "updatedAt": "2024-01-01T12:00:00+09:00"
    }
  ],
  "news": [
    {
      "id": "unique_id", 
      "title": "News Title",
      "summary": "News summary",
      "source": "ITmedia AI+",
      "url": "https://example.com",
      "publishedAt": "2024-01-01T12:00:00+09:00",
      "category": "technology",
      "imageUrl": "https://example.com/image.jpg",
      "tags": ["AI", "GPT-4"]
    }
  ],
  "lastUpdated": "2024-01-01T12:00:00+09:00",
  "metadata": {
    "totalArticles": 150,
    "toolsCount": 25,
    "newsCount": 125,
    "sources": ["itmedia", "ascii", "cnet", "techcrunch", "ai_scholar", "ledge_ai"],
    "timeWindow": "72h",
    "generatedAt": "2024-01-01T12:00:00+09:00"
  }
}
```

## Configuration

Edit `config.py` to customize:

- Source URLs and RSS feeds
- Time window for article fetching
- Category mappings
- AI tool detection keywords
- Request headers and timeouts

## Architecture

### Core Components

1. **BaseScraper** (`scrapers/base_scraper.py`)
   - Abstract base class for all scrapers
   - Common functionality for content extraction
   - Error handling and rate limiting

2. **Individual Scrapers** (`scrapers/`)
   - Each source has its own scraper class
   - Handles source-specific parsing logic
   - Extracts structured data from different layouts

3. **MainScraper** (`main_scraper.py`)
   - Orchestrates all individual scrapers
   - Handles deduplication and output formatting
   - Provides validation and error reporting

4. **Utilities** (`utils.py`)
   - Date parsing and timezone handling (JST)
   - Text cleaning and summarization
   - Duplicate detection algorithms
   - Content categorization

### Data Flow

```
Individual Scrapers → Raw Articles → Main Scraper → Deduplication → 
Category Detection → Tool/News Separation → JSON Output
```

## Respectful Scraping

The scraper implements several measures to be respectful:

- **Rate limiting**: 1-second delays between requests
- **Robots.txt compliance**: Checks and respects robots.txt directives
- **User agent**: Clearly identifies as AI-Updates-72-Bot
- **Concurrent limits**: Maximum 5 concurrent requests
- **Error handling**: Graceful failure without spamming servers
- **Caching**: Reduces redundant requests

## Troubleshooting

### Common Issues

1. **No articles found**
   - Check internet connection
   - Verify source websites are accessible
   - Check if robots.txt blocks access

2. **Import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python path configuration

3. **Encoding issues**
   - The scraper handles Japanese text with UTF-8 encoding
   - Ensure your terminal supports UTF-8

### Debug Mode

Set environment variable for verbose output:
```bash
export DEBUG=1
python main_scraper.py
```

## Development

### Adding a New Source

1. Create a new scraper class in `scrapers/new_source_scraper.py`:
```python
from base_scraper import BaseScraper

class NewSourceScraper(BaseScraper):
    def fetch_articles(self) -> List[Dict]:
        # Implement scraping logic
        pass
```

2. Add source configuration to `config.py`
3. Register scraper in `main_scraper.py`
4. Add to test suite in `test_scrapers.py`

### Testing

Run individual components:
```bash
# Test specific scraper
python -c "from scrapers import ITMediaScraper; s = ITMediaScraper(); print(len(s.fetch_articles()))"

# Test utilities
python -c "from utils import parse_date; print(parse_date('2024年1月1日 12:00'))"

# Full test suite
python test_scrapers.py
```

## License

This scraper is designed for personal and research use. Please respect the terms of service of the scraped websites and use responsibly.

## Contributing

1. Follow the existing code structure
2. Add tests for new functionality
3. Ensure robots.txt compliance
4. Document any new configuration options