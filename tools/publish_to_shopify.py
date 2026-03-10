# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx",
#     "python-dotenv",
# ]
# ///

"""Publish markdown blog posts to Shopify as draft articles.

Converts markdown to HTML via md2html.py, then creates articles in a
specified Shopify blog using the Admin GraphQL API.

Usage:
    uv run tools/publish_to_shopify.py --all
    uv run tools/publish_to_shopify.py idb-main/idb-vs-floss.md
    uv run tools/publish_to_shopify.py --all --dry-run
    uv run tools/publish_to_shopify.py --all --update
    uv run tools/publish_to_shopify.py --list-blogs
"""

import argparse
import subprocess
from pathlib import Path

import httpx
from dotenv import load_dotenv
import os

SHOPIFY_API_VERSION = "2025-01"

BLOG_POSTS = [
    "idb-main/idb-why-you-only-clean-70-percent.md",
    "idb-main/idb-vs-floss.md",
    "idb-main/idb-size-guide.md",
    "idb-main/idb-before-brushing.md",
    "idb-main/idb-myths-debunked.md",
]

BLOG_TITLE = "牙縫清潔"


def get_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def get_access_token(store: str, client_id: str, client_secret: str) -> str:
    """Obtain access token via client_credentials grant."""
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
    token = resp.json()["access_token"]
    return token


def graphql(store: str, token: str, query: str, variables: dict | None = None) -> dict:
    """Execute a Shopify Admin GraphQL request."""
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


def list_blogs(store: str, token: str) -> list[dict]:
    """List all blogs on the store."""
    data = graphql(store, token, """
        query {
            blogs(first: 25) {
                nodes { id title handle }
            }
        }
    """)
    return data["blogs"]["nodes"]


def find_blog_id(store: str, token: str, title: str) -> str:
    """Find a blog's GID by title."""
    blogs = list_blogs(store, token)
    for blog in blogs:
        if blog["title"] == title:
            return blog["id"]
    titles = [b["title"] for b in blogs]
    raise SystemExit(f"Blog '{title}' not found. Available blogs: {titles}")


def find_existing_article(store: str, token: str, blog_id: str, title: str) -> dict | None:
    """Check if an article with the given title exists in the blog."""
    data = graphql(store, token, """
        query findArticle($query: String!) {
            articles(first: 5, query: $query) {
                nodes { id title blog { id } }
            }
        }
    """, {"query": f"title:'{title}'"})
    for article in data["articles"]["nodes"]:
        if article["title"] == title and article["blog"]["id"] == blog_id:
            return article
    return None


def create_article(store: str, token: str, blog_id: str, title: str, handle: str, body: str) -> dict:
    """Create a draft article in the specified blog."""
    data = graphql(store, token, """
        mutation articleCreate($article: ArticleCreateInput!) {
            articleCreate(article: $article) {
                article { id title handle }
                userErrors { field message }
            }
        }
    """, {
        "article": {
            "blogId": blog_id,
            "title": title,
            "handle": handle,
            "body": body,
            "isPublished": False,
            "author": {"name": "TePe"},
        }
    })
    result = data["articleCreate"]
    if result["userErrors"]:
        errors = "; ".join(f"{e['field']}: {e['message']}" for e in result["userErrors"])
        raise RuntimeError(f"Failed to create '{title}': {errors}")
    return result["article"]


def update_article(store: str, token: str, article_id: str, title: str, handle: str, body: str) -> dict:
    """Update an existing article."""
    data = graphql(store, token, """
        mutation articleUpdate($id: ID!, $article: ArticleUpdateInput!) {
            articleUpdate(id: $id, article: $article) {
                article { id title handle }
                userErrors { field message }
            }
        }
    """, {
        "id": article_id,
        "article": {
            "title": title,
            "handle": handle,
            "body": body,
            "isPublished": False,
        }
    })
    result = data["articleUpdate"]
    if result["userErrors"]:
        errors = "; ".join(f"{e['field']}: {e['message']}" for e in result["userErrors"])
        raise RuntimeError(f"Failed to update '{title}': {errors}")
    return result["article"]


def extract_title(md_path: Path) -> str:
    """Extract the first H1 heading from a markdown file."""
    for line in md_path.read_text("utf-8").splitlines():
        if line.startswith("# "):
            return line.lstrip("# ").strip()
    raise ValueError(f"No H1 heading found in {md_path}")


def ensure_html(md_path: Path, repo_root: Path) -> Path:
    """Run md2html.py if HTML is missing or stale."""
    html_path = md_path.with_suffix(".html")
    if not html_path.exists() or html_path.stat().st_mtime < md_path.stat().st_mtime:
        subprocess.run(
            ["uv", "run", str(repo_root / "tools" / "md2html.py"), str(md_path)],
            check=True,
        )
    return html_path


def main():
    parser = argparse.ArgumentParser(
        description="Publish markdown blog posts to Shopify as draft articles."
    )
    parser.add_argument("files", nargs="*", help="Markdown files to publish")
    parser.add_argument("--all", action="store_true", help="Publish all 5 supporting blog posts")
    parser.add_argument("--dry-run", action="store_true", help="Preview without calling Shopify API")
    parser.add_argument("--update", action="store_true", help="Update existing articles instead of skipping")
    parser.add_argument("--list-blogs", action="store_true", help="List all blogs on the store and exit")
    parser.add_argument("--blog", default=BLOG_TITLE, help=f"Blog title to publish to (default: {BLOG_TITLE})")
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

    # Get access token
    print(f"Authenticating with {store}...")
    token = get_access_token(store, client_id, client_secret)
    print("Access token obtained.")

    # List blogs mode
    if args.list_blogs:
        blogs = list_blogs(store, token)
        for b in blogs:
            print(f"  {b['id']}  {b['title']}  ({b['handle']})")
        return

    # Resolve target files
    if args.all:
        md_files = [repo_root / f for f in BLOG_POSTS]
    elif args.files:
        md_files = [Path(f).resolve() for f in args.files]
    else:
        raise SystemExit("Specify markdown files or use --all")

    # Find blog
    blog_id = find_blog_id(store, token, args.blog)
    print(f"Blog: {args.blog} ({blog_id})")
    print()

    # Process each file
    for md_path in md_files:
        if not md_path.exists():
            print(f"SKIP (not found): {md_path}")
            continue

        title = extract_title(md_path)
        handle = md_path.stem  # e.g. "idb-vs-floss"

        if args.dry_run:
            print(f"DRY RUN: '{title}' (handle: {handle})")
            continue

        # Generate HTML
        html_path = ensure_html(md_path, repo_root)
        body = html_path.read_text("utf-8")

        # Check for duplicates
        existing = find_existing_article(store, token, blog_id, title)

        if existing and not args.update:
            print(f"SKIP (exists): {title}")
            continue

        if existing and args.update:
            article = update_article(store, token, existing["id"], title, handle, body)
            print(f"UPDATED: {title}")
            print(f"  ID: {article['id']}")
        else:
            article = create_article(store, token, blog_id, title, handle, body)
            print(f"CREATED: {title}")
            print(f"  ID: {article['id']}")

        print()


if __name__ == "__main__":
    main()
