---
name: shopify-publisher
description: >
  Publish markdown blog posts to Shopify as draft articles via Admin GraphQL API.
  Handles OAuth authentication, blog discovery, article creation/update, duplicate detection,
  and cover image upload. Use when user says "publish to shopify", "upload to shopify",
  "shopify-publisher", "push articles to shopify", "update shopify articles",
  "upload cover images", or any task involving Shopify article management.
  Also use when other skills (like blog-image-prep) have generated HTML and the user
  wants to push it to Shopify.
user_invocable: true
metadata:
  author: TePe Blog
  tags:
    - shopify
    - publishing
    - graphql
    - api
  triggers:
    - "publish to shopify"
    - "upload to shopify"
    - "shopify-publisher"
    - "push articles to shopify"
    - "update shopify articles"
    - "upload cover images"
---

# Shopify Publisher — Blog Article Management via GraphQL API

Publishes markdown blog posts to Shopify as draft articles using the Admin GraphQL API. Supports creating new articles, updating existing ones, and setting cover/featured images.

## Prerequisites

The `.env` file must contain these Shopify credentials:

```
SHOPIFY_STORE=<store-name>.myshopify.com
SHOPIFY_CLIENT_ID=<client-id>
SHOPIFY_CLIENT_SECRET=<client-secret>
```

The script obtains an access token automatically via OAuth `client_credentials` grant — no manual token management needed.

## How to Use

```
/shopify-publisher                          # Interactive — asks what to publish
/shopify-publisher --all                    # Publish all configured blog posts
/shopify-publisher path/to/article.md       # Publish a specific markdown file
```

## Instructions

### Step 1: Ensure HTML Exists

Each markdown file needs a corresponding `.html` file for Shopify. The `blog-image-prep` skill or `tools/md2html.py` handles this conversion.

If the HTML file is missing or older than the markdown:

```bash
uv run tools/md2html.py <markdown-file>
```

This converts relative image paths to GitHub raw URLs and produces content-only HTML (no `<html>/<head>/<body>` wrapper).

### Step 2: Publish Articles

Run the publishing script:

```bash
uv run tools/publish_to_shopify.py --all                    # All configured posts
uv run tools/publish_to_shopify.py path/to/post.md          # Specific file
uv run tools/publish_to_shopify.py --all --dry-run           # Preview without API calls
uv run tools/publish_to_shopify.py --all --update            # Update existing articles
uv run tools/publish_to_shopify.py --list-blogs              # List available blogs
uv run tools/publish_to_shopify.py --all --blog "Blog Title" # Target a specific blog
```

The script:
- Authenticates via `client_credentials` OAuth flow
- Finds the target blog by title (default: 「牙縫清潔」)
- Extracts the H1 heading from each markdown file as the article title
- Uses the filename stem as the URL handle (e.g., `idb-vs-floss.md` → handle `idb-vs-floss`)
- Creates articles as **drafts** (`isPublished: false`) with author "TePe"
- Detects duplicates by title and skips them (or updates with `--update`)

### Step 3: Upload Cover Images (Optional)

To set featured/cover images on articles, use the `articleUpdate` GraphQL mutation with an image URL. The image must be publicly accessible — use GitHub raw URLs after pushing to the repo.

**Workflow:**
1. Prepare cover images (800x450 px, 16:9, webp 85% quality)
2. Save to `idb-main/covers/<article-handle>.webp`
3. Git commit and push so GitHub raw URLs work
4. Call `articleUpdate` with the image URL

**GraphQL mutation for cover image:**

```graphql
mutation articleUpdate($id: ID!, $article: ArticleUpdateInput!) {
  articleUpdate(id: $id, article: $article) {
    article { id title image { altText url } }
    userErrors { field message }
  }
}
```

Variables:
```json
{
  "id": "gid://shopify/Article/<article-id>",
  "article": {
    "image": {
      "altText": "Description in Traditional Chinese",
      "url": "https://raw.githubusercontent.com/<org>/<repo>/main/idb-main/covers/<handle>.webp"
    }
  }
}
```

## Script Reference

**`tools/publish_to_shopify.py`** — CLI for Shopify article management

```
uv run tools/publish_to_shopify.py [files...] [options]

Options:
  --all          Publish all configured blog posts
  --dry-run      Preview without calling Shopify API
  --update       Update existing articles instead of skipping
  --list-blogs   List all blogs on the store and exit
  --blog TITLE   Target blog title (default: 牙縫清潔)
```

## Shopify GraphQL API Reference

### Authentication

OAuth `client_credentials` grant — no user interaction needed:

```
POST https://{store}/admin/oauth/access_token
Content-Type: application/x-www-form-urlencoded

client_id=...&client_secret=...&grant_type=client_credentials
```

Returns `{ "access_token": "..." }`.

### GraphQL Endpoint

```
POST https://{store}/admin/api/2025-01/graphql.json
Headers:
  X-Shopify-Access-Token: <token>
  Content-Type: application/json
```

### Key Mutations

| Operation | Mutation | Notes |
|---|---|---|
| Create article | `articleCreate(article: ArticleCreateInput!)` | `author` field is **required** (cannot be null) |
| Update article | `articleUpdate(id: ID!, article: ArticleUpdateInput!)` | Use for content updates and cover image setting |
| Set cover image | `articleUpdate` with `image: { altText, url }` | URL must be publicly accessible |

### Key Queries

| Operation | Query | Notes |
|---|---|---|
| List blogs | `blogs(first: 25) { nodes { id title handle } }` | Find blog GID by title |
| Find article | `articles(first: 5, query: "title:'...'") { nodes { id title blog { id } } }` | Check for duplicates |

## Gotchas and Lessons Learned

- **`author` is required**: The `articleCreate` mutation fails if `author` is null. Always provide `author: { name: "TePe" }`.
- **No `onlineStoreUrl` on Article**: The Article type does not have an `onlineStoreUrl` field — don't request it in return fields.
- **Cover images need public URLs**: Shopify fetches the image from the URL you provide. GitHub raw URLs work well, but the file must be pushed to the repo first.
- **Handle = filename stem**: The URL handle is derived from the markdown filename (e.g., `idb-vs-floss.md` → `idb-vs-floss`). Keep filenames URL-friendly.
- **Draft by default**: Articles are created with `isPublished: false`. Publish manually from Shopify Admin when ready.
- **Duplicate detection**: The script checks for existing articles with the same title in the same blog before creating. Use `--update` to overwrite.
