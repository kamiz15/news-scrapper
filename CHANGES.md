# Ansu Invest Desktop App — Audit, Fixes & New Features

Full review and overhaul of the news scraper + hydropower dashboard, June 2026.

## Purpose

Work tool for hydropower market intelligence in Nepal: scrape news, research,
companies and market data from Ansu Invest, store in PostgreSQL, and present
competitor/market insight dashboards for planning a hydropower plant.

---

## Bug Fixes

### Critical

| Bug | Impact | Fix |
|---|---|---|
| Hydro keyword filter matched substrings ("mandu" → **Kathmandu**, "upper" → "supper") | Articles/companies wrongly classified as hydropower | Word-boundary regex; `hydro` kept as prefix so "hydroelectric"/"hydropower" still match |
| Launcher ran `taskkill /f /im python.exe` | Killed **every** Python process on the machine | Launcher now tree-kills only its own dashboard process (`taskkill /pid <id> /t /f`) |
| Scraper pagination only stopped on empty response | Infinite loop if API ignores `page` param | Stops when a page repeats the previous page's first ID |
| Streamlit auto-generated a dead sidebar nav from the `pages/` folder name | Broken duplicate navigation | Folder renamed to `dashboard/views/` |
| Stale `__pycache__` shadowed updated source files | `ImportError` for new functions despite correct code on disk | Caches cleared; launcher process-tree kill prevents zombie servers serving old code |

### Functional

- Category filter pagination used the total article count → "Next" led to empty pages. Now uses a per-category count.
- Pagination off-by-one (`count // per_page - 1`) made the last partial page unreachable. Now `(count - 1) // per_page`.
- `init_db` opened `database/schema.sql` relative to the current working directory → crashed when run from elsewhere. Now resolved relative to the module.
- `companies.symbol` was selected and displayed but never written. Now persisted by the scraper.
- Market snapshot chart was titled "Hydro Companies" while showing all companies. Retitled; a real hydro-filtered market view was added (see below).
- API client accepted only `success == "true"` (string); now accepts boolean `true` as well.
- Duplicate `"khola"` keyword removed from config.

### Security / Robustness

- DB credentials moved from hardcoded values to environment variables (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`) with local defaults.
- Dashboard shows a friendly error instead of a raw traceback when PostgreSQL is down.
- All SQL is parameterized (verified — no injection vectors).

---

## New Features

### Market Intelligence view
Latest market data joined to hydropower companies (matched on name): gainers/losers
metrics, top movers chart, volume leaders chart, full price table with symbol and sector.

### News Trends view
Monthly hydropower news coverage trend, most-mentioned terms in hydro headlines,
latest headlines with click-through to full articles.

### Sector Comparison view
Average % change and traded volume per sector — hydro vs the rest of the market.

### Refresh Data button
Sidebar button re-runs the full scrape with a progress bar, so data is always fresh
without returning to the desktop launcher.

### Launcher hardening
"Open Dashboard" now clears any leftover process listening on port 8501 before
starting, and Quit takes the dashboard down with it — no more zombie servers.

---

## Testing

`tests/test_units.py` — 16 unit tests covering the hydro keyword filter
(false-positive regressions like Kathmandu), HTML cleaning, image URL building,
and the pagination formula.

```
python -m pytest tests/
```

---

## Usage

```
Launch_Desktop.cmd        # desktop launcher: Fetch All Data → Open Dashboard
python run.py scrape      # CLI: full scrape
python run.py dashboard   # CLI: dashboard only
```

Requires PostgreSQL running locally with database `ansu_news` (created from
`database/schema.sql`, auto-applied by the scraper's init step).
