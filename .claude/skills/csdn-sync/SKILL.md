---
name: csdn-sync
description: Sync blog articles from CSDN (blog.csdn.net) to local markdown files.
---

## When to use

TRIGGER when:
- User asks to sync CSDN blog/articles
- User mentions fetching or updating articles from CSDN
- User wants to download CSDN blog content

DO NOT TRIGGER when:
- General web scraping tasks unrelated to CSDN
- Working with other blog platforms

## Prerequisites

Before starting:
1. Ensure the `articles` folder exists in the project root
2. Use Chrome UserAgent for all HTTP requests
3. Python 3.11+ with Playwright, html2text, and python-dotenv installed
4. Valid CSDN cookies stored in `.env` file:
   - `CSDN_UUID_TT_DD` (tracking cookie)
   - `CSDN_USERNAME` (CSDN username)
   - `CSDN_USER_TOKEN` (authentication token)
   - `CSDN_COOKIE_STRING` (full cookie string for API requests)
5. **SECURITY**: `.env` file MUST be in `.gitignore` to prevent committing credentials to git

**⚠️ Security Warning:**
- NEVER commit `.env` file to git repository
- NEVER hardcode credentials in Python scripts
- Cookies expire - user may need to refresh them periodically
- If cookies become invalid, re-export from browser after logging into CSDN

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Create .env file with CSDN credentials (see Prerequisites)
# Add to .env:
#   CSDN_UUID_TT_DD=...
#   CSDN_USERNAME=...
#   CSDN_USER_TOKEN=...
#   CSDN_COOKIE_STRING=...

# 3. Fetch article list
python fetch_articles.py

# 4. Fetch article content
python fetch_csdn_content.py

# 5. Download images to local storage
python download_images.py

# 6. (Optional) Re-sync failed articles
python resync_articles.py

# 7. Clean up articles (fix code blocks, remove ads)
python cleanup_articles.py
```

## Overview

The CSDN sync process has four phases:

**Phase 1: Fetch Article List**
- Use `fetch_articles.py` to call CSDN API
- Get article metadata (ID, title, URL, date)
- Save to `articles_metadata.json`
- Loads credentials from `.env` file

**Phase 2: Initial Content Sync**
- Use `fetch_csdn_content.py` with Playwright
- Fetch each article with headless browser
- Full JavaScript rendering for dynamic content
- Convert HTML to Markdown (keeps CSDN CDN image URLs)
- Save to `articles/` folder
- Expected: ~75-80% success rate

**Phase 3: Download Images Locally**
- Use `download_images.py` to download all images
- Downloads from CSDN CDN (i-blog.csdnimg.cn)
- Saves to `images/{article-id}/` folders
- Updates markdown files to reference local paths
- Skips CSDN UI elements (icons, buttons)

**Phase 4: Re-sync Failed Articles (Optional)**
- Use `resync_articles.py` to retry
- Targets articles <1KB or completely missing
- Increased timeout (90s)
- Preserves existing frontmatter

**Why Playwright is needed:**
CSDN uses JavaScript to load article content. Simple HTTP requests only get minimal content. Browser automation is required for full content rendering.

**Why download images:**
- Prevents broken links if CSDN changes/removes images
- Full control over blog content
- Faster loading if hosting locally
- Independence from CSDN CDN

## Workflow

### Step 1: Setup Environment

First, ensure the `.env` file exists with valid CSDN credentials:

```bash
# .env file content
CSDN_UUID_TT_DD=your_uuid_cookie
CSDN_USERNAME=your_username
CSDN_USER_TOKEN=your_token
CSDN_COOKIE_STRING=full_cookie_string_from_browser
```

**How to get cookies:**
1. Open Chrome/Edge and login to CSDN
2. Press F12 → Application → Cookies → https://blog.csdn.net
3. Copy the values for uuid_tt_dd, UserName, UserToken
4. Copy all cookies as a single string for CSDN_COOKIE_STRING

### Step 2: Get List of Articles

Run `fetch_articles.py` to get the article list from CSDN API:

```bash
python fetch_articles.py
```

This script:
- Fetches article list from CSDN API (paginated, 20 per page)
- Saves metadata to `articles_metadata.json`
- Loads credentials from `.env` file automatically

**API Endpoint:**
```
GET https://blog.csdn.net/community/home-api/v1/get-business-list
```

**Query Parameters:**
- `page`: Page number (start with 1, increment as needed)
- `size`: Results per page (20)
- `businessType`: "lately"
- `noMore`: false
- `username`: From CSDN_USERNAME env variable

**Important:**
- Uses CSDN_COOKIE_STRING from .env for authentication
- Automatically paginates through all pages
- If API fails with 521, user needs to refresh cookies in .env file

### Step 3: Fetch Article Content (Initial Sync)

Run `fetch_csdn_content.py` to fetch all article content:

```bash
python fetch_csdn_content.py
```

This script:
- Reads `articles_metadata.json` from Step 2
- Launches headless Chromium browser with Playwright
- Fetches each article with full JavaScript rendering
- Converts HTML to Markdown
- Saves files to `articles/` folder with YAML frontmatter

**Content Extraction Process:**

CSDN uses JavaScript to load article content. The script uses Playwright to:
1. Launch headless browser with anti-bot bypass (cookies + User-Agent)
2. Load each article page with timeout of 60-90 seconds
3. Try multiple content selectors in order:
   - `div.htmledit_views` (primary, cleanest content)
   - `div.markdown_views` (markdown articles)
   - `div#content_views` (older articles)
   - `div.blog-content-box` (fallback, full article container)
4. Validate content length (>100 chars) to ensure actual content
5. Convert HTML to Markdown using html2text

**Authentication:**
- Loads credentials from `.env` file automatically
- Cookies added to browser context:
  - `uuid_tt_dd` (tracking cookie)
  - `UserName` (CSDN username)
  - `UserToken` (authentication token)
- User-Agent: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36`

**Rate Limiting:**
- 2-second delay between requests to avoid anti-bot detection
- 60-90 second timeout per article page
- Don't make more than 30 requests per minute

### Step 4: Markdown Conversion

The `fetch_csdn_content.py` and `resync_articles.py` scripts automatically convert HTML to Markdown with these settings:

**html2text Configuration:**
```python
h = html2text.HTML2Text()
h.ignore_links = False        # Preserve links
h.ignore_images = False       # Preserve images (CSDN CDN URLs)
h.ignore_emphasis = False     # Preserve bold/italic
h.body_width = 0             # Don't wrap lines
h.unicode_snob = True        # Handle Unicode properly
h.skip_internal_links = True # Skip internal anchors
```

**What is preserved:**
- Headings (H1-H6)
- Code blocks with language syntax
- Images (keeps CSDN CDN URLs at i-blog.csdnimg.cn)
- Lists (ordered and unordered)
- Tables
- Links
- Bold, italic, and other formatting

**Important:** Content is kept in original language (Chinese). Filenames use article ID to avoid encoding issues.

### Step 5: File Structure

Each article is saved as a markdown file in the `articles/` folder:

**Filename Pattern:**
```
{article-id}-{sanitized-title}.md
```
- Article ID comes first (e.g., `158568321-`)
- Title is sanitized (Chinese characters preserved in filename)
- Falls back to just `{article-id}.md` if needed

**File Structure:**
```markdown
---
title: 【IT 实战】使用 EntraRadius 打通 FreeRADIUS 与 Microsoft Entra 的认证桥梁
url: https://blog.csdn.net/u012587406/article/details/158568321
date: 2026.03.02
articleId: 158568321
---

[Article content in Markdown]
```

### Step 6: Download Images Locally

Download all article images from CSDN CDN to local storage:

```bash
python download_images.py
```

**What it does:**

1. **Scans all markdown files** in `articles/` folder
2. **Extracts image URLs** using regex pattern `![alt](url)`
3. **Filters for article images only:**
   - Includes: `i-blog.csdnimg.cn` (actual article images)
   - Excludes: `csdnimg.cn/release/blogv2` (CSDN UI elements like icons)
4. **Downloads images** to organized folders:
   - Structure: `images/{article-id}/{image-filename}`
   - Example: `images/158568321/screenshot.png`
5. **Updates markdown files** to reference local paths:
   - Before: `![](https://i-blog.csdnimg.cn/blog_migrate/abc123.png)`
   - After: `![](../images/158568321/abc123.png)`
6. **Skips already downloaded** images to avoid re-downloading

**Output:**
```
🖼️  CSDN Image Downloader
============================================================
Articles directory: D:\shepherd0619.github.io\articles
Images directory: D:\shepherd0619.github.io\images

📚 Found 48 articles to process

📄 Processing: 158568321-IT-实战.md
  📷 Found 5 article images
  ⬇️  Downloading: screenshot1.png
  ✅ Downloaded: screenshot1.png (125672 bytes)
  💾 Updated markdown with 5 local image paths

============================================================
✨ Image Download Complete!
============================================================
📊 Articles processed: 48
📊 Articles with images: 23
✅ Images downloaded: 87
❌ Failed downloads: 2
📁 Images location: D:\shepherd0619.github.io\images
💾 Total image size: 12.34 MB
```

**Benefits:**
- **No broken links** - Images won't disappear if CSDN removes them
- **Faster loading** - No dependency on CSDN CDN
- **Full control** - Complete ownership of content
- **Offline access** - Works without internet connection
- **Version control** - Images tracked in git alongside content

**Image Organization:**
```
shepherd0619.github.io/
├── articles/
│   ├── 158568321-article.md  (references ../images/158568321/...)
│   └── 156699031-article.md  (references ../images/156699031/...)
└── images/
    ├── 158568321/
    │   ├── screenshot1.png
    │   └── diagram.jpg
    └── 156699031/
        └── photo.png
```

### Step 7: Re-sync Articles with Minimal Content

After initial sync, some articles may have minimal content (<1KB) due to JavaScript loading issues.

**Re-sync Workflow:**

Run the resync script to handle failed articles:

```bash
python resync_articles.py
```

**What it does:**

1. **Identifies articles to re-fetch:**
   - Scans `articles/` folder for files <1KB (MIN_CONTENT_SIZE = 1000 bytes)
   - Extracts article IDs from filenames (format: `{article-id}-{title}.md`)
   - Generates article URLs

2. **Fetches with browser automation:**
   - Launches headless Chromium browser with cookies from `.env`
   - Loads each article page with full JavaScript rendering
   - Timeout increased to 90 seconds for slow pages
   - Tries multiple content selectors (htmledit_views, markdown_views, etc.)
   - Validates content length (>100 chars)
   - Converts HTML to Markdown

3. **Updates files while preserving frontmatter:**
   - Extracts existing YAML frontmatter
   - Replaces content section with newly fetched markdown
   - Saves updated file

4. **Reports results:**
   ```
   ============================================================
   ✨ Re-sync Complete!
      Success: 1
      Errors:  0
      Total:   1
   ============================================================
   ```

### Step 8: Clean Up Articles

After syncing, run the cleanup script to fix formatting issues:

```bash
python cleanup_articles.py
```

**What it does:**

1. **Fixes code blocks:**
   - Converts numbered lists that look like code → proper markdown code blocks
   - Detects language (C#, Python, JavaScript, etc.)
   - Removes excessive blank lines within code
   - Preserves one blank line between logical sections

2. **Removes CSDN UI elements:**
   - CSDN toolbar icons (runCode buttons, etc.)
   - CSDN AI tool advertisements ("AI写代码", "AI助手", etc.)
   - CSDN UI buttons ("运行", "测试", "复制", "分享", "收藏", "点赞", "评论")
   - Other CSDN-specific UI artifacts

3. **Cleans up formatting:**
   - Removes excessive consecutive blank lines (max 2)
   - Standardizes spacing
   - Preserves article structure

**Output:**
```
🧹 CSDN Article Cleanup
============================================================
Articles directory: D:\shepherd0619.github.io\articles

📚 Found 48 articles to process

📄 Processing: 134073435-使用partial修饰符.md
  ✅ Fixed! 1 UI elements removed, blank lines cleaned

============================================================
✨ Cleanup Complete!
============================================================
📊 Articles processed: 48
✅ Articles cleaned: 37
ℹ️  No changes needed: 11
```

**Common Issues Fixed:**

| Issue | Before | After |
|-------|--------|-------|
| Code blocks | `1. using System;`<br>`2. public class Foo` | ` ` ```csharp`<br>`using System;`<br>`public class Foo`<br>` ``` ` |
| CSDN UI | `![](https://csdnimg.cn/release/.../icon.png)` | *Removed* |
| Ads | `AI写代码cs` | *Removed* |
| Blank lines | 5+ consecutive blank lines | Max 2 blank lines |

### Step 9: Final Review and Summary

After sync completion, provide a comprehensive summary:

```bash
# Check article count and size
cd articles
ls -1 *.md | wc -l
du -sh .
```

**Summary Format:**
```
📊 CSDN Blog Sync Summary

✅ Overall Results
- Total articles on CSDN: 62
- Successfully synced: 48 articles
- Failed to sync: 14 articles
- Success rate: 77% (48/62)
- Total storage: 324 KB

📁 Article Distribution
- < 1KB: 1 article (may need manual review)
- 1KB - 1MB: 47 articles ✅
- > 1MB: 0 articles

🖼️ Image Statistics
- Articles with images: 23
- Total images downloaded: 87
- Images failed: 2
- Total image size: 12.34 MB
- Image location: images/

⚠️ Failed Articles (14)
[List of article IDs and titles that failed]

🔧 Files Created
- fetch_articles.py
- fetch_csdn_content.py
- download_images.py
- resync_articles.py
- .env (credentials)
- requirements.txt
- articles_metadata.json
- articles/*.md (48 files)
- images/{article-id}/*.{png,jpg,gif} (87 files)
```

**What to tell the user:**
- Number of articles successfully fetched
- Number of articles that failed (with reasons if known)
- Number of images downloaded and total size
- Total storage size (articles + images)
- Location of synced files (`articles/` and `images/` folders)
- How to retry failed articles (update .env cookies and run resync_articles.py)
- Typical success rate is 75-80%

## Error Handling

**Common Issues:**

1. **UnicodeEncodeError on Windows**
   - Symptom: `'gbk' codec can't encode character`
   - Fix: Add UTF-8 wrapper for stdout/stderr:
     ```python
     if sys.platform == 'win32':
         import io
         sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
         sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
     ```

2. **CSDN Anti-Bot Detection**
   - Symptom: Selectors not found, timeouts, CAPTCHA pages
   - Fix: Use authenticated browser context with cookies and User-Agent
   - User must provide valid CSDN cookies from their browser

3. **Content Not Found**
   - Symptom: All selectors return "Not found"
   - Fix: CSDN may have changed HTML structure - inspect live page and update selectors
   - Try multiple selector fallbacks in order

4. **Timeout Errors**
   - Symptom: `Page.goto: Timeout 60000ms exceeded`
   - Fix: Timeout is already set to 90000ms (90s) in resync_articles.py
   - Check network connection
   - Article may have heavy content or slow CSDN server response
   - Some articles may legitimately timeout - this is expected

5. **Minimal Content After Fetch**
   - Symptom: Article saved but <1KB in size
   - Fix: Run `resync_articles.py` which specifically targets articles <1KB
   - Validates content length >100 chars before accepting

**Rate Limiting:**
- Always use 2-second delay between requests
- Don't make more than 30 requests per minute

6. **Missing Environment Variables**
   - Symptom: `❌ Error: Missing required environment variables!`
   - Fix: Check `.env` file exists and contains all required variables
   - Ensure variable names match exactly (case-sensitive)
   - Verify no extra spaces around `=` sign

7. **Cookies Expired**
   - Symptom: API returns 521, empty content, or authentication errors
   - Fix: Login to CSDN in browser, export fresh cookies
   - Update `.env` file with new cookie values
   - Cookies typically expire after a few days/weeks

## Troubleshooting

**Script fails immediately:**
- Check `.env` file exists in project root
- Verify Python dependencies installed: `pip install -r requirements.txt`
- Verify Playwright browser installed: `playwright install chromium`

**Low success rate (<50%):**
- Cookies may be expired - refresh in `.env`
- Network connection issues - check internet
- CSDN may be blocking requests - add longer delays
- Try running resync_articles.py for failed articles

**All articles showing minimal content:**
- Selectors may have changed - check CSDN HTML structure
- JavaScript not rendering - verify Playwright setup
- Timeout too short - increase to 90s or more

**Files have wrong encoding:**
- Verify UTF-8 output wrapper for Windows (already in scripts)
- Check file encoding in editor (should be UTF-8)

## Tools to Use

**Python Scripts (Primary Method):**

1. **`fetch_articles.py`** - Fetch article list from CSDN API
   ```bash
   python fetch_articles.py
   ```
   - Outputs: `articles_metadata.json`
   - Loads credentials from `.env`
   - Paginates through all articles

2. **`fetch_csdn_content.py`** - Fetch all article content (initial sync)
   ```bash
   python fetch_csdn_content.py
   ```
   - Reads: `articles_metadata.json`
   - Outputs: `articles/*.md` files
   - Uses Playwright headless browser
   - Loads credentials from `.env`

3. **`download_images.py`** - Download images from CSDN to local storage
   ```bash
   python download_images.py
   ```
   - Reads: `articles/*.md` files
   - Downloads images from i-blog.csdnimg.cn
   - Outputs: `images/{article-id}/*.{png,jpg,gif}`
   - Updates markdown files with local image paths
   - No credentials needed (public images)

4. **`cleanup_articles.py`** - Clean up article formatting and remove CSDN UI elements
   ```bash
   python cleanup_articles.py
   ```
   - Fixes code blocks (numbered lists → proper markdown)
   - Removes CSDN UI elements (icons, ads, AI tools)
   - Cleans excessive blank lines
   - No credentials needed

5. **`resync_articles.py`** - Re-fetch articles with minimal content
   ```bash
   python resync_articles.py
   ```
   - Scans for files <1KB in `articles/` folder
   - Re-fetches with increased timeout
   - Preserves existing frontmatter
   - Loads credentials from `.env`

**Dependencies:**
```bash
# Install dependencies (run once)
pip install -r requirements.txt
playwright install chromium
```

**Files:**
- `requirements.txt` - Dependencies (playwright, html2text, python-dotenv, requests)
- `.env` - CSDN credentials (must create manually)
- `.gitignore` - Must include `.env` to prevent credential leaks
- `articles/` - Synced markdown files
- `images/` - Downloaded article images (organized by article ID)

**Claude Tools (for orchestration):**
- **Bash**: Run Python scripts, check file counts, view results
- **Read**: Check script output, verify .env file exists
- **Write**: Create .env file template if needed

**Expected Success Rate:**
- ~75-80% success rate (48/62 in last run)
- Common failures: timeouts, anti-bot detection, legitimately short articles, content not found
- Failed articles can be retried by updating cookies in .env

## Success Criteria

- **75-80% of articles** fetched successfully (some failures are expected)
- Content properly converted to clean Markdown with:
  - YAML frontmatter (title, url, date, articleId)
  - Preserved formatting (headings, code blocks, images, links)
  - Original language content (Chinese)
  - Images linked to CSDN CDN
- Files saved in `articles/` folder with article ID in filename
- `.env` file created and added to `.gitignore`
- User informed of:
  - Total articles found
  - Number successfully synced
  - Number failed (with list if <20% of total)
  - Total storage size
  - How to retry failed articles

**Note:** A 100% success rate is unlikely due to:
- CSDN anti-bot detection
- Legitimately short/empty articles
- Network timeouts
- Slow-loading pages
- Temporary CSDN server issues
