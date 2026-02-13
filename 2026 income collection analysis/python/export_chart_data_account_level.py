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

print("=" * 140)
print("PIE INCOME COLLECTION ANALYSIS - ACCOUNT-LEVEL DATA (ALL STATEMENTS)")
print("=" * 140)

# Load account-level data for all statements
print("\nLoading account-level data for all statements...")
with open('/Users/Alfred.Lee/Documents/github/pie_income_collection_over_time_account_level_all_statements.sql', 'r') as f:
    query = f.read()

cursor = conn.cursor()
cursor.execute(query)
df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
cursor.close()
conn.close()

print("\n" + "=" * 140)
print("TABLE: ACCOUNT-LEVEL DATA FOR ALL STATEMENTS")
print("Time Windows: Month 1 = 0-30 days, Month 2 = 31-60 days, ... Month 8 = 211-240 days after PIE")
print("Methodology: Each unique account counted once per statement (account-level deduplication)")
print("=" * 140)

# Pivot data for easier reading - Individual statements
statements = [18, 26, 34, 42]
for stmt in statements:
    stmt_data = df[df['STATEMENT_NUMBER'] == stmt].sort_values('MONTH_OFFSET')

    print(f"\n--- STATEMENT {stmt} (Account-Level) ---")
    print(f"{'Month':<8} {'Days Range':<15} {'Total PIE':>12} {'Collected':>12} {'Collection Rate':>18} {'New This Month':>15}")
    print("-" * 140)

    for _, row in stmt_data.iterrows():
        month_offset = int(row['MONTH_OFFSET'])
        month_label = month_offset + 1  # Display as Month 1-8 instead of 0-7
        days_start = month_offset * 30
        days_end = (month_offset + 1) * 30
        days_range = f"{days_start}-{days_end}"
        total_pie = int(row['PIE_TOTAL_COUNT'])
        collected = int(row['PIE_INCOME_COLLECTED_BY_MONTH'])
        rate = row['PIE_INCOME_COLLECTION_RATE_PCT']
        new_coll = int(row['NEW_INCOME_COLLECTIONS_THIS_MONTH'])

        print(f"Month {month_label:<2} {days_range:<15} {total_pie:>12,} {collected:>12,} {rate:>17.1f}% {new_coll:>15,}")

# Overall Stmt 18+
overall_data = df[df['STATEMENT_NUMBER'] == 999].sort_values('MONTH_OFFSET')
print(f"\n--- OVERALL STMT 18+ (Account-Level - Deduped Across All Statements) ---")
print(f"{'Month':<8} {'Days Range':<15} {'Total PIE':>12} {'Collected':>12} {'Collection Rate':>18} {'New This Month':>15}")
print("-" * 140)

for _, row in overall_data.iterrows():
    month_offset = int(row['MONTH_OFFSET'])
    month_label = month_offset + 1  # Display as Month 1-8 instead of 0-7
    days_start = month_offset * 30
    days_end = (month_offset + 1) * 30
    days_range = f"{days_start}-{days_end}"
    total_pie = int(row['PIE_TOTAL_COUNT'])
    collected = int(row['PIE_INCOME_COLLECTED_BY_MONTH'])
    rate = row['PIE_INCOME_COLLECTION_RATE_PCT']
    new_coll = int(row['NEW_INCOME_COLLECTIONS_THIS_MONTH'])

    print(f"Month {month_label:<2} {days_range:<15} {total_pie:>12,} {collected:>12,} {rate:>17.1f}% {new_coll:>15,}")

# Export to CSV
print("\n" + "=" * 140)
print("EXPORTING DATA TO CSV FILE")
print("=" * 140)

# Prepare export with day ranges
export_df = df.copy()
export_df['MONTH_LABEL'] = export_df['MONTH_OFFSET'] + 1  # Month 1-8 instead of 0-7
export_df['DAYS_START'] = export_df['MONTH_OFFSET'] * 30
export_df['DAYS_END'] = (export_df['MONTH_OFFSET'] + 1) * 30
export_df = export_df[[
    'STATEMENT_LABEL', 'STATEMENT_NUMBER', 'MONTH_LABEL', 'MONTH_OFFSET', 'DAYS_START', 'DAYS_END',
    'PIE_TOTAL_COUNT', 'PIE_INCOME_COLLECTED_BY_MONTH',
    'PIE_INCOME_COLLECTION_RATE_PCT', 'NEW_INCOME_COLLECTIONS_THIS_MONTH'
]]

export_file = '/Users/Alfred.Lee/Documents/github/visualizations/pie_income_data_account_level_all_statements.csv'
export_df.to_csv(export_file, index=False)
print(f"\n✓ Account-level data (all statements) exported to: {export_file}")

# Create a summary table for Month 8 (final results)
print("\n" + "=" * 140)
print("QUICK REFERENCE - FINAL RESULTS (Month 8: 211-240 Days)")
print("=" * 140)

month_8 = df[df['MONTH_OFFSET'] == 7].sort_values('STATEMENT_NUMBER')  # Month offset 7 = Month 8

print(f"\n{'Category':<35} {'Total PIE':>12} {'Collected':>12} {'Collection Rate':>18}")
print("-" * 140)

for _, row in month_8.iterrows():
    label = row['STATEMENT_LABEL']
    total = int(row['PIE_TOTAL_COUNT'])
    collected = int(row['PIE_INCOME_COLLECTED_BY_MONTH'])
    rate = row['PIE_INCOME_COLLECTION_RATE_PCT']
    print(f"{label:<35} {total:>12,} {collected:>12,} {rate:>17.1f}%")

print("\n" + "=" * 140)
print("NOTES:")
print("- ALL LINES use ACCOUNT-LEVEL methodology (each account counted once)")
print("- Statement 18, 26, 34, 42: Unique accounts at each statement")
print("- Overall Stmt 18+: Unique accounts across all statements 18+ (deduped)")
print("- Time Windows: Month 1 = 0-30 days, Month 2 = 31-60 days, ... Month 8 = 211-240 days")
print("- Collection Rate: % of PIE accounts that collected income within that timeframe")
print("=" * 140)
