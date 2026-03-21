---
name: seo-report-generation
description: >
  Generate weekly SEO performance reports for tepetw.com using Google Search Console
  and Google Analytics 4 data. Compares with the previous report, identifies trends,
  tracks action items, and produces a full Traditional Chinese report. Use when user says
  "generate SEO report", "weekly SEO report", "seo-report-generation", or "create SEO report".
user_invocable: true
metadata:
  author: TePe Blog
  tags:
    - seo
    - analytics
    - gsc
    - ga4
    - report
  triggers:
    - "generate SEO report"
    - "weekly SEO report"
    - "create SEO report"
    - "seo report"
---

# SEO Report Generation — Weekly tepetw.com Performance Report

Generates a comprehensive weekly SEO report by pulling data from Google Search Console (GSC) and Google Analytics 4 (GA4), comparing with the previous week's report, and producing a structured analysis in Traditional Chinese.

## When to Use This Skill

- Weekly SEO reporting cadence (every Friday or as needed)
- When the user asks for a new SEO report or performance analysis
- When comparing current vs previous period SEO metrics

## How to Use

```
/seo-report-generation
```

The report will be created at `seo/YYYY-MM-DD-weekly-seo-report.md` using today's date.

## Configuration

| Setting | Value |
|---------|-------|
| GSC Site | `sc-domain:tepetw.com` |
| GA4 Property | `properties/517199426` |
| GCP Project | `tepe-seo` |
| ADC Scopes | `cloud-platform`, `webmasters`, `webmasters.readonly`, `analytics.readonly` |
| GSC Data Lag | 3 days |
| GA4 Data Lag | 1 day |
| Default Window | 90 days |
| Report Language | Traditional Chinese (繁體中文) |

## Instructions

### Step 1: Verify Authentication

Run a quick GSC test to confirm Application Default Credentials (ADC) are valid:

```bash
uv run tools/seo_report.py --gsc-only --days 7
```

If this fails with authentication errors, ask the user to re-authenticate:

```bash
gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/webmasters,https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/analytics.readonly" \
  --project=tepe-seo
```

**Do NOT proceed until auth is confirmed working.**

### Step 2: Gather Primary Data

Run these commands **in parallel** to collect the main datasets:

| Command | Purpose |
|---------|---------|
| `uv run tools/seo_report.py --days 90` | Full 90-day GSC + GA4 data |
| `uv run tools/seo_report.py --days 7` | Last 7 days for recent trends |
| `uv run tools/manage_sitemap.py --list` | Current sitemap status |
| `uv run tools/update_collection_seo.py --list` | Collection SEO titles |

The `seo_report.py` output includes:
- **GSC**: Top 30 queries, top 20 pages, device breakdown, CTR opportunities (top 15)
- **GA4**: Overall summary (sessions, users, views, duration, bounce rate), top 20 pages, traffic sources

### Step 3: Gather GSC Supplementary Data

The `seo_report.py` tool does NOT provide country breakdown, monthly trends, or 90-day totals. Run this inline Python script to get them:

```python
cat << 'PYEOF' | uv run --with google-auth --with google-api-python-client --with rich -
import google.auth
from googleapiclient.discovery import build
from datetime import date, timedelta
from rich.console import Console
from rich.table import Table

console = Console()
creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
gsc = build("searchconsole", "v1", credentials=creds)
site = "sc-domain:tepetw.com"
end = date.today() - timedelta(days=3)
start = end - timedelta(days=89)

# Country Breakdown
resp = gsc.searchanalytics().query(siteUrl=site, body={
    "startDate": start.isoformat(), "endDate": end.isoformat(),
    "dimensions": ["country"], "type": "web", "rowLimit": 10,
}).execute()

t = Table(title=f"GSC Country Breakdown ({start} → {end})")
t.add_column("Country"); t.add_column("Clicks", justify="right")
t.add_column("Impressions", justify="right"); t.add_column("CTR", justify="right")
t.add_column("Position", justify="right")
total_clicks = sum(r["clicks"] for r in resp.get("rows", []))
for r in resp.get("rows", []):
    c = r["clicks"]; i = r["impressions"]; pct = c / total_clicks * 100 if total_clicks else 0
    t.add_row(r["keys"][0], f"{c:,} ({pct:.1f}%)", f"{i:,}", f"{r['ctr']*100:.1f}%", f"{r['position']:.1f}")
console.print(t)

# Monthly Trends
months = []
for y, m, label in [(2025,12,"2025/12"), (2026,1,"2026/01"), (2026,2,"2026/02"), (2026,3,"2026/03"),
                      (2026,4,"2026/04"), (2026,5,"2026/05"), (2026,6,"2026/06")]:
    ms = max(start, date(y, m, 1))
    me = date(y, m+1, 1) - timedelta(days=1) if m < 12 else date(y, 12, 31)
    me = min(me, end)
    if ms <= end and ms <= me:
        months.append((label, ms, me))

t2 = Table(title="GSC Monthly Trends")
t2.add_column("Month"); t2.add_column("Period"); t2.add_column("Clicks", justify="right")
t2.add_column("Impressions", justify="right"); t2.add_column("CTR", justify="right")
t2.add_column("Avg Position", justify="right")
for label, ms, me in months:
    resp = gsc.searchanalytics().query(siteUrl=site, body={
        "startDate": ms.isoformat(), "endDate": me.isoformat(), "type": "web",
    }).execute()
    rows = resp.get("rows", [{}])
    if rows:
        r = rows[0]
        t2.add_row(label, f"{ms} ~ {me}", f"{r['clicks']:,}", f"{r['impressions']:,}",
                   f"{r['ctr']*100:.1f}%", f"{r['position']:.1f}")
console.print(t2)

# Totals
resp = gsc.searchanalytics().query(siteUrl=site, body={
    "startDate": start.isoformat(), "endDate": end.isoformat(), "type": "web",
}).execute()
r = resp.get("rows", [{}])[0]
console.print(f"\n[bold]GSC Totals ({start} → {end}):[/bold]")
console.print(f"  Clicks: {r['clicks']:,}  Impressions: {r['impressions']:,}  CTR: {r['ctr']*100:.1f}%  Avg Position: {r['position']:.1f}")
PYEOF
```

### Step 4: Gather GA4 Supplementary Data

The `seo_report.py` tool does NOT provide GA4 monthly trends or per-page bounce rate. Run this:

```python
cat << 'PYEOF' | uv run --with google-auth --with google-analytics-data --with rich -
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, DateRange, Dimension, Metric, OrderBy
)
from datetime import date, timedelta
from rich.console import Console
from rich.table import Table

console = Console()
client = BetaAnalyticsDataClient()
property_id = "properties/517199426"
end = (date.today() - timedelta(days=1)).isoformat()
start = (date.today() - timedelta(days=90)).isoformat()

# Monthly Trends
resp = client.run_report(RunReportRequest(
    property=property_id,
    date_ranges=[DateRange(start_date=start, end_date=end)],
    dimensions=[Dimension(name="yearMonth")],
    metrics=[Metric(name="sessions"), Metric(name="totalUsers"), Metric(name="screenPageViews")],
    order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="yearMonth"))],
))
t = Table(title=f"GA4 Monthly Trends ({start} → {end})")
t.add_column("Month"); t.add_column("Sessions", justify="right")
t.add_column("Users", justify="right"); t.add_column("Page Views", justify="right")
for row in resp.rows:
    ym = row.dimension_values[0].value
    t.add_row(f"{ym[:4]}/{ym[4:]}", f"{int(row.metric_values[0].value):,}",
              f"{int(row.metric_values[1].value):,}", f"{int(row.metric_values[2].value):,}")
console.print(t)

# Top Landing Pages with bounce rate
resp2 = client.run_report(RunReportRequest(
    property=property_id,
    date_ranges=[DateRange(start_date=start, end_date=end)],
    dimensions=[Dimension(name="landingPage")],
    metrics=[Metric(name="sessions"), Metric(name="bounceRate"), Metric(name="averageSessionDuration")],
    order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
    limit=15,
))
t2 = Table(title=f"GA4 Top Landing Pages ({start} → {end})")
t2.add_column("#"); t2.add_column("Page"); t2.add_column("Sessions", justify="right")
t2.add_column("Bounce Rate", justify="right"); t2.add_column("Avg Duration (s)", justify="right")
for i, row in enumerate(resp2.rows, 1):
    t2.add_row(str(i), row.dimension_values[0].value, f"{int(row.metric_values[0].value):,}",
               f"{float(row.metric_values[1].value)*100:.1f}%", f"{float(row.metric_values[2].value):.0f}")
console.print(t2)
PYEOF
```

### Step 5: Read Previous Report

Find the most recent report in `seo/` and extract baseline metrics for comparison:

```bash
ls -t seo/*weekly-seo-report.md | head -1
```

Read the full report. Extract these key baseline values:

| Metric | Where to Find |
|--------|---------------|
| GSC Total Clicks | Section 一 → 搜尋表現 table |
| GSC Total Impressions | Section 一 → 搜尋表現 table |
| GSC Avg CTR | Section 一 → 搜尋表現 table |
| GSC Avg Position | Section 一 → 搜尋表現 table |
| GA4 Sessions | Section 一 → 網站流量 table |
| GA4 Users | Section 一 → 網站流量 table |
| GA4 Page Views | Section 一 → 網站流量 table |
| GA4 Bounce Rate | Section 一 → 網站流量 table |
| GA4 Avg Duration | Section 一 → 網站流量 table |
| Organic Search Sessions | Section 一 → 流量來源 table |

Also read the previous report's **行動計畫** (action plan) section to track progress on each item.

**Important**: Both reports use 90-day rolling windows shifted by ~7 days, so they share ~83 overlapping days. Deltas will be muted. Focus analysis on the latest month's data for genuine recent trends. Project the current month's partial data to full-month estimates (daily average × days in month).

### Step 6: Analyze and Compare

For each metric, calculate:
- Absolute change: `new - old`
- Percentage change: `(new - old) / old × 100%`

Identify:
- **Improving trends**: metrics moving in the right direction
- **Concerning trends**: metrics deteriorating
- **Breakthroughs**: keywords or pages with sudden jumps
- **New CTR opportunities**: high impression + low CTR keywords from the CTR opportunities table
- **Action item progress**: check each item from the previous report's action plan

For action item verification, use these techniques:
- **301 redirects**: `curl -sI https://www.tepetw.com/<path>` — check for 301 status
- **GA4 tracking**: `curl -s https://tepetw.com/<page> | grep -c "G-JY2RZHXP2H"` — should be ≥1
- **Article SEO fields**: Use Shopify REST API via `tools/publish_to_shopify.py` auth pattern
- **Sitemap**: Already checked in Step 2 via `manage_sitemap.py --list`
- **Collection SEO**: Already checked in Step 2 via `update_collection_seo.py --list`

### Step 7: Write the Report

Create `seo/YYYY-MM-DD-weekly-seo-report.md` (using today's date) with this exact structure:

```markdown
# tepetw.com SEO 週報

**報告日期**: YYYY-MM-DD
**資料期間**: YYYY-MM-DD ~ YYYY-MM-DD（90 天）
**資料來源**: Google Search Console + Google Analytics 4

---

## 一、現況總覽

### 搜尋表現（GSC）
[Table with columns: 指標 | 上週 | 本週 | 變化]
[Metrics: 總點擊, 總曝光, 平均 CTR, 平均排名]

#### 裝置分佈
[Table: 裝置 | 點擊 | 曝光 | CTR | 平均排名]
[Rows: Mobile, Desktop, Tablet with percentages]

#### 地區分佈
[Table: 地區 | 點擊 | 佔比 | 曝光 | CTR]
[Map country codes: twn→台灣, hkg→香港, mac→澳門, jpn→日本, mys→馬來西亞, usa→美國]

#### 月趨勢
[Table: 月份 | 點擊 | 曝光 | CTR | 平均排名]
[Include analysis blockquote with monthly projection for current partial month]

### 網站流量（GA4）
[Table with columns: 指標 | 上週 | 本週 | 變化]
[Metrics: Sessions, 總使用者, 新使用者, 頁面瀏覽, 平均停留時間, 跳出率]

#### 流量來源
[Table: 管道 | Sessions | 佔比 | Users | 頁面瀏覽]

#### GA4 月趨勢
[Table: 月份 | Sessions | Users | 頁面瀏覽]

---

## 二、核心 SEO 問題
[Numbered list of issues, each with:]
[- Status indicator: 已解決 ✅ / 改善中 / 重要 / 嚴重 / 緊急]
[- **現況更新** with data evidence]
[- Retain unresolved issues from previous report, mark resolved ones]
[- Add any NEW issues discovered in this week's data]

---

## 三、行動計畫
### 緊急（本週內）
### 短期（2 週內）
### 中期（1-2 個月）
[Mark completed items with ~~strikethrough~~ ✅]
[Add new items based on current data]

---

## 四、表現最佳內容
### Top 5 搜尋關鍵字（品牌）
[Table: 關鍵字 | 點擊 | 曝光 | CTR | 排名 | vs 上週]

### Top 5 搜尋關鍵字（非品牌）
[Table: 關鍵字 | 點擊 | 曝光 | CTR | 排名 | vs 上週]

### 最佳登陸頁（GA4）
[Table: 頁面 | Sessions | 跳出率 | 平均停留]

---

## 五、上週行動追蹤
[Table: 行動項目 | 狀態 | 說明]
[Status values: ✅ 已完成 / ⏳ 進行中 / ❌ 未開始]

---

## 六、下週追蹤重點
[Checkbox list of items to monitor next week]
```

**Writing guidelines:**
- All narrative in Traditional Chinese (繁體中文); technical terms in English are OK
- Analysis blockquotes (`>`) should provide **actionable insights**, not just restate numbers
- Include "vs 上週" column in keyword tables to show week-over-week changes
- For partial months, calculate daily average and project full-month estimate
- Country codes from GSC API: map `twn`→台灣, `hkg`→香港, `mac`→澳門, `jpn`→日本, `mys`→馬來西亞, `usa`→美國

### Step 8: Commit

```bash
git add seo/YYYY-MM-DD-weekly-seo-report.md
git commit -m "add weekly SEO report for YYYY-MM-DD"
```

## Important Notes

- **GSC data lag**: GSC data has a 3-day lag. The end date should be `today - 3 days`.
- **GA4 data lag**: GA4 has a 1-day lag. The end date should be `today - 1 day`.
- **Rolling window overlap**: Consecutive 90-day reports share ~83 overlapping days. Focus on the latest month's data for genuine week-over-week insight rather than the 90-day totals.
- **GA4 tracking outage**: GA4 tracking was broken in Feb 2026 (7 sessions total). This data is permanently lost. If Feb data appears abnormal, this is the cause.
- **Old site URLs**: `www.tepetw.com` URLs still appear in 90-day GSC data but are 301-redirected. They will naturally age out of the rolling window.
- **Article SEO fields**: Shopify GraphQL does NOT support SEO fields on articles. Use REST API with `metafields_global_title_tag` and `metafields_global_description_tag`. See `tools/publish_to_shopify.py` line 219-230 for the pattern.
- **Report naming**: `seo/YYYY-MM-DD-weekly-seo-report.md` — always use the report creation date, not the data end date.
