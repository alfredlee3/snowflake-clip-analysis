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

# Read the query from file
with open('/Users/Alfred.Lee/Documents/github/pie_income_update_tracking.sql', 'r') as f:
    query = f.read()

print("Running Combined Success Rate Analysis...\n")
print("=" * 120)

cursor = conn.cursor()
cursor.execute(query)
df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
cursor.close()
conn.close()

# Display results
print("RESULTS:")
print("=" * 120)
print(df.to_string(index=False))
print("\n")

# Calculate key metrics
if len(df) > 0:
    row = df.iloc[0]

    print("=" * 120)
    print("COMBINED SUCCESS RATE ANALYSIS")
    print("=" * 120)
    print(f"\nStatement Month:           {row['STMT_MONTH']}")
    print(f"Statement Number:          {int(row['STATEMENT_NUMBER'])}")

    print(f"\nTotal Population:")
    print(f"  All Accounts (APPROVED + PIE):              {int(row['TOTAL_POPULATION']):,}")

    print(f"\nBreakdown by Initial Outcome:")
    print(f"  Approved Outright:                          {int(row['APPROVED_OUTRIGHT_COUNT']):,} ({row['APPROVED_OUTRIGHT_RATE_PCT']:.1f}%)")
    print(f"  PRE_EVAL_APPROVED (PIE):                    {int(row['PIE_TOTAL_COUNT']):,} ({100.0 * row['PIE_TOTAL_COUNT'] / row['TOTAL_POPULATION']:.1f}%)")

    print(f"\nPIE Income Collection (within 8 months):")
    print(f"  Income Collected:                           {int(row['PIE_INCOME_COLLECTED_COUNT']):,} ({row['PIE_INCOME_COLLECTION_RATE_PCT']:.1f}% of PIE)")
    print(f"  Income NOT Collected:                       {int(row['PIE_INCOME_NOT_COLLECTED_COUNT']):,} ({row['PIE_INCOME_MISS_RATE_PCT']:.1f}% of PIE)")

    print(f"\n{'=' * 120}")
    print(f"OVERALL SUCCESS RATE")
    print(f"{'=' * 120}")
    print(f"\n  Success = Approved Outright OR PIE with Income Collected")
    print(f"\n  Total Success:                              {int(row['SUCCESS_COUNT']):,} accounts")
    print(f"    - Approved Outright:                      {int(row['APPROVED_OUTRIGHT_COUNT']):,}")
    print(f"    - PIE → Income Collected:                 {int(row['PIE_INCOME_COLLECTED_COUNT']):,}")
    print(f"\n  SUCCESS RATE:                               {row['SUCCESS_RATE_PCT']:.1f}%")
    print(f"  {'=' * 120}")

    print(f"\n{'=' * 120}")
    print("INTERPRETATION:")
    print("=" * 120)

    success_rate = row['SUCCESS_RATE_PCT']
    pie_income_rate = row['PIE_INCOME_COLLECTION_RATE_PCT']

    print(f"\n✓ {row['SUCCESS_RATE_PCT']:.1f}% of all accounts achieved success")
    print(f"  → {int(row['APPROVED_OUTRIGHT_COUNT']):,} approved immediately (no income barrier)")
    print(f"  → {int(row['PIE_INCOME_COLLECTED_COUNT']):,} were PIE but collected income within 8 months")

    print(f"\n⚠ {int(row['PIE_INCOME_NOT_COLLECTED_COUNT']):,} PIE accounts ({row['PIE_INCOME_MISS_RATE_PCT']:.1f}%) did NOT collect income")
    print(f"  → This represents missed opportunity")

    if pie_income_rate >= 80:
        print(f"\n✓ Strong PIE income collection ({pie_income_rate:.1f}%)")
    elif pie_income_rate >= 50:
        print(f"\n⚠ Moderate PIE income collection ({pie_income_rate:.1f}%)")
        print(f"  → Opportunity to improve through enhanced customer engagement")
    else:
        print(f"\n✗ Low PIE income collection ({pie_income_rate:.1f}%)")
        print(f"  → Significant gap in income collection process")

    print("=" * 120)

else:
    print("No results returned from query")
