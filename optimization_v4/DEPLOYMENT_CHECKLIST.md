# 📋 DEPLOYMENT CHECKLIST - Ads Analyzer v4.1

Use this checklist to ensure successful deployment and testing.

---

## 🔧 PRE-DEPLOYMENT

### Environment Check
- [ ] Python 3.8+ installed (`python --version`)
- [ ] pip is up to date (`pip install --upgrade pip`)
- [ ] Git repository is clean (`git status`)
- [ ] No uncommitted changes

### Backup
- [ ] Backup current `optimized-ads-analyzer.py`
- [ ] Backup current database/data files
- [ ] Document current version number
- [ ] Note any custom modifications

---

## 📦 INSTALLATION

### Files Added
- [ ] `data_mapper.py` copied to optimization_v4/
- [ ] `apply_fixes.py` copied to optimization_v4/
- [ ] All documentation files present:
  - [ ] README.md
  - [ ] USAGE_GUIDE.txt
  - [ ] PATCH_INSTRUCTIONS.txt
  - [ ] QUICK_START.md
  - [ ] EXAMPLES.py
  - [ ] CHANGELOG.md
  - [ ] SUMMARY.txt

### Dependencies
- [ ] Run `pip install -r requirements-file.txt`
- [ ] All packages installed successfully
- [ ] No version conflicts
- [ ] Virtual environment activated (if using)

---

## 🔨 APPLY FIXES

### Automatic Method (Recommended)
- [ ] Navigate to `optimization_v4/` directory
- [ ] Run `python apply_fixes.py`
- [ ] Script completes without errors
- [ ] Backup file created (check for .backup file)
- [ ] Review changes in output

### Manual Method (If automatic fails)
- [ ] Open `PATCH_INSTRUCTIONS.txt`
- [ ] Follow each step carefully
- [ ] Add import statements
- [ ] Update `render_show_health()` function
- [ ] Add Data Mapper section to main()
- [ ] Save changes

---

## ✅ VERIFICATION

### File Integrity
- [ ] `data_mapper.py` exists and is readable
- [ ] `optimized-ads-analyzer.py` has been modified
- [ ] Backup file exists (.backup extension)
- [ ] No syntax errors in Python files

### Import Test
```bash
python -c "from data_mapper import DataMapper; print('✅ DataMapper imports correctly')"
```
- [ ] Import test passes

### Syntax Check
```bash
python -m py_compile optimization_v4/optimized-ads-analyzer.py
```
- [ ] No syntax errors

---

## 🚀 LAUNCH

### Start Application
```bash
streamlit run optimization_v4/optimized-ads-analyzer.py
```

- [ ] App starts without errors
- [ ] Browser opens automatically
- [ ] URL is http://localhost:8501
- [ ] No error messages in terminal

### UI Check
- [ ] Page loads completely
- [ ] Title displays: "🎭 Ads Performance Analyzer v4.0"
- [ ] Sidebar is visible
- [ ] All tabs are present:
  - [ ] 🩺 Show Health
  - [ ] 🎫 Ticket Sales
  - [ ] 📈 Advertising
  - [ ] 🔗 Integration

---

## 📊 DATA LOADING

### Sales Data
- [ ] Sales data loads automatically
- [ ] Success message appears: "✅ X shows loaded"
- [ ] No error messages
- [ ] Show count matches expected number

### Ads Data
- [ ] Upload section visible in sidebar
- [ ] Can select multiple files
- [ ] Upload 3 CSV files:
  - [ ] Days.csv
  - [ ] Days_Placement_Device.csv
  - [ ] Days_Time.csv
- [ ] Success message: "✅ Processed 3 report types"
- [ ] No error messages during processing

---

## 🧪 FUNCTIONALITY TESTING

### Show Health Tab
- [ ] Tab is clickable and loads
- [ ] Show selector dropdown appears
- [ ] Select a show from dropdown
- [ ] **CRITICAL:** No error on line 823 ✨
- [ ] Visual gauges display:
  - [ ] Occupancy gauge
  - [ ] Sales pace gauge
  - [ ] Funnel efficiency gauge
  - [ ] Days countdown
  - [ ] ROAS indicator
- [ ] Key metrics display correctly:
  - [ ] Total Capacity
  - [ ] Tickets Sold
  - [ ] Revenue
  - [ ] Daily Target
- [ ] Budget analysis section works
- [ ] Funnel performance displays
- [ ] All 3 sub-tabs work:
  - [ ] Sales Trajectory
  - [ ] Funnel Analysis
  - [ ] Daily Rhythm

### Ticket Sales Tab
- [ ] Overview metrics display
- [ ] City performance chart loads
- [ ] Occupancy distribution chart loads
- [ ] All values are reasonable
- [ ] No NaN or None values visible

### Advertising Tab
- [ ] Overview metrics display
- [ ] Campaign performance trends load
- [ ] All charts render correctly
- [ ] Data looks accurate

### Integration Tab
- [ ] Correlation charts load
- [ ] Scatter plots display
- [ ] Trendlines show (if statsmodels installed)
- [ ] Correlation matrix displays

---

## 🔍 DATA MAPPING TESTING

### Quality Validation
- [ ] Scroll to bottom of page
- [ ] "🔗 Data Mapping" expander visible
- [ ] Expand the section
- [ ] Sales data quality report shows
- [ ] Ads data quality report shows
- [ ] Quality metrics display:
  - [ ] Row count
  - [ ] Column count
  - [ ] Valid/Invalid status
- [ ] Any warnings are clear and actionable

### Advanced Integration
- [ ] Click "Run Advanced Integration" button
- [ ] Processing spinner appears
- [ ] Success message: "✅ Integration complete!"
- [ ] Statistics display:
  - [ ] Total Shows
  - [ ] Matched Shows
  - [ ] Unmatched Shows
  - [ ] Match Rate
- [ ] Match rate is > 80% (ideally > 90%)
- [ ] Data preview table displays
- [ ] Preview shows at least 20 rows
- [ ] All columns have data

### Data Export
- [ ] "📥 Download Integrated Data (CSV)" button visible
- [ ] Click download button
- [ ] CSV file downloads
- [ ] File name is "integrated_sales_ads_data.csv"
- [ ] Open file in Excel/text editor
- [ ] Data looks correct
- [ ] All expected columns present

---

## 🎯 CAMPAIGN MATCHING TEST

### Test Campaign Names
Create test campaigns with these names and verify matching:

- [ ] `WDC_0927_S2` → Matches show WDC_0927_S2
- [ ] `US-NYC-Sales-1015` → Matches show NYC_1015
- [ ] `LAX_0801` → Matches show LAX_0801
- [ ] Invalid name → Shows in unmatched

### Verify Match Quality
- [ ] Match rate displayed in UI
- [ ] Unmatched campaigns listed
- [ ] Can identify why campaigns didn't match
- [ ] Campaign name suggestions available

---

## 🐛 ERROR HANDLING

### Test Edge Cases
- [ ] Upload empty CSV → Clear error message
- [ ] Upload CSV with wrong columns → Specific error
- [ ] Missing sales data → Graceful degradation
- [ ] Select show with no data → Appropriate message
- [ ] Network interruption → Recovers gracefully

### Error Messages
- [ ] All errors are in English
- [ ] Error messages are clear
- [ ] Suggestions provided where possible
- [ ] No stack traces shown to user
- [ ] Errors logged to terminal

---

## 📊 PERFORMANCE

### Load Times
- [ ] App starts in < 5 seconds
- [ ] Sales data loads in < 3 seconds
- [ ] CSV upload processes in < 10 seconds
- [ ] Tab switching is instant
- [ ] Charts render in < 2 seconds

### Resource Usage
- [ ] CPU usage is reasonable (< 50%)
- [ ] Memory usage is stable
- [ ] No memory leaks over time
- [ ] Browser doesn't freeze

---

## 🔐 SECURITY

### Data Handling
- [ ] No sensitive data in logs
- [ ] No API keys in code
- [ ] CSV data not cached permanently
- [ ] Session data isolated per user

### File Safety
- [ ] Only processes CSV files
- [ ] No arbitrary code execution
- [ ] Safe file name handling
- [ ] Proper error handling

---

## 📱 CROSS-BROWSER TESTING

### Browsers to Test
- [ ] Chrome (recommended)
- [ ] Firefox
- [ ] Safari (if on Mac)
- [ ] Edge

### What to Check
- [ ] UI renders correctly
- [ ] Charts display properly
- [ ] File upload works
- [ ] Download works
- [ ] No console errors

---

## 📝 DOCUMENTATION REVIEW

### Files to Check
- [ ] Read README.md
- [ ] Skim QUICK_START.md
- [ ] Review USAGE_GUIDE.txt highlights
- [ ] Check EXAMPLES.py runs
- [ ] Verify CHANGELOG.md is current

### Understanding
- [ ] Know how to apply fixes
- [ ] Know campaign naming patterns
- [ ] Know where to find help
- [ ] Know how to export data
- [ ] Know troubleshooting steps

---

## 🌐 DEPLOYMENT (Optional)

### Streamlit Cloud
- [ ] Commit all changes to Git
- [ ] Push to GitHub
- [ ] Deploy on streamlit.io
- [ ] Test deployed version
- [ ] Share link with team

### Production Server
- [ ] Set up server environment
- [ ] Configure firewall
- [ ] Set up HTTPS
- [ ] Configure authentication
- [ ] Test from external network

---

## ✅ FINAL VERIFICATION

### Complete Workflow Test
1. [ ] Start app
2. [ ] Load sales data
3. [ ] Upload 3 CSV files
4. [ ] Navigate to Show Health
5. [ ] Select a show
6. [ ] Verify no crash on line 823 ✨
7. [ ] Check all gauges work
8. [ ] Run Data Mapping
9. [ ] Export integrated data
10. [ ] Verify exported data

### Sign-Off
- [ ] All critical features work
- [ ] No blocking bugs
- [ ] Performance acceptable
- [ ] Documentation complete
- [ ] Ready for production

---

## 📞 POST-DEPLOYMENT

### Monitoring (First Week)
- [ ] Check error logs daily
- [ ] Monitor user feedback
- [ ] Track match rates
- [ ] Note any issues
- [ ] Document solutions

### Maintenance
- [ ] Schedule weekly data reviews
- [ ] Plan monthly updates
- [ ] Keep documentation current
- [ ] Back up data regularly

---

## 🎉 SUCCESS CRITERIA

### Must Have (Blockers)
✅ App starts without errors  
✅ Sales data loads correctly  
✅ Can upload CSV files  
✅ Show Health tab works  
✅ No crash on line 823  
✅ Can select and view shows  

### Should Have (Important)
✅ Match rate > 80%  
✅ Data quality reports work  
✅ Can export integrated data  
✅ All tabs functional  
✅ Charts render correctly  

### Nice to Have (Enhancements)
✅ Match rate > 90%  
✅ Fast load times  
✅ No warning messages  
✅ Beautiful visualizations  
✅ Intuitive UI  

---

## 📊 METRICS TO TRACK

### Week 1
- App uptime: ______%
- Average match rate: ______%
- Number of shows processed: ______
- User-reported issues: ______

### Month 1
- Total shows analyzed: ______
- Average ROAS: ______
- Data export frequency: ______
- User satisfaction: ______/10

---

## 🆘 ROLLBACK PLAN

If critical issues occur:

1. [ ] Stop application
2. [ ] Restore from backup:
   ```bash
   cp optimized-ads-analyzer.py.backup_YYYYMMDD_HHMMSS optimized-ads-analyzer.py
   ```
3. [ ] Remove data_mapper.py
4. [ ] Restart app
5. [ ] Investigate issues
6. [ ] Document problems
7. [ ] Plan fix

---

## ✍️ SIGN-OFF

**Deployed by:** _______________  
**Date:** _______________  
**Version:** 4.1.0  
**Status:** ☐ Passed ☐ Failed ☐ Needs Review  

**Notes:**
_____________________________________
_____________________________________
_____________________________________

**Issues Found:**
_____________________________________
_____________________________________
_____________________________________

**Next Steps:**
_____________________________________
_____________________________________
_____________________________________

---

**Checklist Complete!** 🎉

If all items are checked, you're ready to go live!

For support: Check README.md or open GitHub issue
