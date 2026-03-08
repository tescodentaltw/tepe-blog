---
name: sns-post-generator
description: >
  Generate Facebook and Instagram posts from a blog post markdown file. Discovers relevant images
  from images/ and graphics/ directories, asks the user for CTA URLs, and produces 4-5 engaging
  posts per platform in Traditional Chinese. Use when user says "generate sns posts",
  "create social media posts", "sns-post-generator", "generate FB and IG posts", or
  "create posts from blog".
user_invocable: true
metadata:
  author: TePe Blog
  tags:
    - social-media
    - facebook
    - instagram
    - content-repurposing
    - sns
  triggers:
    - "generate sns posts"
    - "create social media posts"
    - "sns-post-generator"
    - "generate FB and IG posts"
    - "create posts from blog"
    - "repurpose blog for social"
    - "make FB IG posts"
---

# SNS Post Generator — Blog to Facebook & Instagram Posts

Generates 4-5 Facebook posts and 4-5 Instagram posts from a markdown blog post, with relevant images from the project's asset directories.

## When to Use This Skill

Activate when the user wants to:
- Create Facebook and Instagram posts from an existing blog post
- Repurpose a markdown blog article into social media content
- Generate SNS content for TePe dental products

## How to Use

```
/sns-post-generator <markdown-file>
```

Example:
```
/sns-post-generator idb-main/idb-main.md
```

## Instructions

Follow these steps in order. Do NOT skip any step.

### Step 1: Read and Analyze the Blog Post

Read the target markdown file to understand:
- The blog post title (H1 heading)
- All section headings (H2, H3) and their content
- Key messages, facts, statistics, and takeaways
- The product line being discussed
- Target audience and tone

Extract 4-5 distinct angles or sub-topics that can each become a standalone social media post.

### Step 2: Ask the User for CTA URLs

Before generating any content, ask the user for exactly two URLs:

1. **Blog post URL** — for the `👉 伸延閱讀:` CTA link
2. **Product page URL** — for the `TePe®` CTA link

Also confirm:
- The **series name** (系列名稱) for the file header (e.g., "牙間刷終極指南系列")
- The **product line name** for the CTA (e.g., "牙間刷系列")

Do NOT proceed until the user provides these.

### Step 3: Discover Relevant Image Assets

1. List all subdirectories under `images/` and `graphics/` using the Bash tool
2. Identify directories whose names relate to the blog post topic
   - Directory names use the pattern `category-subcategory` with Chinese names
   - Match by keyword overlap with the blog post content
3. List all `.webp` files within each relevant directory

### Step 4: View and Select Images

For each relevant directory found in Step 3:
1. Use the Read tool to view each `.webp` image file visually
2. Note what each image depicts
3. Build a catalog of available images with descriptions
4. Select 5-8 images that best illustrate the post angles identified in Step 1
5. Ensure a mix of product photography (from `images/`) and educational illustrations (from `graphics/`)

If no suitable images are found for a particular post:
- Use the `nano-banana` skill to generate an illustration
- Reference the visual style of existing images in `graphics/` (clean line illustrations on white/light backgrounds with TePe brand colors)
- **Save generated images in the corresponding FB/ or IG/ folder** (e.g., `<source-dir>/FB/generated-image-name.webp`)
- Use local relative paths for generated images (e.g., `./generated-image-name.webp`)

### Step 5: Generate Facebook Posts

Create a file at `<source-dir>/FB/posts.md` with exactly this structure:

```markdown
# Facebook 貼文 — [系列名稱]

---

## Post 1：[標題]

![alt text](../../graphics/or/images/path.webp)

【[標題]】

[Body text — 3-5 paragraphs with emojis, engaging tone, educational content]

👉 伸延閱讀: 【[blog post title]】
[blog URL]

TePe® [product line name]
[product URL]

---

## Post 2：[標題]
...
```

**Facebook formatting rules:**
- Each post has exactly ONE image, placed immediately after the `## Post N` heading
- Image path is relative from the FB/ directory (use `../../graphics/...` or `../../images/...` for existing assets; `./filename.webp` for generated images)
- 【bracketed title】appears on its own line directly after the image
- Body uses emojis strategically (not excessively — 3-5 per post)
- Use bullet points, numbered lists (1️⃣2️⃣3️⃣), or comparison formats where appropriate
- Conversational, educational tone in Traditional Chinese
- Each post ends with the identical CTA block (two links)
- Posts are separated by `---` horizontal rules
- Generate 4-5 posts total

### Step 6: Generate Instagram Posts

Create a file at `<source-dir>/IG/posts.md` with this structure:

**Single-image post:**
```markdown
## Post N：單圖知識貼 — [標題]

![alt text](../../graphics/or/images/path.webp)

**Caption：**
[Caption text — concise, hook-first, with emojis]

👉 伸延閱讀: 【[blog post title]】
[blog URL]

TePe® [product line name]
[product URL]

**Hashtags：**
#hashtag1 #hashtag2 ... [~15 relevant hashtags]

---
```

**Carousel post:**
```markdown
## Post N：輪播貼文 — [標題]

**Caption：**
[Caption text with scroll prompt like "滑動看完" 👉]

👉 伸延閱讀: 【[blog post title]】
[blog URL]

TePe® [product line name]
[product URL]

**輪播內容建議：**
- Slide 1：「[slide title]」（[description]）

  ![alt text](../../path/to/image.webp)

- Slide 2：[slide title]

  ![alt text](../../path/to/image.webp)

[Continue for 4-6 slides]

**Hashtags：**
#hashtag1 #hashtag2 ... [~15 relevant hashtags]

---
```

**Instagram formatting rules:**
- File header: `# Instagram 貼文 — [系列名稱]` followed by `---`
- Mix of post types: aim for 2-3 carousel posts (輪播貼文) and 1-2 single-image posts (單圖知識貼)
- Post type is declared in the heading
- For single-image posts: image goes before the `**Caption：**` label
- For carousel posts: images go inside the `**輪播內容建議：**` section, indented under each slide
- Each slide description in carousels includes a parenthetical note about the visual concept
- Carousel slides use 4-6 images
- CTA block is placed inside the Caption section, before carousel content and hashtags
- Each post ends with a `**Hashtags：**` section containing ~15 hashtags (mix Chinese and English)
- Captions are concise (shorter than FB posts), hook-first
- Generate 4-5 posts total

### Step 7: Image Path Verification

After generating both files, verify all image paths:
1. Every `![alt](path)` reference must point to an existing `.webp` file
2. Paths for existing assets: relative from the output directory (`../../graphics/...` or `../../images/...`)
3. Paths for generated images: `./filename.webp` within the FB/ or IG/ folder
4. Use the Bash tool to confirm each referenced file exists
5. Fix any broken paths before finishing

### Step 8: Quality Checklist

Before declaring the task complete, verify:

- [ ] Blog post was fully read and understood
- [ ] User provided both CTA URLs and confirmed series/product names
- [ ] All images were visually inspected (not blindly assigned by filename)
- [ ] FB/posts.md contains 4-5 posts with correct structure
- [ ] IG/posts.md contains 4-5 posts with correct structure (mix of carousel and single-image)
- [ ] Every FB post has 【bracketed title】directly under the image
- [ ] Every IG post has proper Caption/Hashtags sections
- [ ] CTA block is identical across all posts on both platforms
- [ ] CTA format: `👉 伸延閱讀:` line + URL, blank line, `TePe® [name]` line + URL
- [ ] All image paths verified to exist
- [ ] No duplicate images within the same platform's posts
- [ ] Content is in Traditional Chinese (繁體中文)
- [ ] Each post covers a distinct angle (no redundant posts)

## Output Summary

Report to the user:
1. Paths to both generated files
2. Number of posts per platform
3. Brief description of each post's angle
4. Any images that were generated (via nano-banana) vs. found in existing assets

## Important Notes

- All content must be in Traditional Chinese (繁體中文) targeting Hong Kong/Taiwan audiences
- All image assets use `.webp` format
- Product photography lives in `images/`, educational illustrations in `graphics/`
- The `images/` directories typically contain: `cover.webp`, `feature1.webp`, `feature2.webp`, `packing.webp`, `size-*.webp`
- The `graphics/` directories contain descriptive filenames like `idb-vs-floss-comparison.webp`
- Always view images before selecting them — filenames alone can be misleading
- Generated images (via nano-banana) must be saved inside the corresponding FB/ or IG/ folder, not in the shared graphics/ or images/ directories
