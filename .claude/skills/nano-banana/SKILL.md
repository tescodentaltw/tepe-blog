---
name: nano-banana
description: >
  Generates AI images using Google Gemini / Imagen models via Google AI Studio API.
  Enhances user prompts with compositional detail, confirms the final prompt,
  then generates and saves images as .webp. Supports aspect ratios (1:1, 3:4, 4:3, 9:16, 16:9),
  multiple images per request (1-4), and Gemini (free) or Imagen 4 (paid) backends.
  Use when user says "generate image", "create illustration", "nano-banana",
  "make a graphic", "generate a picture", "create an image", or any image generation task.
  Also use proactively when other skills (like sns-post-generator) need images that don't exist
  in the project's asset directories.
user_invocable: true
metadata:
  author: TePe Blog
  tags:
    - image-generation
    - gemini
    - imagen
    - google-ai
    - graphics
  triggers:
    - "generate image"
    - "create illustration"
    - "nano-banana"
    - "make a graphic"
    - "generate a picture"
    - "create an image"
    - "generate artwork"
---

# Nano Banana — AI Image Generator (Google AI Studio)

Generates images using Google Gemini or Imagen 4 models through Google AI Studio. Enhances user prompts for better results and confirms before generating.

## How to Use

```
/nano-banana <rough description of what you want>
```

Examples:
```
/nano-banana a clean illustration of interdental brush cleaning between teeth
/nano-banana product photo of TePe toothbrush on white background, 16:9
```

## Instructions

Follow these steps in order.

### Step 1: Understand the User's Intent

From the user's prompt, identify:
- **Subject**: What should the image depict?
- **Style**: Photo-realistic, illustration, diagram, infographic, cartoon, etc.
- **Aspect ratio**: Default 1:1, or infer from context (e.g., "banner" -> 16:9, "story" -> 9:16)
- **Output path**: Where to save the file (ask if not specified)
- **Count**: How many variations (default: 1, max: 4)

### Step 2: Enhance the Prompt

Transform the user's rough description into a detailed, effective image generation prompt. A good prompt includes:

1. **Subject & action**: What is in the scene and what is happening
2. **Composition**: Camera angle, framing, focal point
3. **Style & medium**: Photography style, illustration technique, art movement
4. **Lighting**: Natural, studio, dramatic, soft, etc.
5. **Color palette**: Specific colors, mood, brand alignment
6. **Background**: Clean, contextual, gradient, etc.
7. **Details**: Textures, materials, specific visual elements

**For TePe dental product content**, apply these defaults unless the user specifies otherwise:
- Clean, modern illustration style on white/light background
- TePe brand colors: green (#00A651), blue (#0072BC), white
- Professional, educational tone
- No text in the image (text is added separately)

**Example enhancement:**

User: "interdental brush cleaning teeth"

Enhanced: "Clean vector-style medical illustration of an interdental brush gently inserted between two adjacent molar teeth, showing the brush bristles fanning out to clean the interproximal surface. Soft pastel colors with green (#00A651) accent on the brush handle. White background, cross-section anatomical view, dental education style. No text."

### Step 3: Confirm with the User

Present the enhanced prompt to the user in a clear format:

```
Enhanced prompt:
"[the enhanced prompt]"

Settings:
- Model: [model name]
- Aspect ratio: [ratio]
- Number of images: [count]
- Output: [file path]
```

Ask: "確認使用這個 prompt 嗎？可以直接修改或告訴我要調整的地方。"

**Do NOT proceed to generation until the user confirms or provides a modified prompt.**

### Step 4: Generate the Image

Run the generation script:

```bash
uv run .claude/skills/nano-banana/scripts/generate_image.py \
  --prompt "the confirmed prompt" \
  --output path/to/output.webp \
  --aspect-ratio 1:1 \
  --count 1
```

The script:
- Reads `GOOGLE_API_KEY` from `.env`
- Default model: `gemini-2.5-flash-image` (requires billing enabled on Google AI Studio)
- Saves output as `.webp` format
- Prints the saved file path(s)

### Step 5: Review and Iterate

After generation:
1. Use the Read tool to view the generated image(s)
2. Show the result to the user
3. If the user wants changes, go back to Step 2 with their feedback

## Script Reference

**`scripts/generate_image.py`** — CLI for image generation

```
uv run .claude/skills/nano-banana/scripts/generate_image.py \
  --prompt "detailed prompt" \
  --output output.webp \
  --aspect-ratio 1:1 \       # 1:1, 3:4, 4:3, 9:16, 16:9
  --count 1 \                 # 1-4 images
  --model gemini-2.5-flash-image  # default
```

Available models (Gemini — via generateContent):
- `gemini-2.5-flash-image` — Best balance of quality and speed (default)
- `gemini-3.1-flash-image-preview` — Latest preview model
- `gemini-3-pro-image-preview` — Pro quality preview
- `gemini-2.0-flash-exp-image-generation` — Legacy experimental

Available models (Imagen — via generateImages):
- `imagen-4.0-generate-001` — Imagen 4 standard
- `imagen-4.0-ultra-generate-001` — Imagen 4 ultra, highest quality
- `imagen-4.0-fast-generate-001` — Imagen 4 fast, quickest

## Important Notes

- All output images use `.webp` format for consistency with project assets
- The `GOOGLE_API_KEY` must be set in the project `.env` file
- Image generation requires billing enabled on the Google AI Studio project (https://ai.dev/projects)
- Generated images include an invisible SynthID watermark (Google policy)
- For TePe project assets, save to appropriate directory (`graphics/` for illustrations, `images/` for product photos, or directly in content folders like `FB/`, `IG/`)
