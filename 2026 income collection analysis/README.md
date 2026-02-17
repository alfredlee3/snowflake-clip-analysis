# 2026 PIE Income Collection Analysis

This folder contains SQL queries, Python scripts, and visualizations for analyzing PIE (PRE_EVAL_APPROVED) income collection performance.

## Overview

**PIE (PRE_EVAL_APPROVED)** = Accounts blocked ONLY by stale income requirement (applies at Statement 18+)

**Key Metrics:**
- **Success Rate** = (Approved Outright + PIE with Income Collected) / Total Population
- **PIE Income Collection Rate** = PIE with Income Collected / Total PIE Accounts

**Measurement Window:** 8 months (240 days) after initial PIE evaluation

## Folder Structure

### `sql/`
SQL queries for extracting PIE income collection data from Snowflake:

- **`pie_income_update_tracking.sql`** - Single statement, single month analysis (simplified version)
- **`pie_income_multi_statement_analysis.sql`** - Multi-statement comparison (Stmt 18, 26, 34, 42) for April 2025 cohort
- **`pie_income_cohort_comparison.sql`** - Multi-month cohort comparison (Mar-May 2025)
- **`pie_income_collection_over_time.sql`** - Monthly progression with overall success rate (includes Stmt 18, 26, 34, 42+, Overall 18+)
- **`pie_income_collection_over_time_account_level.sql`** - Account-level analysis for specific statements
- **`pie_income_collection_over_time_account_level_all_statements.sql`** - Account-level PIE collection rates for all statements

### `python/`
Python scripts for running queries and generating visualizations:

**Analysis & Visualization:**
- **`run_income_tracking.py`** - Runs single statement analysis and displays formatted results
- **`run_multi_statement_analysis.py`** - Runs multi-statement comparison analysis
- **`pie_income_collection_visualization.py`** - Creates 4-panel visualization for single statement
- **`visualize_cohort_comparison.py`** - Creates cohort comparison charts (Mar-May 2025)
- **`visualize_income_collection_over_time.py`** - Creates combined time series visualization
- **`visualize_success_rate_over_time.py`** - Creates overall success rate chart (Approved + PIE with Income)
- **`visualize_success_rate_over_time_cohort_comparison.py`** - Multi-cohort comparison (Mar/Apr/May 2025)
- **`visualize_pie_income_account_level.py`** - Creates PIE income collection rate chart (account-level)
- **`export_chart_data_account_level.py`** - Exports account-level data to CSV for manual analysis

**Export & Integration:**
- **`export_success_rate_for_google_sheets.py`** - Exports success rate data to CSV for Google Sheets
- **`upload_to_google_sheets.py`** - Automated upload to Google Sheets with embedded charts
- **`create_powerpoint_presentation.py`** - Creates PowerPoint presentation with embedded chart data

### `visualizations/`
Generated charts and exports:

**Image Visualizations:**
- **`success_rate_over_time.png`** - Overall success rate progression (Approved + PIE with Income) - April 2025
- **`success_rate_cohort_comparison.png`** - Multi-cohort comparison (Mar/Apr/May 2025) - Overall success rates
- **`pie_income_collection_account_level.png`** - PIE-specific collection rates over time
- **`pie_income_collection_over_time.png`** - Time progression + cohort comparison
- **`pie_cohort_comparison_visualization.png`** - Detailed cohort comparison (4 panels)
- **`pie_income_collection_visualization.png`** - Single statement deep dive

**Data Exports:**
- **`pie_income_data_account_level_all_statements.csv`** - Exported data for all statements
- **`success_rate_google_sheets.csv`** - Wide format data optimized for Google Sheets charting
- **`success_rate_detailed_google_sheets.csv`** - Detailed metrics for Google Sheets import

**Presentations:**
- **`PIE_Success_Rate_Analysis.pptx`** - PowerPoint presentation with embedded chart data (not images)

### Documentation
- **`CLIP_PIE_ANALYSIS_ONBOARDING_GUIDE.md`** - Comprehensive guide for analysts and AI assistants
- **`ACCOUNT_VS_STATEMENT_LEVEL_METHODOLOGY.md`** - Methodology documentation and 30-day rolling windows explanation
- **`GOOGLE_SHEETS_INTEGRATION.md`** - Guide for exporting data to Google Sheets with embedded charts
- **`POWERPOINT_INTEGRATION.md`** - Guide for creating PowerPoint presentations with embedded chart data

## Key Findings

### Statement 18 (Best Performance)
- **Success Rate:** 94.9% (April 2025)
- **PIE Income Collection Rate:** 83.9%
- Peak activity in Month 0 (59.4% collect immediately)
- Strong early momentum: 70.4% collected by Month 1

### Statement 42+ (Late-Stage Accounts)
- **Success Rate:** 80.9% (April 2025)
- **PIE Income Collection Rate:** 58.7%
- Aggregates all statements ≥42 for better statistical power
- Represents 9,557 unique accounts in April 2025 cohort

### Cohort Consistency (Mar-May 2025)
**Overall Stmt 18+ Success Rates (Month 8):**
- Mar 2025: 86.4% (27,837 accounts)
- Apr 2025: 86.1% (28,520 accounts)
- May 2025: 85.8% (28,856 accounts)

**Key Insight:** Remarkable consistency across cohorts validates PIE income collection patterns are stable and reliable for forecasting

## Integration Options

Export your analysis results to different formats:

### Google Sheets
- **Manual Import**: Export CSV and import to Google Sheets (5 minutes)
- **Automated Upload**: Use Google Sheets API for automated uploads with embedded charts
- See [GOOGLE_SHEETS_INTEGRATION.md](GOOGLE_SHEETS_INTEGRATION.md) for details

### PowerPoint
- **Automated Generation**: Create PowerPoint presentation with embedded chart data (not images)
- Charts are native PowerPoint objects that can be edited and updated
- See [POWERPOINT_INTEGRATION.md](POWERPOINT_INTEGRATION.md) for details

### Python Visualizations
- Run visualization scripts to generate PNG images
- Saved to `visualizations/` folder
- Can be embedded in reports, emails, or dashboards

## Important Notes

- **EFX Income Records Expiration:** Income data expires after 1 year, so use cohorts within last 12 months
- **Deduplication Logic:** If account has both PIE and APPROVED in same month, classify as PIE
- **Income Tracking:** Uses `CLIP_USER_INCOMES` table joined via `PERSON_ID`
- **8-Month Window:** Chosen to balance sufficient observation time with data recency

## Usage

1. Connect to Snowflake using external browser authentication
2. Run SQL queries to extract data
3. Use Python scripts to generate visualizations
4. All visualizations saved to `visualizations/` folder

## Analysis Date
February 2026
