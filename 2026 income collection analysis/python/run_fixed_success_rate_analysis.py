"""
Run Fixed PIE Success Rate Over Time Analysis

This script runs the corrected SQL query that fixes the "approved outright" logic.

Key Fix:
- OLD: was_approved_outright = 1 if account was EVER approved at ANY statement
- NEW: approved_outright = accounts that were NEVER PIE at any statement

This ensures mutually exclusive categories and prevents double-counting.
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
print("RUNNING FIXED PIE SUCCESS RATE ANALYSIS")
print("=" * 120)
print("\nKey Fix: 'Approved Outright' now means accounts that were NEVER PIE")
print("(Previously incorrectly counted accounts as 'approved outright' even if they had PIE at other statements)")
print("\n")

# Load fixed query
with open('/Users/Alfred.Lee/Documents/github/2026 income collection analysis/sql/pie_income_collection_over_time_fixed.sql', 'r') as f:
    query = f.read()

print("Executing query...")
cursor = conn.cursor()
cursor.execute(query)
df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
cursor.close()
conn.close()

print(f"✓ Loaded {len(df)} rows\n")

# Add month label (1-8 instead of 0-7)
df['MONTH_LABEL'] = df['MONTH_OFFSET'] + 1

# Display results by statement
statements = [
    (18, 'STATEMENT 18'),
    (26, 'STATEMENT 26'),
    (34, 'STATEMENT 34'),
    (442, 'STATEMENT 42+ (Account-Level)'),
    (999, 'OVERALL STMT 18+ (Account-Level)')
]

for stmt_num, stmt_name in statements:
    print("\n" + "=" * 120)
    print(f"{stmt_name}")
    print("=" * 120)

    stmt_data = df[df['STATEMENT_NUMBER'] == stmt_num].sort_values('MONTH_OFFSET')

    if len(stmt_data) == 0:
        print("No data found")
        continue

    # Get first row for population info
    first_row = stmt_data.iloc[0]
    total_pop = int(first_row['TOTAL_POPULATION'])
    approved_outright = int(first_row['APPROVED_OUTRIGHT_COUNT'])
    pie_total = int(first_row['PIE_TOTAL_COUNT'])

    print(f"\nTotal Population: {total_pop:,}")
    print(f"  - Approved Outright (Never PIE): {approved_outright:,} ({100.0*approved_outright/total_pop:.1f}%)")
    print(f"  - Had PIE: {pie_total:,} ({100.0*pie_total/total_pop:.1f}%)")

    # Verification
    if approved_outright + pie_total == total_pop:
        print(f"  ✓ VERIFICATION PASSED: {approved_outright:,} + {pie_total:,} = {total_pop:,}")
    else:
        print(f"  ❌ VERIFICATION FAILED: {approved_outright:,} + {pie_total:,} ≠ {total_pop:,}")

    print(f"\n{'Month':<8} {'Days':<15} {'Success Rate':>15} {'Approved':>15} {'PIE Collected':>18} {'Success Count':>18}")
    print("-" * 120)

    for _, row in stmt_data.iterrows():
        month_label = int(row['MONTH_LABEL'])
        days_start = int(row['MONTH_OFFSET']) * 30
        days_end = (int(row['MONTH_OFFSET']) + 1) * 30
        days = f"{days_start}-{days_end}"
        success_rate = f"{row['SUCCESS_RATE_PCT']:.1f}%"
        approved = f"{int(row['APPROVED_OUTRIGHT_COUNT']):,}"
        pie_collected = f"{int(row['PIE_INCOME_COLLECTED_BY_MONTH']):,}"
        success = f"{int(row['SUCCESS_COUNT']):,}"

        print(f"Month {month_label:<3} {days:<15} {success_rate:>15} {approved:>15} {pie_collected:>18} {success:>18}")

    # Month 8 summary
    final_row = stmt_data.iloc[-1]
    print(f"\n  ✓ Month 8 (240 days) Results:")
    print(f"    - Success Rate: {final_row['SUCCESS_RATE_PCT']:.1f}%")
    print(f"    - Approved Outright: {int(final_row['APPROVED_OUTRIGHT_COUNT']):,}")
    print(f"    - PIE Collected: {int(final_row['PIE_INCOME_COLLECTED_BY_MONTH']):,}")
    print(f"    - Total Success: {int(final_row['SUCCESS_COUNT']):,} of {total_pop:,}")

# Summary comparison
print("\n" + "=" * 120)
print("MONTH 8 SUMMARY - ALL STATEMENTS")
print("=" * 120)
print(f"\n{'Statement':<25} {'Population':>15} {'Approved':>15} {'PIE Total':>15} {'PIE Collected':>18} {'Success Rate':>15}")
print("-" * 120)

for stmt_num, stmt_name in statements:
    stmt_data = df[df['STATEMENT_NUMBER'] == stmt_num].sort_values('MONTH_OFFSET')
    if len(stmt_data) == 0:
        continue

    final_row = stmt_data.iloc[-1]
    pop = f"{int(final_row['TOTAL_POPULATION']):,}"
    approved = f"{int(final_row['APPROVED_OUTRIGHT_COUNT']):,}"
    pie_total = f"{int(final_row['PIE_TOTAL_COUNT']):,}"
    pie_collected = f"{int(final_row['PIE_INCOME_COLLECTED_BY_MONTH']):,}"
    success_rate = f"{final_row['SUCCESS_RATE_PCT']:.1f}%"

    print(f"{stmt_name:<25} {pop:>15} {approved:>15} {pie_total:>15} {pie_collected:>18} {success_rate:>15}")

print("\n" + "=" * 120)
print("KEY INSIGHTS")
print("=" * 120)
print("\n✓ Success Rate = (Approved Outright + PIE with Income) / Total Population")
print("✓ Approved Outright = Accounts that were NEVER PIE at any statement")
print("✓ PIE with Income = PIE accounts that collected income within 240 days")
print("✓ Categories are mutually exclusive: Approved + PIE Total = Population")
print("✓ Statement-level (18, 26, 34): Count each account once per statement")
print("✓ Account-level (42+, Overall): Count each unique account once across all statements")
print("=" * 120)

# Save results to CSV
output_file = '/Users/Alfred.Lee/Documents/github/visualizations/success_rate_fixed_results.csv'
df.to_csv(output_file, index=False)
print(f"\n✓ Results saved to: {output_file}\n")
