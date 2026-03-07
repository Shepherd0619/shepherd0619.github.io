# CSDN Article Re-sync Guide

This script re-fetches articles with minimal content using a headless browser to properly render JavaScript-loaded content.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

3. **Configure CSDN cookies:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Get your CSDN cookies:
     1. Open Chrome/Edge and go to https://blog.csdn.net
     2. Log in to your CSDN account
     3. Press F12 to open DevTools
     4. Go to Application tab > Cookies > https://blog.csdn.net
     5. Find these cookies: `uuid_tt_dd`, `UserName`, `UserToken`
   - Edit `.env` and paste your cookie values:
     ```
     CSDN_UUID_TT_DD=10_20293285150-1767351027393-718350
     CSDN_USERNAME=u012587406
     CSDN_USER_TOKEN=981a2c51b6c44201ba87633e0b0021c4
     ```

## Usage

Run the script:
```bash
python resync_articles.py
```

## What It Does

1. Scans `articles/` directory for files smaller than 1KB
2. Extracts article IDs from filenames
3. Launches headless Chromium browser
4. Visits each article URL and waits for JavaScript to load
5. Extracts content from `div.blog-content-box`
6. Converts HTML to Markdown
7. Updates the file while preserving YAML frontmatter
8. Adds 2-second delay between requests to be polite

## Expected Output

```
🔍 Scanning for articles with minimal content...
📋 Found 42 articles to re-fetch

🚀 Launching headless browser...

[1/42] Processing: 144303158-windows-mdt-winpe.md (423 bytes)
  Loading https://blog.csdn.net/u012587406/article/details/144303158...
  ✅ Updated! 423B → 15847B

[2/42] Processing: 144226194-windows-win11.md (398 bytes)
  Loading https://blog.csdn.net/u012587406/article/details/144226194...
  ✅ Updated! 398B → 12934B

...

==========================================================
✨ Re-sync Complete!
   Success: 40
   Errors:  2
   Total:   42
==========================================================
```

## Troubleshooting

- **Timeout errors**: Increase timeout in `fetch_article_content()` (line 48)
- **Content still empty**: CSDN might have changed their HTML structure - check `div.blog-content-box` selector
- **Rate limiting**: Increase `DELAY_BETWEEN_REQUESTS` at the top of the script

## Configuration

Edit these variables in `resync_articles.py`:
- `MIN_CONTENT_SIZE`: Size threshold (default: 1000 bytes)
- `DELAY_BETWEEN_REQUESTS`: Delay in seconds (default: 2)
