# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pillow",
# ]
# ///

"""Extract generated image from Gemini via base64 data and save as resized webp.

Usage:
    uv run tools/extract_gemini_image.py <base64-file> <output.webp> [--width 800] [--height 450] [--quality 85]
"""

import argparse
import base64
from io import BytesIO
from pathlib import Path

from PIL import Image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="File containing base64 data URL")
    parser.add_argument("output", help="Output webp file path")
    parser.add_argument("--width", type=int, default=800)
    parser.add_argument("--height", type=int, default=450)
    parser.add_argument("--quality", type=int, default=85)
    args = parser.parse_args()

    raw = Path(args.input).read_text()
    b64 = raw.strip().strip('"').split(",", 1)[1]
    img = Image.open(BytesIO(base64.b64decode(b64)))
    print(f"Original: {img.size}")

    img = img.resize((args.width, args.height), Image.LANCZOS)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    img.save(args.output, format="WEBP", quality=args.quality)
    print(f"Saved: {args.output} ({Path(args.output).stat().st_size} bytes)")


if __name__ == "__main__":
    main()
