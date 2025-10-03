# Ads Analyzer – Changelog

## v2.0.2 – Google Sheet ticket sync
- Removed the ticket CSV upload workflow and now rely exclusively on the shared Google Sheet export.
- Added a sidebar refresh action and status messaging for the Google Sheet sync.
- Updated documentation to reflect the Google Sheet data source requirement.

## v2.0.1 – Ticket upload and English documentation
- Added support for uploading the ticket sales CSV through the Streamlit sidebar.
- Updated the ticket parser to accept uploaded files in addition to the live Google Sheet.
- Displayed ticket KPIs and upload status directly in the sidebar.
- Converted documentation and UI copy to English for international collaborators.

## v2.0 – Major refresh

### Data processing
- Expanded column mapping to cover 20+ naming variations across Meta exports.
- Automatic dataset detection for "Days", "Days + Placement + Device", and "Days + Time" files.
- Validation script (`validate_csv.py`) to check structure before upload.
- Automatic KPI calculation (CTR, CPC, CPM, cost per result) when missing from the export.

### Ticket sales connector
- Normalises the public sheet, stops at the `endRow` marker, and converts revenue to USD based on static FX rates.
- Derives occupancy, remaining inventory, and pacing indicators for each show.
- Matches shows to campaigns using normalised text patterns and show ID conventions.

### Application experience
- Streamlined Streamlit interface with tabs for Ticket Sales, Advertising, Integrated View, and Raw Data.
- Funnel summaries that tie Meta results to ticket sales snapshots.
- Expanded troubleshooting, deployment, and example documentation.

### Tooling
- `validate_csv.py` – Meta export validator.
- `test_installation.py` – Environment smoke test.
- Sample CSVs added for quick testing.

## v1.x – Initial releases
- Baseline Streamlit dashboard combining Meta Ads Manager exports with manual ticket spreadsheets.
- Included ROAS calculations and campaign-to-show matching heuristics.
- Established the data ingestion workflow for CSV uploads.
