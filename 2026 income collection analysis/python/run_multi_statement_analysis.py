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
with open('/Users/Alfred.Lee/Documents/github/pie_income_multi_statement_analysis.sql', 'r') as f:
    query = f.read()

print("Running Multi-Statement Income Collection Analysis...\n")
print("=" * 120)

cursor = conn.cursor()
cursor.execute(query)
df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
cursor.close()
conn.close()

# Display results
print("RESULTS - April 2025 Cohort:")
print("=" * 120)
print(df.to_string(index=False))
print("\n")

# Create a focused summary table
print("=" * 120)
print("KEY METRICS BY STATEMENT")
print("=" * 120)
print(f"\n{'Statement':<12} {'Total Pop':<12} {'PIE Count':<12} {'Success Rate':<15} {'PIE Income Collection Rate':<30}")
print("-" * 120)

for _, row in df.iterrows():
    stmt = f"Stmt {int(row['STATEMENT_NUMBER'])}"
    total_pop = f"{int(row['TOTAL_POPULATION']):,}"
    pie_count = f"{int(row['PIE_TOTAL_COUNT']):,}"
    success_rate = f"{row['SUCCESS_RATE_PCT']:.1f}%"
    pie_income_rate = f"{row['PIE_INCOME_COLLECTION_RATE_PCT']:.1f}%" if pd.notna(row['PIE_INCOME_COLLECTION_RATE_PCT']) else "N/A"

    print(f"{stmt:<12} {total_pop:<12} {pie_count:<12} {success_rate:<15} {pie_income_rate:<30}")

print("\n" + "=" * 120)
print("INSIGHTS:")
print("=" * 120)

# Calculate trends
success_rates = df['SUCCESS_RATE_PCT'].tolist()
pie_income_rates = df['PIE_INCOME_COLLECTION_RATE_PCT'].dropna().tolist()

print(f"\nSuccess Rate Range: {min(success_rates):.1f}% - {max(success_rates):.1f}%")
print(f"PIE Income Collection Rate Range: {min(pie_income_rates):.1f}% - {max(pie_income_rates):.1f}%")

# Find best/worst statements
best_success_idx = df['SUCCESS_RATE_PCT'].idxmax()
worst_success_idx = df['SUCCESS_RATE_PCT'].idxmin()
best_pie_income_idx = df['PIE_INCOME_COLLECTION_RATE_PCT'].idxmax()
worst_pie_income_idx = df['PIE_INCOME_COLLECTION_RATE_PCT'].idxmin()

print(f"\nBest Overall Success: Statement {int(df.iloc[best_success_idx]['STATEMENT_NUMBER'])} ({df.iloc[best_success_idx]['SUCCESS_RATE_PCT']:.1f}%)")
print(f"Worst Overall Success: Statement {int(df.iloc[worst_success_idx]['STATEMENT_NUMBER'])} ({df.iloc[worst_success_idx]['SUCCESS_RATE_PCT']:.1f}%)")
print(f"\nBest PIE Income Collection: Statement {int(df.iloc[best_pie_income_idx]['STATEMENT_NUMBER'])} ({df.iloc[best_pie_income_idx]['PIE_INCOME_COLLECTION_RATE_PCT']:.1f}%)")
print(f"Worst PIE Income Collection: Statement {int(df.iloc[worst_pie_income_idx]['STATEMENT_NUMBER'])} ({df.iloc[worst_pie_income_idx]['PIE_INCOME_COLLECTION_RATE_PCT']:.1f}%)")

print("=" * 120)
