# PowerPoint Integration Guide

This guide explains how to create a PowerPoint presentation with embedded chart data (not images) for your PIE success rate analysis.

## Overview

The PowerPoint presentation will contain:
- **Slide 1**: Title slide
- **Slide 2**: Success rate line chart (native PowerPoint chart with embedded data)
- **Slide 3**: Key findings and metrics summary

The chart is a **native PowerPoint chart object** backed by data, not a static image. You can click on it to edit the data or customize the formatting.

## Automated Generation

### Prerequisites

Install required Python packages:
```bash
pip install python-pptx pandas openpyxl snowflake-connector-python
```

### Generate Presentation

```bash
cd "2026 income collection analysis/python"
python create_powerpoint_presentation.py
```

The script will:
1. ✅ Connect to Snowflake
2. ✅ Load PIE success rate data (April 2025 cohort)
3. ✅ Create PowerPoint presentation
4. ✅ Add title slide
5. ✅ Add line chart with embedded data (5 series: Stmt 18, 26, 34, 42+, Overall)
6. ✅ Add summary slide with key metrics
7. ✅ Save to `visualizations/PIE_Success_Rate_Analysis.pptx`

### Output Location

**File**: `/Users/Alfred.Lee/Documents/github/visualizations/PIE_Success_Rate_Analysis.pptx`

## Chart Features

### Chart Configuration
- **Chart Type**: Line chart (native PowerPoint chart object)
- **Data Range**: 8 months (Month 1-8)
- **Series**: 5 lines
  - Stmt 18 (red, solid)
  - Stmt 26 (blue, solid)
  - Stmt 34 (green, solid)
  - Stmt 42+ (orange, solid)
  - Overall Stmt 18+ (black, dashed)

### Formatting
- **Y-axis**: 70% to 100% (Cumulative Success Rate)
- **X-axis**: Months After PIE Evaluation
- **Line thickness**: 2.5pt
- **Legend**: Bottom position
- **Colors**: Match visualizations (red, blue, green, orange, black)

## Editing the Chart

Since this is a native PowerPoint chart (not an image), you can:

1. **Edit Data**:
   - Click on the chart
   - Right-click > Edit Data
   - Excel datasheet will open
   - Modify values as needed

2. **Change Formatting**:
   - Click on the chart
   - Use Chart Tools > Design and Format tabs
   - Modify colors, line styles, axis ranges, etc.

3. **Resize/Move**:
   - Click and drag to resize
   - Click and drag to move to different position

4. **Update Chart Type**:
   - Click on the chart
   - Chart Tools > Design > Change Chart Type
   - Select different chart type (bar, area, etc.)

## Manual Creation Alternative

If you prefer to create the PowerPoint manually:

### Step 1: Export Data to Excel
```bash
cd "2026 income collection analysis/python"
python export_success_rate_for_google_sheets.py
```

This creates `visualizations/success_rate_google_sheets.csv`

### Step 2: Import to Excel
1. Open Excel
2. File > Open > Browse
3. Select `success_rate_google_sheets.csv`
4. Click "Open"

### Step 3: Create Chart in Excel
1. Select all data (A1:F9)
2. Insert > Line Chart
3. Customize chart (colors, axis ranges, etc.)
4. Copy chart (Ctrl+C)

### Step 4: Paste into PowerPoint
1. Open PowerPoint
2. Create new slide
3. Paste chart (Ctrl+V)
4. Choose "Keep Source Formatting & Embed Workbook"

This embeds the Excel data with the chart, making it editable.

## Customization Options

### Modify Chart Colors

Edit the `COLORS` dictionary in `create_powerpoint_presentation.py`:

```python
COLORS = {
    'Stmt 18': RGBColor(231, 76, 60),      # Red
    'Stmt 26': RGBColor(52, 152, 219),     # Blue
    'Stmt 34': RGBColor(46, 204, 113),     # Green
    'Stmt 42+': RGBColor(243, 156, 18),    # Orange
    'Overall Stmt 18+': RGBColor(0, 0, 0)  # Black
}
```

### Change Y-Axis Range

Modify the axis range in the `create_chart_slide` function:

```python
value_axis.minimum_scale = 70  # Change minimum
value_axis.maximum_scale = 100  # Change maximum
```

### Add More Slides

Add custom slides using the python-pptx API:

```python
def create_custom_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    # Add shapes, text boxes, charts, etc.
```

## Multi-Cohort Presentation

To create a presentation with multiple cohorts (Mar/Apr/May 2025):

1. Modify the script to load data for each cohort
2. Create separate chart slides for each cohort
3. Add a comparison slide showing all three cohorts

Example modification:
```python
cohorts = {
    'Mar 2025': '2025-03-01',
    'Apr 2025': '2025-04-01',
    'May 2025': '2025-05-01'
}

for cohort_name, cohort_date in cohorts.items():
    # Load data for cohort
    # Create chart slide
    create_chart_slide(prs, chart_data, title=f"Success Rate - {cohort_name}")
```

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'pptx'`
**Solution**: Install python-pptx package
```bash
pip install python-pptx
```

### Issue: Chart colors don't match
**Solution**: Check RGB values in `COLORS` dictionary. PowerPoint uses RGB (0-255), not hex colors.

### Issue: Chart data doesn't update
**Solution**: The chart is embedded with data at creation time. To update:
1. Run the script again to regenerate the presentation
2. Or manually edit the chart data in PowerPoint

### Issue: Snowflake authentication fails
**Solution**: Make sure you're using external browser authentication:
```python
'authenticator': 'externalbrowser'
```

### Issue: Y-axis range is wrong
**Solution**: Modify `minimum_scale` and `maximum_scale` in the script:
```python
value_axis.minimum_scale = 70
value_axis.maximum_scale = 100
```

## Advanced: Using Templates

You can create a custom PowerPoint template and use it:

```python
from pptx import Presentation

# Load template
prs = Presentation('template.pptx')

# Add slides using template layouts
slide = prs.slides.add_slide(prs.slide_layouts[0])  # Use template's first layout
```

## Exporting to Other Formats

### Export to PDF
1. Open the PowerPoint presentation
2. File > Save As > PDF
3. Save

### Export to Google Slides
1. Upload .pptx file to Google Drive
2. Right-click > Open with > Google Slides
3. The chart will be converted (may need manual formatting)

### Export to Keynote (Mac)
1. Open .pptx file in Keynote
2. Keynote will convert the presentation
3. Chart should remain editable

## Integration with Workflows

Automate presentation generation in your data pipeline:

```python
# Example: Run after data extraction
import subprocess

# 1. Generate PowerPoint
subprocess.run(["python", "create_powerpoint_presentation.py"])

# 2. Send email with presentation attached
# (use email API or smtplib)

# 3. Upload to SharePoint/Google Drive
# (use respective APIs)
```

## Comparison with Other Formats

| Feature | PowerPoint | Google Sheets | PNG Image |
|---------|-----------|---------------|-----------|
| Editable chart data | ✅ Yes | ✅ Yes | ❌ No |
| Works offline | ✅ Yes | ❌ No | ✅ Yes |
| Easy sharing | ✅ Yes | ✅ Yes | ✅ Yes |
| Presentation-ready | ✅ Yes | ❌ No | ⚠️ Limited |
| Automatic updates | ❌ No | ⚠️ With API | ❌ No |
| Data backup | ✅ Embedded | ☁️ Cloud | ❌ No |

## Best Practices

1. **Version Control**: Save presentations with date in filename
   ```python
   from datetime import datetime
   date_str = datetime.now().strftime('%Y%m%d')
   OUTPUT_FILE = f'PIE_Analysis_{date_str}.pptx'
   ```

2. **Data Verification**: Always verify data before generating presentation
   ```python
   # Check data range
   assert chart_data['Month'].min() == 1
   assert chart_data['Month'].max() == 8
   ```

3. **Template Consistency**: Use corporate templates for professional look

4. **Chart Simplicity**: Don't overcrowd slides with too many series

5. **Accessibility**: Add alt text to charts for screen readers
   ```python
   chart.chart_title.text_frame.text = "Success Rate Over Time"
   ```

## Next Steps

Once your PowerPoint is created:
- Share with stakeholders for review
- Present in meetings with live editable charts
- Export to PDF for distribution
- Upload to SharePoint or Google Drive
- Create recurring automated reports

## Support

For issues with:
- **Script errors**: Check Python package versions (`pip list`)
- **Chart formatting**: Refer to python-pptx documentation
- **Data issues**: Verify Snowflake connection and SQL query

---

**Last Updated**: February 2026
**Maintained By**: Data Analytics Team
