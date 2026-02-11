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
- **`pie_income_collection_over_time.sql`** - Monthly progression analysis (Month 0-8 after PIE)

### `python/`
Python scripts for running queries and generating visualizations:

- **`run_income_tracking.py`** - Runs single statement analysis and displays formatted results
- **`run_multi_statement_analysis.py`** - Runs multi-statement comparison analysis
- **`pie_income_collection_visualization.py`** - Creates 4-panel visualization for single statement
- **`visualize_cohort_comparison.py`** - Creates cohort comparison charts (Mar-May 2025)
- **`visualize_income_collection_over_time.py`** - Creates combined visualization:
  - Top row: Time series (month 0-8 progression) for April 2025 cohort
  - Bottom row: Multi-cohort comparison (Mar-May 2025) at 8 months

### `visualizations/`
Generated charts:

- **`pie_income_collection_over_time.png`** - Main visualization showing time progression + cohort comparison
- **`pie_cohort_comparison_visualization.png`** - Detailed cohort comparison (4 panels)
- **`pie_income_collection_visualization.png`** - Single statement deep dive

## Key Findings

### Statement 18 (Best Performance)
- **Success Rate:** 94.9% (April 2025)
- **PIE Income Collection Rate:** 83.9%
- Peak activity in Month 0 (59.4% collect immediately)
- Strong early momentum: 70.4% collected by Month 1

### Statement 42 (Lowest Performance)
- **Success Rate:** 87.4% (April 2025)
- **PIE Income Collection Rate:** 57.7%
- Slow start (24.8% in Month 0) but steady gains through Month 8
- Late momentum: +25.6pp from Month 1 to 8

### Cohort Stability (Mar-May 2025)
- Success rates: 83.5% - 95.2% (spread: 11.7%)
- PIE income collection rates: 51.3% - 85.8% (spread: 34.5%)
- Consistent patterns across cohorts despite different statement populations

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
