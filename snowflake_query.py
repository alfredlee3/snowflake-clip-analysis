import snowflake.connector
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Snowflake connection using your VS Code settings
conn = snowflake.connector.connect(
    user='ALFRED_LEE',
    account='IJ90379-MISSIONLANE',
    authenticator='externalbrowser',
    database='EDW_DB',
    schema='PUBLIC'
)

# Your query
query = """
select
    left(EVALUATED_TIMESTAMP, 7) as clip_month,
    sum(clip_amount) as exposure,
    sum(case when OUTCOME = 'APPROVED' then 1 else 0 end) as num_CLIP,
    avg(case when OUTCOME = 'APPROVED' then clip_amount else 0 end) as avg_clip_amt,
    avg(pre_clip_line_limit) as avg_PCL,
    avg(DECISION_DATA:fico_08) as avg_FICO
FROM EDW_DB.PUBLIC.clip_results_data
WHERE TO_CHAR(EVALUATED_TIMESTAMP, 'YYYY-MM-DD') >= '2025-01-01'
AND (OUTCOME = 'APPROVED')
Group by 1
order by 1
"""

# Execute query
cursor = conn.cursor()
cursor.execute(query)
df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
cursor.close()
conn.close()

# Display the data
print("\n=== Query Results ===")
print(df.to_string(index=False))
print(f"\n{len(df)} rows returned\n")

# Create visualizations
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('CLIP Results Analysis', fontsize=16)

# Plot 1: Exposure over time
axes[0, 0].plot(df['CLIP_MONTH'], df['EXPOSURE'], marker='o', linewidth=2)
axes[0, 0].set_title('Total Exposure by Month')
axes[0, 0].set_xlabel('Month')
axes[0, 0].set_ylabel('Exposure ($)')
axes[0, 0].tick_params(axis='x', rotation=45)
axes[0, 0].grid(True, alpha=0.3)

# Plot 2: Number of CLIPs
axes[0, 1].bar(df['CLIP_MONTH'], df['NUM_CLIP'], color='steelblue')
axes[0, 1].set_title('Number of Approved CLIPs by Month')
axes[0, 1].set_xlabel('Month')
axes[0, 1].set_ylabel('Count')
axes[0, 1].tick_params(axis='x', rotation=45)
axes[0, 1].grid(True, alpha=0.3)

# Plot 3: Average CLIP Amount
axes[0, 2].plot(df['CLIP_MONTH'], df['AVG_CLIP_AMT'], marker='s', color='green', linewidth=2)
axes[0, 2].set_title('Average CLIP Amount by Month')
axes[0, 2].set_xlabel('Month')
axes[0, 2].set_ylabel('Average Amount ($)')
axes[0, 2].tick_params(axis='x', rotation=45)
axes[0, 2].grid(True, alpha=0.3)

# Plot 4: Average Pre-CLIP Line Limit
axes[1, 0].plot(df['CLIP_MONTH'], df['AVG_PCL'], marker='o', color='orange', linewidth=2)
axes[1, 0].set_title('Average Pre-CLIP Line Limit by Month')
axes[1, 0].set_xlabel('Month')
axes[1, 0].set_ylabel('Average Limit ($)')
axes[1, 0].tick_params(axis='x', rotation=45)
axes[1, 0].grid(True, alpha=0.3)

# Plot 5: Average FICO Score
axes[1, 1].plot(df['CLIP_MONTH'], df['AVG_FICO'], marker='d', color='red', linewidth=2)
axes[1, 1].set_title('Average FICO Score by Month')
axes[1, 1].set_xlabel('Month')
axes[1, 1].set_ylabel('FICO Score')
axes[1, 1].tick_params(axis='x', rotation=45)
axes[1, 1].grid(True, alpha=0.3)

# Plot 6: Summary metrics
axes[1, 2].axis('off')
summary_text = f"""
Summary Statistics:
------------------
Total Exposure: ${df['EXPOSURE'].sum():,.2f}
Total CLIPs: {df['NUM_CLIP'].sum():,.0f}
Avg CLIP Amt: ${df['AVG_CLIP_AMT'].mean():,.2f}
Avg PCL: ${df['AVG_PCL'].mean():,.2f}
Avg FICO: {df['AVG_FICO'].mean():.1f}
"""
axes[1, 2].text(0.1, 0.5, summary_text, fontsize=12, family='monospace',
                verticalalignment='center')

plt.tight_layout()
plt.savefig('/Users/Alfred.Lee/Documents/github/visualizations/clip_results_visualization.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved to: visualizations/clip_results_visualization.png")
