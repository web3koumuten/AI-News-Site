# AI Updates 72 Blog Structure

## Overview
This blog is structured to display AI industry updates daily. Each update contains the latest AI news, tools, and trends from that day.

## Directory Structure
```
AI-Updates-72/
├── index.html           # Main blog page listing all updates
├── posts/              # Directory containing all blog posts
│   ├── 2025-01-28.html # First blog post (January 28, 2025)
│   ├── 2025-01-29.html # Next update
│   └── ...             # Future posts every day
├── article_*.html      # Individual article pages linked from posts
└── update_blog.py      # Helper script for managing updates
```

## How It Works

### Main Page (index.html)
- Displays a hero section with the blog title "AI Updates 72 アーカイブ"
- Shows cards for each daily update
- Each card includes:
  - Date of publication
  - Update number
  - Date covered (e.g., "2025年1月28日")
  - Statistics (number of articles, AI tools, news)
  - Brief summary of highlights
  - "Read more" link to the full post

### Individual Posts (posts/*.html)
- Each post covers a single day
- Contains the full list of AI updates for that day
- Links to individual article pages
- Includes a back link to the main page

### Update Process
1. Every day, run the `update_blog.py` script
2. The script will:
   - Calculate the next update date
   - Create a new post template
   - Update the main index.html page
3. Add the new AI articles to the post
4. Update the statistics and summary on the main page

### Styling
- Modern, clean design with purple gradient accents
- Responsive grid layout
- Hover effects on cards
- Future posts are shown with reduced opacity

## Usage

### Creating a New Update
```bash
python update_blog.py
```
Select option 1 or 3 to create the next post template.

### Manual Update Steps
1. Copy the latest AI articles to `article_*.html` files
2. Edit the new post file in `posts/` to include the articles
3. Update the statistics in both the post and main page
4. Add a summary of key highlights to the main page card

### Customization
- Edit the CSS in index.html to change the design
- Modify the update_blog.py script to adjust the update cycle
- Add more metadata or features as needed