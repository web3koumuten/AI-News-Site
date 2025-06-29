#!/usr/bin/env python3
"""
Blog update helper script for AI Updates 72
This script helps manage the 3-day update cycle for the AI Updates blog
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

def get_next_update_date(base_date=None):
    """Calculate the next update date (1 day from last update)"""
    if base_date is None:
        base_date = datetime(2025, 1, 28)  # Starting date
    else:
        base_date = datetime.strptime(base_date, "%Y-%m-%d")
    
    # Find the latest post
    posts_dir = Path("posts")
    if posts_dir.exists():
        posts = sorted([f for f in posts_dir.glob("*.html") if f.stem != "template"])
        if posts:
            latest = posts[-1].stem
            try:
                latest_date = datetime.strptime(latest, "%Y-%m-%d")
                base_date = latest_date
            except:
                pass
    
    next_date = base_date + timedelta(days=1)
    return next_date

def create_post_template(date, post_number):
    """Create a new post template file"""
    date_str = date.strftime("%Y-%m-%d")
    date_jp = date.strftime("%Y年%-m月%-d日")
    
    # For daily updates, just use the current date
    start_jp = date_jp
    
    template = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Updates 72 - {date_jp}</title>
    <style>
        body {{ font-family: sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ background: white; padding: 40px; text-align: center; border-radius: 10px; margin-bottom: 30px; }}
        h1 {{ color: #333; margin-bottom: 10px; }}
        .tagline {{ color: #666; margin-bottom: 20px; }}
        .stats {{ display: flex; justify-content: center; gap: 30px; }}
        .stat {{ text-align: center; }}
        .stat-number {{ font-size: 2rem; font-weight: bold; color: #0066cc; }}
        .stat-label {{ color: #666; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }}
        .card {{ background: white; border-radius: 10px; padding: 20px; cursor: pointer; transition: transform 0.2s; }}
        .card:hover {{ transform: translateY(-5px); }}
        .category {{ background: #e6f3ff; color: #0066cc; padding: 5px 10px; border-radius: 15px; font-size: 0.8rem; display: inline-block; margin-bottom: 10px; }}
        .title {{ font-size: 1.1rem; font-weight: bold; margin-bottom: 10px; color: #333; }}
        .excerpt {{ color: #666; font-size: 0.9rem; line-height: 1.4; }}
        .footer {{ margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee; display: flex; justify-content: space-between; }}
        .source {{ color: #888; font-size: 0.8rem; }}
        .date {{ color: #aaa; font-size: 0.8rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 AI Updates 72 - {date_jp}</h1>
            <p class="tagline">{date_jp}の最新AI情報</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">0</div>
                    <div class="stat-label">総記事数</div>
                </div>
                <div class="stat">
                    <div class="stat-number">0</div>
                    <div class="stat-label">AIツール</div>
                </div>
                <div class="stat">
                    <div class="stat-number">0</div>
                    <div class="stat-label">ニュース</div>
                </div>
            </div>
            <p style="margin-top: 20px;"><a href="../index.html" style="color: #0066cc; text-decoration: none;">← メインページへ戻る</a></p>
        </header>
        <div class="grid">
            <!-- Articles will be added here -->
        </div>
    </div>
</body>
</html>"""
    
    # Save the template
    post_path = Path(f"posts/{date_str}.html")
    post_path.parent.mkdir(exist_ok=True)
    post_path.write_text(template, encoding='utf-8')
    
    print(f"Created post template: {post_path}")
    return post_path

def update_index_page():
    """Update the main index.html with all posts"""
    posts_dir = Path("posts")
    if not posts_dir.exists():
        print("Posts directory not found!")
        return
    
    # Get all posts
    posts = sorted([f for f in posts_dir.glob("*.html")], reverse=True)
    
    # Generate post cards HTML
    post_cards = []
    for i, post_file in enumerate(posts):
        try:
            date = datetime.strptime(post_file.stem, "%Y-%m-%d")
            date_str = date.strftime("%Y年%-m月%-d日")
            start_str = date_str  # For daily updates, start and end are the same
            post_num = i + 1
            
            # Check if this is a future post
            is_future = date > datetime.now()
            
            if is_future:
                card_html = f"""
            <!-- Placeholder for update #{post_num} -->
            <div class="post-card upcoming">
                <div class="post-header">
                    <div class="post-date">{date_str}</div>
                    <h2 class="post-title">AI Updates #{post_num}</h2>
                    <div class="post-period">{date_str}</div>
                </div>
                <div class="post-content">
                    <div class="coming-soon">
                        次回更新予定
                    </div>
                </div>
            </div>"""
            else:
                # TODO: Parse actual content from the post file
                card_html = f"""
            <!-- Update #{post_num} -->
            <div class="post-card" onclick="window.location.href='posts/{post_file.name}'">
                <div class="post-header">
                    <div class="post-date">{date_str}</div>
                    <h2 class="post-title">AI Updates #{post_num}</h2>
                    <div class="post-period">{date_str}</div>
                </div>
                <div class="post-content">
                    <div class="post-stats">
                        <div class="stat">
                            <div class="stat-number">-</div>
                            <div class="stat-label">記事数</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">-</div>
                            <div class="stat-label">AIツール</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">-</div>
                            <div class="stat-label">ニュース</div>
                        </div>
                    </div>
                    <p class="post-summary">
                        この期間のAI業界の最新動向をお届けします。
                    </p>
                    <a href="posts/{post_file.name}" class="read-more">全文を読む</a>
                </div>
            </div>"""
            
            post_cards.append(card_html)
        except:
            continue
    
    # Read and update index.html
    index_path = Path("index.html")
    if index_path.exists():
        content = index_path.read_text(encoding='utf-8')
        
        # Find the posts grid section
        start_marker = '<div class="posts-grid">'
        end_marker = '</div>\n    </div>\n</body>'
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            new_grid = start_marker + '\n' + '\n'.join(post_cards) + '\n        '
            new_content = content[:start_idx] + new_grid + content[end_idx:]
            
            index_path.write_text(new_content, encoding='utf-8')
            print("Updated index.html with all posts")

def main():
    """Main function to help manage blog updates"""
    print("AI Updates 72 - Blog Update Helper")
    print("=" * 40)
    
    # Get the next update date
    next_date = get_next_update_date()
    print(f"Next update date: {next_date.strftime('%Y-%m-%d')}")
    
    # Ask user what to do
    print("\nOptions:")
    print("1. Create next post template")
    print("2. Update index page")
    print("3. Both")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1" or choice == "3":
        # Count existing posts
        posts_dir = Path("posts")
        post_count = len(list(posts_dir.glob("*.html"))) if posts_dir.exists() else 0
        create_post_template(next_date, post_count + 1)
    
    if choice == "2" or choice == "3":
        update_index_page()
    
    print("\nDone!")

if __name__ == "__main__":
    main()