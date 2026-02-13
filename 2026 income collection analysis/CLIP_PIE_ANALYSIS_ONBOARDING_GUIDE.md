# CLIP PIE Income Collection Analysis - Onboarding Guide

## Table of Contents
1. [Overview](#overview)
2. [Key Concepts](#key-concepts)
3. [Methodology: Account-Level vs Statement-Level](#methodology-account-level-vs-statement-level)
4. [Time Windows: 30-Day Rolling Windows](#time-windows-30-day-rolling-windows)
5. [Success Metrics](#success-metrics)
6. [SQL Patterns & Best Practices](#sql-patterns--best-practices)
7. [Common Pitfalls](#common-pitfalls)
8. [File Structure](#file-structure)
9. [Quick Reference](#quick-reference)

---

## Overview

**What is PIE?**
- PIE = PRE_EVAL_APPROVED
- A CLIP outcome where an account needs to provide income documentation before final approval
- Contrast with APPROVED = approved outright without income requirement

**What We're Measuring:**
- How many PIE accounts successfully collect income over time
- Overall success rate = (Approved Outright + PIE with Income) / Total Population
- PIE collection rate = PIE accounts that collected income / Total PIE accounts

---

## Key Concepts

### 1. CLIP Outcomes
- **APPROVED**: Approved outright (no income documentation needed)
- **PRE_EVAL_APPROVED**: PIE - requires income documentation before final approval
- **DECLINED**: Not approved

### 2. Success Definition
An account is considered **successful** if:
- They were APPROVED outright, OR
- They had PIE AND collected income within the analysis window (typically 240 days / 8 months)

### 3. Cohort Analysis
- **Cohort Definition**: Accounts filtered by statement_end_dt (e.g., April 2025 cohort)
- **Critical Insight**: In a single-month cohort (e.g., April 2025), each account can only be at ONE statement number
  - Statements are sequential over time
  - Account A can be at Stmt 18 in April OR Stmt 26 in April, but not both
  - This means Stmt 18, 26, 34 represent non-overlapping account populations

---

## Methodology: Understanding the Analysis Approach

**IMPORTANT CLARIFICATION**: All lines in our analysis use **account-level methodology** - each unique account is counted exactly once within its scope.

### Key Insight: No Overlap in April 2025 Cohort

Since we filter to `statement_end_dt = '2025-04-01'` (April 2025), each account can only appear at **ONE** statement number in that month. Statements are sequential milestones in an account's lifecycle, so:

- Account A at Stmt 18 in April 2025 ✓
- Account A at Stmt 26 in April 2025 ✗ **Cannot happen** (would be a different month)
- Account A at Stmt 34 in April 2025 ✗ **Cannot happen** (would be a different month)

**This means Stmt 18, 26, and 34 represent completely non-overlapping populations in the April 2025 cohort.**

### The Two Types of Analysis

#### 1. Specific Statement Filter (Stmt 18, 26, 34)
**What it means**: Filter to accounts at a specific statement number, count each account once
- **Stmt 18**: Unique accounts at Stmt 18 in April 2025
- **Stmt 26**: Unique accounts at Stmt 26 in April 2025
- **Stmt 34**: Unique accounts at Stmt 34 in April 2025

**These are non-overlapping sets** - an account appears in only one of these groups.

**SQL Pattern**:
```sql
select
    clip.statement_number,
    clip.account_id,
    min(clip.evaluated_timestamp) as earliest_pie_timestamp
from CLIP_RESULTS_DATA clip
where date_trunc(month, stmt.statement_end_dt) = '2025-04-01'
  and clip.outcome = 'PRE_EVAL_APPROVED'
  and clip.statement_number = 18  -- Specific statement filter
group by clip.statement_number, clip.account_id
```

#### 2. Statement Range Aggregation (Stmt 42+, Overall 18+)
**What it means**: Aggregate across multiple statement numbers, count each unique account once
- **Stmt 42+**: Unique accounts at ANY statement ≥42 in April 2025
- **Overall Stmt 18+**: Unique accounts at ANY statement ≥18 in April 2025

**These require deduplication** because we're aggregating across statement ranges.

**SQL Pattern**:
```sql
select
    clip.account_id,
    -- Use EARLIEST timestamp across ALL statements in the range
    min(clip.evaluated_timestamp) as earliest_pie_timestamp
from CLIP_RESULTS_DATA clip
where date_trunc(month, stmt.statement_end_dt) = '2025-04-01'
  and clip.outcome = 'PRE_EVAL_APPROVED'
  and clip.statement_number >= 18  -- Statement range (all Stmt 18+)
group by clip.account_id  -- Deduplicate across statements
```

### Visual Representation in Charts

**Our Standard Visualization Includes:**
1. **Stmt 18** - Accounts at Stmt 18 only (Red line)
2. **Stmt 26** - Accounts at Stmt 26 only (Blue line)
3. **Stmt 34** - Accounts at Stmt 34 only (Green line)
4. **Stmt 42+** - Accounts at ANY Stmt ≥42 (Orange line, aggregated)
5. **Overall Stmt 18+** - Accounts at ANY Stmt ≥18 (Black dashed line, aggregated)

**Note**: Lines 1-3 are non-overlapping populations. Lines 4-5 aggregate across statement ranges.

**Special Indicators in Code**:
- `statement_number = 442` → Stmt 42+ (all statements ≥42)
- `statement_number = 999` → Overall Stmt 18+ (all statements ≥18)

---

## Time Windows: 30-Day Rolling Windows

### Why Rolling Windows?

**Problem with Calendar Months:**
- Account with PIE on April 1 gets 30 days in "Month 0" (April 1-30)
- Account with PIE on April 30 gets 1 day in "Month 0" (April 30)
- **Unfair comparison** - different accounts get different time windows

**Solution: 30-Day Rolling Windows**
- Every account gets exactly 30 days per window
- Month 0 = 0-30 days after their specific PIE timestamp
- Month 1 = 31-60 days after their specific PIE timestamp
- Month 2 = 61-90 days after their specific PIE timestamp
- ...
- Month 7 = 211-240 days after their specific PIE timestamp

**Display Convention:**
- SQL uses `month_offset` = 0-7 (0-indexed)
- Visualizations display as "Month 1-8" (month_offset + 1)
- Month 1 in viz = Month 0 in SQL = 0-30 days

### SQL Implementation

```sql
-- Calculate which 30-day window the income was collected in
floor(datediff(day, base.earliest_pie_timestamp, inc.CREATED_AT) / 30) as months_to_collection

-- Example:
-- Day 15 after PIE → floor(15/30) = 0 → Month 0 (0-30 days)
-- Day 45 after PIE → floor(45/30) = 1 → Month 1 (31-60 days)
-- Day 220 after PIE → floor(220/30) = 7 → Month 7 (211-240 days)
```

### Month Series Generation

```sql
month_series as (
    select 0 as month_offset union all
    select 1 union all select 2 union all select 3 union all select 4 union all
    select 5 union all select 6 union all select 7
)
```

This creates 8 time buckets (Month 0-7) for cumulative analysis.

---

## Success Metrics

### 1. Overall Success Rate
**Definition**: Percentage of accounts that are either approved outright or collected income (if PIE)

**Formula**:
```
Success Rate = (Approved Outright + PIE with Income Collected) / Total Population
```

**SQL**:
```sql
count(distinct case
    when base.was_approved_outright = 1  -- Ever approved
    or (base.had_pie = 1 and inc.months_to_collection is not null
        and inc.months_to_collection <= m.month_offset)  -- PIE + collected by this month
    then base.account_id
end) as success_count,

round(100.0 * success_count / total_population, 1) as success_rate_pct
```

**Interpretation**: "What percentage of accounts successfully got through CLIP?"

### 2. PIE Income Collection Rate
**Definition**: Percentage of PIE accounts that collected income

**Formula**:
```
PIE Collection Rate = PIE Accounts That Collected / Total PIE Accounts
```

**SQL**:
```sql
count(distinct case
    when base.had_pie = 1
    and inc.months_to_collection is not null
    and inc.months_to_collection <= m.month_offset
    then base.account_id
end) as pie_income_collected_by_month,

round(100.0 * pie_income_collected_by_month / nullif(pie_total_count, 0), 1)
    as pie_income_collection_rate_pct
```

**Interpretation**: "Of accounts that needed to provide income, what percentage actually did?"

### 3. Incremental Collections
**Definition**: New income collections that happened in a specific month

**SQL**:
```sql
pie_income_collected_by_month - lag(pie_income_collected_by_month, 1, 0) over (
    partition by statement_number order by month_offset
) as new_income_collections_this_month
```

**Use Case**: Identify when collection activity plateaus

---

## SQL Patterns & Best Practices

### 1. Deduplication with QUALIFY

**Prioritize PIE over APPROVED** (if account has both):
```sql
qualify row_number() over (
    partition by clip.account_id, clip.statement_number
    order by case when clip.outcome = 'PRE_EVAL_APPROVED' then 0 else 1 end
) = 1
```

**Get FIRST income update** per account:
```sql
qualify row_number() over (
    partition by base.account_id
    order by inc.CREATED_AT
) = 1
```

### 2. Income Collection Window

```sql
left join CLIP_USER_INCOMES inc
    on base.PERSON_ID = inc.PERSON_ID
    and base.had_pie = 1  -- Only track PIE accounts
    and inc.CREATED_AT > base.earliest_pie_timestamp  -- AFTER PIE
    and inc.CREATED_AT <= DATEADD(day, 240, base.earliest_pie_timestamp)  -- Within 240 days
    and inc.annual_income IS NOT NULL  -- Valid income
```

### 3. Cross Join for Cumulative Metrics

```sql
from base_population base
cross join month_series m  -- Creates row for each account × each month
left join income_by_month inc
    on base.account_id = inc.account_id
```

This pattern allows cumulative counting at each time point.

### 4. CTE Structure (Standard Pattern)

```sql
with base_population as (
    -- Define the cohort and get earliest PIE timestamp
),
income_by_month as (
    -- Track WHEN income was collected (which 30-day bucket)
),
month_series as (
    -- Generate 0-7 month offsets
),
cumulative_success as (
    -- Calculate cumulative metrics at each month mark
)
select * from cumulative_success;
```

---

## Common Pitfalls

### 1. ❌ Confusing Account-Level and Statement-Level
**Wrong**: "Stmt 18 uses statement-level, Overall uses account-level"
**Right**: "ALL lines use account-level deduplication, but with different statement filters"
- Stmt 18 = Unique accounts at Stmt 18 only
- Overall Stmt 18+ = Unique accounts across all Stmt ≥18

### 2. ❌ Calendar Month vs Rolling Window Confusion
**Wrong**: Using `date_trunc(month, ...)` for time bucketing
**Right**: Using `floor(datediff(day, ...) / 30)` for fair comparison

### 3. ❌ Not Filtering by `annual_income IS NOT NULL`
- Some income records may exist but be NULL or invalid
- Always validate income data quality

### 4. ❌ Forgetting to Filter `CREATED_AT > evaluated_timestamp`
- Must ensure income was collected AFTER PIE event
- Otherwise counting pre-existing income

### 5. ❌ Using Month 0-7 vs Month 1-8 Inconsistently
**In SQL**: Use `month_offset = 0-7` (0-indexed)
**In Visualizations**: Display as "Month 1-8" via `month_offset + 1`
**In Comments**: Always clarify which convention you're using

### 6. ❌ Overlapping Account Assumptions
**Wrong**: "Account can be at Stmt 18 and Stmt 26 in same month"
**Right**: "In April 2025 cohort, each account can only be at ONE statement"
- Statements are sequential milestones over account lifetime

---

## File Structure

### SQL Queries
1. **[pie_income_collection_over_time.sql](pie_income_collection_over_time.sql)**
   - Overall success rate analysis (Approved + PIE with Income)
   - Includes Stmt 18, 26, 34, Stmt 42+, Overall Stmt 18+
   - Uses 30-day rolling windows
   - Outputs: `statement_number = 442` for Stmt 42+, `999` for Overall

2. **[pie_income_collection_over_time_account_level_all_statements.sql](pie_income_collection_over_time_account_level_all_statements.sql)**
   - PIE income collection rate specifically (not overall success)
   - Account-level for all individual statements + Overall
   - Useful for understanding PIE-specific behavior

### Python Visualization Scripts
1. **[visualize_success_rate_over_time.py](visualize_success_rate_over_time.py)**
   - Overall success rate chart (Approved + PIE)
   - Y-axis: 70-100% (to accommodate lower Stmt 42+ rates)
   - Outputs: `/visualizations/success_rate_over_time.png`

2. **[visualize_pie_income_account_level.py](visualize_pie_income_account_level.py)**
   - PIE income collection rate chart
   - Y-axis: 0-100%
   - Outputs: `/visualizations/pie_income_collection_account_level.png`

3. **[export_chart_data_account_level.py](export_chart_data_account_level.py)**
   - Exports data to CSV for manual analysis
   - Outputs: `/visualizations/pie_income_data_account_level_all_statements.csv`

### Documentation
1. **[ACCOUNT_VS_STATEMENT_LEVEL_METHODOLOGY.md](ACCOUNT_VS_STATEMENT_LEVEL_METHODOLOGY.md)**
   - Deep dive on methodology differences
   - Historical context of why we switched to 30-day windows

2. **[CLIP_PIE_ANALYSIS_ONBOARDING_GUIDE.md](CLIP_PIE_ANALYSIS_ONBOARDING_GUIDE.md)** (this file)
   - Comprehensive onboarding guide

---

## Quick Reference

### Terminology
| Term | Definition | Example |
|------|------------|---------|
| **PIE** | PRE_EVAL_APPROVED outcome | Account needs to provide income |
| **Success Rate** | (Approved + PIE w/ Income) / Total | 87.2% of accounts succeed |
| **Collection Rate** | PIE w/ Income / Total PIE | 58.7% of PIE accounts collect |
| **Month Offset** | 0-indexed month (SQL) | 0, 1, 2, ..., 7 |
| **Month Label** | 1-indexed month (viz) | 1, 2, 3, ..., 8 |
| **Cohort** | Statement month filter | April 2025 cohort |
| **30-Day Window** | Rolling time bucket | Month 0 = 0-30 days after PIE |

### Key Database Tables
- **CLIP_RESULTS_DATA**: CLIP outcomes and timestamps
- **account_statements**: Statement metadata (statement_end_dt, statement_num)
- **CLIP_USER_INCOMES**: Income documentation (CREATED_AT, annual_income)
- **ACCOUNTS_CUSTOMERS_BRIDGE**: Account to Person mapping (PERSON_ID)

### Common Filters
```sql
-- April 2025 cohort
where date_trunc(month, stmt.statement_end_dt) = '2025-04-01'

-- PIE accounts only
and clip.outcome = 'PRE_EVAL_APPROVED'

-- Approved accounts only
and clip.outcome = 'APPROVED'

-- Both PIE and Approved
and clip.outcome in ('APPROVED', 'PRE_EVAL_APPROVED')

-- Specific statements
and clip.statement_number in (18, 26, 34, 42)

-- Statement range
and clip.statement_number >= 18
```

### Month Window Reference
| Month Label (viz) | Month Offset (SQL) | Days After PIE | Description |
|-------------------|-------------------|----------------|-------------|
| Month 1 | 0 | 0-30 | First 30 days |
| Month 2 | 1 | 31-60 | Second 30 days |
| Month 3 | 2 | 61-90 | Third 30 days |
| Month 4 | 3 | 91-120 | Fourth 30 days |
| Month 5 | 4 | 121-150 | Fifth 30 days |
| Month 6 | 5 | 151-180 | Sixth 30 days |
| Month 7 | 6 | 181-210 | Seventh 30 days |
| Month 8 | 7 | 211-240 | Eighth 30 days |

### Typical Results (April 2025 Cohort)
| Category | Total Population | Success Rate (Month 8) | PIE Collection Rate |
|----------|-----------------|----------------------|-------------------|
| Stmt 18 | 1,056 | 91.4% | 83.8% |
| Stmt 26 | 161 | 76.4% | 55.0% |
| Stmt 34 | 251 | 81.3% | 64.1% |
| Stmt 42+ | 9,557 | 80.9% | 57.7% |
| Overall Stmt 18+ | 11,482 | 87.2% | 58.7% |

**Key Insights:**
- ✓ Stmt 18 has highest success rates (newest accounts, most motivated)
- ✓ Most income collection happens early (35.5% by Month 1)
- ✓ Collection plateaus around Month 7-8
- ✓ Overall success rate is strong at 87.2%

---

## Getting Started Checklist

### For New Analysts
- [ ] Read this guide completely
- [ ] Review [ACCOUNT_VS_STATEMENT_LEVEL_METHODOLOGY.md](ACCOUNT_VS_STATEMENT_LEVEL_METHODOLOGY.md)
- [ ] Run [export_chart_data_account_level.py](export_chart_data_account_level.py) to see sample output
- [ ] Examine the SQL queries to understand CTE structure
- [ ] Generate visualizations and compare to this guide's expected outputs
- [ ] Try modifying cohort date (change `'2025-04-01'` to another month)

### For AI Assistants
- [ ] Understand account-level vs statement-level distinctions
- [ ] Always ask for clarification: "Do you want account-level or statement-level?"
- [ ] When in doubt about April 2025 cohort: each account can only be at ONE statement
- [ ] Use 30-day rolling windows, not calendar months
- [ ] Remember special codes: 442 = Stmt 42+, 999 = Overall Stmt 18+
- [ ] Check terminology: "success rate" vs "collection rate" are different metrics

---

**Last Updated**: 2026-02-13
**Maintained By**: Data Analytics Team
**Questions?** Review SQL comments or visualization output for additional context.
