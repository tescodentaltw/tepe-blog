# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx",
#     "python-dotenv",
# ]
# ///

"""Update cover images for 5 IDB blog posts on Shopify.

Uses the FB post images as feature images for the corresponding Shopify articles.

Usage:
    uv run tools/update_cover_images.py
    uv run tools/update_cover_images.py --dry-run
"""

import argparse
import os
import subprocess
from pathlib import Path
from urllib.parse import quote

import httpx
from dotenv import load_dotenv

SHOPIFY_API_VERSION = "2025-01"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/tescodentaltw/tepe-blog/main"
BLOG_TITLE = "牙縫清潔"

# Mapping: (md filename, image repo-relative path, alt text)
COVER_IMAGES = [
    (
        "idb-main/idb-why-you-only-clean-70-percent.md",
        "graphics/idb-牙間刷-簡介/idb-cleans-remaining-30-percent-gaps.webp",
        "牙刷只能清潔70%的牙齒表面",
    ),
    (
        "idb-main/idb-vs-floss.md",
        "graphics/idb-牙間刷-簡介/idb-vs-floss-comparison.webp",
        "牙間刷vs牙線比較",
    ),
    (
        "idb-main/idb-size-guide.md",
        "images/idb-I型牙間刷-普通刷毛/feature1.webp",
        "TePe牙間刷9種尺寸色碼",
    ),
    (
        "idb-main/idb-before-brushing.md",
        "graphics/idb-牙間刷-大小選擇/green-idb-cleaning-front-teeth-gap.webp",
        "牙間刷清潔前牙牙縫",
    ),
    (
        "idb-main/idb-myths-debunked.md",
        "graphics/idb-牙間刷-簡介/idb-usage-scenarios-overview.webp",
        "牙間刷適用場景總覽",
    ),
]


def get_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def encode_path_for_url(repo_relative_path: str) -> str:
    segments = repo_relative_path.split("/")
    return "/".join(quote(seg, safe="") for seg in segments)


def get_access_token(store: str, client_id: str, client_secret: str) -> str:
    url = f"https://{store}/admin/oauth/access_token"
    resp = httpx.post(
        url,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def graphql(store: str, token: str, query: str, variables: dict | None = None) -> dict:
    url = f"https://{store}/admin/api/{SHOPIFY_API_VERSION}/graphql.json"
    payload: dict = {"query": query}
    if variables:
        payload["variables"] = variables
    resp = httpx.post(
        url,
        json=payload,
        headers={
            "X-Shopify-Access-Token": token,
            "Content-Type": "application/json",
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]


def find_blog_id(store: str, token: str, title: str) -> str:
    data = graphql(store, token, """
        query {
            blogs(first: 25) {
                nodes { id title handle }
            }
        }
    """)
    for blog in data["blogs"]["nodes"]:
        if blog["title"] == title:
            return blog["id"]
    titles = [b["title"] for b in data["blogs"]["nodes"]]
    raise SystemExit(f"Blog '{title}' not found. Available: {titles}")


def find_articles_in_blog(store: str, token: str, blog_id: str) -> list[dict]:
    """Fetch all articles in a blog and return them."""
    data = graphql(store, token, """
        query($blogId: ID!) {
            blog(id: $blogId) {
                articles(first: 50) {
                    nodes { id title handle }
                }
            }
        }
    """, {"blogId": blog_id})
    return data["blog"]["articles"]["nodes"]


def update_article_image(store: str, token: str, article_id: str, image_url: str, alt_text: str) -> dict:
    data = graphql(store, token, """
        mutation articleUpdate($id: ID!, $article: ArticleUpdateInput!) {
            articleUpdate(id: $id, article: $article) {
                article { id title image { altText url } }
                userErrors { field message }
            }
        }
    """, {
        "id": article_id,
        "article": {
            "image": {
                "altText": alt_text,
                "url": image_url,
            }
        }
    })
    result = data["articleUpdate"]
    if result["userErrors"]:
        errors = "; ".join(f"{e['field']}: {e['message']}" for e in result["userErrors"])
        raise RuntimeError(f"Failed to update image: {errors}")
    return result["article"]


def extract_title(md_path: Path) -> str:
    for line in md_path.read_text("utf-8").splitlines():
        if line.startswith("# "):
            return line.lstrip("# ").strip()
    raise ValueError(f"No H1 heading found in {md_path}")


def main():
    parser = argparse.ArgumentParser(description="Update cover images for IDB blog posts on Shopify.")
    parser.add_argument("--dry-run", action="store_true", help="Preview without calling Shopify API")
    args = parser.parse_args()

    load_dotenv()
    store = os.environ.get("SHOPIFY_STORE")
    client_id = os.environ.get("SHOPIFY_CLIENT_ID")
    client_secret = os.environ.get("SHOPIFY_CLIENT_SECRET")

    missing = [k for k, v in {
        "SHOPIFY_STORE": store,
        "SHOPIFY_CLIENT_ID": client_id,
        "SHOPIFY_CLIENT_SECRET": client_secret,
    }.items() if not v]
    if missing:
        raise SystemExit(f"Missing environment variables: {', '.join(missing)}")

    repo_root = get_repo_root()

    print(f"Authenticating with {store}...")
    token = get_access_token(store, client_id, client_secret)
    print("Access token obtained.\n")

    blog_id = find_blog_id(store, token, BLOG_TITLE)
    print(f"Blog: {BLOG_TITLE} ({blog_id})\n")

    # Fetch all articles in the blog once
    articles = find_articles_in_blog(store, token, blog_id)
    handle_to_article = {a["handle"]: a for a in articles}

    for md_rel, image_rel, alt_text in COVER_IMAGES:
        md_path = repo_root / md_rel
        handle = md_path.stem  # e.g. "idb-vs-floss"
        encoded_path = encode_path_for_url(image_rel)
        image_url = f"{GITHUB_RAW_BASE}/{encoded_path}"

        if args.dry_run:
            print(f"DRY RUN: handle={handle}")
            print(f"  Image URL: {image_url}")
            print(f"  Alt text: {alt_text}\n")
            continue

        article = handle_to_article.get(handle)
        if not article:
            print(f"SKIP (not found): {handle}\n")
            continue

        updated = update_article_image(store, token, article["id"], image_url, alt_text)
        print(f"UPDATED: {updated['title']}")
        print(f"  ID: {updated['id']}")
        print(f"  Image: {updated['image']['url']}\n")


if __name__ == "__main__":
    main()
