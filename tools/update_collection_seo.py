# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx",
#     "python-dotenv",
#     "rich",
# ]
# ///

"""Update Shopify collection SEO titles and descriptions.

Lists collections and updates their SEO metadata via Admin GraphQL API.

Usage:
    uv run tools/update_collection_seo.py --list
    uv run tools/update_collection_seo.py --update
    uv run tools/update_collection_seo.py --update --dry-run
"""

import argparse
import os
import sys

import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

SHOPIFY_API_VERSION = "2025-01"

# SEO title mapping: collection handle → SEO title
SEO_TITLES: dict[str, str] = {
    "frontpage": "熱門口腔護理商品 - TePe 瑞典專業牙刷牙間刷",
    "toothbrushes": "一般牙刷系列 - TePe 瑞典專業口腔護理",
    "children-toothbrush": "兒童牙刷系列 - TePe 瑞典專業口腔護理",
    "post-oral-surgery-care": "口腔手術後護理系列 - TePe 瑞典專業口腔護理",
    "specialty-brushes": "特殊牙刷系列 - TePe 瑞典專業口腔護理",
    "periodontal-disease-specific-care": "牙周病專屬護理系列 - TePe 瑞典專業口腔護理",
    "orthodontic-cleaning": "矯正清潔護理系列 - TePe 瑞典專業口腔護理",
    "idb": "牙間刷系列｜尺寸選擇與使用指南 - TePe 瑞典專業口腔護理",
    "idc2": "牙線・牙線棒・其他牙縫清潔 - TePe 瑞典專業口腔護理",
    "accessories": "口腔護理配件 - TePe 瑞典專業口腔護理",
    "pet": "寵物口腔護理系列 - TePe 瑞典專業口腔護理",
    "travel-kit": "旅用清潔套裝 - TePe 瑞典專業口腔護理",
    "easypick": "EasyPick 輕鬆剔系列 - TePe 瑞典專業口腔護理",
    "single-tuft-series": "單束毛牙刷系列｜矯正清潔必備 - TePe 瑞典專業口腔護理",
    "dental-implant-care-series": "植牙護理系列 - TePe 瑞典專業口腔護理",
    "value-pack": "超值量販組 - TePe 瑞典專業口腔護理",
    "bundles": "組合優惠 - TePe 瑞典專業口腔護理",
}

console = Console()


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
    return resp.json()["access_token"]


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


def list_collections(store: str, token: str) -> list[dict]:
    """List all collections with SEO info."""
    data = graphql(store, token, """
        query {
            collections(first: 50) {
                nodes {
                    id
                    title
                    handle
                    seo { title description }
                }
            }
        }
    """)
    return data["collections"]["nodes"]


def update_collection_seo(
    store: str, token: str, collection_id: str, seo_title: str, seo_description: str | None = None
) -> dict:
    """Update a collection's SEO title and description."""
    seo_input: dict = {"title": seo_title}
    if seo_description is not None:
        seo_input["description"] = seo_description

    data = graphql(store, token, """
        mutation collectionUpdate($input: CollectionInput!) {
            collectionUpdate(input: $input) {
                collection {
                    id
                    title
                    handle
                    seo { title description }
                }
                userErrors { field message }
            }
        }
    """, variables={"input": {"id": collection_id, "seo": seo_input}})

    errors = data["collectionUpdate"]["userErrors"]
    if errors:
        raise RuntimeError(f"Update errors: {errors}")
    return data["collectionUpdate"]["collection"]


def print_collections(collections: list[dict], title: str = "Shopify Collections"):
    """Print collections in a table."""
    table = Table(title=title)
    table.add_column("#", style="dim", width=4)
    table.add_column("Handle", min_width=30, no_wrap=True)
    table.add_column("Title", min_width=20)
    table.add_column("SEO Title", min_width=30)
    table.add_column("SEO Description", min_width=20)

    for i, c in enumerate(collections, 1):
        seo = c.get("seo") or {}
        table.add_row(
            str(i),
            c["handle"],
            c["title"],
            seo.get("title") or "[dim](empty)[/dim]",
            (seo.get("description") or "[dim](empty)[/dim]")[:50],
        )
    console.print(table)


def main():
    load_dotenv()

    store = os.environ.get("SHOPIFY_STORE")
    client_id = os.environ.get("SHOPIFY_CLIENT_ID")
    client_secret = os.environ.get("SHOPIFY_CLIENT_SECRET")

    if not all([store, client_id, client_secret]):
        console.print("[red]Missing SHOPIFY_STORE, SHOPIFY_CLIENT_ID, or SHOPIFY_CLIENT_SECRET in .env[/red]")
        sys.exit(1)

    assert store is not None
    assert client_id is not None
    assert client_secret is not None

    parser = argparse.ArgumentParser(description="Update Shopify collection SEO metadata")
    parser.add_argument("--list", action="store_true", help="List all collections")
    parser.add_argument("--update", action="store_true", help="Update SEO titles based on mapping")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated without making changes")
    args = parser.parse_args()

    if not any([args.list, args.update]):
        parser.print_help()
        sys.exit(1)

    token = get_access_token(store, client_id, client_secret)

    if args.list:
        collections = list_collections(store, token)
        print_collections(collections)

    if args.update:
        if not SEO_TITLES:
            console.print("[red]SEO_TITLES mapping is empty. Please configure it first.[/red]")
            sys.exit(1)

        collections = list_collections(store, token)
        handle_to_collection = {c["handle"]: c for c in collections}

        for handle, seo_title in SEO_TITLES.items():
            c = handle_to_collection.get(handle)
            if not c:
                console.print(f"[yellow]Collection '{handle}' not found, skipping[/yellow]")
                continue

            current_seo_title = (c.get("seo") or {}).get("title") or ""
            if current_seo_title == seo_title:
                console.print(f"[dim]{handle}: already has correct SEO title, skipping[/dim]")
                continue

            if args.dry_run:
                console.print(f"[cyan]DRY RUN[/cyan] {handle}: '{current_seo_title}' → '{seo_title}'")
            else:
                result = update_collection_seo(store, token, c["id"], seo_title)
                console.print(f"[green]Updated[/green] {handle}: SEO title → '{result['seo']['title']}'")

        if not args.dry_run:
            console.print()
            console.rule("Updated Collections")
            collections = list_collections(store, token)
            print_collections(collections)


if __name__ == "__main__":
    main()
