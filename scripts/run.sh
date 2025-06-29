#!/bin/bash

# AI Updates 72 Scraper Runner
# Simple script to run the scraper with proper setup

set -e  # Exit on any error

echo "🚀 AI Updates 72 Scraper"
echo "========================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not found"
    exit 1
fi

# Create data directory if it doesn't exist
if [ ! -d "../data" ]; then
    echo "📁 Creating data directory..."
    mkdir -p ../data
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run based on argument
case "${1:-run}" in
    "test")
        echo "🧪 Running tests..."
        python test_scrapers.py
        ;;
    "demo")
        echo "🎮 Running demo..."
        python example_usage.py
        ;;
    "run"|*)
        echo "🏃 Running scraper..."
        python main_scraper.py
        ;;
esac

echo "✅ Complete!"

# Deactivate virtual environment
deactivate