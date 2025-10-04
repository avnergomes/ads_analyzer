# Ads Analyzer v2.0 – Troubleshooting Guide

Use this guide to resolve the most common issues encountered when loading or analysing data.

## 🧪 Before you start
- Confirm the app is running on Streamlit `1.39` or later.
- Ensure `pandas`, `numpy`, `plotly`, and `requests` import without errors (run `python test_installation.py`).
- Compare your files with the examples in the `sample/` directory if you need a reference structure.

## ⚠️ Frequent data issues

### 1. File type not recognised
**Symptoms:** Warning stating that the file type could not be identified.

**Resolution:**
1. Verify that the file contains headers from one of the three supported Meta exports.
2. Run `python validate_csv.py <file1> <file2> <file3>` to check the schema.
3. Save the report again as CSV or Excel (UTF-8 encoding) and retry.

### 2. Missing metrics after upload
**Symptoms:** Columns such as spend or impressions appear blank.

**Resolution:**
- Confirm the column names in the export match the expected Meta headers.
- Remove extra header rows that may have been added by manual editing.
- Re-upload the original download from Meta Ads Manager without modifications.

### 3. Ticket sheet sync fails
**Symptoms:** Error message or warning after refreshing ticket sales data.

**Resolution:**
- Confirm the shared Google Sheet still exposes a public CSV export (no access restrictions added).
- Ensure the sheet content ends with the `endRow` marker; rows beneath it are ignored.
- Check that the revenue column includes a currency symbol recognised by the parser.

### 4. Show not linked to campaigns
**Symptoms:** The integrated view shows no match between ads and ticket records.

**Resolution:**
- Include the show ID (e.g., `WDC_0927`) in campaign or ad set names.
- Avoid abbreviations that drop the city or date components.
- Click **Refresh ticket sales data** to pull the latest sheet snapshot and update the show lookup table.

### 5. Memory or performance concerns
**Symptoms:** The browser becomes unresponsive when loading large CSVs.

**Resolution:**
- Split exports into smaller date ranges before downloading.
- Close other heavy browser tabs while interacting with the dashboard.
- Use the command-line validator to confirm there are no duplicate headers or corrupted rows.

### 6. Charts fail to display
**Symptoms:** Blank area where a Plotly chart should render.

**Resolution:**
- Confirm the dataset contains more than one row after filtering.
- Check your browser console for blocked scripts (ad blockers can interfere with Plotly).
- Refresh the page after clearing the Streamlit cache if you changed code locally.

## 🛠 Diagnostic tools

### CSV validator
```bash
python validate_csv.py Days.csv "Days + Placement + Device.csv" "Days + Time.csv"
```
- Detects dataset type
- Counts rows
- Confirms the presence of mandatory headers

### Manual column inspection
Use this quick checklist before reporting a bug:
- [ ] `date` column present (or a normalised equivalent)
- [ ] `spend`, `impressions`, `clicks`, `results` columns populated
- [ ] Campaign names include show identifiers
- [ ] Ticket sheet stops at `endRow`

## 🧭 Reporting an issue
When escalating a bug or support ticket, provide:
- App version (`Ads Analyzer v2.0`)
- Operating system and Python version
- Steps to reproduce
- Sample files (sanitised if necessary)
- Screenshots of the warning or error message

Keeping this information ready accelerates turnaround time and helps the development team reproduce the issue accurately.
