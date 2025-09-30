# Changelog

All notable changes to the Ads Performance Analyzer project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [4.1.0] - 2025-09-30

### 🔧 Fixed

#### Critical Bug Fix
- **Fixed ValueError on line 823** in `render_show_health()` method
  - Issue: `latest.get('remaining', 0)` could return `None` or `NaN`, causing `int()` conversion to fail
  - Solution: Implemented `safe_numeric()` function for robust value handling
  - Impact: Show Health dashboard now works correctly with incomplete data

#### Data Handling
- Added comprehensive `None` and `NaN` value handling throughout the application
- Improved error handling in metric calculations
- Better handling of missing data in sales spreadsheet
- Fixed lambda functions in chart generation to use safe numeric conversion

### 🚀 Added

#### Data Mapper Module (`data_mapper.py`)
- New `DataMapper` class for intelligent Sales ↔ Ads integration
- Multiple campaign naming pattern support:
  - Standard: `CITY_DATE_SEQUENCE` (e.g., `WDC_0927_S2`)
  - Legacy: `US-CITY-Sales-DATE`
  - City name: `CityName_DATE`
  - Tour format: `Tour_CityName_NUM`
- Automatic show_id extraction from campaign names
- Smart matching algorithm with fallback strategies

#### Data Quality Validation
- `validate_data_quality()` method for automatic quality checks
- Missing values detection and reporting
- Data type validation
- Required fields verification
- Comprehensive quality reports with warnings

#### Advanced Integration
- `integrate_sales_and_ads_data()` function for multi-source integration
- Support for all 3 CSV types (Days, Placement+Device, Time)
- Automatic aggregation of metrics by show
- Calculated integrated metrics (ROAS, CPA, Click-to-Purchase Rate)

#### Data Export
- Export integrated data as CSV
- Download button for processed data
- Includes all calculated metrics
- Ready for external analysis tools

#### User Interface
- New "Data Mapping - Quality and Integration" expander
- Quality validation reports in UI
- Integration statistics display
- Match rate indicators
- Preview of integrated data

#### Documentation
- Complete `USAGE_GUIDE.txt` with detailed instructions
- `PATCH_INSTRUCTIONS.txt` for manual fixes
- `EXAMPLES.py` with 11 practical examples
- Enhanced `README.md` with API reference
- This `CHANGELOG.md` file

#### Automation
- `apply_fixes.py` script for automatic patch application
- Automatic backup creation before applying fixes
- Validation of applied changes

### 🎯 Improved

#### Performance
- Optimized data processing pipeline
- Better memory usage with chunked operations
- Faster CSV parsing and normalization
- Reduced redundant calculations

#### User Experience
- More intuitive error messages
- Better visual feedback during processing
- Clearer labeling of metrics
- Improved warning messages

#### Code Quality
- Better separation of concerns
- More maintainable code structure
- Comprehensive inline documentation
- Type hints for better IDE support

#### Reliability
- Robust error handling throughout
- Graceful degradation with missing data
- Better validation of user inputs
- Comprehensive logging

### 📚 Documentation

#### New Files
- `data_mapper.py` - 600+ lines of well-documented code
- `USAGE_GUIDE.txt` - Comprehensive 400+ line guide
- `PATCH_INSTRUCTIONS.txt` - Detailed fix instructions
- `EXAMPLES.py` - 11 practical code examples
- `apply_fixes.py` - Automatic fix application script
- `CHANGELOG.md` - This file
- Enhanced `README.md` - Complete project documentation

#### Updated Files
- `optimized-ads-analyzer.py` - Fixed critical bugs, added new features
- All documentation files translated to English

---

## [4.0.0] - 2025-09-15

### 🚀 Added

#### Visual Health Indicators
- Occupancy gauge with color-coded thresholds
- Sales pace gauge showing target vs actual
- Funnel efficiency gauge
- Days countdown indicator
- ROAS visual indicator

#### Enhanced Dashboard
- Show Health tab with comprehensive metrics
- Ticket Sales overview with city rankings
- Advertising performance tracking
- Integration analysis with correlations

#### Funnel Analysis
- Complete conversion funnel visualization
- Stage-to-stage conversion rates
- Funnel efficiency metrics
- Visual funnel chart with Plotly

#### Budget Tracking
- Show budget input
- Ticket cost calculation
- Cost Per Acquisition (CPA) tracking
- Budget utilization metrics

### 🎯 Improved

#### Data Processing
- Enhanced column detection algorithms
- Better handling of Meta CSV variations
- Improved show matching logic
- More robust data normalization

#### Visualizations
- Interactive Plotly charts
- Responsive design
- Better color schemes
- Improved chart layouts

---

## [3.0.0] - 2025-08-01

### 🚀 Added
- Initial Streamlit application
- Google Sheets integration
- Basic Meta Ads CSV support
- Sales overview dashboard
- Simple campaign tracking

### 🎯 Improved
- Basic data normalization
- Simple visualizations
- Manual show matching

---

## [2.0.0] - 2025-06-15

### 🚀 Added
- Jupyter notebook for analysis
- Manual CSV processing
- Basic metric calculations

---

## [1.0.0] - 2025-05-01

### 🚀 Added
- Initial project setup
- Basic data structures
- Simple analysis scripts

---

## Migration Guide

### Upgrading from v4.0 to v4.1

#### Required Actions:

1. **Backup your current installation**
   ```bash
   cp optimized-ads-analyzer.py optimized-ads-analyzer.py.backup
   ```

2. **Add new file**
   - Copy `data_mapper.py` to your optimization_v4 directory

3. **Apply fixes** (choose one method):
   
   **Option A - Automatic (Recommended):**
   ```bash
   python apply_fixes.py
   ```
   
   **Option B - Manual:**
   - Follow instructions in `PATCH_INSTRUCTIONS.txt`

4. **Update requirements** (if needed):
   ```bash
   pip install -r requirements-file.txt --upgrade
   ```

5. **Test the application**:
   ```bash
   streamlit run optimized-ads-analyzer.py
   ```

#### Breaking Changes:
- None. v4.1 is fully backward compatible with v4.0

#### New Features You Can Now Use:
- Data quality validation
- Advanced integration
- Integrated data export
- Enhanced error handling

---

## Roadmap

### v4.2 (Planned - Q4 2025)
- [ ] Machine learning predictions
- [ ] Automated budget optimization recommendations
- [ ] A/B testing analysis
- [ ] Custom report builder
- [ ] Email alerts for performance thresholds

### v4.3 (Planned - Q1 2026)
- [ ] Multi-platform support (Google Ads, TikTok)
- [ ] Real-time data sync
- [ ] Advanced attribution modeling
- [ ] Cohort analysis
- [ ] API for external integrations

### v5.0 (Planned - Q2 2026)
- [ ] Complete UI redesign
- [ ] Multi-user support with authentication
- [ ] Cloud deployment options
- [ ] Mobile app
- [ ] Advanced AI recommendations

---

## Support

For questions, issues, or feature requests:
- Check the documentation in this repository
- Open an issue on GitHub
- Review the [USAGE_GUIDE.txt](USAGE_GUIDE.txt) for detailed instructions

---

## Contributors

- **Avner Gomes** - Initial work and v4.1 major update

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note**: This changelog follows semantic versioning. Version numbers are formatted as MAJOR.MINOR.PATCH where:
- MAJOR version for incompatible API changes
- MINOR version for added functionality in a backwards compatible manner
- PATCH version for backwards compatible bug fixes
