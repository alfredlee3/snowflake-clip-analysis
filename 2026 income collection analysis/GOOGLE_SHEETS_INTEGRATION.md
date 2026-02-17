# Google Sheets Integration Guide

This guide explains how to get your PIE success rate analysis into Google Sheets with charts.

## Two Approaches

### Option 1: Manual Import (Easiest)
**Time**: 5 minutes | **Difficulty**: Easy | **Setup**: None

1. **Export the data**:
   ```bash
   cd "2026 income collection analysis/python"
   python export_success_rate_for_google_sheets.py
   ```

2. **Import to Google Sheets**:
   - Go to https://sheets.google.com
   - Create new spreadsheet
   - File > Import > Upload
   - Select: `visualizations/success_rate_google_sheets.csv`
   - Import location: Replace current sheet
   - Click "Import data"

3. **Create the chart**:
   - Select all data (A1:F9)
   - Insert > Chart
   - Chart type: Line chart
   - Customize:
     - Title: "Overall Success Rate Over Time - April 2025 Cohort"
     - X-axis: "Months After PIE Evaluation"
     - Y-axis: "Cumulative Success Rate (%)"
     - Y-axis range: 70 to 100
     - Series colors:
       - Stmt 18: `#e74c3c` (red)
       - Stmt 26: `#3498db` (blue)
       - Stmt 34: `#2ecc71` (green)
       - Stmt 42+: `#f39c12` (orange)
       - Overall Stmt 18+: `#000000` (black, dashed line)
     - Line thickness: 3px
   - Click Insert

### Option 2: Automated Upload with API (Advanced)
**Time**: 20-30 min setup + instant uploads | **Difficulty**: Advanced | **Setup**: Google Cloud credentials

#### Prerequisites
1. **Install Python packages**:
   ```bash
   pip install gspread google-auth google-auth-oauthlib google-auth-httplib2
   ```

2. **Set up Google Cloud Project**:
   - Go to https://console.cloud.google.com/
   - Create new project (or select existing)
   - Enable "Google Sheets API" and "Google Drive API"

3. **Create Service Account** (recommended for automation):
   - In Google Cloud Console, go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Name: `pie-analysis-uploader`
   - Click "Create and Continue"
   - Grant role: "Editor" (or custom role with Sheets/Drive access)
   - Click "Done"
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose "JSON" format
   - Download the file
   - Save as: `google_sheets_credentials.json` in the github folder

4. **Run the upload script**:
   ```bash
   cd "2026 income collection analysis/python"
   python upload_to_google_sheets.py
   ```

5. **Share the created sheet** (if needed):
   - The script will output the spreadsheet URL
   - Share it with your email or team members
   - Service account email (in credentials file) will be the owner

#### What the Script Does
- ✅ Authenticates with Google Sheets API
- ✅ Creates a new spreadsheet
- ✅ Uploads chart data (8 months × 5 statement lines)
- ✅ Uploads detailed data (all metrics)
- ✅ Creates an embedded line chart with proper formatting
- ✅ Sets axis ranges, colors, and line styles

#### Alternative: OAuth Authentication (Interactive)
If you prefer OAuth (opens browser for login):

1. Create OAuth Client ID in Google Cloud Console:
   - APIs & Services > Credentials > Create Credentials > OAuth client ID
   - Application type: Desktop app
   - Download `client_secret.json`

2. Modify the script to use OAuth instead of service account:
   ```python
   from google.oauth2.credentials import Credentials
   from google_auth_oauthlib.flow import InstalledAppFlow

   flow = InstalledAppFlow.from_client_secrets_file(
       'client_secret.json', SCOPES)
   creds = flow.run_local_server(port=0)
   ```

## Data Format

### Chart Data (Wide Format)
```
Month | Stmt 18 | Stmt 26 | Stmt 34 | Stmt 42+ | Overall Stmt 18+
------|---------|---------|---------|----------|------------------
1     | 89.4    | 87.3    | 82.5    | 74.6     | 78.3
2     | 91.4    | 88.3    | 83.9    | 76.7     | 80.5
...   | ...     | ...     | ...     | ...      | ...
8     | 94.9    | 92.2    | 88.7    | 82.4     | 86.1
```

### Detailed Data (Long Format)
Includes all metrics: Total Population, Approved Outright, PIE Total, PIE Collected, Success Count, Success Rate %

## Exported Files

After running `export_success_rate_for_google_sheets.py`:

1. **`success_rate_google_sheets.csv`**
   - Wide format optimized for charting
   - 8 rows (months) × 6 columns (Month + 5 statement lines)

2. **`success_rate_detailed_google_sheets.csv`**
   - Detailed metrics for all statements and months
   - Includes days range, approved counts, PIE counts, etc.

## Troubleshooting

### Manual Import Issues

**Problem**: Chart doesn't show all lines
- **Solution**: Make sure you selected ALL data (A1:F9) before creating chart

**Problem**: Y-axis range is wrong (0-100 instead of 70-100)
- **Solution**: Customize > Vertical axis > Set min value: 70, max value: 100

**Problem**: Colors don't match
- **Solution**: Customize > Series > Select each line > Change color manually

### API Upload Issues

**Problem**: `credentials file not found`
- **Solution**: Make sure JSON file is saved at the correct path specified in script

**Problem**: `403 Permission Denied`
- **Solution**: Enable Google Sheets API and Drive API in Google Cloud Console

**Problem**: `404 Not Found`
- **Solution**: Share the spreadsheet with the service account email (found in credentials JSON)

**Problem**: Chart not created
- **Solution**: Chart creation requires specific API permissions. Create manually if automated creation fails.

## Security Notes

⚠️ **IMPORTANT**: Never commit credentials files to git!

Add to your `.gitignore`:
```
google_sheets_credentials.json
client_secret.json
token.json
```

The credentials file grants access to create/edit Google Sheets on your behalf. Keep it secure!

## Integration with Existing Workflows

You can automate this in your data pipeline:

```python
# Example: Run after Snowflake data extraction
import subprocess

# 1. Export from Snowflake
subprocess.run(["python", "export_success_rate_for_google_sheets.py"])

# 2. Upload to Google Sheets
subprocess.run(["python", "upload_to_google_sheets.py"])

# 3. Send notification with spreadsheet URL
# (use email API, Slack webhook, etc.)
```

## Next Steps

Once your data is in Google Sheets, you can:
- Share with stakeholders who prefer Google Sheets
- Embed charts in Google Slides presentations
- Use Google Sheets formulas for ad-hoc analysis
- Connect to Google Data Studio for dashboards
- Export to Excel if needed (File > Download > Microsoft Excel)

## Support

For issues with:
- **Data export**: Check Snowflake connection and SQL query
- **Google Sheets API**: Check Google Cloud Console permissions
- **Chart formatting**: Refer to Google Sheets documentation

---

**Last Updated**: February 2026
**Maintained By**: Data Analytics Team
