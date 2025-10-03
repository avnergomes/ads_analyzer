# Ads Analyzer v2.0

Ads Analyzer v2.0 is a Streamlit application that combines Meta Ads Manager exports with daily ticket sales snapshots to provide a single place to track marketing efficiency and on-sale health. Version 2.0 focuses on reliable CSV ingestion, consistent metrics, and clear visualisations for sales and advertising teams.

## ✨ Highlights in this release

- **Reliable inputs** – Normalises column names across different Meta exports, fills missing KPIs, and validates funnel metrics automatically.
- **Google Sheet sync** – Pulls the daily ticket tracker directly from the shared spreadsheet (the feed ends with the `endRow` marker) and converts all revenue into USD.
- **Currency-aware analytics** – Detects the currency prefix in the revenue column and applies static USD conversion factors for unified reporting.
- **Show-level snapshots** – Collapses the ticket feed to the latest entry per show to avoid double counting capacity, tickets sold, or revenue.
- **Integrated dashboards** – Presents side-by-side tabs for ticket performance, advertising activity, and cross-channel analysis.

## 📥 Required inputs

| Data source | Format | Notes |
|-------------|--------|-------|
| Ticket sales tracker | Google Sheet (CSV export endpoint) | Use the **Refresh ticket sales data** button to pull the latest snapshot. The parser stops at the `endRow` marker automatically. |
| Meta Ads Manager | CSV or Excel (`.csv`, `.xlsx`, `.xls`) | Upload the "Days", "Days + Placement + Device", and "Days + Time" reports. |

## 📊 Dashboards

1. **Ticket Sales** – KPIs, pacing, show health segments, and rolling sales cadence visualisations.
2. **Advertising** – Campaign level efficiency, funnel ratios, and trend charts across impressions, clicks, spend, and purchases.
3. **Integrated View** – Aligns ticket snapshots with ad activity to highlight correlations between spend, tickets sold, and revenue.
4. **Raw Data** – Quick access to preview tables and download the processed datasets.

## 🧠 How ticket parsing works

1. Only rows above the `endRow` marker are processed.
2. Currency symbols (USD, BRL, MXN, CAD, AUD, GBP, EUR, COP, CLP, ARS, PEN) are mapped to a USD exchange table.
3. Each show record is normalised: capacity, sold, revenue, wheelchair holds, and remaining inventory.
4. Latest entry per show is used for KPIs; rolling seven-day sales and daily targets are computed for pacing analysis.

## 🛠 Project structure

```
ads_analyzer/v2/
├── app.py                     # Streamlit front end and controllers
├── public_sheets_connector.py # Ticket data parser and currency utilities
├── requirements.txt           # Python dependencies
├── sample/                    # Example Meta exports (Days, Placement, Time)
├── validate_csv.py            # Helper script to validate Meta CSV files
└── docs/ (various *.md files) # Guides referenced below
```

## 🚀 Getting started

1. Install dependencies: `pip install -r requirements.txt`
2. Launch the app: `streamlit run app.py`
3. Click **Refresh ticket sales data** in the sidebar to download the latest snapshot from Google Sheets.
4. Upload the three Meta exports under "Upload Meta ad exports".
5. Explore the four dashboard tabs for insights.

## 📚 Documentation map

The following guides live in the `v2` directory:

- **[QUICKSTART.md](QUICKSTART.md)** – Installation, first-time setup, and the fastest path to loading data.
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** – File-by-file breakdown of the application.
- **[INDEX.md](INDEX.md)** – Table of contents for every guide.
- **[EXAMPLES.md](EXAMPLES.md)** – Step-by-step analytical workflows.
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** – Resolution paths for common data sync and parsing issues.
- **[DEPLOYMENT.md](DEPLOYMENT.md)** – Instructions for hosting on Streamlit Cloud, Docker, or a VPS.
- **[CHANGELOG.md](CHANGELOG.md)** – Release history.

## 🔐 Deployment tips

- Store sensitive API keys in `.streamlit/secrets.toml` if you extend the app with authenticated data sources.
- Use `streamlit run app.py --server.enableCORS=false --server.enableXsrfProtection=false` when reverse proxying behind Nginx on a VPS.
- For Fly.io deployments, containerise the app with `docker build` and ensure port `8501` is exposed.

## ✅ Verification scripts

- `python validate_csv.py Days.csv "Days + Placement + Device.csv" "Days + Time.csv"` – Checks schema compatibility before uploading Meta exports.
- `python test_installation.py` – Confirms core dependencies are installed and importable.

## 🤝 Support

If you need help adapting the dashboards to a new data source or adding bespoke KPIs, document the request inside the issue tracker so it can be prioritised for the next iteration.
