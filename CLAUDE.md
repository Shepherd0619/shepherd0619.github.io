# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal portfolio & blog site — a static single-page application with a lazy-loaded blog section. Hosted on GitHub Pages at `shepherd0619.github.io`.

## Commands

```bash
npm install                  # Install 11ty (only dev dependency)
npm run build:blog           # Build blog HTML from Markdown into blog/
npx http-server -p 3000      # Serve locally for development
```

There are no tests, linters, or other build steps.

## Architecture

### Frontend (index.html + css/style.css + js/script.js)

The main page is a **single-page application** with section-based navigation. All sections (Home, About, Skills, Blog, Portfolio) live in `index.html` as `<section class="section">` elements. Only the active section is visible — `js/script.js` toggles `.active` and `.back-section` classes on `<section>` elements for slide transitions.

The sidebar (`<div class="aside">`) contains navigation links. On mobile (<1200px), the sidebar is hidden off-screen and toggled via a hamburger button.

**Theme system**: Skin colors are handled by alternate CSS files in `css/skins/` (blue, pink, orange, yellow, green). `js/styleSwitcher.js` enables/disables these `<link>` elements. Light/dark mode is toggled by adding/removing `class="dark"` on `<body>`. Dark mode colors are defined in `style.css` under `body.dark` selectors.

### Blog (Eleventy/11ty)

The blog is a **separate build system** embedded within the site:

- **Source**: `blog/posts-src/*.md` — Markdown files with YAML frontmatter (`title`, `date`, `categories`, `tags`, `source`)
- **Build**: `npx @11ty/eleventy` reads from `blog/` (input), outputs to `blog/` (output, same directory)
- **Templates**: `_include/layouts/` — `post.njk` (individual post layout) and `blog-list.njk` (listing page)
- **Data**: `blog/blog.11tydata.js` — shared frontmatter defaults; applies `post.njk` layout, sets `permalink`, auto-generates `summary` from first 120 chars of Markdown body
- **11ty config**: `.eleventy.js` — defines `dateString`, `truncate`, `categoryClass`, `reverse`, `striptags` filters; `fixImagePaths` transform (rewrites `images/` → `/blog/images/`); `postsIndex` collection

**Generated output**: `blog/index.html` (the list page) and `blog/posts/<slug>.html` (individual posts). Both are committed to the repo and served as static files.

### Blog Loading Mechanism

The blog section of the SPA does NOT contain blog content at build time. Instead, `js/script.js` implements a **lazy-loading pattern**:

1. When the user navigates to `#blog` (or the blog section scrolls into view via `IntersectionObserver`), JavaScript `fetch()`es `/blog/index.html`
2. The fetched HTML is parsed with `DOMParser` and the `.blog-list-section` element is extracted and injected into `#blog-container`
3. Category filter buttons and post click handlers are wired up after injection
4. Clicking a post fetches `/blog/posts/<slug>.html`, extracts `.blog-post-content`, and displays it in the blog lightbox (`#blog-lightbox`)

This means blog styles exist in `css/style.css` but blog HTML only exists on the page after JS loads it.

### Blog Lightbox (post reading)

The blog lightbox (`#blog-lightbox`) is a full-viewport overlay that displays individual post content. On mobile (<767px), it goes full-screen. The close button is always visible at the top, and only the article body scrolls. Close via: close button click, backdrop click, or Escape key.

### CI/CD (`.github/workflows/build-blog.yml`)

Triggered on push to `main` when `blog/**` changes. Steps: checkout → setup Node 20 → `npm ci` → `npm run build:blog` → commit generated `blog/index.html` and `blog/posts/` back to the repo. Uses `[skip ci]` in the commit message to prevent recursive builds.

## Key Design Rules

- When editing blog styles, changes go in `css/style.css` (blog section + blog lightbox styles start around line 917)
- When editing blog templates, changes go in `_include/layouts/` — these are Nunjucks templates processed by 11ty
- Blog frontmatter `categories` maps to CSS class names via the `categoryClass` filter in `.eleventy.js` (Chinese names → Latin slug)
- The `source` frontmatter field in posts provides the "原文链接" (original link) in the post footer
- Images in blog posts use relative paths (`images/xxx.png`) which get rewritten to absolute (`/blog/images/xxx.png`) by the `fixImagePaths` transform — this is needed because post pages live at `/blog/posts/`
