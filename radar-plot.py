#!/usr/bin/env python
"""
Radar plot from Google Sheets data.

SETUP - Google Sheets API Credentials:
1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable the Google Sheets API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API" and enable it
4. Create a service account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in name, click through to finish
5. Create a key for the service account:
   - Click on the service account you created
   - Go to "Keys" tab > "Add Key" > "Create new key" > JSON
   - Save the downloaded JSON file as 'credentials.json' in this directory
6. Share your Google Sheet:
   - Open the JSON file and find the "client_email" field
   - In your Google Sheet, click "Share" and add that email with Viewer access

USAGE:
  ./radar-plot.py <spreadsheet_id> [sheet_name]

  spreadsheet_id: The ID from the Google Sheet URL
                  (e.g., from https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit)
  sheet_name: Optional, defaults to first sheet
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

CREDENTIALS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def extract_spreadsheet_id(url_or_id):
    """Extract spreadsheet ID from full URL or return as-is if already an ID."""
    if 'docs.google.com' in url_or_id:
        # Extract ID from URL like https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
        parts = url_or_id.split('/d/')
        if len(parts) > 1:
            return parts[1].split('/')[0]
    return url_or_id


def read_google_sheet(spreadsheet_id, sheet_name=None):
    spreadsheet_id = extract_spreadsheet_id(spreadsheet_id)
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    range_name = sheet_name if sheet_name else 'Sheet1'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get('values', [])
    if not values:
        print('No data found in sheet.')
        sys.exit(1)

    # First row is headers, rest is data
    headers = values[0]
    num_cols = len(headers)
    # Truncate/pad each row to match header length
    data = []
    for row in values[1:]:
        if len(row) >= num_cols:
            data.append(row[:num_cols])
        else:
            data.append(row + [''] * (num_cols - len(row)))
    df = pd.DataFrame(data, columns=headers)

    # Convert to numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

def create_radar_plot(df):
    categories = df.columns.tolist()
    num_categories = len(categories)

    # Calculate angles for each category
    angles = np.linspace(0, 2 * np.pi, num_categories, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    # Plot each row as a separate line
    for idx, row in df.iterrows():
        values = row.tolist()
        values += values[:1]  # Close the plot
        ax.plot(angles, values, 'o-', linewidth=2, label=f'Row {idx}')
        ax.fill(angles, values, alpha=0.1)

    ax.set_thetagrids(np.degrees(angles[:-1]), categories)
    ax.set_ylim(0, df.values.max() + 1)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

    plt.title('Radar Plot')
    plt.tight_layout()
    plt.savefig('radar_plot.png')
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: ./radar-plot.py <spreadsheet_id> [sheet_name]")
        sys.exit(1)

    spreadsheet_id = sys.argv[1]
    sheet_name = sys.argv[2] if len(sys.argv) > 2 else None

    df = read_google_sheet(spreadsheet_id, sheet_name)
    create_radar_plot(df)
