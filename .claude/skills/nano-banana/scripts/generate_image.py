# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-genai",
#     "python-dotenv",
#     "pillow",
# ]
# ///

"""Generate images using Google Gemini / Imagen via Google AI Studio API.

Supports two backends:
  - Gemini native image generation (free tier, default)
  - Imagen 4 dedicated models (paid plan required)

Reads GOOGLE_API_KEY from .env and saves images as .webp.

Usage:
    uv run scripts/generate_image.py --prompt "a cat" --output cat.webp
    uv run scripts/generate_image.py --prompt "banner" --output banner.webp --aspect-ratio 16:9
    uv run scripts/generate_image.py --prompt "a cat" --output cat.webp --model imagen-4.0-generate-001
"""

import argparse
import os
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image


VALID_ASPECT_RATIOS = ["1:1", "3:4", "4:3", "9:16", "16:9"]

GEMINI_MODELS = [
    "gemini-2.0-flash-exp-image-generation",
    "gemini-2.5-flash-image",
    "gemini-3-pro-image-preview",
    "gemini-3.1-flash-image-preview",
]

IMAGEN_MODELS = [
    "imagen-4.0-generate-001",
    "imagen-4.0-ultra-generate-001",
    "imagen-4.0-fast-generate-001",
]

ALL_MODELS = GEMINI_MODELS + IMAGEN_MODELS
DEFAULT_MODEL = "gemini-2.5-flash-image"


def generate_with_gemini(client: genai.Client, model: str, prompt: str, aspect_ratio: str) -> list[Image.Image]:
    """Generate images using Gemini's native image generation."""
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
        ),
    )
    images = []
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            img = Image.open(BytesIO(part.inline_data.data))
            images.append(img)
    return images


def generate_with_imagen(client: genai.Client, model: str, prompt: str, aspect_ratio: str, count: int) -> list[Image.Image]:
    """Generate images using dedicated Imagen models (paid plan)."""
    response = client.models.generate_images(
        model=model,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=count,
            aspect_ratio=aspect_ratio,
        ),
    )
    if not response.generated_images:
        return []
    return [gi.image for gi in response.generated_images]


def main():
    parser = argparse.ArgumentParser(description="Generate images with Google AI Studio")
    parser.add_argument("--prompt", required=True, help="Image generation prompt")
    parser.add_argument("--output", required=True, help="Output file path (.webp)")
    parser.add_argument("--aspect-ratio", default="1:1", choices=VALID_ASPECT_RATIOS)
    parser.add_argument("--count", type=int, default=1, choices=range(1, 5), help="Number of images (1-4, Imagen only)")
    parser.add_argument("--model", default=DEFAULT_MODEL, choices=ALL_MODELS)
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise SystemExit("GOOGLE_API_KEY not found in environment or .env file")

    client = genai.Client(api_key=api_key)

    print(f"Model: {args.model}")
    print(f"Aspect ratio: {args.aspect_ratio}")
    print(f"Generating...")

    is_imagen = args.model in IMAGEN_MODELS

    if is_imagen:
        images = generate_with_imagen(client, args.model, args.prompt, args.aspect_ratio, args.count)
    else:
        # Gemini generates one image per call; loop for count > 1
        images = []
        for i in range(args.count):
            result = generate_with_gemini(client, args.model, args.prompt, args.aspect_ratio)
            images.extend(result)
            if i < args.count - 1:
                print(f"  Generated {i + 1}/{args.count}...")

    if not images:
        raise SystemExit("No images were generated. The prompt may have been blocked by safety filters.")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    for i, img in enumerate(images):
        if len(images) == 1:
            save_path = output_path
        else:
            save_path = output_path.with_stem(f"{output_path.stem}-{i + 1}")

        img.save(str(save_path), format="WEBP", quality=90)
        print(f"Saved: {save_path}")


if __name__ == "__main__":
    main()
