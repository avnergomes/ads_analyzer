# Ads Performance Analyzer v4.1 🎭

Integrated analytics system for Meta (Facebook/Instagram) ads and ticket sales performance.

![Version](https://img.shields.io/badge/version-4.1-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🆕 What's New in v4.1

### ✅ Bug Fixes
- **Critical error fixed**: `ValueError` on line 823 (render_show_health)
- Robust handling of `None` and `NaN` values in all metrics
- Better handling of missing data

### 🚀 New Features
- **Data Mapper**: Complete Sales ↔ Ads mapping system
- **Quality Validation**: Automatic data quality reports
- **Advanced Integration**: Intelligent merge of multiple data sources
- **Data Export**: Download integrated data as CSV
- **Smart Matching**: Multiple campaign naming pattern support

### 🎯 Improvements
- Visual health indicators for shows (gauges)
- More intuitive dashboard
- Optimized performance
- Complete documentation

---

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Data Structure](#data-structure)
- [Features](#features)
- [Campaign Naming](#campaign-naming)
- [Applying Fixes](#applying-fixes)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)

---

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/avnergomes/ads_analyzer.git
cd ads_analyzer/optimization_v4
```

### 2. Install dependencies
```bash
pip install -r requirements-file.txt
```

### 3. Run the application
```bash
streamlit run optimized-ads-analyzer.py
```

---

## ⚡ Quick Start

### Step 1: Prepare your data

**Sales Data (Google Sheets)**
- Configure the public sheet link in `public_sheets_connector.py`
- Ensure you have columns: `show_id`, `city`, `show_date`, `capacity`, `total_sold`

**Ads Data (Meta Ads)**
- Export 3 reports from Meta Ads Manager:
  1. `Days.csv` - Main report
  2. `Days + Placement + Device.csv` - By platform/device
  3. `Days + Time.csv` - By time of day

### Step 2: Run and upload

```bash
streamlit run optimized-ads-analyzer.py
```

1. Sales spreadsheet loads automatically
2. Use sidebar to upload the 3 Ads CSVs
3. Navigate through tabs to view analyses

### Step 3: Analyze

- **Show Health**: Visual indicators and metrics for each show
- **Ticket Sales**: Sales analysis by city and occupancy
- **Advertising**: Campaign performance and metrics
- **Integration**: Integrated analysis and correlations

---

## 📊 Data Structure

### Ads CSVs (Meta)

#### A) Days.csv
```csv
Reporting starts,Reporting ends,Campaign name,Amount spent (USD),Impressions,Link clicks,Results,...
2024-09-01,2024-09-02,WDC_0927_S2,1250.50,45000,850,45,...
```

**Required columns:**
- Reporting starts / Reporting ends
- Campaign name (CRITICAL for matching)
- Amount spent (USD)
- Impressions
- Link clicks
- CPM, CTR, Reach, Frequency, Results

#### B) Days + Placement + Device.csv
Additional dimensions:
- Platform (Facebook, Instagram, etc.)
- Placement (Feed, Stories, etc.)
- Device platform (Mobile, Desktop)
- Impression device

#### C) Days + Time.csv
Additional dimension:
- Time of day (viewer's time zone)

### Sales Spreadsheet (Google Sheets)

**Required columns:**
```
show_id | city | show_date | capacity | total_sold | remaining | sales_to_date | report_date
WDC_0927_S2 | Washington DC | 2024-09-27 | 5000 | 4250 | 750 | 425000.00 | 2024-09-15
```

**Optional but recommended:**
- occupancy_rate, avg_ticket_price, today_sold
- avg_sales_last_7_days, days_to_show
- show_sequence

---

## 🎯 Campaign Naming

### Critical for Matching!

Campaign names must follow one of these patterns:

#### ✅ Recommended Pattern
```
{CITY_CODE}_{DATE}_{SEQUENCE}
```

**Examples:**
- `WDC_0927_S2` → Washington DC, show 0927, sequence 2
- `NYC_1015_S1` → New York City, show 1015, sequence 1
- `LAX_0801` → Los Angeles, show 0801 (sequence 1 implicit)

#### ✅ Alternative Patterns

1. **Legacy Format**
   ```
   US-{CITY}-Sales-{DATE}
   ```
   Example: `US-WDC-Sales-0927`

2. **City Name Format**
   ```
   {CityName}_{DATE}
   ```
   Example: `WashingtonDC_0927`

3. **Tour Format**
   ```
   Tour_{CityName}_{NUM}
   ```
   Example: `Tour_Washington_27`

4. **Extended Format**
   ```
   {CITY}-Sales-{DATE}-{SEQUENCE}
   ```
   Example: `WDC-Sales-0927-S2`

---

## 🔧 Applying Fixes

### Automatic (Recommended)

```bash
cd optimization_v4
python apply_fixes.py
```

The script will:
1. Create a backup of the original file
2. Apply all corrections automatically
3. Add new Data Mapper functionality
4. Update imports and functions

### Manual

Follow the detailed instructions in `PATCH_INSTRUCTIONS.txt`:
1. Add imports
2. Update `render_show_health` function
3. Replace `latest.get()` calls
4. Add Data Mapper section

---

## 📚 Features

### 🩺 Show Health Dashboard

**Visual Indicators:**
- Occupancy gauge
- Sales pace gauge
- Funnel efficiency gauge
- Days countdown
- ROAS indicator

**Key Metrics:**
- Total capacity & remaining tickets
- Tickets sold & daily sales
- Revenue & average ticket price
- Daily target vs actual performance

**Budget Analysis:**
- Ticket cost calculation
- Cost Per Acquisition (CPA)
- Total ad spend tracking
- ROAS computation

**Performance Trends:**
- Revenue & tickets trajectory
- Daily sales pattern
- 7-day performance rhythm
- Conversion funnel visualization

### 🎫 Ticket Sales Overview

- Active shows summary
- City performance ranking
- Occupancy distribution
- Revenue by market
- Sales trends over time

### 📈 Advertising Performance

- Campaign spend tracking
- Impressions & reach analysis
- Click performance
- Cost metrics (CPC, CPM, CPA)
- Conversion tracking

### 🔗 Integration Analysis

**Correlations:**
- Spend vs Tickets Sold
- Clicks vs Revenue
- Impressions vs Sales

**Metrics:**
- ROAS by show
- CPA by campaign
- Click-to-purchase rate
- Funnel efficiency

### 🔍 Data Mapping & Quality

**Quality Validation:**
- Required fields check
- Missing values analysis
- Data type validation
- Format verification

**Integration:**
- Smart show matching
- Multi-source data merge
- Calculated metrics
- Export functionality

---

## 📖 Documentation

### Main Files

- `optimized-ads-analyzer.py` - Main Streamlit application
- `data_mapper.py` - Data mapping and integration module
- `public_sheets_connector.py` - Google Sheets connector
- `USAGE_GUIDE.txt` - Comprehensive usage guide
- `PATCH_INSTRUCTIONS.txt` - Manual fix instructions
- `apply_fixes.py` - Automatic fix application script

### Key Classes

#### `AdsDataProcessor`
Handles ad data ingestion, normalization, and enrichment.

```python
processor = AdsDataProcessor()
data_by_type, funnel_summary = processor.process_ads_files(
    uploaded_files, sales_df
)
```

#### `DataMapper`
Maps and integrates Sales and Ads data.

```python
mapper = DataMapper()
integrated_df, stats = integrate_sales_and_ads_data(
    sales_df, ads_days_df, ads_placement_df, ads_time_df
)
```

#### `IntegratedDashboard`
Renders all dashboard components.

```python
dashboard = IntegratedDashboard()
dashboard.render_show_health(sales_data, funnel_summary)
```

---

## 🐛 Troubleshooting

### Error: "ValueError on line 823"

**Cause:** Missing or invalid data in sales spreadsheet
**Solution:** Apply fixes from this repository (already included)

### Error: "No shows matched"

**Cause:** Campaign names don't follow expected patterns
**Solutions:**
1. Check campaign naming (see [Campaign Naming](#campaign-naming))
2. Verify show_id format in sales spreadsheet
3. Use Data Mapper validation to identify issues

### Error: "Missing required columns"

**Cause:** CSV doesn't have all required columns
**Solution:**
1. Check CSV export settings in Meta Ads Manager
2. Compare with required columns list above
3. Use quality validation tool in the app

### Low or Zero ROAS

**Causes:**
- Incorrect revenue data
- Missing sales data
- Duplicate ad data
- Wrong currency (should be USD)

**Solutions:**
1. Validate data quality using built-in tool
2. Check for data duplication
3. Verify sales spreadsheet is up-to-date
4. Review integrated data export for anomalies

---

## 🔍 API Reference

### DataMapper

#### `normalize_csv_data(df, csv_type)`
Normalizes CSV data according to type.

```python
df_normalized = mapper.normalize_csv_data(df, csv_type='days')
```

**Parameters:**
- `df`: DataFrame to normalize
- `csv_type`: One of 'days', 'days_placement_device', 'days_time'

**Returns:** Normalized DataFrame

#### `extract_show_id_from_campaign(campaign_name, sales_df)`
Extracts show_id from campaign name.

```python
show_id = mapper.extract_show_id_from_campaign(
    "US-WDC-Sales-0927", sales_df
)
```

**Parameters:**
- `campaign_name`: Campaign name string
- `sales_df`: Sales DataFrame (optional, for validation)

**Returns:** show_id string or None

#### `merge_sales_and_ads(sales_df, ads_df, how)`
Merges sales and ads data.

```python
merged = mapper.merge_sales_and_ads(
    sales_df, ads_df, how='left'
)
```

**Parameters:**
- `sales_df`: Sales DataFrame
- `ads_df`: Ads DataFrame (normalized)
- `how`: Merge type ('left', 'right', 'inner', 'outer')

**Returns:** Merged DataFrame with calculated metrics

#### `validate_data_quality(df, data_type)`
Validates data quality.

```python
report = mapper.validate_data_quality(df, data_type='ads')
```

**Parameters:**
- `df`: DataFrame to validate
- `data_type`: Either 'sales' or 'ads'

**Returns:** Dictionary with quality metrics

### Utility Functions

#### `safe_numeric(value, default=0)`
Safely converts value to numeric.

```python
from data_mapper import safe_numeric
result = safe_numeric(value, default=0)
```

#### `integrate_sales_and_ads_data(...)`
High-level integration function.

```python
integrated_df, stats = integrate_sales_and_ads_data(
    sales_df=sales_df,
    ads_days_df=ads_days_df,
    ads_placement_df=ads_placement_df,
    ads_time_df=ads_time_df
)
```

**Returns:**
- `integrated_df`: Integrated DataFrame
- `stats`: Dictionary with integration statistics

---

## 📊 Calculated Metrics

### Ad Performance Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| CPC | spend / clicks | Cost per click |
| CPM | (spend / impressions) * 1000 | Cost per thousand impressions |
| CTR | (clicks / impressions) * 100 | Click-through rate |
| CPA | spend / results | Cost per acquisition |

### Integrated Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| ROAS | revenue / ad_spend | Return on ad spend |
| Ticket Cost | ad_spend / tickets_sold | Cost to acquire one ticket |
| Click-to-Purchase | (tickets / clicks) * 100 | Conversion rate from clicks |
| Funnel Efficiency | (purchases / clicks) * 100 | Overall funnel performance |

### Sales Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| Occupancy Rate | (total_sold / capacity) * 100 | Venue fill rate |
| Average Ticket Price | revenue / total_sold | Mean ticket price |
| Daily Target | remaining / days_to_show | Tickets needed per day |

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👤 Author

**Avner Gomes**
- GitHub: [@avnergomes](https://github.com/avnergomes)

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Charts powered by [Plotly](https://plotly.com/)
- Data processing with [Pandas](https://pandas.pydata.org/)

---

## 📞 Support

For issues, questions, or suggestions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review `USAGE_GUIDE.txt` for detailed instructions
3. Open an issue on GitHub
4. Check existing issues for similar problems

---

**Version:** 4.1  
**Last Updated:** September 2025  
**Status:** Production Ready ✅
