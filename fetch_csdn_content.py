#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fetch CSDN article content using Playwright and save as Markdown files.
This script fetches ALL articles from articles_metadata.json.
"""
import sys
import io
import json
import time
import re
import os
import html2text
from playwright.sync_api import sync_playwright
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fix Windows encoding issue
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuration
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

# Content selectors to try (in order of preference)
SELECTORS = [
    "div.htmledit_views",  # Primary, cleanest content
    "div.markdown_views",  # Markdown articles
    "div#content_views",   # Older articles
    "div.blog-content-box" # Fallback, full article container
]

def setup_html2text():
    """Configure html2text converter."""
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    h.body_width = 0  # Don't wrap lines
    h.unicode_snob = True
    h.skip_internal_links = True
    return h

def extract_article_id(url):
    """Extract article ID from CSDN URL."""
    match = re.search(r'/article/details/(\d+)', url)
    return match.group(1) if match else None

def sanitize_filename(title, article_id):
    """
    Create a clean, English-only filename from Chinese title.
    Falls back to article ID if translation is complex.
    """
    # Simple approach: use article ID + first few words
    # For production, you might want to use a translation API

    # Remove special characters
    clean_title = re.sub(r'[^\w\s-]', '', title)
    clean_title = re.sub(r'[\s]+', '-', clean_title)

    # If title is all Chinese, just use article ID
    if not re.search(r'[a-zA-Z]', clean_title):
        return f"{article_id}.md"

    # Limit length
    clean_title = clean_title[:50]
    return f"{article_id}-{clean_title}.md"

def fetch_article_content(page, url, article_id):
    """Fetch article content from CSDN using Playwright."""
    try:
        print(f"  📄 Loading {url}")
        page.goto(url, timeout=60000, wait_until="networkidle")

        # Try each selector
        content_html = None
        for selector in SELECTORS:
            try:
                element = page.query_selector(selector)
                if element:
                    content_html = element.inner_html()
                    if len(content_html) > 100:  # Validate content length
                        print(f"  ✅ Content found using selector: {selector}")
                        break
            except Exception as e:
                continue

        if not content_html or len(content_html) < 100:
            print(f"  ⚠️  No substantial content found")
            return None

        return content_html

    except Exception as e:
        print(f"  ❌ Error fetching article: {e}")
        return None

def convert_to_markdown(html_content):
    """Convert HTML to Markdown."""
    h = setup_html2text()
    markdown = h.handle(html_content)
    return markdown

def save_article(article, markdown_content, output_dir):
    """Save article as markdown file with YAML frontmatter."""
    article_id = extract_article_id(article['url'])
    if not article_id:
        print(f"  ❌ Could not extract article ID from {article['url']}")
        return False

    # Create filename (English only)
    filename = sanitize_filename(article['title'], article_id)
    filepath = output_dir / filename

    # Create YAML frontmatter
    frontmatter = f"""---
title: {article['title']}
url: {article['url']}
date: {article['formatTime']}
articleId: {article_id}
---

"""

    # Combine frontmatter and content
    full_content = frontmatter + markdown_content

    # Save file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        print(f"  💾 Saved to: {filename} ({len(full_content)} bytes)")
        return True
    except Exception as e:
        print(f"  ❌ Error saving file: {e}")
        return False

def main():
    # Load article metadata
    try:
        with open('articles_metadata.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("❌ articles_metadata.json not found. Run fetch_articles.py first.")
        return

    print(f"📚 Found {len(articles)} articles to fetch\n")

    # Create output directory
    output_dir = Path("articles")
    output_dir.mkdir(exist_ok=True)

    # Statistics
    success_count = 0
    error_count = 0

    # Launch browser
    with sync_playwright() as p:
        print("🌐 Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT)

        # Load cookies from environment variables
        uuid_tt_dd = os.getenv("CSDN_UUID_TT_DD")
        username = os.getenv("CSDN_USERNAME", "u012587406")
        user_token = os.getenv("CSDN_USER_TOKEN")

        if not uuid_tt_dd or not user_token:
            print("❌ Error: Missing required environment variables!")
            print("   Please set CSDN_UUID_TT_DD and CSDN_USER_TOKEN in .env file")
            return

        # Add cookies
        context.add_cookies([
            {"name": "uuid_tt_dd", "value": uuid_tt_dd, "domain": ".csdn.net", "path": "/"},
            {"name": "UserName", "value": username, "domain": ".csdn.net", "path": "/"},
            {"name": "UserToken", "value": user_token, "domain": ".csdn.net", "path": "/"},
        ])

        page = context.new_page()

        # Process each article
        for i, article in enumerate(articles, 1):
            print(f"\n[{i}/{len(articles)}] {article['title']}")
            article_id = extract_article_id(article['url'])

            if not article_id:
                print(f"  ⚠️  Skipping - invalid URL")
                error_count += 1
                continue

            # Fetch content
            html_content = fetch_article_content(page, article['url'], article_id)

            if html_content:
                # Convert to markdown
                markdown_content = convert_to_markdown(html_content)

                # Save file
                if save_article(article, markdown_content, output_dir):
                    success_count += 1
                else:
                    error_count += 1
            else:
                error_count += 1

            # Rate limiting
            time.sleep(2)

        browser.close()

    # Summary
    print("\n" + "="*60)
    print("✨ Sync Complete!")
    print("="*60)
    print(f"✅ Success: {success_count}")
    print(f"❌ Errors:  {error_count}")
    print(f"📊 Total:   {len(articles)}")
    print(f"📁 Output:  {output_dir.absolute()}")

if __name__ == "__main__":
    main()
