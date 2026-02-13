# Account-Level vs Statement-Level Methodology

## Summary of Changes

1. Updated the "Overall Stmt 18+" line to use **account-level** methodology, where each unique account is counted only once regardless of how many statements they appear at.
2. Changed time bucketing from **calendar months** to **30-day rolling windows** for consistent, fair comparison across all accounts.

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

## The Two Methodologies

### Statement-Level (Original - Individual Lines)
**Logic**: Count each account+statement combination separately
- Account A has PIE at Stmt 18 → Count 1
- Account A has PIE at Stmt 26 → Count 1
- **Total**: 2 PIE instances

**Use Case**: Analyzing performance at specific discrete statements

**Example Query**:
```sql
-- Each row = one account at one statement
select statement_number, count(*) as pie_instances
from pie_accounts
group by statement_number
```

### Account-Level (Updated - Overall Line)
**Logic**: Count each unique account only once
- Account A has PIE at Stmt 18 AND Stmt 26 → Count 1
- If Account A collects income, it counts as 1 success (not 2)
- **Total**: 1 PIE account

**Use Case**: Portfolio-wide KPIs, unique customer counts

**Example Query**:
```sql
-- Each row = one unique account (deduped across statements)
select count(distinct account_id) as unique_pie_accounts
from pie_accounts
```

## Results Comparison (April 2025)

### Statement-Level Aggregation (OLD)
- **PIE Instances**: 1,388 (905+140+206+137)
- **Collected**: 1,047 (759+77+132+79)
- **Rate**: 75.4%
- **Interpretation**: "Of all PIE instances across statements, 75.4% collected income"

### Account-Level Aggregation (NEW)
- **Unique PIE Accounts**: 1,244
- **Collected**: 732
- **Rate**: 58.8%
- **Interpretation**: "Of unique customers who had PIE, 58.8% collected income"

## Why the Difference?

The statement-level rate (75.4%) is higher because:
1. **Good customers appear multiple times**: Accounts that collect income tend to appear at multiple statements (they're progressing through the program)
2. **Double-counting success**: If Account A collects income and appears at 2 statements, both instances count as "success"
3. **Missing the non-responders**: Some accounts only appear at 1 statement and don't collect

Example:
- 100 accounts total
- 50 "good" accounts collect income and appear at 2 statements each = 100 successful instances
- 50 "bad" accounts don't collect and appear at 1 statement each = 50 failed instances
- **Statement-level**: 100/(100+50) = 66.7%
- **Account-level**: 50/100 = 50.0%

## Which Should You Use?

**Use Statement-Level** when:
- Analyzing specific statement performance (Stmt 18 vs Stmt 26)
- Understanding statement-specific interventions
- Discrete statement comparisons

**Use Account-Level** when:
- Reporting portfolio-wide KPIs
- Counting unique customers
- Avoiding double-counting
- Understanding true customer behavior

## Updated Results (30-Day Rolling Windows)

**Account-Level Overall Performance (April 2025):**
- Total Unique PIE Accounts: 1,244
- **Month 0 (0-30 days)**: 35.5% collection rate (3,403 accounts)
- **Month 8 (211-240 days)**: 58.8% collection rate (5,634 accounts)

**Comparison to Old Calendar Month Approach:**
- Old Month 0 (calendar): 30.5%
- New Month 0 (30-day): 35.5% (+5.0pp improvement!)
- This shows that many accounts collected income in days 1-30, but were previously counted in "Month 1" due to calendar boundary effects

## Updated Visualization

The updated visualization now shows:
- **Individual statement lines (18, 26, 34, 42)**: Statement-level with 30-day windows
  - "Of accounts with PIE at Stmt 18, what % collected in each 30-day window?"
- **Overall Stmt 18+ line**: Account-level with 30-day windows
  - "Of unique accounts with PIE at any Stmt 18+, what % collected?"
  - Label: "Overall Stmt 18+ (Acct-Level)"
  - Uses 30-day rolling windows for fair comparison
  - **Final rate: 58.8%** (Month 8 = 211-240 days after PIE)

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
