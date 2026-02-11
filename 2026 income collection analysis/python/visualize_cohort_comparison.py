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

# Read the query from file
with open('/Users/Alfred.Lee/Documents/github/pie_income_cohort_comparison.sql', 'r') as f:
    query = f.read()

print("Running Multi-Cohort Comparison Analysis...")

cursor = conn.cursor()
cursor.execute(query)
df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
cursor.close()
conn.close()

print("Query completed. Creating visualizations...")

# Format month names
df['MONTH_NAME'] = pd.to_datetime(df['STMT_MONTH']).dt.strftime('%b %Y')

# Create visualizations
fig = plt.figure(figsize=(18, 14))
gs = fig.add_gridspec(3, 2, height_ratios=[0.15, 1, 1], hspace=0.35, wspace=0.3)

# Header section with explanations
ax_header = fig.add_subplot(gs[0, :])
ax_header.axis('off')

header_text = """PIE Income Collection Performance - Multi-Cohort Comparison (Mar-May 2025)

KEY METRICS EXPLAINED:
• Success Rate = (Approved Outright + PIE with Income Collected) / Total Population
  ➜ "% of accounts that either had no income barrier OR successfully overcame it"

• PIE Income Collection Rate = PIE with Income Collected / Total PIE Accounts
  ➜ "Of PIE accounts (blocked ONLY by stale income), % that updated income within 8 months"

MEASUREMENT WINDOW: All metrics track 8 months after initial evaluation (240 days)
PIE (PRE_EVAL_APPROVED) = Account blocked ONLY by stale income requirement (applies at Statement 18+)"""

ax_header.text(0.5, 0.5, header_text,
              ha='center', va='center', fontsize=10, family='monospace',
              bbox=dict(boxstyle='round,pad=1', facecolor='lightblue', alpha=0.3, edgecolor='black', linewidth=2))

fig.suptitle('', fontsize=1)  # Remove default suptitle

# Create the 4 main plots
ax1 = fig.add_subplot(gs[1, 0])
ax2 = fig.add_subplot(gs[1, 1])
ax3 = fig.add_subplot(gs[2, 0])
ax4 = fig.add_subplot(gs[2, 1])

# Define colors for each month
month_colors = {
    'Mar 2025': '#e74c3c',
    'Apr 2025': '#3498db',
    'May 2025': '#2ecc71'
}

statements = sorted(df['STATEMENT_NUMBER'].unique())

# Plot 1: Success Rate by Statement (grouped by month)
x = np.arange(len(statements))
width = 0.25

for i, month in enumerate(['Mar 2025', 'Apr 2025', 'May 2025']):
    month_data = df[df['MONTH_NAME'] == month].sort_values('STATEMENT_NUMBER')
    values = month_data['SUCCESS_RATE_PCT'].values
    ax1.bar(x + i*width, values, width, label=month, color=month_colors[month], edgecolor='black', linewidth=1)

    # Add value labels
    for j, val in enumerate(values):
        ax1.text(x[j] + i*width, float(val) + 0.5, f'{float(val):.1f}%',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

ax1.set_xlabel('Statement Number', fontsize=11)
ax1.set_ylabel('Success Rate (%)', fontsize=11)
ax1.set_title('Overall Success Rate by Statement\n(Approved Outright + PIE with Income Collected)',
             fontweight='bold', fontsize=12, pad=10)
ax1.set_xticks(x + width)
ax1.set_xticklabels([f'Stmt {s}' for s in statements])
ax1.legend(title='Cohort Month', fontsize=10)
ax1.grid(True, alpha=0.3, axis='y')
ax1.set_ylim(80, 100)
# Add interpretation note
ax1.text(0.5, 0.02, 'Higher = Better overall performance (fewer accounts stuck at PIE without income)',
        transform=ax1.transAxes, ha='center', fontsize=8, style='italic', color='gray')

# Plot 2: PIE Income Collection Rate by Statement (grouped by month)
for i, month in enumerate(['Mar 2025', 'Apr 2025', 'May 2025']):
    month_data = df[df['MONTH_NAME'] == month].sort_values('STATEMENT_NUMBER')
    values = month_data['PIE_INCOME_COLLECTION_RATE_PCT'].values
    ax2.bar(x + i*width, values, width, label=month, color=month_colors[month], edgecolor='black', linewidth=1)

    # Add value labels
    for j, val in enumerate(values):
        if pd.notna(val):
            ax2.text(x[j] + i*width, float(val) + 1, f'{float(val):.1f}%',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

ax2.set_xlabel('Statement Number', fontsize=11)
ax2.set_ylabel('PIE Income Collection Rate (%)', fontsize=11)
ax2.set_title('PIE Income Collection Rate by Statement\n(% of PIE Accounts That Updated Income in 8 Months)',
             fontweight='bold', fontsize=12, pad=10)
ax2.set_xticks(x + width)
ax2.set_xticklabels([f'Stmt {s}' for s in statements])
ax2.legend(title='Cohort Month', fontsize=10)
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_ylim(40, 100)
# Add interpretation note
ax2.text(0.5, 0.02, 'Higher = More effective income collection from PIE accounts',
        transform=ax2.transAxes, ha='center', fontsize=8, style='italic', color='gray')

# Plot 3: Trend Lines - Success Rate Across Statements
for month in ['Mar 2025', 'Apr 2025', 'May 2025']:
    month_data = df[df['MONTH_NAME'] == month].sort_values('STATEMENT_NUMBER')
    ax3.plot(month_data['STATEMENT_NUMBER'], month_data['SUCCESS_RATE_PCT'],
            marker='o', linewidth=2, label=month, color=month_colors[month], markersize=8)

ax3.set_xlabel('Statement Number', fontsize=11)
ax3.set_ylabel('Success Rate (%)', fontsize=11)
ax3.set_title('Success Rate Trend Across Statements\n(Declining trend shows increasing difficulty at later statements)',
             fontweight='bold', fontsize=12, pad=10)
ax3.legend(title='Cohort Month', fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.set_ylim(80, 100)
# Highlight the trend
ax3.axhline(y=90, color='red', linestyle='--', alpha=0.3, linewidth=1)
ax3.text(statements[-1], 90.5, '90% threshold', fontsize=8, color='red', ha='right')

# Plot 4: Trend Lines - PIE Income Collection Rate Across Statements
for month in ['Mar 2025', 'Apr 2025', 'May 2025']:
    month_data = df[df['MONTH_NAME'] == month].sort_values('STATEMENT_NUMBER')
    ax4.plot(month_data['STATEMENT_NUMBER'], month_data['PIE_INCOME_COLLECTION_RATE_PCT'],
            marker='o', linewidth=2, label=month, color=month_colors[month], markersize=8)

ax4.set_xlabel('Statement Number', fontsize=11)
ax4.set_ylabel('PIE Income Collection Rate (%)', fontsize=11)
ax4.set_title('PIE Income Collection Trend Across Statements\n(Sharp drop after Stmt 18 indicates engagement challenges)',
             fontweight='bold', fontsize=12, pad=10)
ax4.legend(title='Cohort Month', fontsize=10)
ax4.grid(True, alpha=0.3)
ax4.set_ylim(40, 100)
# Highlight key thresholds
ax4.axhline(y=80, color='green', linestyle='--', alpha=0.3, linewidth=1)
ax4.text(statements[-1], 80.5, 'Strong (80%)', fontsize=8, color='green', ha='right')
ax4.axhline(y=50, color='orange', linestyle='--', alpha=0.3, linewidth=1)
ax4.text(statements[-1], 50.5, 'Moderate (50%)', fontsize=8, color='orange', ha='right')

# No tight_layout needed since we used gridspec with manual spacing

# Save the plot
output_file = '/Users/Alfred.Lee/Documents/github/visualizations/pie_cohort_comparison_visualization.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\nVisualization saved to: {output_file}")

# Display summary statistics
print("\n" + "=" * 120)
print("SUMMARY STATISTICS BY COHORT")
print("=" * 120)

for month in ['Mar 2025', 'Apr 2025', 'May 2025']:
    print(f"\n{month}:")
    print("-" * 120)
    month_data = df[df['MONTH_NAME'] == month].sort_values('STATEMENT_NUMBER')

    for _, row in month_data.iterrows():
        stmt = f"Stmt {int(row['STATEMENT_NUMBER'])}"
        success = f"{row['SUCCESS_RATE_PCT']:.1f}%"
        pie_income = f"{row['PIE_INCOME_COLLECTION_RATE_PCT']:.1f}%" if pd.notna(row['PIE_INCOME_COLLECTION_RATE_PCT']) else "N/A"
        pop = f"{int(row['TOTAL_POPULATION']):,}"
        pie_count = f"{int(row['PIE_TOTAL_COUNT']):,}"

        print(f"  {stmt}: Pop={pop:>6}, PIE={pie_count:>6}, Success={success:>6}, PIE Income Collection={pie_income:>6}")

# Cross-cohort insights
print("\n" + "=" * 120)
print("CROSS-COHORT INSIGHTS")
print("=" * 120)

# Find best/worst performers
best_success = df.loc[df['SUCCESS_RATE_PCT'].idxmax()]
worst_success = df.loc[df['SUCCESS_RATE_PCT'].idxmin()]
best_pie_income = df.loc[df['PIE_INCOME_COLLECTION_RATE_PCT'].idxmax()]
worst_pie_income = df.loc[df['PIE_INCOME_COLLECTION_RATE_PCT'].idxmin()]

print(f"\nBest Overall Success: {pd.to_datetime(best_success['STMT_MONTH']).strftime('%b %Y')}, Stmt {int(best_success['STATEMENT_NUMBER'])} ({best_success['SUCCESS_RATE_PCT']:.1f}%)")
print(f"Worst Overall Success: {pd.to_datetime(worst_success['STMT_MONTH']).strftime('%b %Y')}, Stmt {int(worst_success['STATEMENT_NUMBER'])} ({worst_success['SUCCESS_RATE_PCT']:.1f}%)")
print(f"\nBest PIE Income Collection: {pd.to_datetime(best_pie_income['STMT_MONTH']).strftime('%b %Y')}, Stmt {int(best_pie_income['STATEMENT_NUMBER'])} ({best_pie_income['PIE_INCOME_COLLECTION_RATE_PCT']:.1f}%)")
print(f"Worst PIE Income Collection: {pd.to_datetime(worst_pie_income['STMT_MONTH']).strftime('%b %Y')}, Stmt {int(worst_pie_income['STATEMENT_NUMBER'])} ({worst_pie_income['PIE_INCOME_COLLECTION_RATE_PCT']:.1f}%)")

# Cohort stability
print(f"\nCohort Stability:")
print(f"  Success Rate Range: {df['SUCCESS_RATE_PCT'].min():.1f}% - {df['SUCCESS_RATE_PCT'].max():.1f}% (spread: {df['SUCCESS_RATE_PCT'].max() - df['SUCCESS_RATE_PCT'].min():.1f}%)")
print(f"  PIE Income Collection Rate Range: {df['PIE_INCOME_COLLECTION_RATE_PCT'].min():.1f}% - {df['PIE_INCOME_COLLECTION_RATE_PCT'].max():.1f}% (spread: {df['PIE_INCOME_COLLECTION_RATE_PCT'].max() - df['PIE_INCOME_COLLECTION_RATE_PCT'].min():.1f}%)")

print("=" * 120)
