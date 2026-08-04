# shepherd0619.github.io

Personal portfolio & blog site, built as a static single-page application.

## Tech Stack

- **Frontend:** Vanilla HTML/CSS/JS with lazy-loaded blog section
- **Blog:** [11ty (Eleventy)](https://www.11ty.dev/) — Markdown → static HTML
- **CI/CD:** GitHub Actions auto-builds blog on push to `blog/**`
- **Images:** Git LFS for binary assets

## Project Structure

```
├── index.html              # Main single-page portfolio
├── css/style.css           # All styles (including blog)
├── js/script.js            # Lazy blog loader + lightbox
├── images/                 # Portfolio & profile images (LFS)
├── blog/
│   ├── posts-src/          # Markdown source files
│   ├── posts/              # Generated HTML (committed by CI)
│   ├── index.njk           # Blog list template entry
│   └── blog.11tydata.js    # Shared frontmatter defaults
├── _include/layouts/       # Nunjucks layout templates
├── .eleventy.js            # 11ty config
├── .github/workflows/      # CI pipeline
└── package.json            # Node dependencies (11ty)
```

## Local Development

```bash
npm install
npm run build:blog          # Build blog HTML from Markdown
npx http-server -p 3000    # Serve locally
```

## Blog Posts

Add new posts as `.md` files under `blog/posts-src/` with the following frontmatter:

```yaml
---
title: "Post Title"
date: 2024-01-15
source: https://example.com/original-post
categories: IT 运维
tags:
  - Entra ID
  - Terraform
---
```
