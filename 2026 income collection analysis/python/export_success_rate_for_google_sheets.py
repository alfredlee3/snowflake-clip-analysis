import snowflake.connector
import pandas as pd
import csv

# Snowflake connection
conn = snowflake.connector.connect(
    user='ALFRED_LEE',
    account='IJ90379-MISSIONLANE',
    authenticator='externalbrowser',
    database='EDW_DB',
    schema='PUBLIC'
)

print("Exporting Success Rate Data for Google Sheets...")

# Load time series data for April 2025 cohort
with open('/Users/Alfred.Lee/Documents/github/2026 income collection analysis/sql/pie_income_collection_over_time.sql', 'r') as f:
    query = f.read()

cursor = conn.cursor()
cursor.execute(query)
df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
cursor.close()
conn.close()

# Add month label (1-8 instead of 0-7)
df['MONTH_LABEL'] = df['MONTH_OFFSET'] + 1

# Filter to only the data we need for the chart
statements = [18, 26, 34, 442, 999]  # 442 = Stmt 42+, 999 = Overall 18+
df_chart = df[df['STATEMENT_NUMBER'].isin(statements)].copy()

# Create a wide-format table for Google Sheets (easier to chart)
pivot_data = df_chart.pivot(
    index='MONTH_LABEL',
    columns='STATEMENT_LABEL',
    values='SUCCESS_RATE_PCT'
).reset_index()

# Rename columns for clarity
pivot_data = pivot_data.rename(columns={
    'MONTH_LABEL': 'Month',
    'Stmt 18': 'Stmt 18',
    'Stmt 26': 'Stmt 26',
    'Stmt 34': 'Stmt 34',
    'Stmt 42+': 'Stmt 42+',
    'Overall Stmt 18+': 'Overall Stmt 18+'
})

# Reorder columns
column_order = ['Month', 'Stmt 18', 'Stmt 26', 'Stmt 34', 'Stmt 42+', 'Overall Stmt 18+']
pivot_data = pivot_data[column_order]

# Export to CSV
output_file = '/Users/Alfred.Lee/Documents/github/visualizations/success_rate_google_sheets.csv'
pivot_data.to_csv(output_file, index=False)

print(f"\n✓ Data exported to: {output_file}")
print(f"\nRows: {len(pivot_data)}")
print(f"Columns: {', '.join(pivot_data.columns)}")

# Display the data
print("\n" + "=" * 100)
print("SUCCESS RATE DATA - READY FOR GOOGLE SHEETS")
print("=" * 100)
print("\n" + pivot_data.to_string(index=False))

# Also create a detailed data export with all metrics
print("\n\nCreating detailed data export...")

# Prepare detailed export
df_detailed = df_chart.copy()
df_detailed['DAYS_START'] = df_detailed['MONTH_OFFSET'] * 30
df_detailed['DAYS_END'] = (df_detailed['MONTH_OFFSET'] + 1) * 30
df_detailed['DAYS_RANGE'] = df_detailed['DAYS_START'].astype(str) + '-' + df_detailed['DAYS_END'].astype(str)

# Select relevant columns
export_cols = [
    'STATEMENT_LABEL', 'MONTH_LABEL', 'DAYS_RANGE',
    'TOTAL_POPULATION', 'APPROVED_OUTRIGHT_COUNT',
    'PIE_TOTAL_COUNT', 'PIE_INCOME_COLLECTED_BY_MONTH',
    'SUCCESS_COUNT', 'SUCCESS_RATE_PCT'
]

df_detailed_export = df_detailed[export_cols].copy()
df_detailed_export = df_detailed_export.rename(columns={
    'STATEMENT_LABEL': 'Statement',
    'MONTH_LABEL': 'Month',
    'DAYS_RANGE': 'Days Range',
    'TOTAL_POPULATION': 'Total Accounts',
    'APPROVED_OUTRIGHT_COUNT': 'Approved Outright',
    'PIE_TOTAL_COUNT': 'PIE Total',
    'PIE_INCOME_COLLECTED_BY_MONTH': 'PIE Collected',
    'SUCCESS_COUNT': 'Total Success',
    'SUCCESS_RATE_PCT': 'Success Rate %'
})

detailed_output = '/Users/Alfred.Lee/Documents/github/visualizations/success_rate_detailed_google_sheets.csv'
df_detailed_export.to_csv(detailed_output, index=False)

print(f"✓ Detailed data exported to: {detailed_output}")

print("\n" + "=" * 100)
print("GOOGLE SHEETS IMPORT INSTRUCTIONS")
print("=" * 100)
print("\n1. Open Google Sheets: https://sheets.google.com")
print("2. Create a new spreadsheet")
print("3. File > Import > Upload > Browse")
print(f"4. Select: {output_file}")
print("5. Import location: Replace current sheet")
print("6. Separator type: Comma")
print("7. Click 'Import data'")

print("\n" + "=" * 100)
print("CHART CREATION INSTRUCTIONS")
print("=" * 100)
print("\n1. Select all data (columns A-F, rows 1-9)")
print("2. Insert > Chart")
print("3. Chart type: Line chart")
print("4. Customize chart:")
print("   - Chart title: 'Overall Success Rate Over Time - April 2025 Cohort'")
print("   - X-axis title: 'Months After PIE Evaluation'")
print("   - Y-axis title: 'Cumulative Success Rate (%)'")
print("   - Series colors:")
print("     * Stmt 18: #e74c3c (red)")
print("     * Stmt 26: #3498db (blue)")
print("     * Stmt 34: #2ecc71 (green)")
print("     * Stmt 42+: #f39c12 (orange)")
print("     * Overall Stmt 18+: #000000 (black, dashed)")
print("5. Customize > Series:")
print("   - Make 'Overall Stmt 18+' line dashed")
print("   - Increase line thickness to 3px for all lines")
print("6. Customize > Vertical axis:")
print("   - Min value: 70")
print("   - Max value: 100")
print("7. Click 'Insert'")

print("\n" + "=" * 100)
print("ALTERNATIVE: GOOGLE SHEETS API SCRIPT")
print("=" * 100)
print("\nIf you want to automate this with Google Sheets API:")
print("1. Enable Google Sheets API in Google Cloud Console")
print("2. Create service account credentials")
print("3. Share the Google Sheet with the service account email")
print("4. Use gspread library to upload data and create charts")
print("\nWould you like me to create a Python script that uses Google Sheets API?")
print("=" * 100)
