# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx",
#     "python-dotenv",
#     "rich",
# ]
# ///

"""Update Shopify product descriptions and SEO meta descriptions.

Lists products with CJK character counts and SEO info, updates descriptions
and/or SEO meta descriptions from JSON mappings (handle → content).

Usage:
    uv run tools/update_product_descriptions.py --list
    uv run tools/update_product_descriptions.py --update descriptions.json
    uv run tools/update_product_descriptions.py --update-seo meta.json
    uv run tools/update_product_descriptions.py --update-seo meta.json --dry-run
"""

import argparse
import json
import os
import re
import sys

import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

SHOPIFY_API_VERSION = "2025-01"
MIN_CHINESE_CHARS = 500

PRODUCTS_QUERY = """
query ($cursor: String) {
    products(first: 250, after: $cursor) {
        nodes {
            id
            title
            handle
            description
            descriptionHtml
            seo { title description }
        }
        pageInfo {
            hasNextPage
            endCursor
        }
    }
}
"""

PRODUCT_UPDATE_MUTATION = """
mutation productUpdate($input: ProductInput!) {
    productUpdate(input: $input) {
        product {
            id
            title
            descriptionHtml
            seo { title description }
        }
        userErrors {
            field
            message
        }
    }
}
"""

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


def count_chinese_chars(text: str) -> int:
    """Count CJK Unified Ideographs characters."""
    if not text:
        return 0
    return len(re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf]", text))


def fetch_all_products(store: str, token: str) -> list[dict]:
    """Fetch all products with cursor-based pagination."""
    products = []
    cursor = None
    while True:
        data = graphql(store, token, PRODUCTS_QUERY, {"cursor": cursor})
        nodes = data["products"]["nodes"]
        products.extend(nodes)
        page_info = data["products"]["pageInfo"]
        if not page_info["hasNextPage"]:
            break
        cursor = page_info["endCursor"]
    return products


def update_product_description(
    store: str, token: str, product_id: str, description_html: str
) -> dict:
    """Update a product's description via GraphQL."""
    data = graphql(
        store,
        token,
        PRODUCT_UPDATE_MUTATION,
        variables={"input": {"id": product_id, "descriptionHtml": description_html}},
    )
    errors = data["productUpdate"]["userErrors"]
    if errors:
        raise RuntimeError(f"Update errors: {errors}")
    return data["productUpdate"]["product"]


def update_product_seo(
    store: str, token: str, product_id: str, seo_description: str
) -> dict:
    """Update a product's SEO meta description via GraphQL."""
    data = graphql(
        store,
        token,
        PRODUCT_UPDATE_MUTATION,
        variables={"input": {"id": product_id, "seo": {"description": seo_description}}},
    )
    errors = data["productUpdate"]["userErrors"]
    if errors:
        raise RuntimeError(f"Update errors: {errors}")
    return data["productUpdate"]["product"]


def print_products(products: list[dict], title: str = "Shopify Products"):
    """Print products in a rich table."""
    table = Table(title=title)
    table.add_column("#", style="dim", width=4)
    table.add_column("Title", min_width=20, no_wrap=True)
    table.add_column("Handle", min_width=20, no_wrap=True)
    table.add_column("CJK", justify="right", width=6)
    table.add_column("SEO Desc", min_width=30)

    for i, p in enumerate(products, 1):
        char_count = count_chinese_chars(p["description"])
        style = "red" if char_count < MIN_CHINESE_CHARS else "green"
        seo = (p.get("seo") or {}).get("description") or ""
        seo_display = seo[:50] + "…" if len(seo) > 50 else seo
        table.add_row(
            str(i),
            p["title"],
            p["handle"],
            f"[{style}]{char_count}[/{style}]",
            seo_display if seo_display else "[dim](empty)[/dim]",
        )
    console.print(table)


def main():
    load_dotenv()

    store = os.environ.get("SHOPIFY_STORE")
    client_id = os.environ.get("SHOPIFY_CLIENT_ID")
    client_secret = os.environ.get("SHOPIFY_CLIENT_SECRET")

    if not all([store, client_id, client_secret]):
        console.print(
            "[red]Missing SHOPIFY_STORE, SHOPIFY_CLIENT_ID, or SHOPIFY_CLIENT_SECRET in .env[/red]"
        )
        sys.exit(1)

    assert store is not None
    assert client_id is not None
    assert client_secret is not None

    parser = argparse.ArgumentParser(
        description="Update Shopify product descriptions from a JSON file"
    )
    parser.add_argument(
        "--list", action="store_true", help="List all products with CJK char counts"
    )
    parser.add_argument(
        "--update",
        metavar="JSON_FILE",
        help="Update descriptions from JSON file (handle → HTML mapping)",
    )
    parser.add_argument(
        "--update-seo",
        metavar="JSON_FILE",
        help="Update SEO meta descriptions from JSON file (handle → text mapping)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes",
    )
    args = parser.parse_args()

    if not args.list and not args.update and not args.update_seo:
        parser.print_help()
        sys.exit(1)

    token = get_access_token(store, client_id, client_secret)
    products = fetch_all_products(store, token)
    console.print(f"[bold]Fetched {len(products)} products[/bold]\n")

    if args.list:
        print_products(products)

    if args.update:
        with open(args.update) as f:
            descriptions: dict[str, str] = json.load(f)

        handle_to_product = {p["handle"]: p for p in products}
        updated = 0

        for handle, new_html in descriptions.items():
            p = handle_to_product.get(handle)
            if not p:
                console.print(f"[yellow]Product '{handle}' not found, skipping[/yellow]")
                continue

            current_count = count_chinese_chars(p["description"])
            new_count = count_chinese_chars(new_html)

            if args.dry_run:
                console.print(
                    f"[cyan]DRY RUN[/cyan] {p['title']}: {current_count} → {new_count} CJK chars"
                )
                console.print(f"  [dim]{new_html[:150]}...[/dim]\n")
            else:
                try:
                    update_product_description(store, token, p["id"], new_html)
                    console.print(
                        f"[green]Updated[/green] {p['title']}: {current_count} → {new_count} CJK chars"
                    )
                    updated += 1
                except Exception as e:
                    console.print(f"[red]Error[/red] {p['title']}: {e}")

        if not args.dry_run:
            console.print(f"\n[bold]Updated {updated}/{len(descriptions)} products[/bold]")

    if args.update_seo:
        with open(args.update_seo) as f:
            seo_descriptions: dict[str, str] = json.load(f)

        handle_to_product = {p["handle"]: p for p in products}
        updated = 0

        for handle, new_seo in seo_descriptions.items():
            p = handle_to_product.get(handle)
            if not p:
                console.print(f"[yellow]Product '{handle}' not found, skipping[/yellow]")
                continue

            current_seo = (p.get("seo") or {}).get("description") or ""

            if args.dry_run:
                console.print(f"[cyan]DRY RUN[/cyan] {p['title']}:")
                console.print(f"  [dim]Old: {current_seo[:80]}[/dim]")
                console.print(f"  [bold]New: {new_seo}[/bold]\n")
            else:
                try:
                    update_product_seo(store, token, p["id"], new_seo)
                    console.print(f"[green]Updated SEO[/green] {p['title']}")
                    updated += 1
                except Exception as e:
                    console.print(f"[red]Error[/red] {p['title']}: {e}")

        if not args.dry_run:
            console.print(f"\n[bold]Updated SEO for {updated}/{len(seo_descriptions)} products[/bold]")


if __name__ == "__main__":
    main()
