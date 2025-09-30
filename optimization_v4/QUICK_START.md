# 🚀 QUICK START GUIDE - Ads Performance Analyzer v4.1

Get up and running in 5 minutes!

---

## ⚡ Super Quick Start (30 seconds)

```bash
cd optimization_v4
python apply_fixes.py
streamlit run optimized-ads-analyzer.py
```

Done! The app is now running at http://localhost:8501

---

## 📋 Prerequisites

✅ Python 3.8 or higher  
✅ pip (Python package manager)  
✅ Internet connection (for first-time setup)  

---

## 🎯 5-Minute Setup

### Step 1: Install (1 minute)

```bash
# Navigate to project
cd ads_analyzer/optimization_v4

# Install dependencies
pip install -r requirements-file.txt
```

### Step 2: Apply Fixes (30 seconds)

```bash
# Run automatic fix script
python apply_fixes.py
```

**Output should be:**
```
✅ Backup created
✅ Fixes applied
✅ All tests passed
```

### Step 3: Configure Sales Data (1 minute)

Edit `public_sheets_connector.py`:

```python
SHEET_URL = "your-google-sheets-public-url-here"
```

### Step 4: Run (30 seconds)

```bash
streamlit run optimized-ads-analyzer.py
```

App opens automatically at http://localhost:8501

### Step 5: Upload Data (2 minutes)

1. **Sales data loads automatically** ✅
2. Click "📤 Upload Ad Reports" in sidebar
3. Upload 3 CSV files:
   - Days.csv
   - Days_Placement_Device.csv
   - Days_Time.csv
4. **Done!** See your integrated analytics

---

## 📊 What You'll See

### Main Tabs

| Tab | What It Shows |
|-----|---------------|
| 🩺 **Show Health** | Visual indicators, metrics, trends per show |
| 🎫 **Ticket Sales** | Sales overview, city performance, occupancy |
| 📈 **Advertising** | Ad performance, spend, clicks, conversions |
| 🔗 **Integration** | Combined analysis, ROAS, correlations |

### Key Features

✅ **Visual Health Indicators**
- Occupancy gauge
- Sales pace meter
- Funnel efficiency
- Days countdown
- ROAS display

✅ **Smart Matching**
- Automatic campaign ↔ show matching
- Multiple naming pattern support
- Match rate statistics

✅ **Quality Validation**
- Data quality reports
- Missing values detection
- Field validation

✅ **Data Export**
- Download integrated data
- CSV format ready for Excel/Power BI

---

## 🎬 First Use Walkthrough

### 1. Check Sales Data (5 seconds)

Sidebar shows:
```
✅ 50 shows loaded
```

If you see ❌ instead, check your Google Sheets URL.

### 2. Upload Ads Data (30 seconds)

In sidebar:
1. Click "📤 Upload Ad Reports"
2. Select all 3 CSV files
3. Wait for "✅ Processed 3 report types"

### 3. Navigate to Show Health (10 seconds)

Click the **🩺 Show Health** tab at the top.

### 4. Select a Show (5 seconds)

Use the dropdown to select any show, e.g., "WDC_0927_S2"

### 5. Explore Metrics (2 minutes)

You'll see:
- 5 visual gauges at the top
- Key metrics (capacity, sold, revenue)
- Budget analysis
- Funnel performance
- 3 tabs with detailed charts

### 6. Try Data Mapping (1 minute)

Scroll to bottom and expand **🔗 Data Mapping - Quality and Integration**

Click **"Run Advanced Integration"** to see:
- Match statistics
- Data quality report
- Integrated data preview
- Download button

---

## 🎨 Campaign Naming Quick Reference

For auto-matching to work, name your campaigns like:

### ✅ Good Examples

```
WDC_0927_S2          ← Best: Clear and standard
NYC_1015_S1          ← Best: Easy to parse
US-WDC-Sales-0927    ← Good: Legacy format
WashingtonDC_0927    ← OK: City name
Tour_Chicago_27      ← OK: Tour format
```

### ❌ Bad Examples

```
Washington Show      ← No date
Show 27              ← No city code
Campaign 123         ← No identifiable pattern
Test Ad              ← Not descriptive
```

**Pattern:** `{CITY_CODE}_{DATE}_{SEQUENCE}`

---

## 🔍 Quick Troubleshooting

### Problem: App won't start

```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements-file.txt --force-reinstall
```

### Problem: Sales data not loading

1. Check `public_sheets_connector.py` has correct URL
2. Ensure Google Sheet is public
3. Verify sheet has required columns:
   - show_id, city, show_date, capacity, total_sold

### Problem: No shows matched

1. Check campaign names follow pattern
2. Compare campaign name with show_id in sales sheet
3. Use Data Mapper validation to identify issues

### Problem: Error on line 823

This is the bug we fixed! If you still see it:
```bash
# Run fix script again
python apply_fixes.py
```

---

## 💡 Pro Tips

### Tip 1: Use Consistent Naming
Keep campaign names consistent: `CITY_DATE_SEQ`

### Tip 2: Export Data Regularly
Download integrated data weekly for backups

### Tip 3: Check Quality First
Always run data validation before trusting results

### Tip 4: Monitor Match Rate
Aim for 95%+ match rate between sales and ads

### Tip 5: Document Custom Patterns
If you use custom naming, document it in comments

---

## 📚 Next Steps

### Learn More

1. **Read README.md** - Complete documentation
2. **Check USAGE_GUIDE.txt** - Detailed instructions
3. **Try EXAMPLES.py** - 11 code examples
4. **Review CHANGELOG.md** - What's new

### Customize

1. Modify campaign patterns in `data_mapper.py`
2. Adjust visual thresholds in dashboard
3. Add custom metrics
4. Create new visualizations

### Integrate

1. Connect to your database
2. Set up automated exports
3. Schedule daily refreshes
4. Create custom reports

---

## 🎯 Common Use Cases

### Use Case 1: Daily Check
**Time:** 2 minutes
1. Open app
2. Go to Show Health
3. Check gauges for each show
4. Review any red/yellow indicators

### Use Case 2: Weekly Report
**Time:** 10 minutes
1. Run Advanced Integration
2. Download integrated data
3. Create Excel pivot tables
4. Share with team

### Use Case 3: Campaign Optimization
**Time:** 15 minutes
1. Review Advertising tab
2. Check CPA and ROAS by show
3. Identify underperforming campaigns
4. Adjust budgets accordingly

### Use Case 4: Budget Planning
**Time:** 20 minutes
1. Export integrated data
2. Calculate average ticket cost
3. Project ROI for new shows
4. Set budget recommendations

---

## 🚀 Ready to Scale?

### For Teams

1. Deploy to Streamlit Cloud (free)
2. Share link with team members
3. Set up automated data refresh
4. Create role-based views

### For Production

1. Move to dedicated server
2. Set up database backend
3. Implement user authentication
4. Add API endpoints

### For Enterprise

1. Multi-tenant deployment
2. Advanced security
3. Custom integrations
4. SLA support

---

## ✅ Success Checklist

After setup, you should be able to:

- [ ] Start app without errors
- [ ] See sales data loaded automatically
- [ ] Upload 3 CSV files successfully
- [ ] View Show Health dashboard
- [ ] See visual gauges working
- [ ] Select different shows
- [ ] View all metrics correctly
- [ ] Run Data Mapping integration
- [ ] Download integrated data
- [ ] See match rate > 80%

If all checked, you're good to go! 🎉

---

## 📞 Need Help?

### Quick Answers
- **Installation issues**: Check Python version and dependencies
- **Data not matching**: Review campaign naming
- **Export not working**: Check write permissions
- **Slow performance**: Reduce data size or upgrade hardware

### Documentation
- README.md - Full docs
- USAGE_GUIDE.txt - Detailed guide
- EXAMPLES.py - Code examples
- GitHub Issues - Report bugs

---

## 🎊 You're All Set!

The Ads Performance Analyzer is now ready to help you:
- ✅ Track show performance in real-time
- ✅ Optimize ad spend
- ✅ Predict ticket sales
- ✅ Make data-driven decisions

**Happy analyzing!** 📊🎭

---

**Version:** 4.1.0  
**Last Updated:** September 30, 2025  
**Support:** Check README.md or open GitHub issue

---

*P.S. Star the repo if you find this useful! ⭐*
