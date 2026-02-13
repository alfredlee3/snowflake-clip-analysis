# PIE Income Collection Analysis Methodology

## Summary of Changes

1. Replaced Stmt 42 with **Stmt 42+** (all statements ≥42) to capture all late-stage accounts
2. Changed time bucketing from **calendar months** to **30-day rolling windows** for fair comparison
3. Clarified that **ALL lines use account-level methodology** - the distinction is filtered vs aggregated populations

## Time Window Methodology: 30-Day Rolling Windows

**New Approach (30-Day Rolling Windows):**
- Month 0: 0-30 days after PIE
- Month 1: 31-60 days after PIE
- Month 2: 61-90 days after PIE
- ...
- Month 8: 211-240 days after PIE

**Why This Is Better:**
- ✅ **Consistent timeframe**: Every account gets exactly 30 days per "month"
- ✅ **Fairer comparison**: Accounts aren't penalized based on when they got PIE within a calendar month
- ✅ **No edge effects**: PIE on April 30th gets same window as PIE on April 1st

**Old Approach (Calendar Months):**
- Month 0: Same calendar month as PIE (variable: 1-30 days)
- Month 1: Next calendar month
- etc.

This could create unfair comparisons where an account with PIE on April 30th only got 1 day for "Month 0" while an account with PIE on April 1st got 30 days.

## Understanding the April 2025 Cohort: No Overlap

**CRITICAL INSIGHT**: In the April 2025 cohort analysis, each account appears at exactly ONE statement number.

Since we filter by `statement_end_dt = '2025-04-01'` (April 2025), and statements are sequential milestones in an account's lifecycle:
- Account A can be at Stmt 18 in April 2025 ✓
- Account A **cannot** also be at Stmt 26 in April 2025 (would be a different calendar month)

**This means:**
- Stmt 18, 26, 34 are **non-overlapping populations** in April 2025
- An account appears in only one of these groups
- There's no "double-counting" issue within the single-month cohort

## The Two Analysis Approaches

### 1. Specific Statement Filter (Stmt 18, 26, 34)
**What it is**: Filter to accounts at a specific statement number only

**Example**:
- Stmt 18: 905 unique accounts at Stmt 18 in April 2025
- Stmt 26: 140 unique accounts at Stmt 26 in April 2025
- Stmt 34: 206 unique accounts at Stmt 34 in April 2025

**These are separate, non-overlapping groups.**

**SQL Pattern**:
```sql
select
    clip.account_id,
    min(clip.evaluated_timestamp) as earliest_pie_timestamp
from CLIP_RESULTS_DATA clip
where date_trunc(month, stmt.statement_end_dt) = '2025-04-01'
  and clip.outcome = 'PRE_EVAL_APPROVED'
  and clip.statement_number = 18  -- Specific statement filter
group by clip.account_id
```

### 2. Statement Range Aggregation (Stmt 42+, Overall 18+)
**What it is**: Aggregate across multiple statement numbers, deduplicate accounts

**Example**:
- Stmt 42+: Accounts at Stmt 42, 43, 44, 45, ... in April 2025 (deduplicated)
- Overall 18+: Accounts at Stmt 18, 19, 20, 21, ... in April 2025 (deduplicated)

**Why deduplication matters here**: While most statements have only a few accounts (18, 26, 34 have ~100-900 each), there are many statements ≥42 with very small populations. Aggregating them gives better statistical power.

**SQL Pattern**:
```sql
select
    clip.account_id,
    min(clip.evaluated_timestamp) as earliest_pie_timestamp  -- Earliest across all Stmt ≥42
from CLIP_RESULTS_DATA clip
where date_trunc(month, stmt.statement_end_dt) = '2025-04-01'
  and clip.outcome = 'PRE_EVAL_APPROVED'
  and clip.statement_number >= 42  -- Statement range
group by clip.account_id  -- Deduplicate across statements
```

## Results (April 2025 Cohort)

### Individual Statements (Non-Overlapping)
- **Stmt 18**: 905 accounts → 759 collected (83.9%)
- **Stmt 26**: 140 accounts → 77 collected (55.0%)
- **Stmt 34**: 206 accounts → 132 collected (64.1%)
- **Stmt 42**: 137 accounts → 79 collected (57.7%)

### Aggregated Ranges
- **Stmt 42+**: 9,557 unique accounts → 5,627 collected (58.7% at Month 8)
- **Overall Stmt 18+**: 11,482 unique accounts → 10,005 succeeded (87.2% success rate at Month 8)

**Note**: "Success" = Approved Outright OR PIE with Income Collected

## Updated Results (30-Day Rolling Windows)

**Account-Level Overall Performance (April 2025):**
- Total Unique PIE Accounts: 1,244
- **Month 0 (0-30 days)**: 35.5% collection rate (3,403 accounts)
- **Month 8 (211-240 days)**: 58.8% collection rate (5,634 accounts)

**Comparison to Old Calendar Month Approach:**
- Old Month 0 (calendar): 30.5%
- New Month 0 (30-day): 35.5% (+5.0pp improvement!)
- This shows that many accounts collected income in days 1-30, but were previously counted in "Month 1" due to calendar boundary effects

## Visualization Structure

The visualizations show:

### Success Rate Chart (Approved + PIE with Income)
- **Stmt 18**: 905 accounts at Stmt 18 only (Red line) → 91.4% success by Month 8
- **Stmt 26**: 140 accounts at Stmt 26 only (Blue line) → 76.4% success by Month 8
- **Stmt 34**: 206 accounts at Stmt 34 only (Green line) → 81.3% success by Month 8
- **Stmt 42+**: 9,557 accounts at ANY Stmt ≥42 (Orange line) → 80.9% success by Month 8
- **Overall Stmt 18+**: 11,482 accounts at ANY Stmt ≥18 (Black dashed) → 87.2% success by Month 8

### PIE Collection Rate Chart (PIE accounts only)
- **Stmt 18**: Of 905 PIE accounts at Stmt 18, 83.9% collected income
- **Stmt 26**: Of 140 PIE accounts at Stmt 26, 55.0% collected income
- **Stmt 34**: Of 206 PIE accounts at Stmt 34, 64.1% collected income
- **Overall Stmt 18+**: Of 9,589 PIE accounts at ANY Stmt ≥18, 58.7% collected income

**All lines use 30-day rolling windows** for fair time comparison.

## Files Updated

1. **pie_income_collection_over_time_account_level.sql** (NEW)
   - Account-level query for overall Stmt 18+ performance
   - Deduplicates accounts across statements
   - Uses earliest PIE timestamp per account

2. **visualize_income_collection_over_time.py** (UPDATED)
   - Loads both statement-level and account-level data
   - Individual statements use statement-level
   - Overall line uses account-level
   - Added account-level summary section

3. **pie_income_collection_over_time.png** (UPDATED)
   - Overall line now shows 58.8% at Month 8 (down from 75.4%)
   - Label indicates "(Acct-Level)" to clarify methodology
