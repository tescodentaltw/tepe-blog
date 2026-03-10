# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pillow",
# ]
# ///

"""Generate cover images for blog posts via Gemini web UI + agent-browser.

Requires Chrome with --remote-debugging-port=9222 and logged into Google.

Usage:
    uv run tools/generate_covers.py
"""

import base64
import subprocess
import time
from io import BytesIO
from pathlib import Path

from PIL import Image

CDP = ["agent-browser", "--cdp", "9222"]
COVERS_DIR = Path("idb-main/covers")

PROMPTS = {
    "idb-vs-floss": (
        "Clean flat illustration comparing interdental brush (left) and dental floss (right) "
        "side by side. Each shown cleaning between two molar teeth in cross-section. "
        "Soft teal background (#7CC4D1). Green interdental brush with bristles fanning out, "
        "white dental floss threaded through contact point. VS symbol in the center. "
        "Bold black outlines, modern dental education style. No text. 800x450 banner format, 16:9 aspect ratio."
    ),
    "idb-size-guide": (
        "Clean flat illustration of 8 interdental brushes arranged in a rainbow gradient from "
        "smallest (pink) to largest (black), each with different colored handles matching TePe color codes. "
        "Soft teal background (#7CC4D1). Brushes shown at different sizes with subtle size indicators. "
        "Bold black outlines, modern dental education style. No text. 800x450 banner format, 16:9 aspect ratio."
    ),
    "idb-before-brushing": (
        "Clean flat illustration showing correct dental cleaning sequence as 3 numbered steps with arrows: "
        "Step 1 green interdental brush, Step 2 white dental floss, Step 3 blue toothbrush with toothpaste. "
        "Each step connected by curved arrows. Soft teal background (#7CC4D1). Green checkmark on step 1. "
        "Bold black outlines, modern dental education style. No text. 800x450 banner format, 16:9 aspect ratio."
    ),
    "idb-myths-debunked": (
        "Clean flat illustration showing 3 myth-busting bubbles: (1) two teeth with a gap and an X mark, "
        "(2) a bleeding gum with an X mark, (3) toothpaste tube with an X mark. Each bubble has a green "
        "checkmark replacing the X, suggesting myths debunked. Soft teal background (#7CC4D1). "
        "Bold black outlines, modern dental education style. No text. 800x450 banner format, 16:9 aspect ratio."
    ),
}


def run(args: list[str], timeout: int = 30) -> str:
    result = subprocess.run(CDP + args, capture_output=True, text=True, timeout=timeout)
    return result.stdout.strip()


def generate_one(name: str, prompt: str) -> Path:
    output_path = COVERS_DIR / f"{name}.webp"
    print(f"\n{'='*60}")
    print(f"Generating: {name}")
    print(f"{'='*60}")

    # Navigate to new chat
    run(["open", "https://gemini.google.com/app"])
    time.sleep(3)

    # Click Create image
    snap = run(["snapshot", "-i"])
    # Find the Create image button ref
    create_ref = None
    for line in snap.splitlines():
        if "Create image" in line and "button" in line and "Deselect" not in line:
            ref = line.split("[ref=")[1].split("]")[0] if "[ref=" in line else None
            if ref:
                create_ref = ref
                break

    if create_ref:
        run(["click", f"@{create_ref}"])
        time.sleep(2)

    # Get snapshot to find the input box
    snap = run(["snapshot", "-i"])
    input_ref = None
    for line in snap.splitlines():
        if "textbox" in line and "prompt" in line.lower():
            ref = line.split("[ref=")[1].split("]")[0] if "[ref=" in line else None
            if ref:
                input_ref = ref
                break

    if not input_ref:
        print(f"ERROR: Could not find input textbox for {name}")
        return output_path

    # Fill and submit prompt
    run(["fill", f"@{input_ref}", prompt])
    run(["press", "Enter"])

    # Wait for generation (can take 15-30 seconds)
    print("Waiting for image generation...")
    time.sleep(35)

    # Find the generated image URL
    img_url_js = """(() => {
  const imgs = document.querySelectorAll("img");
  for (const img of imgs) {
    if (img.width > 200 && img.alt && img.alt.includes("AI generated")) {
      return img.src.replace(/=s\\d+-rj$/, "=s2048");
    }
  }
  return "not found";
})()"""

    img_url = run(["eval", "--stdin"], timeout=10)
    # Use stdin approach
    result = subprocess.run(
        CDP + ["eval", "--stdin"],
        input=img_url_js,
        capture_output=True,
        text=True,
        timeout=15,
    )
    img_url = result.stdout.strip().strip('"')

    if img_url == "not found" or not img_url.startswith("http"):
        print(f"ERROR: Could not find generated image for {name}")
        # Take screenshot for debugging
        run(["screenshot", f"/tmp/gemini-error-{name}.png"])
        return output_path

    # Open image in new tab
    open_js = f'(() => {{ window.open("{img_url}", "_blank"); return "ok"; }})()'
    subprocess.run(CDP + ["eval", "--stdin"], input=open_js, capture_output=True, text=True, timeout=10)
    time.sleep(3)

    # Extract image as base64 from the image tab
    extract_js = """(() => {
  const img = document.querySelector("img");
  if (!img) return "no img";
  const canvas = document.createElement("canvas");
  canvas.width = img.naturalWidth;
  canvas.height = img.naturalHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(img, 0, 0);
  return canvas.toDataURL("image/png");
})()"""

    result = subprocess.run(
        CDP + ["eval", "--stdin"],
        input=extract_js,
        capture_output=True,
        text=True,
        timeout=30,
    )
    b64_data = result.stdout.strip().strip('"')

    if not b64_data.startswith("data:image"):
        print(f"ERROR: Failed to extract image data for {name}")
        return output_path

    # Decode and save
    b64 = b64_data.split(",", 1)[1]
    img = Image.open(BytesIO(base64.b64decode(b64)))
    print(f"Original size: {img.size}")
    img = img.resize((800, 450), Image.LANCZOS)
    img.save(str(output_path), format="WEBP", quality=85)
    print(f"Saved: {output_path} ({output_path.stat().st_size} bytes)")

    return output_path


def main():
    COVERS_DIR.mkdir(parents=True, exist_ok=True)

    for name, prompt in PROMPTS.items():
        try:
            generate_one(name, prompt)
        except Exception as e:
            print(f"ERROR generating {name}: {e}")

    print("\n\nDone! Generated covers:")
    for f in sorted(COVERS_DIR.glob("*.webp")):
        print(f"  {f}")


if __name__ == "__main__":
    main()
