# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "markdown",
# ]
# ///

"""Convert markdown blog posts to content-only HTML for Shopify.

Relative image paths (../images/*, ../graphics/*) are converted to
publicly accessible GitHub raw URLs with proper percent-encoding.

Usage:
    uv run tools/md2html.py <markdown-file>

Example:
    uv run tools/md2html.py idb-main/idb-main.md
    # outputs: idb-main/idb-main.html
"""

import argparse
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

import markdown

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/tescodentaltw/tepe-blog/main"


def get_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def encode_path_for_url(repo_relative_path: str) -> str:
    """URL-encode each segment of a repo-relative path, preserving slashes."""
    segments = repo_relative_path.split("/")
    return "/".join(quote(seg, safe="") for seg in segments)


def resolve_relative_path(src: str, md_dir: Path, repo_root: Path) -> str | None:
    """Resolve a relative src path to a repo-relative path string.

    Returns None if the path doesn't point inside the repo.
    """
    resolved = (md_dir / src).resolve()
    try:
        return str(resolved.relative_to(repo_root))
    except ValueError:
        return None


def convert_image_urls(content: str, md_file: Path, repo_root: Path) -> str:
    """Replace relative src="..." paths in <img> tags with GitHub raw URLs."""
    md_dir = md_file.parent.resolve()

    def replace_src(match: re.Match) -> str:
        prefix = match.group(1)  # 'src="'
        src = match.group(2)  # the path
        suffix = match.group(3)  # '"'

        if src.startswith(("http://", "https://", "//")):
            return match.group(0)

        repo_rel = resolve_relative_path(src, md_dir, repo_root)
        if repo_rel is None:
            return match.group(0)

        encoded = encode_path_for_url(repo_rel)
        return f'{prefix}{GITHUB_RAW_BASE}/{encoded}{suffix}'

    return re.sub(r'(src=["\'])(\.\./[^"\']+)(["\'])', replace_src, content)


MAX_IMG_SIZE = 600


def add_img_max_size(html: str) -> str:
    """Add max-width and max-height to all <img> tags."""
    style = f"max-width: {MAX_IMG_SIZE}px; max-height: {MAX_IMG_SIZE}px; height: auto;"
    return re.sub(
        r"<img ",
        f'<img style="{style}" ',
        html,
    )


def md_to_html(content: str) -> str:
    """Convert markdown content to HTML using the markdown library."""
    return markdown.markdown(
        content,
        extensions=["tables", "md_in_html"],
    )


def main():
    parser = argparse.ArgumentParser(
        description="Convert markdown blog posts to Shopify-ready HTML."
    )
    parser.add_argument("markdown_file", help="Path to the markdown file to convert")
    args = parser.parse_args()

    md_file = Path(args.markdown_file).resolve()
    if not md_file.exists():
        raise SystemExit(f"File not found: {md_file}")

    repo_root = get_repo_root()
    content = md_file.read_text(encoding="utf-8")

    # Step 1: Convert relative image paths to GitHub raw URLs
    content = convert_image_urls(content, md_file, repo_root)

    # Step 2: Convert markdown to HTML
    html = md_to_html(content)

    # Step 3: Restrict image size
    html = add_img_max_size(html)

    # Step 4: Write output
    output_file = md_file.with_suffix(".html")
    output_file.write_text(html, encoding="utf-8")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
