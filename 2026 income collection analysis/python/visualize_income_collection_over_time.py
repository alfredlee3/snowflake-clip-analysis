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

print("Running PIE Income Collection Over Time Analysis...")

# Load time series data - STATEMENT-LEVEL (April 2025 cohort)
with open('/Users/Alfred.Lee/Documents/github/pie_income_collection_over_time.sql', 'r') as f:
    query_time_stmt = f.read()

cursor = conn.cursor()
cursor.execute(query_time_stmt)
df_time = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
cursor.close()

print("Statement-level time series loaded. Loading account-level overall data...")

# Load account-level data for Overall Stmt 18+ line
with open('/Users/Alfred.Lee/Documents/github/pie_income_collection_over_time_account_level.sql', 'r') as f:
    query_account_level = f.read()

cursor = conn.cursor()
cursor.execute(query_account_level)
df_account_level = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
cursor.close()

print("Account-level data loaded. Loading cohort comparison data...")

# Load cohort comparison data (Mar-May 2025)
with open('/Users/Alfred.Lee/Documents/github/pie_income_cohort_comparison.sql', 'r') as f:
    query_cohort = f.read()

cursor = conn.cursor()
cursor.execute(query_cohort)
df_cohort = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
cursor.close()
conn.close()

print("All data loaded. Creating visualizations...")

# Format month names for cohort data
df_cohort['MONTH_NAME'] = pd.to_datetime(df_cohort['STMT_MONTH']).dt.strftime('%b %Y')

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('PIE Income Collection Performance - Monthly Progression & Cohort Comparison',
             fontsize=16, fontweight='bold', y=0.995)

# Define colors
statement_colors = {
    18: '#e74c3c',
    26: '#3498db',
    34: '#2ecc71',
    42: '#f39c12'
}

month_colors = {
    'Mar 2025': '#e74c3c',
    'Apr 2025': '#3498db',
    'May 2025': '#2ecc71'
}

statements = sorted(df_time['STATEMENT_NUMBER'].unique())

# ============================================================================
# TOP ROW: Monthly progression over 8-month window (April 2025 cohort)
# ============================================================================

# Plot 1: Cumulative Success Rate Over Time
ax1 = axes[0, 0]
for stmt in statements:
    stmt_data = df_time[df_time['STATEMENT_NUMBER'] == stmt].sort_values('MONTH_OFFSET')
    ax1.plot(stmt_data['MONTH_OFFSET'], stmt_data['SUCCESS_RATE_PCT'],
            marker='o', linewidth=2.5, label=f'Stmt {stmt}',
            color=statement_colors[stmt], markersize=8)

ax1.set_xlabel('Months After PIE Evaluation', fontsize=11)
ax1.set_ylabel('Cumulative Success Rate (%)', fontsize=11)
ax1.set_title('Overall Success Rate Over Time - April 2025 Cohort\n(Approved Outright + PIE with Income Collected)',
             fontweight='bold', fontsize=12, pad=10)
ax1.legend(fontsize=10, loc='lower right')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(75, 100)
ax1.set_xticks(range(0, 9))

# Add annotation
ax1.text(0.02, 0.02, 'Month N = 30-day rolling windows (0-30, 31-60, 61-90... days after PIE)',
        transform=ax1.transAxes, fontsize=8, style='italic', color='gray')

# Plot 2: Cumulative PIE Income Collection Rate Over Time
ax2 = axes[0, 1]

# Track label positions to avoid overlaps
label_positions = []

def can_add_label(x, y, min_distance=3.0):
    """Check if a label can be added without overlapping existing labels"""
    for (lx, ly) in label_positions:
        if abs(lx - x) < 0.5 and abs(float(ly) - float(y)) < min_distance:
            return False
    return True

# Plot individual statement lines
for stmt in statements:
    stmt_data = df_time[df_time['STATEMENT_NUMBER'] == stmt].sort_values('MONTH_OFFSET')
    ax2.plot(stmt_data['MONTH_OFFSET'], stmt_data['PIE_INCOME_COLLECTION_RATE_PCT'],
            marker='o', linewidth=2.5, label=f'Stmt {stmt}',
            color=statement_colors[stmt], markersize=8)

    # Add labels for start and end points
    start_val = stmt_data.iloc[0]['PIE_INCOME_COLLECTION_RATE_PCT']
    end_val = stmt_data.iloc[-1]['PIE_INCOME_COLLECTION_RATE_PCT']

    # Start label (Month 0)
    if can_add_label(0, start_val):
        ax2.text(0, start_val, f'{start_val:.1f}%',
                fontsize=8, ha='right', va='center',
                color=statement_colors[stmt], fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=statement_colors[stmt], linewidth=1, alpha=0.8))
        label_positions.append((0, start_val))

    # End label (Month 8)
    if can_add_label(8, end_val):
        ax2.text(8, end_val, f'{end_val:.1f}%',
                fontsize=8, ha='left', va='center',
                color=statement_colors[stmt], fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=statement_colors[stmt], linewidth=1, alpha=0.8))
        label_positions.append((8, end_val))

# Plot overall Stmt 18+ line (ACCOUNT-LEVEL: each account counted once)
ax2.plot(df_account_level['MONTH_OFFSET'], df_account_level['PIE_INCOME_COLLECTION_RATE_PCT'],
        marker='s', linewidth=3, label='Overall Stmt 18+ (Acct-Level)',
        color='black', markersize=10, linestyle='--', alpha=0.7)

# Add labels for overall line
overall_start = df_account_level.iloc[0]['PIE_INCOME_COLLECTION_RATE_PCT']
overall_end = df_account_level.iloc[-1]['PIE_INCOME_COLLECTION_RATE_PCT']

if can_add_label(0, overall_start):
    ax2.text(0, overall_start, f'{overall_start:.1f}%',
            fontsize=8, ha='right', va='center',
            color='black', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black', linewidth=1.5, alpha=0.9))
    label_positions.append((0, overall_start))

if can_add_label(8, overall_end):
    ax2.text(8, overall_end, f'{overall_end:.1f}%',
            fontsize=8, ha='left', va='center',
            color='black', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black', linewidth=1.5, alpha=0.9))
    label_positions.append((8, overall_end))

ax2.set_xlabel('Months After PIE Evaluation', fontsize=11)
ax2.set_ylabel('Cumulative PIE Income Collection Rate (%)', fontsize=11)
ax2.set_title('PIE Income Collection Rate Over Time - April 2025 Cohort\n(% of PIE Accounts That Collected Income by Month N)',
             fontweight='bold', fontsize=12, pad=10)
ax2.legend(fontsize=10, loc='lower right')
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 100)
ax2.set_xticks(range(0, 9))

# ============================================================================
# BOTTOM ROW: Cohort comparison (Mar-May 2025)
# ============================================================================

# Plot 3: Success Rate by Statement (grouped by month)
ax3 = axes[1, 0]
x = np.arange(len(statements))
width = 0.25

for i, month in enumerate(['Mar 2025', 'Apr 2025', 'May 2025']):
    month_data = df_cohort[df_cohort['MONTH_NAME'] == month].sort_values('STATEMENT_NUMBER')
    values = month_data['SUCCESS_RATE_PCT'].values
    ax3.bar(x + i*width, values, width, label=month, color=month_colors[month], edgecolor='black', linewidth=1)

    # Add value labels
    for j, val in enumerate(values):
        ax3.text(x[j] + i*width, float(val) + 0.5, f'{float(val):.1f}%',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

ax3.set_xlabel('Statement Number', fontsize=11)
ax3.set_ylabel('Success Rate (%)', fontsize=11)
ax3.set_title('Overall Success Rate by Statement - Multi-Cohort Comparison\n(8 Months After PIE: Approved Outright + PIE with Income Collected)',
             fontweight='bold', fontsize=12, pad=10)
ax3.set_xticks(x + width)
ax3.set_xticklabels([f'Stmt {s}' for s in statements])
ax3.legend(title='Cohort Month', fontsize=10)
ax3.grid(True, alpha=0.3, axis='y')
ax3.set_ylim(80, 100)

# Plot 4: PIE Income Collection Rate by Statement (grouped by month)
ax4 = axes[1, 1]

for i, month in enumerate(['Mar 2025', 'Apr 2025', 'May 2025']):
    month_data = df_cohort[df_cohort['MONTH_NAME'] == month].sort_values('STATEMENT_NUMBER')
    values = month_data['PIE_INCOME_COLLECTION_RATE_PCT'].values
    ax4.bar(x + i*width, values, width, label=month, color=month_colors[month], edgecolor='black', linewidth=1)

    # Add value labels
    for j, val in enumerate(values):
        if pd.notna(val):
            ax4.text(x[j] + i*width, float(val) + 1, f'{float(val):.1f}%',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

ax4.set_xlabel('Statement Number', fontsize=11)
ax4.set_ylabel('PIE Income Collection Rate (%)', fontsize=11)
ax4.set_title('PIE Income Collection Rate by Statement - Multi-Cohort Comparison\n(8 Months After PIE: % of PIE Accounts That Updated Income)',
             fontweight='bold', fontsize=12, pad=10)
ax4.set_xticks(x + width)
ax4.set_xticklabels([f'Stmt {s}' for s in statements])
ax4.legend(title='Cohort Month', fontsize=10)
ax4.grid(True, alpha=0.3, axis='y')
ax4.set_ylim(40, 100)

plt.tight_layout()

# Save the plot
output_file = '/Users/Alfred.Lee/Documents/github/visualizations/pie_income_collection_over_time.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\nVisualization saved to: {output_file}")

# Display summary statistics
print("\n" + "=" * 120)
print("SUMMARY: MONTHLY PROGRESSION BY STATEMENT (April 2025 Cohort)")
print("=" * 120)

for stmt in statements:
    print(f"\n{'=' * 120}")
    print(f"STATEMENT {stmt}")
    print(f"{'=' * 120}")

    stmt_data = df_time[df_time['STATEMENT_NUMBER'] == stmt].sort_values('MONTH_OFFSET')

    print(f"\n{'Month':<8} {'Success Rate':<15} {'PIE Income Rate':<20} {'New Collections':<20} {'Cumulative Collections':<25}")
    print("-" * 120)

    for _, row in stmt_data.iterrows():
        month = f"Month {int(row['MONTH_OFFSET'])}"
        success = f"{row['SUCCESS_RATE_PCT']:.1f}%"
        pie_rate = f"{row['PIE_INCOME_COLLECTION_RATE_PCT']:.1f}%"
        new_coll = f"{int(row['NEW_INCOME_COLLECTIONS_THIS_MONTH']):,}"
        cum_coll = f"{int(row['PIE_INCOME_COLLECTED_BY_MONTH']):,}"

        print(f"{month:<8} {success:<15} {pie_rate:<20} {new_coll:<20} {cum_coll:<25}")

# Key insights
print("\n" + "=" * 120)
print("KEY INSIGHTS - TIME SERIES (April 2025)")
print("=" * 120)

for stmt in statements:
    stmt_data = df_time[df_time['STATEMENT_NUMBER'] == stmt].sort_values('MONTH_OFFSET')

    # Find month with most activity
    max_activity_row = stmt_data.loc[stmt_data['NEW_INCOME_COLLECTIONS_THIS_MONTH'].idxmax()]
    max_month = int(max_activity_row['MONTH_OFFSET'])
    max_count = int(max_activity_row['NEW_INCOME_COLLECTIONS_THIS_MONTH'])

    # Final results
    final_row = stmt_data[stmt_data['MONTH_OFFSET'] == 8].iloc[0]
    final_success = final_row['SUCCESS_RATE_PCT']
    final_pie_rate = final_row['PIE_INCOME_COLLECTION_RATE_PCT']

    # Month 1 vs Month 8
    month_1_pie_rate = stmt_data[stmt_data['MONTH_OFFSET'] == 1].iloc[0]['PIE_INCOME_COLLECTION_RATE_PCT']

    print(f"\nStatement {stmt}:")
    print(f"  • Peak activity: Month {max_month} ({max_count:,} new collections)")
    print(f"  • Final success rate (Month 8): {final_success:.1f}%")
    print(f"  • Final PIE income collection rate: {final_pie_rate:.1f}%")
    print(f"  • Early momentum (Month 1): {month_1_pie_rate:.1f}% of PIE accounts collected income")
    print(f"  • Late momentum (Month 1 to 8 gain): +{final_pie_rate - month_1_pie_rate:.1f}pp")

print("\n" + "=" * 120)
print("ACCOUNT-LEVEL OVERALL PERFORMANCE (April 2025 - Unique Accounts)")
print("=" * 120)

print(f"\nTotal Unique PIE Accounts (Stmt 18+): {int(df_account_level.iloc[0]['PIE_TOTAL_COUNT']):,}")
print(f"\nMonthly Progression:")
print(f"{'Month':<8} {'Collected':>10} {'Collection Rate':>18} {'New This Month':>18}")
print("-" * 120)
for _, row in df_account_level.iterrows():
    month = f"Month {int(row['MONTH_OFFSET'])}"
    collected = f"{int(row['PIE_INCOME_COLLECTED_BY_MONTH']):,}"
    rate = f"{row['PIE_INCOME_COLLECTION_RATE_PCT']:.1f}%"
    new_coll = f"{int(row['NEW_INCOME_COLLECTIONS_THIS_MONTH']):,}"
    print(f"{month:<8} {collected:>10} {rate:>18} {new_coll:>18}")

print("\n" + "=" * 120)
print("COHORT COMPARISON - FINAL RESULTS (Mar-May 2025, Month 8)")
print("=" * 120)

for month in ['Mar 2025', 'Apr 2025', 'May 2025']:
    print(f"\n{month}:")
    print("-" * 120)
    month_data = df_cohort[df_cohort['MONTH_NAME'] == month].sort_values('STATEMENT_NUMBER')

    for _, row in month_data.iterrows():
        stmt = f"Stmt {int(row['STATEMENT_NUMBER'])}"
        success = f"{row['SUCCESS_RATE_PCT']:.1f}%"
        pie_income = f"{row['PIE_INCOME_COLLECTION_RATE_PCT']:.1f}%" if pd.notna(row['PIE_INCOME_COLLECTION_RATE_PCT']) else "N/A"
        pop = f"{int(row['TOTAL_POPULATION']):,}"
        pie_count = f"{int(row['PIE_TOTAL_COUNT']):,}"

        print(f"  {stmt}: Pop={pop:>6}, PIE={pie_count:>6}, Success={success:>6}, PIE Income Collection={pie_income:>6}")

print("\n" + "=" * 120)
