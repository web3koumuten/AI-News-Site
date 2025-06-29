"""
Robots.txt checker for AI Updates 72 scraper
Ensures compliance with robots.txt directives
"""
import requests
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse
from typing import Dict, Optional
import time

from config import DEFAULT_HEADERS, USER_AGENT


class RobotsChecker:
    """Check robots.txt compliance for web scraping"""
    
    def __init__(self):
        self.robots_cache = {}
        self.user_agent = USER_AGENT
    
    def can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt"""
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Get robots.txt for this domain
            rp = self._get_robots_parser(base_url)
            if rp is None:
                # If we can't read robots.txt, assume we can fetch
                return True
            
            # Check if we can fetch this URL
            return rp.can_fetch(self.user_agent, url)
            
        except Exception as e:
            print(f"Error checking robots.txt for {url}: {e}")
            # If there's an error, err on the side of caution but still allow
            return True
    
    def get_crawl_delay(self, url: str) -> Optional[float]:
        """Get crawl delay for domain from robots.txt"""
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            rp = self._get_robots_parser(base_url)
            if rp is None:
                return None
            
            delay = rp.crawl_delay(self.user_agent)
            return float(delay) if delay else None
            
        except Exception as e:
            print(f"Error getting crawl delay for {url}: {e}")
            return None
    
    def _get_robots_parser(self, base_url: str) -> Optional[RobotFileParser]:
        """Get cached robots.txt parser for domain"""
        if base_url in self.robots_cache:
            return self.robots_cache[base_url]
        
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            
            # Fetch robots.txt
            response = requests.get(
                robots_url,
                headers=DEFAULT_HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                rp = RobotFileParser()
                rp.set_url(robots_url)
                
                # Parse robots.txt content
                robots_content = response.text
                rp.read()
                
                # Create a new parser and read from string
                rp = RobotFileParser()
                rp.set_url(robots_url)
                
                # Split content into lines and feed to parser
                lines = robots_content.split('\n')
                robots_data = '\n'.join(lines)
                
                # Use a simple approach - create temp file
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write(robots_data)
                    temp_path = f.name
                
                try:
                    rp.set_url(f"file://{temp_path}")
                    rp.read()
                finally:
                    os.unlink(temp_path)
                
                self.robots_cache[base_url] = rp
                return rp
            else:
                # No robots.txt found, cache None
                self.robots_cache[base_url] = None
                return None
                
        except Exception as e:
            print(f"Error fetching robots.txt from {base_url}: {e}")
            self.robots_cache[base_url] = None
            return None


# Global instance
robots_checker = RobotsChecker()


def check_robots_compliance(url: str) -> bool:
    """Check if URL can be fetched"""
    return robots_checker.can_fetch(url)


def get_recommended_delay(url: str) -> float:
    """Get recommended delay for URL"""
    crawl_delay = robots_checker.get_crawl_delay(url)
    if crawl_delay:
        return max(crawl_delay, 1.0)  # At least 1 second
    return 1.0  # Default 1 second delay


import os  # Add this import