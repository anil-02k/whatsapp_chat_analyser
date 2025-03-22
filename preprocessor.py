import re
import pandas as pd
from typing import Optional
from datetime import datetime

def preprocess(data: str) -> pd.DataFrame:
    """
    Preprocess WhatsApp chat data into a structured DataFrame.
    
    Args:
        data (str): Raw WhatsApp chat export text
        
    Returns:
        pd.DataFrame: Processed chat data with columns for date, user, message, and time features
        
    Raises:
        ValueError: If input data is empty or invalid
    """
    if not data or not isinstance(data, str):
        raise ValueError("Input data must be a non-empty string")
        
    # Normalize different space characters and line endings
    # Handle various types of spaces including the special WhatsApp space
    data = data.replace('\u202f', ' ').replace('\xa0', ' ').replace('\r\n', '\n').replace('\u200b', '').strip()
    
    if not data:
        raise ValueError("No valid data found after normalization")

    # Print first few lines for debugging
    print("First few lines of input data:")
    print("\n".join(data.split('\n')[:5]))

    # Split the data into lines
    lines = data.split('\n')
    
    # Initialize lists to store data
    dates = []
    messages = []
    
    # Process each line
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
            
        # Try to match the date pattern at the start of the line
        match = re.match(r'(\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}(?::\d{2})?\s*[APap][Mm])\s*-\s*(.*)', line)
        if match:
            date_str = match.group(1)
            message = match.group(2).strip()
            dates.append(date_str)
            messages.append(message)
            
    if not dates or not messages:
        raise ValueError("No valid date-message pairs found")

    print(f"Found {len(dates)} valid messages")
    print("Sample date:", dates[0])
    print("Sample message:", messages[0])

    # Create DataFrame
    df = pd.DataFrame({'date': dates, 'message': messages})

    # Convert dates with error handling
    try:
        # Try multiple date formats
        date_formats = [
            '%d/%m/%y, %I:%M %p',
            '%d/%m/%Y, %I:%M %p',
            '%d/%m/%y, %I:%M:%S %p',
            '%d/%m/%Y, %I:%M:%S %p',
            '%d/%m/%y %I:%M %p',
            '%d/%m/%Y %I:%M %p',
            '%d/%m/%y %I:%M:%S %p',
            '%d/%m/%Y %I:%M:%S %p',
            '%d/%m/%y, %H:%M',
            '%d/%m/%Y, %H:%M',
            '%d/%m/%y, %H:%M:%S',
            '%d/%m/%Y, %H:%M:%S',
            '%d/%m/%y %H:%M',
            '%d/%m/%Y %H:%M',
            '%d/%m/%y %H:%M:%S',
            '%d/%m/%Y %H:%M:%S'
        ]
        
        for fmt in date_formats:
            try:
                df['date'] = pd.to_datetime(df['date'], format=fmt, errors='raise')
                print(f"Successfully parsed dates with format: {fmt}")
                break
            except ValueError:
                continue
        else:
            raise ValueError("Could not parse dates with any known format")
            
        df = df.dropna(subset=['date'])
        
    except Exception as e:
        raise ValueError(f"Date conversion error: {str(e)}")

    # Extract user/message with improved regex
    # Handles cases where there might be multiple colons in the message
    user_message = df['message'].str.extract(r'^([^:]+):\s*(.*)$', expand=True)
    df['user'] = user_message[0].fillna('system')
    df['message'] = user_message[1].fillna(df['message'])

    # Add time features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['period'] = df['hour'].apply(lambda h: f"{h:02d}-{(h+1 if h < 23 else 0):02d}")

    # Validate the processed data
    if df.empty:
        raise ValueError("No valid messages found after processing")
        
    print(f"✅ Successfully processed {len(df)} messages!")
    return df