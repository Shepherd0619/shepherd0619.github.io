# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a static personal portfolio website for Shepherd Zhu, hosted on GitHub Pages at `shepherd0619.github.io`. The site is built with pure HTML, CSS, and vanilla JavaScript with no build tools or dependencies.

## Architecture

### Single-Page Application Structure

The entire site is contained in [index.html](index.html) (891 lines), which implements a single-page application with section-based navigation:

- **Home** (`#home`) - Introduction and social links
- **About** (`#about`) - Resume with education, work experience, and project experience timelines
- **Portfolio** (`#portfolio`) - Portfolio items with filtering and lightbox viewer
- **Services** (`#services`) - Skills showcase

Navigation is handled by [js/script.js](js/script.js), which:
- Shows/hides sections using `.active` and `.back-section` classes
- Updates the aside navigation state
- Toggles mobile navigation on screens < 1200px

### Key JavaScript Features

#### Portfolio System ([js/script.js](js/script.js))
- **Filtering**: Portfolio items have `data-category` attributes. Filter buttons update visibility using `.show` and `.hide` classes
- **Lightbox**: Clicking portfolio items opens a full-screen image viewer with prev/next navigation
- **Image cycling**: `itemIndex` tracks current image, wraps around at boundaries

#### Theme System ([js/styleSwitcher.js](js/styleSwitcher.js))
- **Color themes**: 5 color skins in `css/skins/` (blue, pink, orange, yellow, green)
- **Theme switching**: Enables/disables alternate stylesheets based on `title` attribute
- **Dark mode**: Toggle between `body.className = "dark"` and `body.className = ""`

### Styling Architecture

- [css/style.css](css/style.css) - Base styles, layout system, component styles
- [css/skins/*.css](css/skins/) - Color theme variables (override CSS custom properties)
- [css/styleSwitcher.css](css/styleSwitcher.css) - Theme switcher widget styles

The layout uses a sidebar (`aside`) + main content pattern with custom grid/flexbox layout (no framework).

## Local Development

### Preview the Site

Since this is a static site, open [index.html](index.html) directly in a browser:

```bash
# Option 1: Open directly
open index.html  # macOS
start index.html # Windows

# Option 2: Use a simple HTTP server (recommended for testing Google Translate widget)
python -m http.server 8000
# or
npx serve .
```

Visit `http://localhost:8000` if using a server.

### Testing Considerations

- **Responsive design**: Test at breakpoint `1200px` (mobile nav triggers) and `768px` (Google Translate widget adjusts)
- **Section navigation**: Click nav links and verify smooth scrolling and section visibility
- **Portfolio**: Test filtering (all, metaverse, unity, etc.) and lightbox navigation
- **Theme switcher**: Test all 5 color themes and dark/light mode toggle

## Content Update Patterns

### Adding Timeline Items

Timeline items (education, work experience, project experience) follow this structure:

```html
<div class="timeline-item">
  <div class="circle-dot"></div>
  <h6 class="timeline-date">
    <i class="fa fa-calendar"></i> START_DATE - END_DATE
  </h6>
  <h4 class="timeline-title">TITLE</h4>
  <p class="timeline-text">CONTENT</p>
</div>
```

### Adding Portfolio Items

Portfolio items require:
1. HTML structure with `data-category` attribute matching filter buttons
2. Image path (local or external URL)
3. Title in `<h4>` (displayed in lightbox caption)

### Special Callout Styling

The Wicresoft job experience uses a custom callout:

```html
<div class="callout callout-warning">
  因美国总统拜登签署的第14117号行政命令...
</div>
```

This styling is defined inline in [css/style.css](css/style.css) for visual emphasis.

## Git and Deployment

### Workflow

- Main branch: `main` (auto-deploys to GitHub Pages)
- Feature branches: Use descriptive names like `feature/csdn-blog-sync`
- Commits are typically direct to main for content updates, or via feature branches for larger changes

### GitHub Pages

Changes pushed to `main` branch automatically deploy to `https://shepherd0619.github.io`. No build step required.

### Recent Patterns

Recent commits show:
- Content updates (job experience, certifications, project details)
- UI refinements (widescreen fixes, callout styles)
- Feature additions (Google Translate widget)

## Code Organization Notes

- Chinese content is used throughout (primary language)
- Font Awesome 4.7.0 icons via CDN
- Google Fonts: Montserrat (body), Rubik (headings)
- No linting, formatting, or code quality tools configured
- No automated testing
