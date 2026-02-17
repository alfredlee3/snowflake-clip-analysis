"""
Google Sheets Upload Script for Success Rate Analysis

Prerequisites:
1. Install required packages:
   pip install gspread google-auth google-auth-oauthlib google-auth-httplib2

2. Set up Google Cloud Project:
   - Go to https://console.cloud.google.com/
   - Create a new project (or select existing)
   - Enable Google Sheets API
   - Create credentials (OAuth 2.0 Client ID or Service Account)
   - Download credentials.json file

3. For Service Account method (recommended for automation):
   - Create Service Account
   - Download JSON key file
   - Share your Google Sheet with the service account email

4. For OAuth method (interactive):
   - Create OAuth 2.0 Client ID
   - Download client_secret.json
   - First run will open browser for authentication
"""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import sys
import os

# Configuration
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Path to your credentials file (you need to create this)
CREDENTIALS_FILE = '/Users/Alfred.Lee/Documents/github/google_sheets_credentials.json'

# CSV file to upload
CSV_FILE = '/Users/Alfred.Lee/Documents/github/visualizations/success_rate_google_sheets.csv'
DETAILED_CSV = '/Users/Alfred.Lee/Documents/github/visualizations/success_rate_detailed_google_sheets.csv'


def authenticate_google_sheets():
    """Authenticate with Google Sheets API"""
    try:
        if not os.path.exists(CREDENTIALS_FILE):
            print(f"\n❌ Error: Credentials file not found at {CREDENTIALS_FILE}")
            print("\nPlease follow these steps:")
            print("1. Go to https://console.cloud.google.com/")
            print("2. Create a new project")
            print("3. Enable Google Sheets API")
            print("4. Create Service Account credentials")
            print("5. Download JSON key file")
            print(f"6. Save it as: {CREDENTIALS_FILE}")
            sys.exit(1)

        # Authenticate using service account
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        print("✓ Successfully authenticated with Google Sheets")
        return client

    except Exception as e:
        print(f"❌ Authentication error: {e}")
        sys.exit(1)


def create_spreadsheet(client, title="PIE Success Rate Analysis - April 2025"):
    """Create a new Google Spreadsheet"""
    try:
        spreadsheet = client.create(title)
        print(f"✓ Created spreadsheet: {title}")
        print(f"  URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
        return spreadsheet
    except Exception as e:
        print(f"❌ Error creating spreadsheet: {e}")
        sys.exit(1)


def upload_data(spreadsheet, csv_file, sheet_name="Chart Data"):
    """Upload CSV data to a sheet"""
    try:
        # Read CSV
        df = pd.read_csv(csv_file)

        # Get or create worksheet
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=20)

        # Clear existing data
        worksheet.clear()

        # Upload data
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        print(f"✓ Uploaded data to sheet: {sheet_name}")
        return worksheet

    except Exception as e:
        print(f"❌ Error uploading data: {e}")
        sys.exit(1)


def create_line_chart(spreadsheet, worksheet, data_range="A1:F9"):
    """Create a line chart in the spreadsheet"""
    try:
        # Chart configuration
        chart_spec = {
            "title": "Overall Success Rate Over Time - April 2025 Cohort",
            "basicChart": {
                "chartType": "LINE",
                "legendPosition": "BOTTOM_LEGEND",
                "axis": [
                    {
                        "position": "BOTTOM_AXIS",
                        "title": "Months After PIE Evaluation"
                    },
                    {
                        "position": "LEFT_AXIS",
                        "title": "Cumulative Success Rate (%)",
                        "viewWindowOptions": {
                            "viewWindowMin": 70,
                            "viewWindowMax": 100
                        }
                    }
                ],
                "domains": [
                    {
                        "domain": {
                            "sourceRange": {
                                "sources": [
                                    {
                                        "sheetId": worksheet.id,
                                        "startRowIndex": 0,
                                        "endRowIndex": 9,
                                        "startColumnIndex": 0,
                                        "endColumnIndex": 1
                                    }
                                ]
                            }
                        }
                    }
                ],
                "series": [
                    {
                        "series": {
                            "sourceRange": {
                                "sources": [
                                    {
                                        "sheetId": worksheet.id,
                                        "startRowIndex": 0,
                                        "endRowIndex": 9,
                                        "startColumnIndex": 1,
                                        "endColumnIndex": 2
                                    }
                                ]
                            }
                        },
                        "targetAxis": "LEFT_AXIS",
                        "color": {"red": 0.906, "green": 0.298, "blue": 0.235},  # #e74c3c
                        "lineStyle": {"width": 3}
                    },
                    {
                        "series": {
                            "sourceRange": {
                                "sources": [
                                    {
                                        "sheetId": worksheet.id,
                                        "startRowIndex": 0,
                                        "endRowIndex": 9,
                                        "startColumnIndex": 2,
                                        "endColumnIndex": 3
                                    }
                                ]
                            }
                        },
                        "targetAxis": "LEFT_AXIS",
                        "color": {"red": 0.204, "green": 0.596, "blue": 0.859},  # #3498db
                        "lineStyle": {"width": 3}
                    },
                    {
                        "series": {
                            "sourceRange": {
                                "sources": [
                                    {
                                        "sheetId": worksheet.id,
                                        "startRowIndex": 0,
                                        "endRowIndex": 9,
                                        "startColumnIndex": 3,
                                        "endColumnIndex": 4
                                    }
                                ]
                            }
                        },
                        "targetAxis": "LEFT_AXIS",
                        "color": {"red": 0.180, "green": 0.800, "blue": 0.443},  # #2ecc71
                        "lineStyle": {"width": 3}
                    },
                    {
                        "series": {
                            "sourceRange": {
                                "sources": [
                                    {
                                        "sheetId": worksheet.id,
                                        "startRowIndex": 0,
                                        "endRowIndex": 9,
                                        "startColumnIndex": 4,
                                        "endColumnIndex": 5
                                    }
                                ]
                            }
                        },
                        "targetAxis": "LEFT_AXIS",
                        "color": {"red": 0.953, "green": 0.612, "blue": 0.071},  # #f39c12
                        "lineStyle": {"width": 3}
                    },
                    {
                        "series": {
                            "sourceRange": {
                                "sources": [
                                    {
                                        "sheetId": worksheet.id,
                                        "startRowIndex": 0,
                                        "endRowIndex": 9,
                                        "startColumnIndex": 5,
                                        "endColumnIndex": 6
                                    }
                                ]
                            }
                        },
                        "targetAxis": "LEFT_AXIS",
                        "color": {"red": 0, "green": 0, "blue": 0},  # #000000
                        "lineStyle": {
                            "width": 3,
                            "type": "LONG_DASHED"
                        }
                    }
                ],
                "headerCount": 1
            }
        }

        # Add chart to spreadsheet
        request = {
            "addChart": {
                "chart": {
                    "spec": chart_spec,
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": worksheet.id,
                                "rowIndex": 1,
                                "columnIndex": 7
                            }
                        }
                    }
                }
            }
        }

        spreadsheet.batch_update({"requests": [request]})
        print("✓ Created line chart")

    except Exception as e:
        print(f"⚠️  Note: Chart creation requires advanced API features")
        print(f"   You can create the chart manually using Insert > Chart")
        print(f"   Error details: {e}")


def main():
    """Main execution function"""
    print("\n" + "=" * 80)
    print("GOOGLE SHEETS UPLOAD - PIE SUCCESS RATE ANALYSIS")
    print("=" * 80)

    # Step 1: Authenticate
    print("\n[1/5] Authenticating with Google Sheets...")
    client = authenticate_google_sheets()

    # Step 2: Create spreadsheet
    print("\n[2/5] Creating new spreadsheet...")
    spreadsheet = create_spreadsheet(client)

    # Step 3: Upload chart data
    print("\n[3/5] Uploading chart data...")
    chart_worksheet = upload_data(spreadsheet, CSV_FILE, "Chart Data")

    # Step 4: Upload detailed data
    print("\n[4/5] Uploading detailed data...")
    detail_worksheet = upload_data(spreadsheet, DETAILED_CSV, "Detailed Data")

    # Step 5: Create chart
    print("\n[5/5] Creating line chart...")
    create_line_chart(spreadsheet, chart_worksheet)

    # Success!
    print("\n" + "=" * 80)
    print("✓ SUCCESS!")
    print("=" * 80)
    print(f"\nYour Google Sheet is ready:")
    print(f"URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
    print("\nThe sheet contains:")
    print("  - Tab 1 'Chart Data': Success rates by month and statement")
    print("  - Tab 2 'Detailed Data': Full metrics with all fields")
    print("  - Embedded chart with all 5 lines (Stmt 18, 26, 34, 42+, Overall)")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
