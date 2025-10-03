# ⚡ Quick Start – Ads Analyzer v2.0

Set up Ads Analyzer and load your first datasets in under five minutes.

## 📦 Rapid installation

### 1. Clone the repository
```bash
git clone https://github.com/avnergomes/ads_analyzer.git
cd ads_analyzer/v2
```

### 2. Create a virtual environment (recommended)

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Validate the environment
```bash
python test_installation.py
```
All checks should display ✅ when the environment is ready.

### 5. Launch the Streamlit app
```bash
streamlit run app.py
```
The browser opens at `http://localhost:8501` by default.

---

## 🎯 First run checklist

### Step 1 – Export the ticket report
Download the daily ticket tracker as a CSV file. The file should end with the `endRow` marker.

### Step 2 – Export Meta reports
From Meta Ads Manager export three datasets:
- **Days**
- **Days + Placement + Device**
- **Days + Time**

CSV exports are preferred, but Excel files are also supported.

### Step 3 – Upload files in the sidebar
1. Under **Ticket sales data**, upload the ticket tracker CSV.
2. Under **Upload Meta ad exports**, upload the three Meta reports (CSV or Excel).
3. Wait for the processing spinner to finish.

### Step 4 – Explore the dashboards
- **Ticket Sales**: KPI cards, pacing insights, show health grid, and sales cadence.
- **Advertising**: Campaign efficiency scatter, trend charts, and funnel summary.
- **Integrated View**: Correlations between ad spend, tickets sold, and revenue.
- **Raw Data**: Preview and download the processed datasets.

---

## 🔧 File validation (optional but recommended)
Before uploading, validate the Meta exports using the helper script:
```bash
python validate_csv.py Days.csv "Days + Placement + Device.csv" "Days + Time.csv"
```
The script confirms:
- ✅ Expected column headers are present
- ✅ Dataset type can be identified
- ✅ Files contain rows of data

---

## 💡 Tips

- **Campaign naming**: Include the show ID in campaign or ad set names so the app can auto-match campaigns to shows (e.g., `WDC_0927`, `NYC_1015_S2`).
- **Budget planning**: Use the Show Health panel to set a per-show budget target; the dashboard highlights pace versus the goal.
- **Currency sanity check**: If the ticket report mixes currencies, confirm the summary numbers reflect USD after upload.
- **Data refresh**: Uploading a new ticket CSV replaces the previous snapshot—use consistent filenames to keep track of versions.
