---
name: blog-image-prep
description: >
  Discover and insert relevant images into a markdown blog post. Scans images/ and graphics/
  directories for matching assets, views each image to verify relevance, then inserts centered
  figure elements with alt text and captions. Use when user says "add images to blog",
  "insert images", "blog-image-prep", "prepare blog images", or "find images for blog post".
user_invocable: true
metadata:
  author: TePe Blog
  tags:
    - blog
    - images
    - markdown
  triggers:
    - "add images to blog"
    - "insert images"
    - "blog-image-prep"
    - "prepare blog images"
    - "find images for blog post"
---

# Blog Image Prep — Discover & Insert Images into Markdown

Discovers relevant images from `images/` and `graphics/` directories, views them to verify content, and inserts properly formatted `<figure>` elements into a markdown blog post.

## When to Use This Skill

Activate when the user wants to:
- Add images and illustrations from `images/` and `graphics/` to a markdown blog post
- Find relevant product photos or educational graphics for a blog post
- Insert `<figure>` elements with alt text and captions into markdown

This skill does NOT handle HTML conversion or Shopify publishing — use `shopify-publisher` for that.

## How to Use

```
/blog-image-prep <markdown-file>
```

Example:
```
/blog-image-prep idb-main/idb-main.md
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
- **Paths**: Use relative paths (`../images/...` or `../graphics/...`)
- **Alt text**: Concise, descriptive, for accessibility and SEO (can be in Chinese or English)
- **Captions**: Written in Traditional Chinese, reader-friendly, describing what the image shows
- **No duplicates**: Do not insert the same image twice
- **Skip existing**: If the markdown already has `<figure>` elements, do not duplicate them

### Step 6: Report Results

Summarize what was done:
- How many images were inserted
- Which sections received images
- Any sections where no suitable image was found

## Important Notes

- All content is in Traditional Chinese (繁體中文)
- All image assets use `.webp` format
- Product photography lives in `images/`, educational illustrations in `graphics/`
- The `images/` directories typically contain: `cover.webp`, `feature1.webp`, `feature2.webp`, `packing.webp`, `size-*.webp`
- The `graphics/` directories contain descriptive filenames like `idb-vs-floss-comparison.webp`
