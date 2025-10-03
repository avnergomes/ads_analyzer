# 📚 Documentation Index – Ads Analyzer v2.0

Welcome to the complete documentation set for Ads Analyzer v2.0. Use this index to jump straight to the guide you need.

## 🚀 Getting started

### For new users
1. **[QUICKSTART.md](QUICKSTART.md)** ⚡ – Configure the environment and load your first files.
   - Installation checklist
   - Upload walkthrough
   - Tips for first-time analysts

2. **[README.md](README.md)** 📖 – Full project overview.
   - Highlights of version 2.0
   - Dashboard capabilities
   - Supported file formats

### For developers
1. **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** 📁 – Codebase structure.
   - File layout
   - Data flow
   - Component responsibilities

2. **[CHANGELOG.md](CHANGELOG.md)** 📝 – Release history.
   - What changed in v2.0
   - Enhancements by module
   - Items planned for future iterations

---

## 📖 Usage guides

### Core workflows
- **[QUICKSTART.md](QUICKSTART.md)** – Install, upload, and navigate the dashboards.

### Advanced scenarios
- **[EXAMPLES.md](EXAMPLES.md)** 📊 – Practical walkthroughs.
  - Campaign performance reviews
  - Budget pacing by show
  - ROI/ROAS deep dives
  - Audience and placement efficiency
  - Dayparting trends
  - Executive dashboard snapshots

---

## 🔧 Troubleshooting

### Diagnostic tools
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** 🐛 – Comprehensive issue resolution.
  - Common upload errors
  - Data completeness checks
  - Expected schema references
  - Performance tuning tips

### Issues covered
1. File type not recognised
2. Missing metrics after upload
3. File parsing failures
4. Incorrect show matching
5. Memory pressure during processing
6. Charts not rendering
7. Unexpected date formats

---

## 🚀 Deployment

### Deployment guides
- **[DEPLOYMENT.md](DEPLOYMENT.md)** 🌐 – Production roll-out instructions.
  - Streamlit Cloud
  - Docker images
  - Fly.io and generic VPS setups
  - CI/CD hints
  - Security considerations

### Supported targets
- ✅ Streamlit Cloud (hosted)
- ✅ Docker containers
- ✅ Fly.io / Heroku (PaaS)
- ✅ Ubuntu VPS (self-hosted)
- ✅ GitHub Actions (automation)

---

## 🔍 Technical reference

### Architecture
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** – Deep dive on modules.
  - Core classes (`AdsDataProcessor`, `IntegratedDashboard`, `FunnelSummary`)
  - Ticket ingestion (`PublicSheetsConnector`)
  - Helper scripts

### Code entry points
- **[app.py](app.py)** – Streamlit application and UI logic.
- **[public_sheets_connector.py](public_sheets_connector.py)** – Ticket parsing, normalisation, and USD conversion utilities.
- **[validate_csv.py](validate_csv.py)** – Command-line validator for Meta exports.
- **[test_installation.py](test_installation.py)** – Environment sanity check.
