import snowflake.connector
import pandas as pd
import matplotlib
matplotlib.use('Agg')
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
with open('/Users/Alfred.Lee/Documents/github/pie_collection_rate_by_cohort.sql', 'r') as f:
    query = f.read()

print("Running PIE Collection Rate Analysis by Statement Cohort...\n")
cursor = conn.cursor()
cursor.execute(query)
df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
cursor.close()
conn.close()

# Display results
print("=" * 120)
print("PIE COLLECTION RATE BY STATEMENT COHORT (November 2024)")
print("=" * 120)
print(df.to_string(index=False))
print("\n")

# Summary by cohort
print("=" * 120)
print("SUMMARY BY COHORT (Final 8-Month Collection Rate)")
print("=" * 120)

summary = df.groupby('STATEMENT_COHORT').agg({
    'TOTAL_POP': 'first',
    'PRE_EVAL_APPROVED': 'first',
    'APPROVED_INITIAL': 'first',
    'RUNNING_APPROVAL_COUNT': 'max',
    'PIE_COLLECTION_RATE_PCT': 'max',
    'COLLECTION_RATE_PCT': 'max'
}).reset_index()

summary.columns = ['Cohort', 'Total Pop', 'PRE_EVAL_APPROVED', 'Initially Approved',
                   'PIE Collected (8mo)', 'PIE Collection %', 'Overall Collection %']

print(summary.to_string(index=False))
print("=" * 120)

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('PIE Collection Rate Analysis by Statement Cohort (Nov 2024)',
             fontsize=16, fontweight='bold')

cohorts = df['STATEMENT_COHORT'].unique()
colors = plt.cm.Set2(np.linspace(0, 1, len(cohorts)))

# Plot 1: Overall Collection Rate Over Time by Cohort
ax1 = axes[0, 0]
for i, cohort in enumerate(cohorts):
    cohort_data = df[df['STATEMENT_COHORT'] == cohort]
    ax1.plot(cohort_data['MONTHS_SINCE_PRE_EVAL'],
             cohort_data['COLLECTION_RATE_PCT'],
             marker='o', linewidth=2, label=cohort, color=colors[i])

ax1.set_title('Overall Collection Rate Over Time', fontweight='bold')
ax1.set_xlabel('Months Since PRE_EVAL_APPROVED')
ax1.set_ylabel('Overall Collection Rate (%)')
ax1.legend(loc='lower right')
ax1.grid(True, alpha=0.3)
ax1.set_xlim(0, 8)
ax1.set_ylim(80, 100)

# Plot 2: Hide this plot
ax2 = axes[0, 1]
ax2.axis('off')

# Plot 3: Final Collection Rate by Cohort (Vertical Bar Chart)
ax3 = axes[1, 0]
final_rates = summary.sort_values('Overall Collection %', ascending=False)
x_pos = np.arange(len(final_rates))
bars = ax3.bar(x_pos, final_rates['Overall Collection %'], color=colors)
ax3.set_title('Final Overall Collection Rate by Cohort (After 8 Months)', fontweight='bold')
ax3.set_ylabel('Overall Collection Rate (%)')
ax3.set_xticks(x_pos)
ax3.set_xticklabels(final_rates['Cohort'], rotation=0)
ax3.grid(True, alpha=0.3, axis='y')
ax3.set_ylim(80, 100)

# Add value labels on top of bars
for i, (bar, val) in enumerate(zip(bars, final_rates['Overall Collection %'])):
    ax3.text(bar.get_x() + bar.get_width()/2, float(val) + 0.3,
             f'{float(val):.1f}%', ha='center', va='bottom', fontweight='bold')

# Plot 4: Population Size by Cohort
ax4 = axes[1, 1]
cohort_summary = summary.sort_values('Total Pop', ascending=False)
x = np.arange(len(cohort_summary))
width = 0.35

bars1 = ax4.bar(x - width/2, cohort_summary['PRE_EVAL_APPROVED'],
                width, label='PRE_EVAL_APPROVED', alpha=0.8, color='orange')
bars2 = ax4.bar(x + width/2, cohort_summary['Initially Approved'],
                width, label='Initially Approved', alpha=0.8, color='green')

ax4.set_title('Population Breakdown by Cohort')
ax4.set_ylabel('Number of Accounts')
ax4.set_xticks(x)
ax4.set_xticklabels([c.replace('Stmt ', '').replace(' (', '\n(')
                      for c in cohort_summary['Cohort']], rotation=0, ha='center')
ax4.legend()
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('/Users/Alfred.Lee/Documents/github/visualizations/pie_collection_cohort_visualization.png',
            dpi=300, bbox_inches='tight')
print("\nVisualization saved to: visualizations/pie_collection_cohort_visualization.png")
