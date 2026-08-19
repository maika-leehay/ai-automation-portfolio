import os
import gspread
from google.oauth2 import service_account


def get_sheets_client(credentials_path: str = None):
    """
    Initializes and returns a gspread Google Sheets client.
    """
    cred_file = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = service_account.Credentials.from_service_account_file(cred_file, scopes=scopes)
    return gspread.authorize(credentials)


def log_lead_to_sheet(
    company: str,
    email: str,
    prop_name: str,
    drive_link: str,
    date_pitched: str,
    follow_up_due: str,
    sheet_name: str = None,
    credentials_path: str = None
):
    """
    Appends a new outreach lead record to the Google Sheet tracker.
    """
    target_sheet_name = sheet_name or os.getenv("GOOGLE_SHEET_NAME", "Real Estate Outreach Leads")
    client = get_sheets_client(credentials_path)
    sheet = client.open(target_sheet_name).sheet1

    row = [company, email, prop_name, drive_link, date_pitched, follow_up_due, "Pitched"]
    sheet.append_row(row)
