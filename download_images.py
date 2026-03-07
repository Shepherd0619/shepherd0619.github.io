#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download images from CSDN articles and update markdown files to use local paths.
Only downloads actual article images (i-blog.csdnimg.cn), skips CSDN UI elements.
"""
import sys
import io
import re
import os
import time
import requests
from pathlib import Path
from urllib.parse import urlparse

# Fix Windows encoding issue
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuration
ARTICLES_DIR = Path("articles")
IMAGES_DIR = Path("images")
DELAY_BETWEEN_DOWNLOADS = 1  # seconds
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

# Regex to find markdown images: ![alt](url)
IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\((https?://[^\)]+)\)')

def extract_article_id(filename):
    """Extract article ID from filename (format: {article-id}-{title}.md)"""
    match = re.match(r'^(\d+)', filename.name)
    return match.group(1) if match else None

def is_article_image(url):
    """Check if URL is an actual article image (not CSDN UI element)"""
    return 'i-blog.csdnimg.cn' in url

def download_image(url, save_path):
    """Download image from URL to local path"""
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Save image
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(response.content)

        return True
    except Exception as e:
        print(f"    ❌ Error downloading: {e}")
        return False

def get_image_filename(url, alt_text=""):
    """Generate a filename for the image"""
    # Try to extract filename from URL
    parsed = urlparse(url)
    path = parsed.path

    # Get the last part of the path
    original_filename = path.split('/')[-1]

    # If we have alt text and it looks like a filename, use it
    if alt_text and ('.' in alt_text):
        return alt_text

    # Otherwise use the URL filename
    return original_filename

def process_article(filepath):
    """Process a single article file to download images and update paths"""
    article_id = extract_article_id(filepath)
    if not article_id:
        print(f"  ⚠️  Could not extract article ID from {filepath.name}")
        return 0, 0

    print(f"\n📄 Processing: {filepath.name}")

    # Read article content
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all images
    images = IMAGE_PATTERN.findall(content)

    if not images:
        print(f"  ℹ️  No images found")
        return 0, 0

    # Filter for article images only
    article_images = [(alt, url) for alt, url in images if is_article_image(url)]

    if not article_images:
        print(f"  ℹ️  No article images found (only UI elements)")
        return 0, 0

    print(f"  📷 Found {len(article_images)} article images")

    # Create image directory for this article
    article_image_dir = IMAGES_DIR / article_id
    article_image_dir.mkdir(parents=True, exist_ok=True)

    # Download images and build replacement map
    downloaded = 0
    failed = 0
    replacements = {}

    for alt_text, url in article_images:
        # Generate filename
        filename = get_image_filename(url, alt_text)
        local_path = article_image_dir / filename

        # Skip if already downloaded
        if local_path.exists():
            print(f"  ✓ Already exists: {filename}")
            replacements[url] = f"../images/{article_id}/{filename}"
            downloaded += 1
            continue

        # Download image
        print(f"  ⬇️  Downloading: {filename}")
        if download_image(url, local_path):
            print(f"  ✅ Downloaded: {filename} ({local_path.stat().st_size} bytes)")
            replacements[url] = f"../images/{article_id}/{filename}"
            downloaded += 1
            time.sleep(DELAY_BETWEEN_DOWNLOADS)
        else:
            failed += 1

    # Update markdown content with local paths
    if replacements:
        updated_content = content
        for old_url, new_path in replacements.items():
            # Replace all occurrences of the URL
            updated_content = updated_content.replace(old_url, new_path)

        # Write updated content back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        print(f"  💾 Updated markdown with {len(replacements)} local image paths")

    return downloaded, failed

def main():
    print("🖼️  CSDN Image Downloader")
    print("="*60)
    print(f"Articles directory: {ARTICLES_DIR.absolute()}")
    print(f"Images directory: {IMAGES_DIR.absolute()}")
    print()

    # Create images directory
    IMAGES_DIR.mkdir(exist_ok=True)

    # Get all markdown files
    articles = list(ARTICLES_DIR.glob("*.md"))

    if not articles:
        print("❌ No markdown files found in articles/ directory")
        return

    print(f"📚 Found {len(articles)} articles to process")

    # Process each article
    total_downloaded = 0
    total_failed = 0
    articles_with_images = 0

    for filepath in sorted(articles):
        downloaded, failed = process_article(filepath)
        total_downloaded += downloaded
        total_failed += failed

        if downloaded > 0 or failed > 0:
            articles_with_images += 1

    # Summary
    print("\n" + "="*60)
    print("✨ Image Download Complete!")
    print("="*60)
    print(f"📊 Articles processed: {len(articles)}")
    print(f"📊 Articles with images: {articles_with_images}")
    print(f"✅ Images downloaded: {total_downloaded}")
    print(f"❌ Failed downloads: {total_failed}")
    print(f"📁 Images location: {IMAGES_DIR.absolute()}")

    # Calculate total size
    total_size = 0
    for image_file in IMAGES_DIR.rglob("*"):
        if image_file.is_file():
            total_size += image_file.stat().st_size

    print(f"💾 Total image size: {total_size / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    main()
