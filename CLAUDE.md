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
4. **Publish to Shopify** → use `blog-publisher` skill to add images and generate HTML
5. **Generate SNS posts** → use `sns-post-generator` skill to create FB & IG posts with images and CTA
6. **Repurpose** → use `social-media-content-repurposer` skill to adapt for additional platforms
7. **Create posts** → use `social-media` skill for platform-specific content (LinkedIn, X)
8. **Save to folders** → place results in `FB/`, `IG/`, `Threads/` subdirectories

## Installed Skills

| Skill | Source | Purpose |
|---|---|---|
| `seo-content-writer` | aaron-he-zhu/seo-geo-claude-skills | SEO-optimized content creation with CORE-EEAT checklist |
| `content-gap-analysis` | aaron-he-zhu/seo-geo-claude-skills | Identify content gaps and opportunities |
| `social-media` | langchain-ai/deepagents | Platform-specific social media content (FB, IG, Threads, LinkedIn, X) |
| `social-media-content-repurposer` | onewave-ai/claude-skills | Convert long-form content into multi-platform posts |
| `blog-publisher` | local | Insert images from images/ & graphics/, generate Shopify HTML |
| `sns-post-generator` | local | Generate FB & IG posts from blog post with images and CTA links |

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

## Important Notes

- All image assets use `.webp` format
- Content language: Traditional Chinese (繁體中文)
- After installing skills with `npx skills add`, remove `.agents/`, `.windsurf/`, `.kiro/` directories — only keep `.claude/skills/`
- This is a content-only repository — no build system, no framework, no package.json
