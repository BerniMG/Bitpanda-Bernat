
# Telegram BTC Message Extractor

This project provides two versions of a script for extracting messages from a Telegram channel that contain the word "BTC" and saving them to a Google Sheets document. The messages can be extracted from either the last day or a specific date range. The available versions are:

- **Streamlit Version**: Provides a graphical user interface (GUI) for easy interaction.
- **CMD Version**: Allows you to run the script directly from the command line.

## Features

- Extracts Telegram messages from the `bitpanda_de` channel that contain the keyword "BTC".
- Inserts the messages into a Google Sheets document.
- Avoids duplicates: only adds messages that haven't been previously recorded.
- Sorts the messages by date, displaying the most recent ones first.
- Allows you to select between extracting messages from the last day or from a custom date range.

## Prerequisites

1. **Python 3.8+** installed on your system.
2. A **Google Cloud** account with the **Google Sheets API** enabled.
3. A **credentials.json** file to authenticate the Google service account. This file is required for both versions.
4. A **Telegram account** to authenticate the Telegram client using the **API ID** and **API Hash** provided by Telegram.

## Installation

### Dependencies

You need to install the required dependencies using **pip** by running the following command:

```bash
pip install -r requirements.txt
```

Make sure you have the necessary `requirements.txt` file, or manually install the dependencies listed below:

```bash
pip install gspread google-auth telethon streamlit
```

### Google Sheets API

1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Sheets API**.
3. Create a **service account** and download the `credentials.json` file.
4. Share access to the Google Sheets document with the service account's email address.

### Telegram API

1. Create a Telegram application to obtain the **API ID** and **API Hash** at [Telegram API](https://my.telegram.org/auth).

---

## Usage

### Version 1: Script for **Streamlit**

This version provides a graphical user interface (GUI) using **Streamlit**.

#### Running the Script

1. Ensure you have **Streamlit** installed:
   ```bash
   pip install streamlit
   ```

2. Run the **Streamlit** script:
   ```bash
   streamlit run path/to/telegram_btc_extractor_streamlit.py
   ```

#### Features

1. **Upload the Google Credentials JSON**: Upload the `credentials.json` file from Google that authenticates the service account.
2. **Enter the Google Sheet ID**: Provide the ID of the Google Sheets document where the messages will be saved.
3. **Select the date range**:
   - You can extract messages from the last day or select a specific date range.
4. **Extract the messages**: Click the "Extract BTC Messages" button to begin extracting and logging the messages into Google Sheets.
5. **View the messages in Google Sheets**: After extraction, a direct link to the Google Sheets document will be provided.

#### `fetch_btc_messages` Function

This function connects to the Telegram channel and extracts messages that contain the "BTC" keyword within the selected date range. The extracted messages include the date and the message text.

#### `update_btc_messages_sheet` Function

After extracting the messages, this function:
1. **Checks if the sheet has the necessary columns** (`Date` and `BTC Messages`).
2. **Avoids duplicates**: Only adds messages that are not already in the sheet.
3. **Sorts by date**: Sorts the sheet by the date column in descending order (showing the most recent messages first).

---

### Version 2: Script for **Command Line (CMD)**

This version allows you to run the script directly from the command line.

#### Running the Script

1. Ensure you have the dependencies installed using **pip**:
   ```bash
   pip install gspread google-auth telethon
   ```

2. Run the **CMD** script:
   ```bash
   python path/to/telegram_btc_extractor_cmd.py
   ```

#### Features

1. **Enter the Google Credentials JSON file path**: The script will prompt you to enter the path to the `credentials.json` file from Google.
2. **Enter the Google Sheet ID**: The script will prompt you to provide the Google Sheets document ID where the messages will be saved.
3. **Select the date range**:
   - The script will ask if you want to extract messages from the last day or if you prefer to provide a specific date range.
4. **View the messages in Google Sheets**: Once the messages have been extracted, the script will provide you with a direct link to the Google Sheets document.

#### Example CMD Execution

```bash
$ python telegram_btc_extractor_cmd.py
Enter the path to your Google Credentials JSON file: /path/to/credentials.json
Enter the Google Sheet ID to update: 1Bc9kX6XYZabc1234
Do you want to extract messages from the last day? (y/n): y
Connected to Google Sheets.
Fetching messages...
5 new BTC messages added.
Open Google Sheet: https://docs.google.com/spreadsheets/d/1Bc9kX6XYZabc1234
```

---

### Technical Explanation

#### Message Validation
In both versions, the script validates that both the **date** and **message** are present before inserting them into Google Sheets. This prevents the insertion of empty or incorrect rows.

```python
new_messages = [msg for msg in btc_messages if tuple(msg) not in existing_messages and all(msg)]
```

#### Date Sorting
After inserting the new messages, the script sorts the **Date** column in descending order to ensure that the most recent messages always appear at the top.

```python
worksheet.sort((1, 'des'))  # Sort by the Date column, descending
```

#### Error Handling
In both scripts, Google authentication errors and Google Sheets access errors are handled gracefully. If the sheet is inaccessible or the ID is incorrect, the user is notified with a clear message.

```python
except DefaultCredentialsError as e:
    st.error(f"Error with Google Sheets credentials: {e}")
except gspread.SpreadsheetNotFound:
    st.error("The provided Google Sheet ID does not exist or cannot be accessed.")
```

---

## Additional Considerations

- Ensure you share the Google Sheets document with the service account associated with the `credentials.json` file, otherwise, the script will not be able to access the sheet.
- Double-check that your **API ID** and **API Hash** from Telegram are correct to avoid authentication errors when connecting to the Telegram channel.

---

## Conclusion

The **Streamlit** version offers a user-friendly graphical interface for non-technical users, while the **CMD** version is ideal for more technical users who prefer running scripts directly from the command line.
