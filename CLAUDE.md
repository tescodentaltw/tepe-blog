# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Content repository for TePe dental products marketing — interdental brushes (IDB/牙間刷), toothbrushes, floss, and oral care accessories. All content is in Traditional Chinese targeting Hong Kong/Taiwan audiences.

GitHub: https://github.com/hoishing/tepe-blog

## Repository Structure

```
graphics/          # Educational illustrations & marketing graphics (.webp)
images/            # Product photography (.webp)
tools/             # Utility scripts (Python, run with uv)
idb-main/          # Long-form content hub (markdown + social media folders)
  ├── idb-main.md  # Comprehensive IDB guide (source content for repurposing)
  ├── FB/          # Facebook posts
  ├── IG/          # Instagram posts
  └── Threads/     # Threads posts
```

### Naming Conventions

Asset directories use `category-subcategory` pattern with Chinese names:
- `brush-*` — toothbrush products
- `idb-牙間刷-*` — interdental brush content (by use case or topic)
- `edu-*` — educational content
- `floss-*`, `easypick-*`, `plaqueSearch-*`, `tongue-cleaner-*` — other products

Image directories typically contain: `cover.webp`, `feature1.webp`, `feature2.webp`, `packing.webp`, `size-*.webp`

## Content Workflow

The intended pipeline for each content piece:

1. **Write core content** → long-form markdown (e.g., `idb-main/idb-main.md`)
2. **SEO optimize** → use `seo-content-writer` skill
3. **Gap analysis** → use `content-gap-analysis` skill to find opportunities
4. **Add images** → use `blog-image-prep` skill to discover and insert relevant images into markdown
5. **Publish to Shopify** → use `shopify-publisher` skill to generate HTML and create/update draft articles
6. **Generate content hub** → use `content-hub-generator` skill to create supporting blogs, FB & IG posts, and publish to Shopify
7. **Repurpose** → use `social-media-content-repurposer` skill to adapt for additional platforms
8. **Create posts** → use `social-media` skill for platform-specific content (LinkedIn, X)
9. **Save to folders** → place results in `FB/`, `IG/`, `Threads/` subdirectories

## Installed Skills

| Skill | Source | Purpose |
|---|---|---|
| `seo-content-writer` | aaron-he-zhu/seo-geo-claude-skills | SEO-optimized content creation with CORE-EEAT checklist |
| `content-gap-analysis` | aaron-he-zhu/seo-geo-claude-skills | Identify content gaps and opportunities |
| `social-media` | langchain-ai/deepagents | Platform-specific social media content (FB, IG, Threads, LinkedIn, X) |
| `social-media-content-repurposer` | onewave-ai/claude-skills | Convert long-form content into multi-platform posts |
| `blog-image-prep` | local | Discover & insert relevant images into markdown blog posts |
| `shopify-publisher` | local | Publish articles to Shopify via GraphQL API, manage cover images |
| `content-hub-generator` | local | Generate supporting blogs, FB & IG posts from long-form content; publish to Shopify |

## Tools

### md2html — Markdown to Shopify HTML converter

Converts markdown blog posts to content-only HTML (no `<html>/<head>/<body>` wrapper) for pasting into Shopify. Relative image paths are converted to public GitHub raw URLs with proper percent-encoding.

```
uv run tools/md2html.py <markdown-file>
```

Example:
```
uv run tools/md2html.py idb-main/idb-main.md
# outputs: idb-main/idb-main.html
```

### publish_to_shopify — Shopify article publisher

Publishes markdown blog posts to Shopify as draft articles via Admin GraphQL API. Requires `SHOPIFY_STORE`, `SHOPIFY_CLIENT_ID`, `SHOPIFY_CLIENT_SECRET` in `.env`.

```
uv run tools/publish_to_shopify.py --all                 # Publish all configured posts
uv run tools/publish_to_shopify.py post.md               # Publish specific file
uv run tools/publish_to_shopify.py --all --update         # Update existing articles
uv run tools/publish_to_shopify.py --list-blogs           # List available blogs
uv run tools/publish_to_shopify.py post.md --template-suffix "blogs-no-feature-img"
uv run tools/publish_to_shopify.py post.md --cover-image "graphics/img.webp" --meta-description "描述"
```

## Important Notes

- All image assets use `.webp` format
- Content language: Traditional Chinese (繁體中文)
- After installing skills with `npx skills add`, remove `.agents/`, `.windsurf/`, `.kiro/` directories — only keep `.claude/skills/`
- This is a content-only repository — no build system, no framework, no package.json
