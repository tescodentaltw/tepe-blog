# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-auth",
#     "google-api-python-client",
#     "rich",
# ]
# ///

"""Manage sitemaps in Google Search Console for tepetw.com.

Supports listing, submitting, and deleting sitemaps.
Uses Application Default Credentials (ADC).
"""

import argparse
import sys

import google.auth
from googleapiclient.discovery import build
from rich.console import Console
from rich.table import Table

GSC_SITE = "sc-domain:tepetw.com"
console = Console()


def get_service():
    scopes = ["https://www.googleapis.com/auth/webmasters"]
    creds, _ = google.auth.default(scopes=scopes)
    return build("searchconsole", "v1", credentials=creds)


def list_sitemaps():
    service = get_service()
    resp = service.sitemaps().list(siteUrl=GSC_SITE).execute()
    sitemaps = resp.get("sitemap", [])

    if not sitemaps:
        console.print("[yellow]No sitemaps found.[/yellow]")
        return

    table = Table(title="GSC Sitemaps")
    table.add_column("URL", min_width=40)
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Last Submitted")
    table.add_column("Last Downloaded")
    table.add_column("Errors")
    table.add_column("Warnings")

    for s in sitemaps:
        table.add_row(
            s.get("path", ""),
            s.get("type", ""),
            s.get("isPending", False) and "Pending" or "Active",
            s.get("lastSubmitted", "N/A"),
            s.get("lastDownloaded", "N/A"),
            str(s.get("errors", 0)),
            str(s.get("warnings", 0)),
        )
    console.print(table)


def submit_sitemap(url: str):
    service = get_service()
    console.print(f"Submitting sitemap: [bold]{url}[/bold]")
    service.sitemaps().submit(siteUrl=GSC_SITE, feedpath=url).execute()
    console.print(f"[green]Successfully submitted: {url}[/green]")


def delete_sitemap(url: str):
    service = get_service()
    console.print(f"Deleting sitemap: [bold]{url}[/bold]")
    service.sitemaps().delete(siteUrl=GSC_SITE, feedpath=url).execute()
    console.print(f"[green]Successfully deleted: {url}[/green]")


def main():
    parser = argparse.ArgumentParser(description="Manage GSC sitemaps for tepetw.com")
    parser.add_argument("--list", action="store_true", help="List all sitemaps")
    parser.add_argument("--submit", type=str, help="Submit a sitemap URL")
    parser.add_argument("--delete", type=str, help="Delete a sitemap URL")
    args = parser.parse_args()

    if not any([args.list, args.submit, args.delete]):
        parser.print_help()
        sys.exit(1)

    if args.list:
        list_sitemaps()

    if args.submit:
        submit_sitemap(args.submit)

    if args.delete:
        delete_sitemap(args.delete)

    # Show final state if we made changes
    if args.submit or args.delete:
        console.print()
        console.rule("Current Sitemaps")
        list_sitemaps()


if __name__ == "__main__":
    main()
