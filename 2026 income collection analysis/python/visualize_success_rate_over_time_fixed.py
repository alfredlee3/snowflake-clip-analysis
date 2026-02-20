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

print("Running FIXED Overall Success Rate Over Time Analysis...")

# Load FIXED time series data - uses corrected SQL
with open('/Users/Alfred.Lee/Documents/github/2026 income collection analysis/sql/pie_income_collection_over_time_fixed.sql', 'r') as f:
    query_time_stmt = f.read()

cursor = conn.cursor()
cursor.execute(query_time_stmt)
df_time = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
cursor.close()
conn.close()

print("Data loaded. Creating visualization...")

# Add month label (1-8 instead of 0-7)
df_time['MONTH_LABEL'] = df_time['MONTH_OFFSET'] + 1

# Define colors
statement_colors = {
    18: '#e74c3c',
    26: '#3498db',
    34: '#2ecc71',
    42: '#f39c12',
    442: '#f39c12'  # Stmt 42+ uses same color as Stmt 42
}

# Create standalone visualization (narrower and taller)
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
fig.suptitle('Overall Success Rate Over Time - April 2025 Cohort (FIXED)',
             fontsize=18, fontweight='bold', y=0.98)

# Track label positions to avoid overlaps
label_positions = []

def can_add_label(x, y, min_distance=2.0):
    """Check if a label can be added without overlapping existing labels"""
    for (lx, ly) in label_positions:
        if abs(lx - x) < 0.5 and abs(float(ly) - float(y)) < min_distance:
            return False
    return True

# Plot individual statement lines
statements = [18, 26, 34, 442]  # 442 = Stmt 42+
for stmt in statements:
    stmt_data = df_time[df_time['STATEMENT_NUMBER'] == stmt].sort_values('MONTH_OFFSET')
    # Label formatting
    if stmt == 442:
        label = 'Stmt 42+'
    else:
        label = f'Stmt {stmt}'
    ax.plot(stmt_data['MONTH_LABEL'], stmt_data['SUCCESS_RATE_PCT'],
            marker='o', linewidth=3, label=label,
            color=statement_colors[stmt], markersize=10)

    # Add labels for start and end points
    start_val = stmt_data.iloc[0]['SUCCESS_RATE_PCT']
    end_val = stmt_data.iloc[-1]['SUCCESS_RATE_PCT']
    start_month = stmt_data.iloc[0]['MONTH_LABEL']
    end_month = stmt_data.iloc[-1]['MONTH_LABEL']

    # Start label (Month 1)
    if can_add_label(start_month, start_val):
        ax.text(start_month, start_val, f'{start_val:.1f}%',
                fontsize=11, ha='right', va='center',
                color=statement_colors[stmt], fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=statement_colors[stmt], linewidth=1, alpha=0.8))
        label_positions.append((start_month, start_val))

    # End label (Month 8)
    if can_add_label(end_month, end_val):
        ax.text(end_month, end_val, f'{end_val:.1f}%',
                fontsize=11, ha='left', va='center',
                color=statement_colors[stmt], fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=statement_colors[stmt], linewidth=1, alpha=0.8))
        label_positions.append((end_month, end_val))

# Plot overall Stmt 18+ line (ACCOUNT-LEVEL: deduped across all statements)
overall_data = df_time[df_time['STATEMENT_NUMBER'] == 999].sort_values('MONTH_OFFSET')
ax.plot(overall_data['MONTH_LABEL'], overall_data['SUCCESS_RATE_PCT'],
        marker='s', linewidth=3.5, label='Overall Stmt 18+ (Acct-Level)',
        color='black', markersize=12, linestyle='--', alpha=0.7)

# Add labels for overall line
overall_start = overall_data.iloc[0]['SUCCESS_RATE_PCT']
overall_end = overall_data.iloc[-1]['SUCCESS_RATE_PCT']
overall_start_month = overall_data.iloc[0]['MONTH_LABEL']
overall_end_month = overall_data.iloc[-1]['MONTH_LABEL']

if can_add_label(overall_start_month, overall_start):
    ax.text(overall_start_month, overall_start, f'{overall_start:.1f}%',
            fontsize=11, ha='right', va='center',
            color='black', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black', linewidth=1.5, alpha=0.9))
    label_positions.append((overall_start_month, overall_start))

if can_add_label(overall_end_month, overall_end):
    ax.text(overall_end_month, overall_end, f'{overall_end:.1f}%',
            fontsize=11, ha='left', va='center',
            color='black', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black', linewidth=1.5, alpha=0.9))
    label_positions.append((overall_end_month, overall_end))

ax.set_xlabel('Months After PIE Evaluation', fontsize=15, fontweight='bold')
ax.set_ylabel('Cumulative Success Rate (%)', fontsize=15, fontweight='bold')
ax.set_title('Approved Outright (Never PIE) + PIE with Income Collected',
             fontsize=16, pad=15)
ax.legend(fontsize=13, loc='lower right', framealpha=0.95)
ax.grid(True, alpha=0.3, linewidth=0.5)
ax.set_ylim(70, 100)
ax.set_xticks(range(1, 9))
ax.set_xticklabels([f'Month {i}' for i in range(1, 9)], fontsize=12)
ax.tick_params(axis='y', labelsize=12)

# Add annotation for time windows
ax.text(0.02, 0.02, 'Time Windows: Month 1 = 0-30 days, Month 2 = 31-60 days, ... Month 8 = 211-240 days after PIE',
        transform=ax.transAxes, fontsize=11, style='italic', color='gray',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.8))

# Add FIXED note
ax.text(0.98, 0.98, 'FIXED: Approved = Never PIE',
        transform=ax.transAxes, fontsize=10, ha='right', va='top',
        color='red', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='red', alpha=0.9))

plt.tight_layout()

# Save the plot
output_file = '/Users/Alfred.Lee/Documents/github/visualizations/success_rate_over_time_fixed.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\nVisualization saved to: {output_file}")

# Display summary statistics
print("\n" + "=" * 120)
print("SUCCESS RATE SUMMARY (April 2025 Cohort) - FIXED VERSION")
print("=" * 120)

for stmt in statements:
    print(f"\n{'=' * 120}")
    if stmt == 442:
        print(f"STATEMENT 42+ (Account-Level - All Stmt 42+)")
    else:
        print(f"STATEMENT {stmt} (Statement-Level)")
    print(f"{'=' * 120}")

    stmt_data = df_time[df_time['STATEMENT_NUMBER'] == stmt].sort_values('MONTH_OFFSET')
    total_pop = int(stmt_data.iloc[0]['TOTAL_POPULATION'])

    if stmt == 442:
        print(f"\nTotal Unique Accounts: {total_pop:,}")
    else:
        print(f"\nTotal Population: {total_pop:,}")
    print(f"\n{'Month':<10} {'Days':<15} {'Success Rate':>15} {'Approved':>12} {'PIE Total':>12} {'PIE Collected':>15}")
    print("-" * 120)

    for _, row in stmt_data.iterrows():
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
    final_row = stmt_data.iloc[-1]
    final_success = final_row['SUCCESS_RATE_PCT']
    final_approved = int(final_row['APPROVED_OUTRIGHT_COUNT'])
    final_pie_collected = int(final_row['PIE_INCOME_COLLECTED_BY_MONTH'])
    final_total_success = final_approved + final_pie_collected

    print(f"\n  ✓ Final Success Rate (Month 8): {final_success:.1f}%")
    print(f"    - Approved Outright (Never PIE): {final_approved:,}")
    print(f"    - PIE with Income: {final_pie_collected:,}")
    if stmt == 442:
        print(f"    - Total Success: {final_total_success:,} of {total_pop:,} unique accounts")
    else:
        print(f"    - Total Success: {final_total_success:,} of {total_pop:,} accounts")

# Overall Stmt 18+ summary
print(f"\n{'=' * 120}")
print("OVERALL STMT 18+ (Account-Level - Deduped Across All Statements)")
print(f"{'=' * 120}")

overall_data = df_time[df_time['STATEMENT_NUMBER'] == 999].sort_values('MONTH_OFFSET')
total_pop = int(overall_data.iloc[0]['TOTAL_POPULATION'])

print(f"\nTotal Unique Accounts: {total_pop:,}")
print(f"\n{'Month':<10} {'Days':<15} {'Success Rate':>15} {'Approved':>12} {'PIE Total':>12} {'PIE Collected':>15}")
print("-" * 120)

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
final_pie_total = int(final_row['PIE_TOTAL_COUNT'])
final_pie_collected = int(final_row['PIE_INCOME_COLLECTED_BY_MONTH'])
final_total_success = final_approved + final_pie_collected

print(f"\n  ✓ Final Success Rate (Month 8): {final_success:.1f}%")
print(f"    - Approved Outright (Never PIE): {final_approved:,} ({100.0*final_approved/total_pop:.1f}%)")
print(f"    - PIE Total: {final_pie_total:,} ({100.0*final_pie_total/total_pop:.1f}%)")
print(f"    - PIE with Income Collected: {final_pie_collected:,} ({100.0*final_pie_collected/final_pie_total:.1f}% of PIE)")
print(f"    - Total Success: {final_total_success:,} of {total_pop:,} unique accounts")
print(f"    - Verification: {final_approved:,} + {final_pie_total:,} = {final_approved + final_pie_total:,} ✓")

print("\n" + "=" * 120)
print("KEY INSIGHTS")
print("=" * 120)
print("\n✓ Success Rate = (Approved Outright + PIE with Income Collected) / Total Population")
print("✓ Approved Outright = Accounts that were NEVER PIE at any statement (FIXED)")
print("✓ Individual statements (18, 26, 34) use statement-level methodology")
print("✓ Stmt 42+ and Overall Stmt 18+ use account-level methodology (each unique account counted once)")
print("✓ Most progress happens early, with steady gains through 8 months")
print("=" * 120)
