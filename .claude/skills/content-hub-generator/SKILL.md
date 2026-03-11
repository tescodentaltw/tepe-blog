---
name: content-hub-generator
description: >
  Generate supporting blog posts, Facebook posts, and Instagram posts from a long-form blog article.
  Discovers relevant images, creates focused supporting blogs with images and captions,
  generates 4-5 SNS posts per platform, and publishes supporting blogs to Shopify as hidden articles.
  All content in Traditional Chinese. Use when user says "generate content hub",
  "content-hub-generator", "create supporting blogs and sns posts", "generate sns posts",
  "create social media posts", or "create posts from blog".
user_invocable: true
metadata:
  author: TePe Blog
  tags:
    - content-hub
    - blog
    - shopify
    - social-media
    - facebook
    - instagram
    - content-repurposing
    - sns
  triggers:
    - "generate content hub"
    - "content-hub-generator"
    - "create supporting blogs and sns posts"
    - "generate sns posts"
    - "create social media posts"
    - "generate FB and IG posts"
    - "create posts from blog"
    - "repurpose blog for social"
---

# Content Hub Generator — Blog to Supporting Posts, Facebook & Instagram

Generates a complete content hub from a long-form markdown blog post:
- 4-5 supporting blog posts (markdown with images, published to Shopify)
- 4-5 Facebook posts
- 4-5 Instagram posts (mix of carousel and single-image)

## When to Use This Skill

Activate when the user wants to:
- Create a content hub from a long-form blog article
- Generate supporting blog posts and social media content from a main blog
- Repurpose a markdown blog article into multi-platform content

## How to Use

```
/content-hub-generator <markdown-file>
```

Example:
```
/content-hub-generator idb-main/idb-main.md
```

## Reference Sample

The `idb-main/` directory is a complete reference for the expected output:
- `idb-main.md` — long-form source blog
- `idb-why-you-only-clean-70-percent.md` — supporting blog 1
- `idb-vs-floss.md` — supporting blog 2
- `idb-size-guide.md` — supporting blog 3
- `idb-before-brushing.md` — supporting blog 4
- `idb-myths-debunked.md` — supporting blog 5
- `FB/posts.md` — 5 Facebook posts
- `IG/posts.md` — 5 Instagram posts

## Instructions

Follow these steps in order. Do NOT skip any step.

### Step 1: Read and Analyze the Blog Post

Read the target markdown file to understand:
- The blog post title (H1 heading)
- All section headings (H2, H3) and their content
- Key messages, facts, statistics, and takeaways
- The product line being discussed
- Target audience and tone

Extract 4-5 distinct angles or sub-topics that can each become:
1. A standalone supporting blog post (500-800 words)
2. A Facebook post
3. An Instagram post

### Step 2: Ask the User for CTA URLs and Publishing Info

Before generating any content, ask the user for:

1. **Blog post URL** — for the CTA link (e.g., `https://tepetw.com/blogs/interdental/idb-main`)
2. **Product page URL** — for the `TePe®` CTA link (e.g., `https://tepetw.com/collections/idb`)
3. **Series name** (系列名稱) for file headers (e.g., "牙間刷終極指南系列")
4. **Product line name** for the CTA (e.g., "牙間刷系列")
5. **Shopify blog title** — for publishing supporting blogs (e.g., "牙縫清潔")

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
4. Select images for:
   - Supporting blog posts: 2-4 images per blog (educational illustrations + product photos)
   - Facebook posts: 1 image per post (5 total)
   - Instagram posts: 1-6 images per post depending on type
5. Ensure a mix of product photography (from `images/`) and educational illustrations (from `graphics/`)

If no suitable images are found for a particular post:
- Use the `nano-banana` skill to generate an illustration
- Reference the visual style of existing images in `graphics/` (clean line illustrations on white/light backgrounds with TePe brand colors)
- **Save generated images in the corresponding FB/ or IG/ folder** (e.g., `<source-dir>/FB/generated-image-name.webp`)
- Use local relative paths for generated images (e.g., `./generated-image-name.webp`)

### Step 5: Generate Supporting Blog Posts

For each of the 4-5 angles extracted in Step 1, generate a focused supporting blog post as a markdown file.

**Filename**: `<source-dir>/<prefix>-<kebab-case-topic>.md` where prefix matches the main blog's prefix (e.g., `idb-` for `idb-main`).

**Content structure** (reference: `idb-main/idb-vs-floss.md`):

1. **H1 title** — SEO-friendly, engaging, in Traditional Chinese. Can use question format, "how-to" format, or surprising fact format.

2. **Opening paragraph** — Hook the reader with a question or surprising fact. 1-2 sentences.

3. **3-5 H2 sections** — Deep dive into the topic. Each section should:
   - Address one aspect of the angle
   - Use bold (`**text**`) for emphasis
   - Address the reader directly with "你"
   - Be educational and conversational in tone

4. **2-4 `<figure>` elements** — Insert images using this exact format:
   ```html
   <figure align="center">
     <img src="../graphics/category/filename.webp" alt="concise descriptive alt text">
     <figcaption>Reader-friendly caption in Traditional Chinese</figcaption>
   </figure>
   ```
   - Place figures AFTER the paragraph they illustrate (never before a heading)
   - Use relative paths from the source directory (`../graphics/...` or `../images/...`)
   - No duplicate images within the same blog post
   - Alt text should be concise and descriptive

5. **500-800 words** total length

6. **Closing section** — Call-to-action with links:
   ```markdown
   延伸閱讀：[main blog title](main-blog-handle) | 選購：[TePe product line](product-url)
   ```

**Important**: Each supporting blog must cover a DISTINCT angle. No redundancy between posts.

### Step 6: Generate Facebook Posts

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
- Use bullet points, numbered lists, or comparison formats where appropriate
- Conversational, educational tone in Traditional Chinese
- Each post ends with the identical CTA block (two links) pointing to the **main long-form blog post**
- Posts are separated by `---` horizontal rules
- Generate 4-5 posts total
- Each FB post corresponds to one supporting blog post (same angle/topic)
- The image used in each FB post will become the cover image of the corresponding supporting blog on Shopify

### Step 7: Generate Instagram Posts

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

### Step 8: Publish Supporting Blogs to Shopify

For each supporting blog post generated in Step 5:

1. **Generate HTML**: Run `uv run tools/md2html.py <file>` to convert markdown to Shopify-ready HTML

2. **Write a meta description**: Create a 1-2 sentence SEO meta description in Traditional Chinese (under 160 characters) that:
   - Includes the core keyword for the angle
   - Summarizes the key value proposition
   - Encourages click-through

3. **Determine cover image**: Use the same image assigned to the corresponding FB post in Step 6

4. **Publish to Shopify**: Run:
   ```bash
   uv run tools/publish_to_shopify.py <file> \
     --blog "<shopify-blog-title>" \
     --template-suffix "blogs-no-feature-img" \
     --cover-image "<repo-relative-image-path>" \
     --meta-description "<seo-description>"
   ```

5. If articles already exist, add `--update` flag

6. **Important**: Cover images require files to be pushed to GitHub. Remind the user:
   - Files must be git committed and pushed before cover images resolve via GitHub raw URLs
   - If cover images fail, push the repo first, then re-run with `--update`

### Step 9: Image Path Verification

After generating all files, verify all image paths:
1. Every `![alt](path)` reference in FB/IG posts must point to an existing `.webp` file
2. Every `<img src="...">` reference in supporting blog posts must point to an existing `.webp` file
3. Paths for existing assets: relative from the output directory (`../../graphics/...` or `../../images/...` for SNS posts; `../graphics/...` or `../images/...` for supporting blogs)
4. Paths for generated images: `./filename.webp` within the FB/ or IG/ folder
5. Use the Bash tool to confirm each referenced file exists
6. Fix any broken paths before finishing

### Step 10: Quality Checklist

Before declaring the task complete, verify:

**Content analysis:**
- [ ] Blog post was fully read and understood
- [ ] User provided CTA URLs, series/product names, and Shopify blog title
- [ ] All images were visually inspected (not blindly assigned by filename)
- [ ] Each post/blog covers a distinct angle (no redundancy)
- [ ] Content is in Traditional Chinese (繁體中文)

**Supporting blog posts:**
- [ ] 4-5 supporting blog posts generated as markdown files
- [ ] Each has an SEO-friendly H1 title
- [ ] Each has 3-5 H2 sections, 500-800 words
- [ ] Each contains 2-4 `<figure align="center">` elements with valid image paths
- [ ] Each ends with links to main blog and product page
- [ ] Filenames follow `<prefix>-<kebab-case-topic>.md` convention

**Facebook posts:**
- [ ] FB/posts.md contains 4-5 posts with correct structure
- [ ] Every FB post has 【bracketed title】directly under the image
- [ ] CTA block is identical across all posts, linking to the main long-form blog

**Instagram posts:**
- [ ] IG/posts.md contains 4-5 posts with correct structure (mix of carousel and single-image)
- [ ] Every IG post has proper Caption/Hashtags sections
- [ ] CTA format: `👉 伸延閱讀:` line + URL, blank line, `TePe® [name]` line + URL

**Shopify publishing:**
- [ ] HTML generated for each supporting blog via md2html.py
- [ ] All supporting blogs published to Shopify as hidden draft articles
- [ ] Template suffix set to `blogs-no-feature-img` on all articles
- [ ] Cover images set (matching FB post images)
- [ ] Meta descriptions set for SEO

**Image paths:**
- [ ] All image paths verified to exist
- [ ] No duplicate images within the same platform's posts or blog

## Output Summary

Report to the user:
1. Paths to all generated files (supporting blogs, FB/posts.md, IG/posts.md)
2. Number of supporting blogs, FB posts, and IG posts
3. Brief description of each angle/topic
4. Shopify publishing status (created/updated, article IDs)
5. Any images that were generated (via nano-banana) vs. found in existing assets

## Important Notes

- All content must be in Traditional Chinese (繁體中文) targeting Hong Kong/Taiwan audiences
- All image assets use `.webp` format
- Product photography lives in `images/`, educational illustrations in `graphics/`
- The `images/` directories typically contain: `cover.webp`, `feature1.webp`, `feature2.webp`, `packing.webp`, `size-*.webp`
- The `graphics/` directories contain descriptive filenames like `idb-vs-floss-comparison.webp`
- Always view images before selecting them — filenames alone can be misleading
- Generated images (via nano-banana) must be saved inside the corresponding FB/ or IG/ folder, not in the shared graphics/ or images/ directories
- Supporting blog posts are saved alongside the main blog in the same directory
- The `publish_to_shopify.py` tool handles HTML generation, article creation, cover images, meta descriptions, and template suffixes
