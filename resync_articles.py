#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSDN Article Re-sync Script
Re-fetches articles with minimal content using Playwright headless browser
"""

import os
import re
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import html2text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fix Windows console encoding for Unicode
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuration
ARTICLES_DIR = Path("articles")
MIN_CONTENT_SIZE = 1000  # bytes - articles smaller than this will be re-fetched
CSDN_USER = "u012587406"
DELAY_BETWEEN_REQUESTS = 2  # seconds

def extract_article_id(filename):
    """Extract article ID from filename like '158568321-title.md'"""
    match = re.match(r'^(\d+)-', filename)
    return match.group(1) if match else None

def get_article_url(article_id):
    """Generate CSDN article URL from ID"""
    return f"https://blog.csdn.net/{CSDN_USER}/article/details/{article_id}"

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content"""
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if match:
        return match.group(0), content[match.end():]
    return "", content

def fetch_article_content(url, context):
    """Fetch article content using Playwright"""
    page = context.new_page()

    try:
        print(f"  Loading {url}...")
        page.goto(url, wait_until="networkidle", timeout=90000)  # Increased timeout to 90s

        # For article content, use htmledit_views which contains the actual article
        # blog-content-box contains header + content, but htmledit_views is cleaner
        selectors_to_try = [
            "div.htmledit_views",         # Actual content (preferred)
            "div.markdown_views",         # Markdown articles
            "div#content_views",          # Older articles
            "div.blog-content-box",       # Full article container
        ]

        content_element = None
        for selector in selectors_to_try:
            content_element = page.query_selector(selector)
            if content_element:
                html = content_element.inner_html()
                text = content_element.inner_text()
                # DEBUG: Show what we found
                print(f"  - Trying {selector}: HTML={len(html)} chars, Text={len(text)} chars")
                # Make sure we got actual content, not just empty div
                if len(text.strip()) > 100:
                    print(f"  ✓ Found content using: {selector} ({len(text)} chars)")
                    break
                else:
                    content_element = None
            else:
                print(f"  - Selector {selector}: Not found")

        if not content_element:
            print("  ⚠️  Warning: No content container found or content too short")
            return None

        html_content = html

        # Also try to get the title from the page
        title_element = page.query_selector("h1.title-article")
        title = title_element.inner_text() if title_element else None

        return {
            'html': html_content,
            'title': title
        }

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None
    finally:
        page.close()

def html_to_markdown(html_content):
    """Convert HTML to Markdown"""
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    h.body_width = 0  # Don't wrap lines
    h.unicode_snob = True
    h.skip_internal_links = True

    markdown = h.handle(html_content)
    return markdown.strip()

def update_article_file(filepath, frontmatter, new_content):
    """Update article file with new content while preserving frontmatter"""
    full_content = frontmatter + "\n" + new_content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)

def main():
    # Find articles with minimal content
    print("🔍 Scanning for articles with minimal content...")
    articles_to_refetch = []

    for filepath in ARTICLES_DIR.glob("*.md"):
        size = filepath.stat().st_size
        if size < MIN_CONTENT_SIZE:
            article_id = extract_article_id(filepath.name)
            if article_id:
                articles_to_refetch.append({
                    'filepath': filepath,
                    'article_id': article_id,
                    'size': size
                })

    if not articles_to_refetch:
        print("✅ No articles need re-fetching!")
        return

    print(f"📋 Found {len(articles_to_refetch)} articles to re-fetch\n")

    # Launch browser with cookies
    with sync_playwright() as p:
        print("🚀 Launching headless browser...")
        browser = p.chromium.launch(headless=True)

        # Create context with cookies (to avoid anti-bot detection)
        # You can update these cookies if needed
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )

        # Add CSDN cookies to bypass anti-bot detection
        # Get cookies from environment variables
        uuid_tt_dd = os.getenv("CSDN_UUID_TT_DD")
        username = os.getenv("CSDN_USERNAME", CSDN_USER)
        user_token = os.getenv("CSDN_USER_TOKEN")

        if not uuid_tt_dd or not user_token:
            print("❌ Error: Missing required environment variables!")
            print("   Please set CSDN_UUID_TT_DD and CSDN_USER_TOKEN in .env file")
            print("   See RESYNC_README.md for instructions")
            return

        context.add_cookies([
            {"name": "uuid_tt_dd", "value": uuid_tt_dd, "domain": ".csdn.net", "path": "/"},
            {"name": "UserName", "value": username, "domain": ".csdn.net", "path": "/"},
            {"name": "UserToken", "value": user_token, "domain": ".csdn.net", "path": "/"},
        ])

        success_count = 0
        error_count = 0

        for i, article in enumerate(articles_to_refetch, 1):
            filepath = article['filepath']
            article_id = article['article_id']

            print(f"\n[{i}/{len(articles_to_refetch)}] Processing: {filepath.name} ({article['size']} bytes)")

            # Read existing file to preserve frontmatter
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_content = f.read()

            frontmatter, _ = extract_frontmatter(existing_content)

            # Fetch new content
            url = get_article_url(article_id)
            result = fetch_article_content(url, context)

            if result and result['html']:
                # Convert to markdown
                markdown_content = html_to_markdown(result['html'])

                if len(markdown_content) < 100:
                    print(f"  ⚠️  Warning: Content still seems empty ({len(markdown_content)} chars)")
                    error_count += 1
                else:
                    # Update file
                    update_article_file(filepath, frontmatter, markdown_content)
                    new_size = filepath.stat().st_size
                    print(f"  ✅ Updated! {article['size']}B → {new_size}B")
                    success_count += 1
            else:
                print(f"  ❌ Failed to fetch content")
                error_count += 1

            # Delay between requests to be polite
            if i < len(articles_to_refetch):
                time.sleep(DELAY_BETWEEN_REQUESTS)

        browser.close()

    # Summary
    print(f"\n{'='*60}")
    print(f"✨ Re-sync Complete!")
    print(f"   Success: {success_count}")
    print(f"   Errors:  {error_count}")
    print(f"   Total:   {len(articles_to_refetch)}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
