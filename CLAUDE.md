# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Content repository for TePe dental products marketing — interdental brushes (IDB/牙間刷), toothbrushes, floss, and oral care accessories. All content is in Traditional Chinese targeting Taiwan audiences.

GitHub: https://github.com/tescodentaltw/tepe-blog

## Repository Structure

```
graphics/          # Educational illustrations & marketing graphics (.webp)
images/            # Product photography (.webp)
tools/             # Python utility scripts (run with uv, inline dependencies)
seo/               # Weekly SEO reports (YYYY-MM-DD-weekly-seo-report.md)
feature-img/       # Feature images
market-research/   # Market research files
idb-main/          # Long-form content hub (markdown + social media folders)
  ├── idb-main.md  # Comprehensive IDB guide (source content for repurposing)
  ├── covers/      # Generated cover images for blog posts
  ├── FB/          # Facebook posts
  └── IG/          # Instagram posts
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

All tools are standalone Python scripts with inline `uv` dependency declarations. Run with `uv run tools/<script>.py`.

### md2html — Markdown to Shopify HTML converter

Converts markdown blog posts to content-only HTML (no `<html>/<head>/<body>` wrapper) for pasting into Shopify. Relative image paths are converted to public GitHub raw URLs with proper percent-encoding.

```
uv run tools/md2html.py <markdown-file>
# outputs: <filename>.html in same directory
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

### update_cover_images — Shopify article cover image updater

Updates cover/feature images on existing Shopify blog articles. Maps configured blog posts to image assets via GitHub raw URLs.

```
uv run tools/update_cover_images.py              # Update all configured cover images
uv run tools/update_cover_images.py --dry-run     # Preview changes without applying
```

### update_collection_seo — Shopify collection SEO metadata

Updates Shopify collection page SEO titles and descriptions via Admin GraphQL API. Has a built-in mapping of all 17 collection handles to SEO titles.

```
uv run tools/update_collection_seo.py --list              # List all collections with SEO info
uv run tools/update_collection_seo.py --update            # Apply SEO title updates
uv run tools/update_collection_seo.py --update --dry-run  # Preview changes
```

### update_product_descriptions — Shopify product description updater

Lists products with CJK character counts and updates descriptions from a JSON file (handle → HTML mapping). Use with Claude Code sub-agents to generate SEO-friendly descriptions.

```
uv run tools/update_product_descriptions.py --list                        # List all products with CJK char counts
uv run tools/update_product_descriptions.py --update descriptions.json    # Update from JSON file
uv run tools/update_product_descriptions.py --update desc.json --dry-run  # Preview changes
```

### seo_report — GSC + GA4 SEO performance report

Pulls search performance (GSC) and site analytics (GA4) data using Application Default Credentials. Requires ADC login on the `tepe-seo` GCP project.

```
uv run tools/seo_report.py                  # Full report (GSC + GA4, 90 days)
uv run tools/seo_report.py --days 30        # Last 30 days
uv run tools/seo_report.py --gsc-only       # GSC data only
uv run tools/seo_report.py --ga4-only       # GA4 data only
```

GSC config: `sc-domain:tepetw.com` | GA4 property: `properties/517199426` (tepetw.com)

ADC login (required scopes):
```
gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/webmasters,https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/analytics.readonly" \
  --project=tepe-seo
```

### manage_sitemap — Google Search Console sitemap management

List, submit, and delete sitemaps in GSC. Uses same ADC credentials as seo_report.

```
uv run tools/manage_sitemap.py --list                          # List current sitemaps
uv run tools/manage_sitemap.py --submit "https://tepetw.com/sitemap.xml"
uv run tools/manage_sitemap.py --delete "https://www.tepetw.com/sitemap.xml"
```

## Shopify API Details

- **Store**: `tepe-taiwan.myshopify.com` (domain: `tepetw.com`)
- **API version**: `2025-01` (Admin GraphQL)
- **Auth**: OAuth `client_credentials` grant (no manual token management)
- **Default blog**: "牙縫清潔"
- **Articles**: Created as drafts (`isPublished: false`), author "TePe"
- **SEO meta descriptions**: Set via REST API (GraphQL doesn't support SEO fields on articles)
- **Image URLs**: GitHub raw URLs from `https://raw.githubusercontent.com/tescodentaltw/tepe-blog/main` (images must be committed and pushed first)

## Multi-Account CLI Setup

### gcloud (multiple configurations)

| Configuration | Account | Project |
|---|---|---|
| `default` | `tescodentaltw@gmail.com` | `tepe-seo` |
| `ascdm` | `ascdm.cc@gmail.com` | `tepe-seo-ascdm` |

```bash
gcloud config configurations activate default  # switch to tescodentaltw
gcloud config configurations activate ascdm    # switch to ascdm.cc
```

### gws (Google Workspace CLI — env var per account)

gws does not support multiple profiles natively. Use `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` to switch accounts:

| Account | Config Dir |
|---|---|
| `tescodentaltw@gmail.com` (default) | `~/.config/gws` |
| `ascdm.cc@gmail.com` | `~/.config/gws-ascdm` |

```bash
# tescodentaltw (default — no env var needed)
gws drive files list --params '{"pageSize": 10}'

# ascdm.cc — prefix with env var
GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws-ascdm gws drive files list --params '{"pageSize": 10}'
```

> `gws-ascdm` is authenticated as `ascdm.cc@gmail.com` (GCP project: `tepe-seo-ascdm`).

## Important Notes

- All image assets use `.webp` format
- Content language: Traditional Chinese (繁體中文)
- After installing skills with `npx skills add`, remove `.agents/`, `.windsurf/`, `.kiro/` directories — only keep `.claude/skills/`
- This is a content-only repository — no build system, no framework, no package.json
