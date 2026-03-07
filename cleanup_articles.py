#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive cleanup script for CSDN articles:
1. Fix code blocks (numbered lists → proper code blocks)
2. Remove CSDN UI elements (ads, icons, buttons)
3. Remove excessive blank lines
4. Clean up formatting issues
"""
import sys
import io
import re
from pathlib import Path

# Fix Windows encoding issue
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuration
ARTICLES_DIR = Path("articles")

# CSDN UI elements to remove (these are not article content)
CSDN_UI_PATTERNS = [
    r'!\[\]\(https://csdnimg\.cn/release/blogv2/dist/pc/img/.*?\)',  # CSDN UI images
    r'!\[.*?\]\(https://csdnimg\.cn/release/.*?\)',  # Any CSDN release images
    r'^\s*AI写代码.*$',  # AI code writing ads
    r'^\s*CSDN.*助手.*$',  # CSDN assistant ads
    r'^\s*生成.*代码.*$',  # Code generation ads
]

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content"""
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if match:
        return match.group(1), match.group(2)
    return None, content

def is_code_line(line):
    """Check if a line looks like code"""
    cleaned = re.sub(r'^\s*\d+\.\s*', '', line).strip()

    code_patterns = [
        r'^\s*(using|import|from|include|#include)',
        r'^\s*(public|private|protected|internal|static|class|interface|struct|enum)',
        r'^\s*(void|int|float|double|bool|string|var|let|const)',
        r'^\s*{|\s*}',
        r'^\s*//',
        r'^\s*\[.*\]',
        r'^\s*return\s+',
        r'^\s*if\s*\(|while\s*\(|for\s*\(',
        r'.*\(.*\)\s*{?\s*$',
        r'.*[;{}]\s*$',
        r'^\s*<.*>',
        r'^\s*override\s+',
    ]

    for pattern in code_patterns:
        if re.match(pattern, cleaned):
            return True

    return False

def remove_csdn_ui_elements(content):
    """Remove CSDN UI elements (ads, icons, buttons)"""
    # Remove pattern-based UI elements
    for pattern in CSDN_UI_PATTERNS:
        content = re.sub(pattern, '', content, flags=re.MULTILINE)

    # Remove lines that are clearly CSDN ads/UI (case-insensitive, whole line match)
    lines = content.split('\n')
    cleaned_lines = []

    for line in lines:
        line_lower = line.strip().lower()

        # Skip lines that are CSDN ads or UI elements
        # Must be standalone (not part of actual content)
        stripped = line.strip()

        # Skip if it's JUST a UI keyword (not part of normal text)
        if stripped in [
            '运行',  # Run button
            '测试',  # Test button
            '复制',  # Copy button
            '分享',  # Share button
            '收藏',  # Favorite button
            '点赞',  # Like button
            '评论',  # Comment button
        ] or any(ad_keyword in line_lower for ad_keyword in [
            'ai写代码',
            'ai工具',
            'ai助手',
            '智能工具',
            'copilot',
            '代码助手',
            'csdn助手',
        ]):
            continue

        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)

def remove_excessive_blank_lines(content):
    """Remove more than 2 consecutive blank lines"""
    # Replace 3+ blank lines with just 2
    content = re.sub(r'\n\n\n+', '\n\n', content)
    return content

def fix_code_blocks(content):
    """Convert numbered lists that look like code into proper markdown code blocks"""
    lines = content.split('\n')
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this looks like the start of a numbered code block
        if re.match(r'^\s*1\.\s+', line) and is_code_line(line):
            # Found potential code block, collect all numbered lines
            code_lines = []

            # Collect consecutive numbered lines
            j = i
            while j < len(lines):
                current = lines[j]

                if re.match(r'^\s*\d+\.\s+', current):
                    # Extract the actual code (remove number and leading spaces)
                    code_content = re.sub(r'^\s*\d+\.\s+', '', current)
                    code_lines.append(code_content)
                    j += 1
                elif current.strip() == '' and j + 1 < len(lines) and re.match(r'^\s*\d+\.\s+', lines[j + 1]):
                    code_lines.append('')
                    j += 1
                else:
                    break

            # If we collected multiple lines that look like code, convert to code block
            if len(code_lines) >= 3:
                # Detect language
                lang = 'csharp'  # Default to C# for Unity articles
                first_code = code_lines[0].lower()
                if 'using system' in first_code or 'using unity' in first_code:
                    lang = 'csharp'
                elif 'import' in first_code or 'from ' in first_code:
                    lang = 'python'
                elif 'const' in first_code or 'let' in first_code or 'var' in first_code:
                    lang = 'javascript'
                elif '#include' in first_code:
                    lang = 'cpp'
                elif 'bash' in first_code or '#!/bin' in first_code:
                    lang = 'bash'

                # Clean up code lines - remove all blank lines (CSDN adds lots of them)
                # Keep only one blank line max between sections
                cleaned_code = []
                blank_count = 0
                for code_line in code_lines:
                    is_blank = code_line.strip() == ''
                    if is_blank:
                        blank_count += 1
                        # Allow max 1 blank line
                        if blank_count <= 1:
                            cleaned_code.append(code_line)
                    else:
                        blank_count = 0
                        cleaned_code.append(code_line)

                # Add code block
                result.append(f'```{lang}')
                result.extend(cleaned_code)
                result.append('```')
                result.append('')

                i = j
                continue

        result.append(line)
        i += 1

    return '\n'.join(result)

def cleanup_article(content):
    """Apply all cleanup operations"""
    # 1. Remove CSDN UI elements
    content = remove_csdn_ui_elements(content)

    # 2. Fix code blocks
    content = fix_code_blocks(content)

    # 3. Remove excessive blank lines
    content = remove_excessive_blank_lines(content)

    return content

def process_file(filepath):
    """Process a single markdown file"""
    print(f"📄 Processing: {filepath.name}")

    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract frontmatter
        frontmatter, body = extract_frontmatter(content)

        # Cleanup body
        cleaned_body = cleanup_article(body)

        # Check if anything changed
        if cleaned_body == body:
            print(f"  ℹ️  No changes needed")
            return False

        # Reconstruct file with frontmatter
        if frontmatter:
            new_content = f"---\n{frontmatter}\n---\n{cleaned_body}"
        else:
            new_content = cleaned_body

        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # Count changes
        ui_elements_removed = body.count('csdnimg.cn/release') - cleaned_body.count('csdnimg.cn/release')
        code_blocks_created = (new_content.count('```') - content.count('```')) // 2
        blank_lines_removed = body.count('\n\n\n') - cleaned_body.count('\n\n\n')

        changes = []
        if ui_elements_removed > 0:
            changes.append(f"{ui_elements_removed} UI elements removed")
        if code_blocks_created > 0:
            changes.append(f"{code_blocks_created} code blocks fixed")
        if blank_lines_removed > 0:
            changes.append(f"blank lines cleaned")

        print(f"  ✅ Fixed! {', '.join(changes) if changes else 'improved formatting'}")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("🧹 CSDN Article Cleanup")
    print("="*60)
    print(f"Articles directory: {ARTICLES_DIR.absolute()}")
    print()

    # Get all markdown files
    articles = list(ARTICLES_DIR.glob("*.md"))

    if not articles:
        print("❌ No markdown files found in articles/ directory")
        return

    print(f"📚 Found {len(articles)} articles to process\n")

    # Process each article
    fixed_count = 0

    for filepath in sorted(articles):
        if process_file(filepath):
            fixed_count += 1

    # Summary
    print("\n" + "="*60)
    print("✨ Cleanup Complete!")
    print("="*60)
    print(f"📊 Articles processed: {len(articles)}")
    print(f"✅ Articles cleaned: {fixed_count}")
    print(f"ℹ️  No changes needed: {len(articles) - fixed_count}")

if __name__ == "__main__":
    main()
