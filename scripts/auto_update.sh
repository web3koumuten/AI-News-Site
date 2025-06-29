#!/bin/bash

# AI Updates 72 - Automatic scraper script
# This script runs the scraper and updates the website data

# Set the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to scripts directory
cd "$SCRIPT_DIR"

echo "=== AI Updates 72 Auto Update ==="
echo "Started at: $(date)"
echo "Script dir: $SCRIPT_DIR"
echo "Project root: $PROJECT_ROOT"

# Run the main scraper
echo "Running main scraper..."
python3 main_scraper.py

# Check if scraping was successful
if [ $? -eq 0 ]; then
    echo "✓ Scraping completed successfully"
    
    # Copy the scraped data to the website data folder
    if [ -f "data/ai_updates.json" ]; then
        cp "data/ai_updates.json" "$PROJECT_ROOT/data/ai_updates.json"
        echo "✓ Data copied to website folder"
        
        # Show summary
        echo "=== Scraping Summary ==="
        python3 -c "
import json
with open('data/ai_updates.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'Total articles: {data[\"metadata\"][\"totalArticles\"]}')
print(f'Tools: {data[\"metadata\"][\"toolsCount\"]}')
print(f'News: {data[\"metadata\"][\"newsCount\"]}')
print(f'Sources: {len(data[\"metadata\"][\"sources\"])}')
print(f'Last updated: {data[\"lastUpdated\"]}')
"
    else
        echo "⚠️ Warning: No scraped data file found"
    fi
else
    echo "❌ Scraping failed"
    exit 1
fi

echo "Completed at: $(date)"
echo "================================="