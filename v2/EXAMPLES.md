# 📚 Example Workflows – Ads Analyzer v2.0

This guide outlines practical ways to explore the dashboards and interrogate your data.

## 🎯 Core use cases

### 1. Campaign performance review
- Navigate to the **Advertising** tab.
- Inspect the "Spend vs. Purchases" scatter to compare efficiency across campaigns.
- Use the hover tooltip to confirm impressions, clicks, and purchases.
- Identify outliers with high spend but low conversions and add them to an optimisation list.

### 2. Show-level budget pacing
- Open the **Ticket Sales** tab and focus on the Show Health grid.
- Enter the planned budget per show in the sidebar if you extend the app with budget inputs.
- Prioritise shows with low occupancy and high remaining capacity.
- Cross-reference daily targets with the seven-day rolling average for realistic expectations.

### 3. ROI / ROAS monitoring
- Combine the **Integrated View** scatter plots with the ticket revenue metrics.
- Filter the data table to the current month (using Streamlit filters if enabled) to track recent performance.
- Flag campaigns whose return ratio drifts below your target threshold.

### 4. Placement and device efficiency
- In the **Advertising** tab, switch to the dataset identified as "Days + Placement + Device".
- Build a pivot table (outside the app) using the exported CSV if you need deeper slicing.
- Allocate more budget to placements that yield better purchase-to-spend ratios.

### 5. Dayparting insights
- Upload the "Days + Time" dataset and check the hourly breakdown chart.
- Align ad delivery with peak sales windows discovered in the ticket cadence chart.
- Consider suppressing ads during low-conversion windows to preserve budget.

### 6. City comparison
- Use the **Ticket Sales** tab to sort the table by city (city is extracted from the show name when available).
- Export the processed CSV and filter in spreadsheets for deeper comparison.
- Map shows by city to visualise geographic saturation.

### 7. Funnel health check
- In the Show Health section, review the funnel summary for the selected show.
- Compare impressions, clicks, landing page views, and purchases.
- Investigate large drop-offs (e.g., high clicks but low add-to-cart numbers) for creative or landing page issues.

### 8. Sales forecasting back-of-the-envelope
- For shows with high remaining capacity, multiply the seven-day rolling sales by the days left to estimate final totals.
- Adjust budgets or promotions if the projection falls short of the target capacity.

### 9. Creative A/B testing recap
- Tag campaigns with identifiers such as `_A` and `_B` in the name.
- Review the scatter and time-series charts to see which variant yields better conversions at lower cost.
- Use the Raw Data tab to export and archive the results for post-mortems.

## 🔧 Advanced analysis ideas

### Bid strategy optimisation
1. Segment campaigns by bidding strategy (manual vs. automated) in the exported CSV.
2. Compare average CPC and purchase volume to determine which approach performs best per show.
3. Use the findings to refine campaign budgets and bidding caps.

### Inventory risk alerts
1. Sort the Show Health grid by "days to show" ascending.
2. Highlight shows with low occupancy and fewer than 10 days remaining.
3. Trigger promotional pushes or last-minute offers to reduce the risk of unsold seats.

## 🎓 Expert tips
- Maintain consistent naming conventions (`CITY_MMDD` or `CITY_MMDD_S#`) across campaigns and shows.
- Refresh uploads after major sales pushes or campaign changes to keep dashboards current.
- Use the download buttons in the Raw Data tab as snapshots for stakeholder reports or further modelling.
