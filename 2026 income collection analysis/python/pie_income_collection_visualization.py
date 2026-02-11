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
with open('/Users/Alfred.Lee/Documents/github/pie_income_update_tracking.sql', 'r') as f:
    query = f.read()

print("Running PIE Income Collection Analysis...")

cursor = conn.cursor()
cursor.execute(query)
df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
cursor.close()
conn.close()

print("Query completed. Creating visualization...")

# Extract data
row = df.iloc[0]
stmt_month = row['STMT_MONTH']
stmt_num = int(row['STATEMENT_NUMBER'])

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle(f'PIE Income Collection Analysis - Statement {stmt_num} ({stmt_month.strftime("%B %Y")})',
             fontsize=16, fontweight='bold')

# Plot 1: Success Breakdown (Waterfall-style bar chart)
ax1 = axes[0, 0]
categories = ['Total\nPopulation', 'Approved\nOutright', 'PIE\nAccounts', 'Income\nCollected', 'Income\nNot Collected']
values = [
    int(row['TOTAL_POPULATION']),
    int(row['APPROVED_OUTRIGHT_COUNT']),
    int(row['PIE_TOTAL_COUNT']),
    int(row['PIE_INCOME_COLLECTED_COUNT']),
    int(row['PIE_INCOME_NOT_COLLECTED_COUNT'])
]
colors = ['#3498db', '#2ecc71', '#f39c12', '#27ae60', '#e74c3c']

bars = ax1.bar(categories, values, color=colors, edgecolor='black', linewidth=1.5)
ax1.set_title('Population Breakdown', fontweight='bold', fontsize=12)
ax1.set_ylabel('Number of Accounts')
ax1.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar, val in zip(bars, values):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, height + 10,
             f'{val:,}', ha='center', va='bottom', fontweight='bold', fontsize=10)

# Plot 2: Success Rate Pie Chart
ax2 = axes[0, 1]
success_labels = ['Approved\nOutright', 'PIE → Income\nCollected', 'PIE → Income\nNOT Collected']
success_values = [
    int(row['APPROVED_OUTRIGHT_COUNT']),
    int(row['PIE_INCOME_COLLECTED_COUNT']),
    int(row['PIE_INCOME_NOT_COLLECTED_COUNT'])
]
success_colors = ['#2ecc71', '#27ae60', '#e74c3c']
explode = (0.05, 0.05, 0.1)

wedges, texts, autotexts = ax2.pie(success_values, labels=success_labels, autopct='%1.1f%%',
                                     colors=success_colors, explode=explode,
                                     startangle=90, textprops={'fontweight': 'bold'})
ax2.set_title('Overall Success Distribution', fontweight='bold', fontsize=12)

# Plot 3: Success Metrics (Horizontal Bar Chart)
ax3 = axes[1, 0]
metrics = ['Overall\nSuccess Rate', 'Approved\nOutright %', 'PIE Income\nCollection %']
metric_values = [
    float(row['SUCCESS_RATE_PCT']),
    float(row['APPROVED_OUTRIGHT_RATE_PCT']),
    float(row['PIE_INCOME_COLLECTION_RATE_PCT'])
]
metric_colors = ['#3498db', '#2ecc71', '#27ae60']

y_pos = np.arange(len(metrics))
bars = ax3.barh(y_pos, metric_values, color=metric_colors, edgecolor='black', linewidth=1.5)
ax3.set_yticks(y_pos)
ax3.set_yticklabels(metrics)
ax3.set_xlabel('Percentage (%)')
ax3.set_title('Key Success Metrics', fontweight='bold', fontsize=12)
ax3.grid(True, alpha=0.3, axis='x')
ax3.set_xlim(0, 100)

# Add value labels on bars
for i, (bar, val) in enumerate(zip(bars, metric_values)):
    width = bar.get_width()
    ax3.text(width + 2, bar.get_y() + bar.get_height()/2,
             f'{val:.1f}%', ha='left', va='center', fontweight='bold', fontsize=10)

# Plot 4: PIE Income Collection Details
ax4 = axes[1, 1]
pie_categories = ['Income\nCollected', 'Income NOT\nCollected']
pie_values = [
    int(row['PIE_INCOME_COLLECTED_COUNT']),
    int(row['PIE_INCOME_NOT_COLLECTED_COUNT'])
]
pie_pcts = [
    float(row['PIE_INCOME_COLLECTION_RATE_PCT']),
    float(row['PIE_INCOME_MISS_RATE_PCT'])
]
pie_colors_chart = ['#27ae60', '#e74c3c']

x_pos = np.arange(len(pie_categories))
bars = ax4.bar(x_pos, pie_values, color=pie_colors_chart, edgecolor='black', linewidth=1.5)
ax4.set_xticks(x_pos)
ax4.set_xticklabels(pie_categories)
ax4.set_ylabel('Number of Accounts')
ax4.set_title(f'PIE Income Collection Detail (n={int(row["PIE_TOTAL_COUNT"])})', fontweight='bold', fontsize=12)
ax4.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for i, (bar, val, pct) in enumerate(zip(bars, pie_values, pie_pcts)):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2, height + 3,
             f'{val:,}\n({pct:.1f}%)', ha='center', va='bottom', fontweight='bold', fontsize=10)

plt.tight_layout()

# Save the plot
output_file = '/Users/Alfred.Lee/Documents/github/visualizations/pie_income_collection_visualization.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\nVisualization saved to: {output_file}")

# Display summary
print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)
print(f"\nStatement Month: {stmt_month.strftime('%B %Y')}")
print(f"Statement Number: {stmt_num}")
print(f"\nTotal Population: {int(row['TOTAL_POPULATION']):,}")
print(f"  - Approved Outright: {int(row['APPROVED_OUTRIGHT_COUNT']):,} ({row['APPROVED_OUTRIGHT_RATE_PCT']:.1f}%)")
print(f"  - PRE_EVAL_APPROVED (PIE): {int(row['PIE_TOTAL_COUNT']):,} ({100.0 * row['PIE_TOTAL_COUNT'] / row['TOTAL_POPULATION']:.1f}%)")
print(f"\nPIE Income Collection:")
print(f"  - Income Collected: {int(row['PIE_INCOME_COLLECTED_COUNT']):,} ({row['PIE_INCOME_COLLECTION_RATE_PCT']:.1f}% of PIE)")
print(f"  - Income NOT Collected: {int(row['PIE_INCOME_NOT_COLLECTED_COUNT']):,} ({row['PIE_INCOME_MISS_RATE_PCT']:.1f}% of PIE)")
print(f"\nOverall Success Rate: {row['SUCCESS_RATE_PCT']:.1f}%")
print(f"  - {int(row['SUCCESS_COUNT']):,} accounts achieved success")
print("=" * 80)
