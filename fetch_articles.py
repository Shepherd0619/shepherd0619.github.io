#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import io
import json
import time
import os
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fix Windows encoding issue
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load configuration from environment variables
COOKIE = os.getenv("CSDN_COOKIE_STRING")
USERNAME = os.getenv("CSDN_USERNAME", "u012587406")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

if not COOKIE:
    print("❌ Error: Missing CSDN_COOKIE_STRING in .env file")
    sys.exit(1)

articles = []

print("Fetching article list from CSDN API...")

for page in range(1, 6):  # Try up to 5 pages
    url = f"https://blog.csdn.net/community/home-api/v1/get-business-list?page={page}&size=20&businessType=lately&noMore=false&username={USERNAME}"

    cmd = [
        'curl', '-s', url,
        '-H', f'Cookie: {COOKIE}',
        '-H', f'User-Agent: {USER_AGENT}',
        '-H', 'Referer: https://blog.csdn.net/?type=blog'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        data = json.loads(result.stdout)

        if data['code'] != 200:
            print(f"❌ Page {page}: API error - {data.get('message', 'Unknown error')}")
            break

        page_articles = data['data']['list']

        if not page_articles:
            print(f"📄 Page {page}: No more articles")
            break

        articles.extend(page_articles)
        print(f"✅ Page {page}: {len(page_articles)} articles fetched (total: {len(articles)})")

        time.sleep(2)  # Rate limiting

    except Exception as e:
        print(f"❌ Page {page}: Error - {e}")
        break

print(f"\n📊 Total articles fetched: {len(articles)}")

# Save to file
with open('articles_metadata.json', 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"💾 Saved metadata to articles_metadata.json")

# Print summary
print("\n" + "="*60)
print("Article Summary:")
print("="*60)
for i, article in enumerate(articles[:5], 1):
    article_id = article['url'].split('/')[-1]
    print(f"{i}. [{article_id}] {article['title']}")
print(f"... and {len(articles) - 5} more articles" if len(articles) > 5 else "")
