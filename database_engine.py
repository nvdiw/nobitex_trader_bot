import sqlite3
import datetime

# save symbol data to data base with symbol name
def database_process_symbol_data(data, db_file='database.db', symbol="BTCUSDT"):
    """
    Processes stock price data, inserts it into an SQLite database,
    and returns a summary of the operation.

    Args:
        data (dict): A dictionary containing stock data with keys like 't', 'o', 'h', 'l', 'c', 'v'.
                     't' is a list of timestamps, others are lists of corresponding prices/volumes.
        db_file (str): The name of the SQLite database file.

    Returns:
        str: A summary message indicating the number of records inserted and skipped.
    """
    
    # Function to convert Unix timestamps to a readable datetime format
    def format_timestamp(ts):
        # Using ISO 8601 format for better compatibility, e.g., 'YYYY-MM-DD HH:MM:SS'
        return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    # Connect to the database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    # Using a UNIQUE constraint on open_time to ensure no duplicate entries based on this field
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {symbol}_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        open_time TEXT NOT NULL UNIQUE,
        close_time TEXT NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL
    )
    ''')
    conn.commit()

    # Process and insert data
    inserted_count = 0
    skipped_count = 0

    # Check if all lists have the same length before processing
    if 't' in data and 'o' in data and 'h' in data and 'l' in data and 'c' in data and 'v' in data and \
       len(data['t']) == len(data['o']) == len(data['h']) == len(data['l']) == len(data['c']) == len(data['v']):
        
        # Iterate through each data point
        for i in range(len(data['t']) - 1):
            row_times = data['t'] # Assuming 't' contains timestamps relevant to the current processing logic

            if len(row_times) > 0:
                open_time_ts = row_times[i] 
                
                if len(row_times) > 1:
                    close_time_ts = row_times[i + 1]
                else:
                    close_time_ts = row_times[i] 

                open_time_str = format_timestamp(open_time_ts)
                close_time_str = format_timestamp(close_time_ts)

                open_price = data['o'][i]
                high_price = data['h'][i]
                low_price = data['l'][i]
                close_price = data['c'][i]
                volume = data['v'][i]

                try:
                    cursor.execute(f'''
                    INSERT INTO {symbol}_prices (open_time, close_time, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (open_time_str, close_time_str, open_price, high_price, low_price, close_price, volume))
                    conn.commit()
                    inserted_count += 1
                except sqlite3.IntegrityError:
                    skipped_count += 1
            else:
                # If timestamp list 't' is empty, we might want to skip or log this
                # For now, assuming other lists are also empty or this iteration is invalid
                pass 
    else:
        # Handle inconsistent data lengths or missing keys
        # For this specific request, we'll assume valid input or skip processing if not.
        # If data is missing/inconsistent, counts remain 0.
        pass

    # Close the database connection
    conn.close()

    print(f"Operation completed. {inserted_count} new records inserted and {skipped_count} duplicate records skipped.")
    return True

