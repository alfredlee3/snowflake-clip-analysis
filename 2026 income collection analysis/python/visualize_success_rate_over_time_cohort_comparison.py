import snowflake.connector
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Snowflake connection
conn = snowflake.connector.connect(
    user='ALFRED_LEE',
    account='IJ90379-MISSIONLANE',
    authenticator='externalbrowser',
    database='EDW_DB',
    schema='PUBLIC'
)

print("Running Multi-Cohort Success Rate Comparison...")

# Load SQL query template
with open('/Users/Alfred.Lee/Documents/github/2026 income collection analysis/sql/pie_income_collection_over_time.sql', 'r') as f:
    query_template = f.read()

# Define cohorts to analyze
cohorts = {
    'Mar 2025': '2025-03-01',
    'Apr 2025': '2025-04-01',
    'May 2025': '2025-05-01'
}

# Load data for each cohort
cohort_data = {}
cursor = conn.cursor()

for cohort_name, cohort_date in cohorts.items():
    print(f"Loading data for {cohort_name}...")

    # Replace the date in the query
    query = query_template.replace("'2025-04-01'", f"'{cohort_date}'")

    cursor.execute(query)
    df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
    df['MONTH_LABEL'] = df['MONTH_OFFSET'] + 1
    df['COHORT'] = cohort_name
    cohort_data[cohort_name] = df

cursor.close()
conn.close()

print("\nData loaded. Creating visualizations...")

# Combine all cohort data
df_all = pd.concat(cohort_data.values(), ignore_index=True)

# Define colors
cohort_colors = {
    'Mar 2025': '#e74c3c',  # Red
    'Apr 2025': '#3498db',  # Blue
    'May 2025': '#2ecc71'   # Green
}

statement_colors = {
    18: '#e74c3c',
    26: '#3498db',
    34: '#2ecc71',
    442: '#f39c12'
}

# Create figure with two subplots
fig = plt.figure(figsize=(20, 10))
gs = fig.add_gridspec(1, 2, hspace=0.3, wspace=0.25)

# ============================================================================
# LEFT PLOT: April 2025 Cohort Detail (Individual Statements + Overall)
# ============================================================================
ax1 = fig.add_subplot(gs[0, 0])

df_apr = cohort_data['Apr 2025']

# Plot individual statement lines for April 2025
statements = [18, 26, 34, 442]
for stmt in statements:
    stmt_data = df_apr[df_apr['STATEMENT_NUMBER'] == stmt].sort_values('MONTH_OFFSET')
    if len(stmt_data) == 0:
        continue

    label = 'Stmt 42+' if stmt == 442 else f'Stmt {stmt}'
    ax1.plot(stmt_data['MONTH_LABEL'], stmt_data['SUCCESS_RATE_PCT'],
            marker='o', linewidth=2.5, label=label,
            color=statement_colors[stmt], markersize=8)

# Plot overall line for April 2025
overall_apr = df_apr[df_apr['STATEMENT_NUMBER'] == 999].sort_values('MONTH_OFFSET')
ax1.plot(overall_apr['MONTH_LABEL'], overall_apr['SUCCESS_RATE_PCT'],
        marker='s', linewidth=3, label='Overall Stmt 18+',
        color='black', markersize=10, linestyle='--', alpha=0.7)

ax1.set_xlabel('Months After PIE Evaluation', fontsize=14, fontweight='bold')
ax1.set_ylabel('Cumulative Success Rate (%)', fontsize=14, fontweight='bold')
ax1.set_title('April 2025 Cohort - Statement Detail\n(Approved Outright + PIE with Income)',
             fontsize=15, fontweight='bold', pad=15)
ax1.legend(fontsize=11, loc='lower right', framealpha=0.95)
ax1.grid(True, alpha=0.3, linewidth=0.5)
ax1.set_ylim(70, 100)
ax1.set_xticks(range(1, 9))
ax1.set_xticklabels([f'Month {i}' for i in range(1, 9)], fontsize=11)
ax1.tick_params(axis='y', labelsize=11)

# ============================================================================
# RIGHT PLOT: Cohort Comparison (Overall Stmt 18+ Only)
# ============================================================================
ax2 = fig.add_subplot(gs[0, 1])

# Plot Overall Stmt 18+ line for each cohort
for cohort_name, color in cohort_colors.items():
    df_cohort = cohort_data[cohort_name]
    overall_data = df_cohort[df_cohort['STATEMENT_NUMBER'] == 999].sort_values('MONTH_OFFSET')

    if len(overall_data) == 0:
        continue

    ax2.plot(overall_data['MONTH_LABEL'], overall_data['SUCCESS_RATE_PCT'],
            marker='o', linewidth=3, label=cohort_name,
            color=color, markersize=10)

    # Add end label
    end_val = overall_data.iloc[-1]['SUCCESS_RATE_PCT']
    end_month = overall_data.iloc[-1]['MONTH_LABEL']
    ax2.text(end_month + 0.1, end_val, f'{end_val:.1f}%',
            fontsize=11, ha='left', va='center',
            color=color, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color, linewidth=1.5, alpha=0.9))

ax2.set_xlabel('Months After PIE Evaluation', fontsize=14, fontweight='bold')
ax2.set_ylabel('Cumulative Success Rate (%)', fontsize=14, fontweight='bold')
ax2.set_title('Cohort Comparison - Overall Stmt 18+\n(Account-Level: Each Account Counted Once)',
             fontsize=15, fontweight='bold', pad=15)
ax2.legend(fontsize=12, loc='lower right', framealpha=0.95)
ax2.grid(True, alpha=0.3, linewidth=0.5)
ax2.set_ylim(70, 100)
ax2.set_xticks(range(1, 9))
ax2.set_xticklabels([f'Month {i}' for i in range(1, 9)], fontsize=11)
ax2.tick_params(axis='y', labelsize=11)

# Main title
fig.suptitle('PIE Success Rate Analysis - Multi-Cohort Comparison',
             fontsize=18, fontweight='bold', y=0.98)

# Add annotation
fig.text(0.5, 0.02, 'Time Windows: Month 1 = 0-30 days, Month 2 = 31-60 days, ... Month 8 = 211-240 days after PIE | Success = Approved Outright OR PIE with Income Collected',
         ha='center', fontsize=11, style='italic', color='gray',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.8))

plt.tight_layout()

# Save the plot
output_file = '/Users/Alfred.Lee/Documents/github/visualizations/success_rate_cohort_comparison.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\nVisualization saved to: {output_file}")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("\n" + "=" * 140)
print("SUCCESS RATE SUMMARY - MULTI-COHORT COMPARISON")
print("=" * 140)

for cohort_name in ['Mar 2025', 'Apr 2025', 'May 2025']:
    print(f"\n{'=' * 140}")
    print(f"COHORT: {cohort_name}")
    print(f"{'=' * 140}")

    df_cohort = cohort_data[cohort_name]
    overall_data = df_cohort[df_cohort['STATEMENT_NUMBER'] == 999].sort_values('MONTH_OFFSET')

    if len(overall_data) == 0:
        print("No data available for this cohort")
        continue

    total_pop = int(overall_data.iloc[0]['TOTAL_POPULATION'])
    print(f"\nTotal Unique Accounts (Overall Stmt 18+): {total_pop:,}")

    print(f"\n{'Month':<10} {'Days':<15} {'Success Rate':>15} {'Approved':>12} {'PIE Total':>12} {'PIE Collected':>15}")
    print("-" * 140)

    for _, row in overall_data.iterrows():
        month_label = int(row['MONTH_LABEL'])
        days_start = int(row['MONTH_OFFSET']) * 30
        days_end = (int(row['MONTH_OFFSET']) + 1) * 30
        days = f"{days_start}-{days_end}"
        success_rate = f"{row['SUCCESS_RATE_PCT']:.1f}%"
        approved = f"{int(row['APPROVED_OUTRIGHT_COUNT']):,}"
        pie_total = f"{int(row['PIE_TOTAL_COUNT']):,}"
        pie_collected = f"{int(row['PIE_INCOME_COLLECTED_BY_MONTH']):,}"

        print(f"Month {month_label:<4} {days:<15} {success_rate:>15} {approved:>12} {pie_total:>12} {pie_collected:>15}")

    # Final results
    final_row = overall_data.iloc[-1]
    final_success = final_row['SUCCESS_RATE_PCT']
    final_approved = int(final_row['APPROVED_OUTRIGHT_COUNT'])
    final_pie_collected = int(final_row['PIE_INCOME_COLLECTED_BY_MONTH'])
    final_total_success = final_approved + final_pie_collected

    print(f"\n  ✓ Final Success Rate (Month 8): {final_success:.1f}%")
    print(f"    - Approved Outright: {final_approved:,}")
    print(f"    - PIE with Income: {final_pie_collected:,}")
    print(f"    - Total Success: {final_total_success:,} of {total_pop:,} unique accounts")

# Cohort comparison table
print(f"\n{'=' * 140}")
print("COHORT COMPARISON - MONTH 8 (211-240 Days After PIE)")
print(f"{'=' * 140}")

print(f"\n{'Cohort':<15} {'Total Accounts':>15} {'Success Rate':>15} {'Approved':>12} {'PIE w/ Income':>15}")
print("-" * 140)

for cohort_name in ['Mar 2025', 'Apr 2025', 'May 2025']:
    df_cohort = cohort_data[cohort_name]
    overall_data = df_cohort[df_cohort['STATEMENT_NUMBER'] == 999].sort_values('MONTH_OFFSET')

    if len(overall_data) > 0:
        final_row = overall_data.iloc[-1]
        total_pop = int(overall_data.iloc[0]['TOTAL_POPULATION'])
        success_rate = f"{final_row['SUCCESS_RATE_PCT']:.1f}%"
        approved = f"{int(final_row['APPROVED_OUTRIGHT_COUNT']):,}"
        pie_collected = f"{int(final_row['PIE_INCOME_COLLECTED_BY_MONTH']):,}"

        print(f"{cohort_name:<15} {total_pop:>15,} {success_rate:>15} {approved:>12} {pie_collected:>15}")

print("\n" + "=" * 140)
print("KEY INSIGHTS")
print("=" * 140)
print("\n✓ Success Rate = (Approved Outright + PIE with Income Collected) / Total Population")
print("✓ All cohorts use 30-day rolling windows for fair time comparison")
print("✓ Overall Stmt 18+ uses account-level methodology (each account counted once)")
print("✓ Cohort consistency validates the reliability of PIE income collection patterns")
print("=" * 140)
