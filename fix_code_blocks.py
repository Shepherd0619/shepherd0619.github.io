#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix code blocks in markdown files that were incorrectly converted as numbered lists.
CSDN code blocks often get converted to numbered lists by html2text.
This script detects and fixes them to proper markdown code blocks.
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

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content"""
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if match:
        return match.group(1), match.group(2)
    return None, content

def is_code_line(line):
    """Check if a line looks like code (has common code patterns)"""
    # Remove leading numbers and whitespace
    cleaned = re.sub(r'^\s*\d+\.\s*', '', line).strip()

    # Check for common code patterns
    code_patterns = [
        r'^\s*(using|import|from|include|#include)',  # Imports
        r'^\s*(public|private|protected|internal|static|class|interface|struct|enum)',  # Access modifiers
        r'^\s*(void|int|float|double|bool|string|var|let|const)',  # Type declarations
        r'^\s*{|\s*}',  # Braces
        r'^\s*//',  # Comments
        r'^\s*\[.*\]',  # Attributes
        r'^\s*return\s+',  # Return statements
        r'^\s*if\s*\(|while\s*\(|for\s*\(',  # Control flow
        r'.*\(.*\)\s*{?\s*$',  # Function calls/declarations
        r'.*[;{}]\s*$',  # Ends with semicolon or braces
        r'^\s*<.*>',  # Generic types or XML
        r'^\s*override\s+',  # Override keyword
    ]

    for pattern in code_patterns:
        if re.match(pattern, cleaned):
            return True

    return False

def fix_code_blocks(content):
    """
    Convert numbered lists that look like code into proper markdown code blocks.
    """
    lines = content.split('\n')
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this looks like the start of a numbered code block
        # Pattern: "1. some code" or nested like "    1. using System;"
        # Note: In the markdown source, it's just "1." not "1\."
        if re.match(r'^\s*1\.\s+', line) and is_code_line(line):
            # Found potential code block, collect all numbered lines
            code_lines = []
            indent_level = len(line) - len(line.lstrip())

            # Collect consecutive numbered lines
            j = i
            while j < len(lines):
                current = lines[j]

                # Check if this is a continuation of the numbered list
                if re.match(r'^\s*\d+\.\s+', current):
                    # Extract the actual code (remove number and leading spaces)
                    code_content = re.sub(r'^\s*\d+\.\s+', '', current)
                    code_lines.append(code_content)
                    j += 1
                # Also include empty lines between numbered items (might be part of code)
                elif current.strip() == '' and j + 1 < len(lines) and re.match(r'^\s*\d+\.\s+', lines[j + 1]):
                    code_lines.append('')
                    j += 1
                else:
                    break

            # If we collected multiple lines that look like code, convert to code block
            if len(code_lines) >= 3:  # Minimum 3 lines to be considered a code block
                # Detect language based on first line
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

                # Clean up code lines - remove excessive blank lines
                cleaned_code = []
                prev_blank = False
                for line in code_lines:
                    is_blank = line.strip() == ''
                    # Only add blank line if previous wasn't blank (max 1 consecutive blank line)
                    if not is_blank or not prev_blank:
                        cleaned_code.append(line)
                    prev_blank = is_blank

                # Add code block
                result.append(f'```{lang}')
                result.extend(cleaned_code)
                result.append('```')
                result.append('')  # Add blank line after code block

                i = j
                continue

        result.append(line)
        i += 1

    return '\n'.join(result)

def process_file(filepath):
    """Process a single markdown file to fix code blocks"""
    print(f"📄 Processing: {filepath.name}")

    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract frontmatter
        frontmatter, body = extract_frontmatter(content)

        # Fix code blocks in body
        fixed_body = fix_code_blocks(body)

        # Check if anything changed
        if fixed_body == body:
            print(f"  ℹ️  No code blocks to fix")
            return False

        # Reconstruct file with frontmatter
        if frontmatter:
            new_content = f"---\n{frontmatter}\n---\n{fixed_body}"
        else:
            new_content = fixed_body

        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # Count how many code blocks were created
        code_block_count = new_content.count('```')
        print(f"  ✅ Fixed! Created {code_block_count // 2} code blocks")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("🔧 CSDN Code Block Fixer")
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
    print("✨ Code Block Fix Complete!")
    print("="*60)
    print(f"📊 Articles processed: {len(articles)}")
    print(f"✅ Articles fixed: {fixed_count}")
    print(f"ℹ️  No changes needed: {len(articles) - fixed_count}")

if __name__ == "__main__":
    main()
