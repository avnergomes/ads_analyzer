# 📁 Project Structure – Ads Analyzer v2.0

```
ads_analyzer/v2/
│
├── app.py                        # Streamlit application and dashboards
├── public_sheets_connector.py    # Ticket sheet parsing and enrichment
├── requirements.txt              # Python dependencies
│
├── documentation
│   ├── README.md                 # Product overview
│   ├── QUICKSTART.md             # Fast setup guide
│   ├── INDEX.md                  # Documentation index
│   ├── EXAMPLES.md               # Analytical walkthroughs
│   ├── TROUBLESHOOTING.md        # Issue resolution
│   ├── DEPLOYMENT.md             # Hosting instructions
│   ├── PROJECT_STRUCTURE.md      # (this file)
│   └── CHANGELOG.md              # Release history
│
├── utilities
│   ├── validate_csv.py           # Meta CSV schema validator
│   └── test_installation.py      # Dependency smoke test
│
├── .streamlit/
│   ├── config.toml               # Optional Streamlit theming
│   └── secrets.toml.example      # Template for credentials
│
└── sample/
    ├── Days.csv                  # Meta "Days" export example
    ├── Days + Placement + Device.csv
    └── Days + Time.csv
```

## 🔑 Key files

### `app.py`
- Main Streamlit entry point.
- Coordinates file uploads, state management, and interactive visualisations.
- Houses:
  - `AdsDataProcessor` – Normalises Meta exports, calculates missing KPIs, and enriches with ticket show IDs.
  - `IntegratedDashboard` – Renders KPI summaries, charts, and tables.
  - `FunnelSummary` – Lightweight data class for per-show funnel metrics.

### `public_sheets_connector.py`
- Parses the ticket sales CSV exported from the shared sheet or the live Google Sheet.
- Stops reading at the `endRow` marker to avoid footer noise.
- Normalises currencies and converts revenue into USD.
- Adds pacing indicators: daily sales targets, seven-day rolling sales, and performance categories.

### `requirements.txt`
- Captures the Python dependencies used by the Streamlit app: `streamlit`, `pandas`, `plotly`, `numpy`, `requests`, `openpyxl`, and helpers for validation/visualisation.

### Utility scripts
- `validate_csv.py` – Command-line helper to confirm that Meta exports contain the expected columns before upload.
- `test_installation.py` – Quick import test to verify a new environment is ready to run the app.

## 🧭 Data flow overview

1. **Ticket sales upload** – Users provide the CSV export, which is parsed by `PublicSheetsConnector` and stored in `st.session_state`.
2. **Meta exports upload** – The `AdsDataProcessor` ingests the three Meta reports, harmonises the schema, and matches campaigns to shows when possible.
3. **Dashboard rendering** – `IntegratedDashboard` compiles the processed data into KPIs, funnel charts, and pacing insights, displayed across the four tabs.

## 🗂 Adding new modules

- Place Streamlit-related components alongside `app.py` or break out into a `components/` folder if the UI grows substantially.
- Keep parser logic in dedicated modules (e.g., a future `spotify_connector.py`) to isolate data access from UI code.
- Document new scripts inside `INDEX.md` and update `README.md` whenever new data inputs are supported.
