import sqlite3
import datetime

# save symbol data to database with symbol name
def database_process_symbol_data(data, db_file='database.db', symbol="BTCUSDT"):
    """
    Processes stock price data, inserts it into an SQLite database,
    and returns a summary of the operation.
    """
    
    def format_timestamp(ts):
        return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

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

    new_count = 0
    old_count = 0

    if 't' in data and 'o' in data and 'h' in data and 'l' in data and 'c' in data and 'v' in data and \
       len(data['t']) == len(data['o']) == len(data['h']) == len(data['l']) == len(data['c']) == len(data['v']):
        
        # sorting data with open_time
        combined_data = list(zip(data['t'], data['o'], data['h'], data['l'], data['c'], data['v']))
        combined_data.sort(key=lambda x: x[0])
        sorted_times = [item[0] for item in combined_data]
        sorted_open = [item[1] for item in combined_data]
        sorted_high = [item[2] for item in combined_data]
        sorted_low = [item[3] for item in combined_data]
        sorted_close = [item[4] for item in combined_data]
        sorted_volume = [item[5] for item in combined_data]
        
        for i in range(len(sorted_times) - 1):
            row_times = sorted_times

            if len(row_times) > 0:
                open_time_ts = row_times[i] 
                
                if len(row_times) > 1:
                    close_time_ts = row_times[i + 1]
                else:
                    close_time_ts = row_times[i] 

                open_time_str = format_timestamp(open_time_ts)
                close_time_str = format_timestamp(close_time_ts)

                open_price = sorted_open[i]
                high_price = sorted_high[i]
                low_price = sorted_low[i]
                close_price = sorted_close[i]
                volume = sorted_volume[i]

                # ========== Added: Check if record exists before inserting ==========
                cursor.execute(f'''
                SELECT COUNT(*) FROM {symbol}_prices WHERE open_time = ?
                ''', (open_time_str,))
                
                exists = cursor.fetchone()[0] > 0
                # ============================================================
                
                try:
                    cursor.execute(f'''
                    INSERT OR REPLACE INTO {symbol}_prices (open_time, close_time, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (open_time_str, close_time_str, open_price, high_price, low_price, close_price, volume))
                    
                    conn.commit()
                    
                    # ========== old or new ==========
                    if exists:
                        old_count += 1
                    else:
                        new_count += 1
                    # ========================================
                    
                except sqlite3.IntegrityError:
                    pass
            else:
                pass 
    else:
        pass

    conn.close()

    total = new_count + old_count
    print(f"Operation completed: {new_count} new, {old_count} old (total {total} records processed) insert to database")
    return True

# get balance from database
def get_balance_from_db(db_file='database.db', default_balance=100):
    """
    Get balance from database. If balance table doesn't exist or no balance record,
    create it with default value and return default balance.
    
    Args:
        db_file (str): The name of the SQLite database file.
        default_balance (float): Default balance value if not exists.
    
    Returns:
        float: Current balance
    """
    import sqlite3
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Create balance table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS balance (
        id INTEGER PRIMARY KEY CHECK (id = 1),  -- Only one row allowed
        amount REAL NOT NULL DEFAULT 100
    )
    ''')
    
    # Check if balance record exists
    cursor.execute('SELECT amount FROM balance WHERE id = 1')
    result = cursor.fetchone()
    
    if result is None:
        # No balance record, insert default value
        cursor.execute('INSERT INTO balance (id, amount) VALUES (1, ?)', (default_balance,))
        conn.commit()
        balance = default_balance
        print(f"Balance table created with default balance: {balance}")
    else:
        balance = result[0]
        # print(f"Current balance: {balance}")
    
    conn.close()
    return balance


# set balance in database
def set_balance_in_db(new_balance, db_file='database.db'):
    """
    Update balance value in database.
    
    Args:
        new_balance (float): New balance value to set
        db_file (str): The name of the SQLite database file.
    
    Returns:
        float: The new balance value that was set
    """
    import sqlite3
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Create balance table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS balance (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        amount REAL NOT NULL DEFAULT 100
    )
    ''')
    
    # Update or insert balance
    cursor.execute('''
    INSERT OR REPLACE INTO balance (id, amount) VALUES (1, ?)
    ''', (new_balance,))
    
    conn.commit()
    conn.close()

    return new_balance


set_balance_in_db(100)