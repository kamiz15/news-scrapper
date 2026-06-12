# Ansu Invest Desktop App

Desktop application for scraping, storing, and visualizing news and research data from [Ansu Invest](https://ansuinvest.com/research-opinion), with a dedicated hydropower sector dashboard.

---

## Architecture

```
news_scrapper/
├── config.py              # API URLs, DB credentials, hydro keywords, utilities
├── run.py                 # CLI entry point
├── launcher.pyw           # Desktop GUI launcher (tkinter)
├── Launch_Desktop.cmd     # One-click launcher shortcut
├── requirements.txt       # Python dependencies
├── scraper.log            # Auto-generated log file
│
├── scraper/
│   ├── api_client.py      # HTTP client for Ansu Invest backend API
│   ├── runner.py          # Scrape orchestrator with pagination
│   ├── hydro_filter.py    # Keyword + sector matching for hydropower content
│   └── models.py          # Pydantic data models
│
├── database/
│   ├── schema.sql         # PostgreSQL table definitions
│   ├── connection.py      # Connection pool management
│   └── repository.py      # All insert/query functions
│
└── dashboard/
    ├── app.py             # Streamlit main app with sidebar navigation
    ├── components/
    │   └── charts.py      # Plotly chart functions
    └── views/
        ├── home.py             # General News with category filter + pagination
        ├── hydropower.py       # Hydropower Dashboard with charts
        ├── market_intel.py     # Hydro market intelligence (movers, volume, prices)
        ├── news_trends.py      # Hydro news coverage trends + top terms
        ├── sector_compare.py   # Hydro vs other sectors performance
        ├── research.py         # Expert Research with tabs + pagination
        ├── companies.py        # Hydropower companies list + market data
        └── article_detail.py   # Full article/report detail view
```

---

## Data Source

**Backend API:** `https://backend.ansuinvest.com/api/web/v1/`

| Endpoint | Method | Description |
|---|---|---|
| `/news/all-posts` | GET | All news articles (paginated) |
| `/research/list-expert-research` | POST | Expert research reports |
| `/news/category` | GET | News categories |
| `/news/today` | GET | Today's updates |
| `/company/company-search` | GET | All listed companies |
| `/live-market-info/stock-market` | POST | Market indicators & company data |
| `/notice/list-notice` | POST | Corporate notices |

---

## Database (PostgreSQL)

**Database name:** `ansu_news`

### Tables

| Table | Rows | Description |
|---|---|---|
| `news_articles` | ~1,000 unique | News articles with category, date, hydro flag |
| `research_reports` | ~793 | Expert research with premium flag |
| `companies` | ~393 | Listed companies with sector classification |
| `market_data` | Time-series | Stock market indicators per company |
| `categories` | 4 | News categories |

Each article/report has an `is_hydro` boolean flag set by keyword + sector matching.

---

## Hydropower Detection

Two methods combined:

1. **Keyword matching** on title + summary:
   `hydro`, `hydropower`, `jal vidyut`, `power plant`, `energy`, `dam`, `reservoir`, `run-of-river`, `sanigad`, `mandu`, etc.

2. **Company sector lookup**: companies in energy/power sectors are marked as hydro.

---

## Desktop Launcher

**File:** `Launch_Desktop.cmd` (double-click to run)

- **Fetch All Data** — scrapes all news (pagination through all pages), all research, companies, market data. Shows progress bar.
- **Open Dashboard** — launches Streamlit dashboard in browser. Kills stale Streamlit processes first.
- **View Logs** — opens `scraper.log` in Notepad.

---

## Dashboard Pages

### General News
- Category filter buttons (Markets, Stocks, etc.)
- Paginated article feed with images and previews
- "Read More" button opens full article in-app

### Expert Research
- Tabbed view: All Research / Hydropower Only
- Premium reports flagged with star
- "Read Report" opens full report detail

### Hydropower Dashboard
- KPI metrics (news count, reports, companies)
- Market snapshot bar chart (Plotly)
- News timeline bar chart
- Research topics pie chart
- Latest hydropower news with "Read" buttons
- Hydropower companies table

### Hydro Companies
- Full list of 117 hydropower companies
- Latest market data table (LTP, change, volume)

### Article/Report Detail
- Title, subtitle, image, date, category
- Full cleaned summary (HTML tags stripped, entities decoded)
- Back button returns to previous page

---

## Installation

1. Install [PostgreSQL 16+](https://www.postgresql.org/download/)
2. Create the database:
   ```sql
   CREATE DATABASE ansu_news;
   ```
3. Install Python dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Set PostgreSQL password in `config.py` if different from `postgres`
5. Run the scraper:
   ```powershell
   python run.py scrape
   ```
6. Launch dashboard:
   ```powershell
   python run.py dashboard
   ```

---

## Usage

```powershell
python run.py scrape      # Fetch all data
python run.py dashboard   # Launch dashboard
python run.py all         # Scrape + dashboard
python run.py desktop     # Launch tkinter desktop app
```

Or double-click `Launch_Desktop.cmd` for the GUI launcher.

---

## Dependencies

- `requests` — HTTP client for API
- `psycopg2-binary` — PostgreSQL driver
- `streamlit` — Dashboard framew