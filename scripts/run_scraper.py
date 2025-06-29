#!/usr/bin/env python3
"""
Simple script to run the AI Updates 72 scraper
"""
import sys
import os
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from main_scraper import main

if __name__ == '__main__':
    main()