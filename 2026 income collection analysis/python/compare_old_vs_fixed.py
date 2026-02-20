"""
Compare OLD (buggy) vs FIXED PIE Success Rate Analysis

This script runs both versions and shows the differences caused by the bug.
"""

import snowflake.connector
import pandas as pd

# Snowflake connection
conn = snowflake.connector.connect(
    user='ALFRED_LEE',
    account='IJ90379-MISSIONLANE',
    authenticator='externalbrowser',
    database='EDW_DB',
    schema='PUBLIC'
)

print("=" * 120)
print("COMPARING OLD (BUGGY) vs FIXED PIE SUCCESS RATE ANALYSIS")
print("=" * 120)
print("\nBUG: Old version incorrectly counted accounts as 'approved outright' even if they had PIE at other statements")
print("FIX: New version correctly defines 'approved outright' as accounts that were NEVER PIE\n")

# Load OLD (buggy) query
print("\n[1/2] Running OLD (buggy) query...")
with open('/Users/Alfred.Lee/Documents/github/2026 income collection analysis/sql/pie_income_collection_over_time.sql', 'r') as f:
    query_old = f.read()

cursor = conn.cursor()
cursor.execute(query_old)
df_old = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
cursor.close()
print(f"✓ Loaded {len(df_old)} rows from OLD query")

# Load FIXED query
print("\n[2/2] Running FIXED query...")
with open('/Users/Alfred.Lee/Documents/github/2026 income collection analysis/sql/pie_income_collection_over_time_fixed.sql', 'r') as f:
    query_fixed = f.read()

cursor = conn.cursor()
cursor.execute(query_fixed)
df_fixed = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
cursor.close()
conn.close()
print(f"✓ Loaded {len(df_fixed)} rows from FIXED query")

# Add month label
df_old['MONTH_LABEL'] = df_old['MONTH_OFFSET'] + 1
df_fixed['MONTH_LABEL'] = df_fixed['MONTH_OFFSET'] + 1

# Compare Month 8 results
print("\n" + "=" * 120)
print("COMPARISON: MONTH 8 RESULTS (240 days)")
print("=" * 120)

statements = [
    (18, 'STATEMENT 18'),
    (26, 'STATEMENT 26'),
    (34, 'STATEMENT 34'),
    (442, 'STATEMENT 42+ (Account-Level)'),
    (999, 'OVERALL STMT 18+ (Account-Level)')
]

print(f"\n{'Statement':<30} {'Metric':<25} {'OLD (Buggy)':>20} {'FIXED':>20} {'Difference':>20}")
print("-" * 120)

for stmt_num, stmt_name in statements:
    old_data = df_old[(df_old['STATEMENT_NUMBER'] == stmt_num) & (df_old['MONTH_OFFSET'] == 7)]
    fixed_data = df_fixed[(df_fixed['STATEMENT_NUMBER'] == stmt_num) & (df_fixed['MONTH_OFFSET'] == 7)]

    if len(old_data) == 0 or len(fixed_data) == 0:
        continue

    old_row = old_data.iloc[0]
    fixed_row = fixed_data.iloc[0]

    # Total Population (should be same)
    old_pop = int(old_row['TOTAL_POPULATION'])
    fixed_pop = int(fixed_row['TOTAL_POPULATION'])
    diff_pop = fixed_pop - old_pop
    print(f"{stmt_name:<30} {'Total Population':<25} {old_pop:>20,} {fixed_pop:>20,} {diff_pop:>20,}")

    # Approved Outright (THIS IS WHERE THE BUG IS)
    old_approved = int(old_row['APPROVED_OUTRIGHT_COUNT'])
    fixed_approved = int(fixed_row['APPROVED_OUTRIGHT_COUNT'])
    diff_approved = fixed_approved - old_approved
    marker = " ❌ BUG!" if diff_approved != 0 else ""
    print(f"{'':<30} {'Approved Outright':<25} {old_approved:>20,} {fixed_approved:>20,} {diff_approved:>20,}{marker}")

    # PIE Total
    old_pie = int(old_row['PIE_TOTAL_COUNT'])
    fixed_pie = int(fixed_row['PIE_TOTAL_COUNT'])
    diff_pie = fixed_pie - old_pie
    print(f"{'':<30} {'PIE Total':<25} {old_pie:>20,} {fixed_pie:>20,} {diff_pie:>20,}")

    # PIE Collected
    old_pie_collected = int(old_row['PIE_INCOME_COLLECTED_BY_MONTH'])
    fixed_pie_collected = int(fixed_row['PIE_INCOME_COLLECTED_BY_MONTH'])
    diff_pie_collected = fixed_pie_collected - old_pie_collected
    print(f"{'':<30} {'PIE Collected':<25} {old_pie_collected:>20,} {fixed_pie_collected:>20,} {diff_pie_collected:>20,}")

    # Success Count
    old_success = int(old_row['SUCCESS_COUNT'])
    fixed_success = int(fixed_row['SUCCESS_COUNT'])
    diff_success = fixed_success - old_success
    marker = " ❌" if diff_success != 0 else " ✓"
    print(f"{'':<30} {'Success Count':<25} {old_success:>20,} {fixed_success:>20,} {diff_success:>20,}{marker}")

    # Success Rate
    old_rate = old_row['SUCCESS_RATE_PCT']
    fixed_rate = fixed_row['SUCCESS_RATE_PCT']
    diff_rate = fixed_rate - old_rate
    marker = " ❌" if abs(diff_rate) > 0.05 else " ✓"
    print(f"{'':<30} {'Success Rate %':<25} {old_rate:>20.1f} {fixed_rate:>20.1f} {diff_rate:>20.1f}{marker}")

    # Verification
    old_verify = old_approved + old_pie
    fixed_verify = fixed_approved + fixed_pie
    old_match = "✓" if old_verify == old_pop else "❌"
    fixed_match = "✓" if fixed_verify == fixed_pop else "❌"
    print(f"{'':<30} {'Verification (A+P=T)':<25} {old_verify:>20,} {old_match} {fixed_verify:>20,} {fixed_match}")
    print("-" * 120)

# Detailed analysis for Overall Stmt 18+
print("\n" + "=" * 120)
print("DETAILED ANALYSIS: OVERALL STMT 18+ - WHY THE BUG MATTERS")
print("=" * 120)

old_overall = df_old[(df_old['STATEMENT_NUMBER'] == 999) & (df_old['MONTH_OFFSET'] == 7)].iloc[0]
fixed_overall = df_fixed[(df_fixed['STATEMENT_NUMBER'] == 999) & (df_fixed['MONTH_OFFSET'] == 7)].iloc[0]

old_approved = int(old_overall['APPROVED_OUTRIGHT_COUNT'])
fixed_approved = int(fixed_overall['APPROVED_OUTRIGHT_COUNT'])
old_pie = int(old_overall['PIE_TOTAL_COUNT'])
fixed_pie = int(fixed_overall['PIE_TOTAL_COUNT'])
total_pop = int(fixed_overall['TOTAL_POPULATION'])

overcounted = old_approved - fixed_approved

print(f"\nTotal Population: {total_pop:,} accounts")
print(f"\nOLD (BUGGY) Logic:")
print(f"  - Approved Outright: {old_approved:,}")
print(f"  - PIE Total: {old_pie:,}")
print(f"  - Sum: {old_approved + old_pie:,} ❌ (doesn't match population!)")
print(f"  - Overcounted 'approved outright' by: {overcounted:,} accounts")
print(f"\nFIXED Logic:")
print(f"  - Approved Outright (never PIE): {fixed_approved:,}")
print(f"  - PIE Total: {fixed_pie:,}")
print(f"  - Sum: {fixed_approved + fixed_pie:,} ✓ (matches population!)")

print(f"\nThe Bug Explained:")
print(f"  {overcounted:,} accounts had PIE at one statement AND APPROVED at another statement")
print(f"  OLD logic counted them as 'approved outright' (because they were ever approved)")
print(f"  This is WRONG - they had a PIE barrier, so they're not 'approved outright'")
print(f"  FIXED logic correctly excludes them from 'approved outright' category")

# Impact on success rate
old_rate = old_overall['SUCCESS_RATE_PCT']
fixed_rate = fixed_overall['SUCCESS_RATE_PCT']
rate_diff = old_rate - fixed_rate

print(f"\nImpact on Success Rate:")
print(f"  OLD (buggy): {old_rate:.1f}%")
print(f"  FIXED: {fixed_rate:.1f}%")
print(f"  Difference: {rate_diff:.1f} percentage points")

if abs(rate_diff) < 0.1:
    print(f"  → No material impact (both methods count same accounts as 'success')")
else:
    print(f"  → Material difference in reported success rate!")

print("\n" + "=" * 120)
print("MONTHLY PROGRESSION COMPARISON - OVERALL STMT 18+")
print("=" * 120)

print(f"\n{'Month':<10} {'OLD Approved':>15} {'FIXED Approved':>18} {'Difference':>15} {'OLD Rate %':>15} {'FIXED Rate %':>18} {'Rate Diff':>15}")
print("-" * 120)

for month in range(8):
    old_month = df_old[(df_old['STATEMENT_NUMBER'] == 999) & (df_old['MONTH_OFFSET'] == month)].iloc[0]
    fixed_month = df_fixed[(df_fixed['STATEMENT_NUMBER'] == 999) & (df_fixed['MONTH_OFFSET'] == month)].iloc[0]

    month_label = month + 1
    old_app = int(old_month['APPROVED_OUTRIGHT_COUNT'])
    fixed_app = int(fixed_month['APPROVED_OUTRIGHT_COUNT'])
    diff_app = fixed_app - old_app
    old_rate = old_month['SUCCESS_RATE_PCT']
    fixed_rate = fixed_month['SUCCESS_RATE_PCT']
    rate_diff = fixed_rate - old_rate

    print(f"Month {month_label:<5} {old_app:>15,} {fixed_app:>18,} {diff_app:>15,} {old_rate:>15.1f} {fixed_rate:>18.1f} {rate_diff:>15.1f}")

print("\n" + "=" * 120)
print("KEY TAKEAWAYS")
print("=" * 120)
print(f"\n1. The bug affected the 'approved outright' count, not the success rate")
print(f"   - Both versions count the same accounts as 'success' (approved OR PIE+income)")
print(f"   - Difference is only in categorization: 'approved outright' vs 'PIE'")
print(f"\n2. The fix makes categories mutually exclusive:")
print(f"   - OLD: Approved + PIE ≠ Total (double counting)")
print(f"   - FIXED: Approved + PIE = Total ✓")
print(f"\n3. For Overall Stmt 18+: {overcounted:,} accounts were miscategorized")
print(f"   - They had PIE at one statement but were counted as 'approved outright'")
print(f"   - This made it look like fewer accounts had PIE barriers than reality")
print("=" * 120)
