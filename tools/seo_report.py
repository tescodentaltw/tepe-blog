# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-auth",
#     "google-api-python-client",
#     "google-analytics-data",
#     "rich",
# ]
# ///

"""SEO Performance Report for tepetw.com

Pulls data from Google Search Console and Google Analytics 4,
using Application Default Credentials (ADC).
"""

import argparse
from datetime import date, timedelta

import google.auth
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    OrderBy,
    RunReportRequest,
)
from googleapiclient.discovery import build
from rich.console import Console
from rich.table import Table

# ── Config ──────────────────────────────────────────────────────────
GSC_SITE = "sc-domain:tepetw.com"
GA4_PROPERTY = "properties/517199426"  # tepetw.com

console = Console()


# ── Google Search Console ───────────────────────────────────────────
def gsc_report(days: int = 90):
    scopes = ["https://www.googleapis.com/auth/webmasters.readonly"]
    creds, _ = google.auth.default(scopes=scopes)
    service = build("searchconsole", "v1", credentials=creds)

    end = date.today() - timedelta(days=3)  # GSC data has ~3 day lag
    start = end - timedelta(days=days)

    # ── Top queries ─────────────────────────────────────────────────
    resp = (
        service.searchanalytics()
        .query(
            siteUrl=GSC_SITE,
            body={
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "dimensions": ["query"],
                "rowLimit": 30,
                "type": "web",
            },
        )
        .execute()
    )

    table = Table(title=f"🔍 GSC Top Queries ({start} → {end})")
    table.add_column("#", style="dim", width=4)
    table.add_column("Query", min_width=30)
    table.add_column("Clicks", justify="right")
    table.add_column("Impressions", justify="right")
    table.add_column("CTR", justify="right")
    table.add_column("Position", justify="right")

    for i, row in enumerate(resp.get("rows", []), 1):
        table.add_row(
            str(i),
            row["keys"][0],
            f"{row['clicks']:,.0f}",
            f"{row['impressions']:,.0f}",
            f"{row['ctr']:.1%}",
            f"{row['position']:.1f}",
        )
    console.print(table)
    console.print()

    # ── Top pages ───────────────────────────────────────────────────
    resp = (
        service.searchanalytics()
        .query(
            siteUrl=GSC_SITE,
            body={
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "dimensions": ["page"],
                "rowLimit": 20,
                "type": "web",
            },
        )
        .execute()
    )

    table = Table(title=f"📄 GSC Top Pages ({start} → {end})")
    table.add_column("#", style="dim", width=4)
    table.add_column("Page", min_width=40)
    table.add_column("Clicks", justify="right")
    table.add_column("Impressions", justify="right")
    table.add_column("CTR", justify="right")
    table.add_column("Position", justify="right")

    for i, row in enumerate(resp.get("rows", []), 1):
        page = row["keys"][0].replace("https://tepetw.com", "")
        table.add_row(
            str(i),
            page or "/",
            f"{row['clicks']:,.0f}",
            f"{row['impressions']:,.0f}",
            f"{row['ctr']:.1%}",
            f"{row['position']:.1f}",
        )
    console.print(table)
    console.print()

    # ── By device ───────────────────────────────────────────────────
    resp = (
        service.searchanalytics()
        .query(
            siteUrl=GSC_SITE,
            body={
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "dimensions": ["device"],
                "type": "web",
            },
        )
        .execute()
    )

    table = Table(title=f"📱 GSC By Device ({start} → {end})")
    table.add_column("Device")
    table.add_column("Clicks", justify="right")
    table.add_column("Impressions", justify="right")
    table.add_column("CTR", justify="right")
    table.add_column("Position", justify="right")

    for row in resp.get("rows", []):
        table.add_row(
            row["keys"][0],
            f"{row['clicks']:,.0f}",
            f"{row['impressions']:,.0f}",
            f"{row['ctr']:.1%}",
            f"{row['position']:.1f}",
        )
    console.print(table)
    console.print()

    # ── CTR opportunities (high impressions, low CTR) ───────────────
    resp = (
        service.searchanalytics()
        .query(
            siteUrl=GSC_SITE,
            body={
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "dimensions": ["query"],
                "rowLimit": 100,
                "type": "web",
            },
        )
        .execute()
    )

    rows = resp.get("rows", [])
    # Filter: position <= 20 and CTR < 5%, sort by impressions desc
    opps = [
        r
        for r in rows
        if r["position"] <= 20 and r["ctr"] < 0.05 and r["impressions"] >= 10
    ]
    opps.sort(key=lambda r: r["impressions"], reverse=True)

    if opps:
        table = Table(title="💡 CTR Opportunities (Position ≤ 20, CTR < 5%)")
        table.add_column("#", style="dim", width=4)
        table.add_column("Query", min_width=30)
        table.add_column("Clicks", justify="right")
        table.add_column("Impressions", justify="right")
        table.add_column("CTR", justify="right")
        table.add_column("Position", justify="right")

        for i, row in enumerate(opps[:15], 1):
            table.add_row(
                str(i),
                row["keys"][0],
                f"{row['clicks']:,.0f}",
                f"{row['impressions']:,.0f}",
                f"{row['ctr']:.1%}",
                f"{row['position']:.1f}",
            )
        console.print(table)
        console.print()


# ── Google Analytics 4 ──────────────────────────────────────────────
def ga4_report(days: int = 90):
    client = BetaAnalyticsDataClient()

    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days)
    date_range = DateRange(start_date=start.isoformat(), end_date=end.isoformat())

    # ── Overall summary ─────────────────────────────────────────────
    resp = client.run_report(
        RunReportRequest(
            property=GA4_PROPERTY,
            date_ranges=[date_range],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="newUsers"),
                Metric(name="screenPageViews"),
                Metric(name="averageSessionDuration"),
                Metric(name="bounceRate"),
            ],
        )
    )

    if resp.rows:
        r = resp.rows[0]
        table = Table(title=f"📊 GA4 Overview ({start} → {end})")
        table.add_column("Metric")
        table.add_column("Value", justify="right")

        labels = [
            "Sessions",
            "Total Users",
            "New Users",
            "Page Views",
            "Avg Session Duration (s)",
            "Bounce Rate",
        ]
        for label, val in zip(labels, r.metric_values):
            v = val.value
            if label == "Bounce Rate":
                v = f"{float(v):.1%}"
            elif label == "Avg Session Duration (s)":
                v = f"{float(v):.0f}"
            else:
                v = f"{int(float(v)):,}"
            table.add_row(label, v)
        console.print(table)
        console.print()

    # ── Top pages ───────────────────────────────────────────────────
    resp = client.run_report(
        RunReportRequest(
            property=GA4_PROPERTY,
            date_ranges=[date_range],
            dimensions=[Dimension(name="pagePath")],
            metrics=[
                Metric(name="screenPageViews"),
                Metric(name="totalUsers"),
                Metric(name="averageSessionDuration"),
            ],
            order_bys=[
                OrderBy(
                    metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"),
                    desc=True,
                )
            ],
            limit=20,
        )
    )

    table = Table(title=f"📄 GA4 Top Pages ({start} → {end})")
    table.add_column("#", style="dim", width=4)
    table.add_column("Page", min_width=40)
    table.add_column("Views", justify="right")
    table.add_column("Users", justify="right")
    table.add_column("Avg Duration (s)", justify="right")

    for i, row in enumerate(resp.rows, 1):
        table.add_row(
            str(i),
            row.dimension_values[0].value,
            f"{int(float(row.metric_values[0].value)):,}",
            f"{int(float(row.metric_values[1].value)):,}",
            f"{float(row.metric_values[2].value):.0f}",
        )
    console.print(table)
    console.print()

    # ── Traffic sources ─────────────────────────────────────────────
    resp = client.run_report(
        RunReportRequest(
            property=GA4_PROPERTY,
            date_ranges=[date_range],
            dimensions=[Dimension(name="sessionDefaultChannelGroup")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="screenPageViews"),
            ],
            order_bys=[
                OrderBy(
                    metric=OrderBy.MetricOrderBy(metric_name="sessions"),
                    desc=True,
                )
            ],
            limit=15,
        )
    )

    table = Table(title=f"🌐 GA4 Traffic Sources ({start} → {end})")
    table.add_column("Channel")
    table.add_column("Sessions", justify="right")
    table.add_column("Users", justify="right")
    table.add_column("Page Views", justify="right")

    for row in resp.rows:
        table.add_row(
            row.dimension_values[0].value,
            f"{int(float(row.metric_values[0].value)):,}",
            f"{int(float(row.metric_values[1].value)):,}",
            f"{int(float(row.metric_values[2].value)):,}",
        )
    console.print(table)
    console.print()


# ── Main ────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="SEO Performance Report for tepetw.com")
    parser.add_argument(
        "--days", type=int, default=90, help="Number of days to look back (default: 90)"
    )
    parser.add_argument(
        "--gsc-only", action="store_true", help="Only show GSC data"
    )
    parser.add_argument(
        "--ga4-only", action="store_true", help="Only show GA4 data"
    )
    args = parser.parse_args()

    if not args.ga4_only:
        console.rule("[bold]Google Search Console[/bold]")
        console.print()
        gsc_report(days=args.days)

    if not args.gsc_only:
        console.rule("[bold]Google Analytics 4[/bold]")
        console.print()
        ga4_report(days=args.days)


if __name__ == "__main__":
    main()
