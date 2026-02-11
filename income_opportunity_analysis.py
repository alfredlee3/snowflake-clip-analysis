import snowflake.connector
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Snowflake connection
conn = snowflake.connector.connect(
    user='ALFRED_LEE',
    account='IJ90379-MISSIONLANE',
    authenticator='externalbrowser',
    database='EDW_DB',
    schema='PUBLIC'
)

# Query to analyze income-related opportunity
query = """
-- Analyze CLIP opportunity blocked by income recency requirement
WITH recent_evaluations AS (
    SELECT
        left(EVALUATED_TIMESTAMP, 7) as clip_month,
        OUTCOME,
        STATEMENT_NUMBER,
        CLIP_AMOUNT,
        PRE_CLIP_LINE_LIMIT,
        DECISION_DATA:fico_08 as FICO,
        CASE
            WHEN OUTCOME IN ('PRE_EVAL_APPROVED', 'PRE_EVAL_DECLINED') THEN 'Blocked by Income'
            WHEN OUTCOME = 'APPROVED' THEN 'Approved'
            WHEN OUTCOME = 'DECLINED' THEN 'Declined (Other Reasons)'
            ELSE OUTCOME
        END as outcome_category,
        CASE
            WHEN OUTCOME = 'PRE_EVAL_APPROVED' THEN CLIP_AMOUNT
            ELSE 0
        END as opportunity_clip_amount
    FROM EDW_DB.PUBLIC.clip_results_data
    WHERE TO_CHAR(EVALUATED_TIMESTAMP, 'YYYY-MM-DD') >= '2025-01-01'
    AND STATEMENT_NUMBER >= 18  -- Year 2+ where income requirement applies
)

SELECT
    clip_month,
    -- Counts by category
    COUNT(*) as total_evaluations,
    SUM(CASE WHEN outcome_category = 'Approved' THEN 1 ELSE 0 END) as approved_count,
    SUM(CASE WHEN outcome_category = 'Blocked by Income' THEN 1 ELSE 0 END) as blocked_by_income_count,
    SUM(CASE WHEN outcome_category = 'Declined (Other Reasons)' THEN 1 ELSE 0 END) as declined_other_count,

    -- Exposure metrics
    SUM(CASE WHEN outcome_category = 'Approved' THEN CLIP_AMOUNT ELSE 0 END) as actual_exposure,
    SUM(opportunity_clip_amount) as opportunity_exposure,

    -- Opportunity percentage
    ROUND(100.0 * SUM(CASE WHEN outcome_category = 'Blocked by Income' THEN 1 ELSE 0 END) / COUNT(*), 2) as pct_blocked_by_income,

    -- Average metrics for blocked accounts
    AVG(CASE WHEN outcome_category = 'Blocked by Income' THEN opportunity_clip_amount ELSE NULL END) as avg_opportunity_clip,
    AVG(CASE WHEN outcome_category = 'Blocked by Income' THEN PRE_CLIP_LINE_LIMIT ELSE NULL END) as avg_pcl_blocked,
    AVG(CASE WHEN outcome_category = 'Blocked by Income' THEN FICO ELSE NULL END) as avg_fico_blocked

FROM recent_evaluations
GROUP BY 1
ORDER BY 1;
"""

print("Running income opportunity analysis...\n")
cursor = conn.cursor()
cursor.execute(query)
df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
cursor.close()
conn.close()

# Display results
print("=" * 100)
print("CLIP INCOME OPPORTUNITY ANALYSIS (Year 2+, Statement 18+)")
print("=" * 100)
print(df.to_string(index=False))
print("\n")

# Calculate totals
total_opportunity_exposure = df['OPPORTUNITY_EXPOSURE'].sum()
total_actual_exposure = df['ACTUAL_EXPOSURE'].sum()
total_blocked = df['BLOCKED_BY_INCOME_COUNT'].sum()
total_approved = df['APPROVED_COUNT'].sum()

print("=" * 100)
print("SUMMARY STATISTICS")
print("=" * 100)
print(f"Total Actual CLIP Exposure (Approved):          ${total_actual_exposure:,.0f}")
print(f"Total Opportunity Exposure (Blocked by Income): ${total_opportunity_exposure:,.0f}")
print(f"Incremental Opportunity:                        ${total_opportunity_exposure:,.0f}")
print(f"Opportunity as % of Actual:                     {100 * total_opportunity_exposure / total_actual_exposure if total_actual_exposure > 0 else 0:.1f}%")
print(f"\nTotal Accounts Approved:                        {total_approved:,.0f}")
print(f"Total Accounts Blocked by Income:               {total_blocked:,.0f}")
print(f"Blocked as % of Approved:                       {100 * total_blocked / total_approved if total_approved > 0 else 0:.1f}%")
print("=" * 100)

# Create visualization
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('CLIP Income Opportunity Analysis (Year 2+)', fontsize=16, fontweight='bold')

# Plot 1: Exposure Comparison
axes[0, 0].bar(df['CLIP_MONTH'], df['ACTUAL_EXPOSURE'], label='Actual (Approved)', alpha=0.7, color='green')
axes[0, 0].bar(df['CLIP_MONTH'], df['OPPORTUNITY_EXPOSURE'], label='Opportunity (Blocked by Income)', alpha=0.7, color='orange')
axes[0, 0].set_title('Actual vs Opportunity Exposure by Month')
axes[0, 0].set_xlabel('Month')
axes[0, 0].set_ylabel('Exposure ($)')
axes[0, 0].legend()
axes[0, 0].tick_params(axis='x', rotation=45)
axes[0, 0].grid(True, alpha=0.3)

# Plot 2: Count Comparison
axes[0, 1].bar(df['CLIP_MONTH'], df['APPROVED_COUNT'], label='Approved', alpha=0.7, color='green')
axes[0, 1].bar(df['CLIP_MONTH'], df['BLOCKED_BY_INCOME_COUNT'], label='Blocked by Income', alpha=0.7, color='orange')
axes[0, 1].set_title('Account Counts by Month')
axes[0, 1].set_xlabel('Month')
axes[0, 1].set_ylabel('Number of Accounts')
axes[0, 1].legend()
axes[0, 1].tick_params(axis='x', rotation=45)
axes[0, 1].grid(True, alpha=0.3)

# Plot 3: Percentage Blocked
axes[1, 0].plot(df['CLIP_MONTH'], df['PCT_BLOCKED_BY_INCOME'], marker='o', linewidth=2, color='red')
axes[1, 0].set_title('% of Evaluations Blocked by Income')
axes[1, 0].set_xlabel('Month')
axes[1, 0].set_ylabel('Percentage (%)')
axes[1, 0].tick_params(axis='x', rotation=45)
axes[1, 0].grid(True, alpha=0.3)

# Plot 4: Average Opportunity CLIP Amount
axes[1, 1].plot(df['CLIP_MONTH'], df['AVG_OPPORTUNITY_CLIP'], marker='s', linewidth=2, color='purple')
axes[1, 1].set_title('Average CLIP Amount for Income-Blocked Accounts')
axes[1, 1].set_xlabel('Month')
axes[1, 1].set_ylabel('Average CLIP Amount ($)')
axes[1, 1].tick_params(axis='x', rotation=45)
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/Users/Alfred.Lee/Documents/github/visualizations/income_opportunity_visualization.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved to: visualizations/income_opportunity_visualization.png")
