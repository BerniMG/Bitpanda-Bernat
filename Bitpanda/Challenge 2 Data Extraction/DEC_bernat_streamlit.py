import asyncio
import json
from datetime import datetime, timedelta
import streamlit as st
import gspread
from telethon.sync import TelegramClient
from google.oauth2.service_account import Credentials
from google.auth.exceptions import DefaultCredentialsError

# --- Configuration ---
API_ID = ""  # Insert API ID
API_HASH = ""  # Insert API Hash
CHANNEL_USERNAME = 'bitpanda_de'

# --- Helper Functions ---
def authorize_google_sheets(credentials_file):
    """Authorize and return Google Sheets client."""
    creds = Credentials.from_service_account_info(
        json.load(credentials_file),
        scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    )
    return gspread.authorize(creds)

async def fetch_btc_messages(client, start_date, end_date):
    """Fetch messages containing 'BTC' within the date range."""
    messages_with_dates = []
    offset_id = 0

    while True:
        messages = await client.get_messages(CHANNEL_USERNAME, offset_id=offset_id, limit=100)
        if not messages:
            break

        for msg in messages:
            msg_date = msg.date.replace(tzinfo=None)
            if msg_date < start_date:
                return messages_with_dates
            if msg_date <= end_date and msg.text and 'btc' in msg.text.lower():
                messages_with_dates.append([msg_date.strftime('%Y-%m-%d %H:%M:%S'), msg.text])

        offset_id = messages[-1].id

    return messages_with_dates

def ensure_columns_exist(worksheet):
    """Ensure the columns 'Date' and 'BTC Messages' are present in the first row."""
    if worksheet.row_values(1) != ["Date", "BTC Messages"]:
        worksheet.insert_row(["Date", "BTC Messages"], index=1)
        worksheet.format('A1:B1', {'textFormat': {'bold': True}})  # Apply bold formatting

def update_btc_messages_sheet(worksheet, btc_messages):
    """Append new messages and dates, avoiding duplicates and ensuring data is valid."""
    existing_messages = set(tuple(row) for row in worksheet.get_all_values()[1:])  # Exclude header
    new_messages = [msg for msg in btc_messages if tuple(msg) not in existing_messages and all(msg)]

    if new_messages:
        current_rows = len(worksheet.get_all_values())
        worksheet.insert_rows(new_messages, row=current_rows + 1)

    # Sort the 'Date' column in descending order (most recent first)
    worksheet.sort((1, 'des'))  # Sort by the first column (Date), descending
    return len(new_messages)

# --- Streamlit Interface ---
st.title("Telegram BTC Message Extractor")

# File uploader for credentials and input for Google Sheet ID
credentials_file = st.file_uploader("Upload Google Credentials JSON", type=["json"])
sheet_id = st.text_input("Enter the Google Sheet ID to update:")

# Date selection
is_last_day = st.checkbox("Last Day")
if is_last_day:
    start_date, end_date = datetime.combine(datetime.now() - timedelta(days=1), datetime.min.time()), datetime.now()
else:
    start_date = st.date_input("Start Date", datetime.now() - timedelta(days=1))
    end_date = st.date_input("End Date", datetime.now())
    if start_date > end_date:
        st.error("Start date must be before the end date.")
    else:
        start_date, end_date = datetime.combine(start_date, datetime.min.time()), datetime.combine(end_date, datetime.max.time())

# Extract and update BTC messages
if credentials_file and sheet_id:
    try:
        client_sheets = authorize_google_sheets(credentials_file)
        st.success("Connected to Google Sheets and Google Drive.")
        
        if st.button("Extract BTC Messages"):
            with st.spinner("Fetching messages..."):
                async def main():
                    async with TelegramClient('streamlit_session', API_ID, API_HASH) as client:
                        btc_messages = await fetch_btc_messages(client, start_date, end_date)
                        if btc_messages:
                            google_sheet = client_sheets.open_by_key(sheet_id)
                            worksheet = google_sheet.worksheet("BTC Messages") if "BTC Messages" in [ws.title for ws in google_sheet.worksheets()] else google_sheet.add_worksheet(title="BTC Messages", rows="100", cols="2")
                            ensure_columns_exist(worksheet)
                            new_message_count = update_btc_messages_sheet(worksheet, btc_messages)
                            if new_message_count > 0:
                                st.success(f"{new_message_count} new BTC messages added.")
                            else:
                                st.info("No new BTC messages to add.")
                            st.write(f"[Open Google Sheet](https://docs.google.com/spreadsheets/d/{sheet_id})")
                        else:
                            st.warning("No BTC messages found in the specified date range.")
                asyncio.run(main())

    except DefaultCredentialsError as e:
        st.error(f"Error with Google Sheets credentials: {e}")
    except gspread.SpreadsheetNotFound:
        st.error("The provided Google Sheet ID does not exist or cannot be accessed.")
else:
    st.info("Please upload credentials and provide a valid Google Sheet ID to proceed.")