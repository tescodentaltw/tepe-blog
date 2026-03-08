---
name: blog-publisher
description: >
  Prepare a markdown blog post for Shopify publishing. Scans images/ and graphics/ directories
  for relevant assets, inserts centered figures with alt text and captions into the markdown,
  then generates Shopify-ready HTML via tools/md2html.py. Use when user says "publish blog",
  "prepare for Shopify", "add images to blog post", or "blog-publisher".
user_invocable: true
metadata:
  author: TePe Blog
  tags:
    - blog
    - shopify
    - images
    - publishing
  triggers:
    - "publish blog"
    - "prepare for shopify"
    - "add images and generate html"
    - "blog-publisher"
---

# Blog Publisher — Image Insertion & Shopify HTML Generator

Automates the full workflow of preparing a markdown blog post for Shopify: discovering relevant images, inserting them with proper formatting, and generating content-only HTML.

## When to Use This Skill

Activate when the user wants to:
- Prepare a markdown blog post for publishing on Shopify
- Add images and illustrations from `images/` and `graphics/` to a blog post
- Generate Shopify-ready HTML from a markdown blog post

## How to Use

```
/blog-publisher <markdown-file>
```

Example:
```
/blog-publisher idb-main/idb-main.md
```

## Instructions

Follow these steps in order. Do NOT skip any step.

### Step 1: Read the Markdown File

Read the target markdown file to understand:
- The blog post topic and structure
- All section headings (H2, H3)
- What each section discusses
- Any images already present (skip re-inserting)

### Step 2: Discover Relevant Assets

1. List all subdirectories under `images/` and `graphics/` using the Bash tool
2. Identify directories whose names relate to the blog post topic
   - Directory names use the pattern `category-subcategory` with Chinese names
   - Examples: `idb-牙間刷-簡介`, `brush-植牙護理牙刷`, `edu-蛀牙`
3. List all `.webp` files within each relevant directory

### Step 3: View and Catalog Images

For each relevant directory found in Step 2:
1. Use the Read tool to view each `.webp` image file
2. Note what each image depicts — this is critical for accurate matching
3. Build a mental catalog of available assets and what they show

### Step 4: Match Images to Content Sections

For each section of the blog post:
1. Determine if an available image would genuinely enhance reader understanding
2. Select the most relevant image — do NOT force images where they don't fit
3. A section may have zero, one, or multiple images depending on content

### Step 5: Insert Figure Elements

Insert images into the markdown using this exact HTML format:

```html
<figure align="center">
  <img src="../images/category/file.webp" alt="concise descriptive alt text">
  <figcaption>Reader-friendly caption in Traditional Chinese</figcaption>
</figure>
```

Rules:
- **Placement**: Insert AFTER the paragraph the image illustrates, never before a heading
- **Paths**: Use relative paths (`../images/...` or `../graphics/...`) — the md2html script handles URL conversion
- **Alt text**: Concise, descriptive, for accessibility and SEO (can be in Chinese or English)
- **Captions**: Written in Traditional Chinese, reader-friendly, describing what the image shows
- **No duplicates**: Do not insert the same image twice
- **Skip existing**: If the markdown already has `<figure>` elements, do not duplicate them

### Step 6: Generate Shopify HTML

Run the conversion script:

```bash
uv run tools/md2html.py <markdown-file>
```

This will:
- Convert relative image paths to public GitHub raw URLs (percent-encoded)
- Convert markdown to content-only HTML (no `<html>/<head>/<body>` wrapper)
- Restrict all images to max 600x600px
- Output a `.html` file next to the source markdown

### Step 7: Verify Output

1. Confirm the `.html` file was created
2. Spot-check that image URLs in the HTML use `https://raw.githubusercontent.com/hoishing/tepe-blog/main/...`
3. Report the output file path to the user

## Important Notes

- All content is in Traditional Chinese (繁體中文)
- All image assets use `.webp` format
- Product photography lives in `images/`, educational illustrations in `graphics/`
- The `images/` directories typically contain: `cover.webp`, `feature1.webp`, `feature2.webp`, `packing.webp`, `size-*.webp`
- The `graphics/` directories contain descriptive filenames like `idb-vs-floss-comparison.webp`
