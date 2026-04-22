import sqlite3
import datetime
import pytz


class DataBaseEngine:
    def __init__(self, db_file):
        self.db_file = db_file


    # save symbol data to database with symbol name
    def database_process_symbol_data(self, data, symbol="BTCUSDT"):
        """
        Processes stock price data, inserts it into an SQLite database,
        and returns a summary of the operation.
        """
        
        def format_timestamp(ts):
            return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        conn = sqlite3.connect(self.db_file)
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
    def get_balance_from_db(self, balance_state="balance", default_balance=100.0):
        """
        Get balance from database. If balance table doesn't exist or no balance record,
        create it with default value and return default balance.
        
        Args:
            balance_state (str): The type/name of balance (e.g., "balance", "first_balance")
            db_file (str): The name of the SQLite database file.
            default_balance (float): Default balance value if not exists.
        
        Returns:
            float: Current balance for the specified state
        """
        import sqlite3
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create balance table if it doesn't exist (with state column)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT NOT NULL UNIQUE,
            amount REAL NOT NULL DEFAULT 100
        )
        ''')
        
        # Check if balance record exists for this state
        cursor.execute('SELECT amount FROM balance WHERE state = ?', (balance_state,))
        result = cursor.fetchone()
        
        if result is None:
            # No balance record for this state, insert default value
            cursor.execute('INSERT INTO balance (state, amount) VALUES (?, ?)', 
                        (balance_state, default_balance))
            conn.commit()
            balance = default_balance
            print(f"Balance '{balance_state}' created with default balance: {balance}")
        else:
            balance = result[0]
            # print(f"Current balance for '{balance_state}': {balance}")
        
        conn.close()
        return balance


    # set balance in database
    def set_balance_in_db(self, balance_state="balance", new_value=100.0):
        """
        Update balance value in database for a specific balance state.
        
        Args:
            balance_state (str): The type/name of balance (e.g., "balance", "first_balance")
            new_value (float): New balance value to set
            db_file (str): The name of the SQLite database file.
        
        Returns:
            float: The new balance value that was set
        """
        import sqlite3
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create balance table if it doesn't exist (with state column)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT NOT NULL UNIQUE,
            amount REAL NOT NULL DEFAULT 100
        )
        ''')
        
        # Update or insert balance for the specific state
        cursor.execute('''
        INSERT OR REPLACE INTO balance (state, amount) VALUES (?, ?)
        ''', (balance_state, new_value))
        
        conn.commit()
        conn.close()
        
        # print(f"Balance '{balance_state}' updated to: {new_value}")
        return new_value

    # save orders to database
    def save_order_to_db(self, order_data, status="OPEN"):
        """
        Save order to database with OPEN/CLOSE status
        status: "OPEN" for buy orders, "CLOSE" for sell orders
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create table with status column
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                order_type TEXT,
                market TEXT,
                price REAL,
                amount REAL,
                total_order_price REAL,
                client_order_id TEXT,
                created_at TEXT,
                status TEXT
            )
        ''')
        
        order = order_data['order']
        
        # Convert UTC to Tehran time
        utc_time = datetime.datetime.fromisoformat(order['created_at'].replace('+00:00', ''))
        utc_time = utc_time.replace(tzinfo=datetime.timezone.utc)
        tehran_tz = pytz.timezone('Asia/Tehran')
        tehran_time = utc_time.astimezone(tehran_tz)
        tehran_time_str = tehran_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Insert or replace order with status
        cursor.execute('''
            INSERT OR REPLACE INTO orders 
            (order_id, order_type, market, price, amount, total_order_price, client_order_id, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order['id'],
            order['type'],
            order['market'],
            float(order['price']),
            float(order['amount']),
            float(order['totalOrderPrice']),
            order.get('clientOrderId'),
            tehran_time_str,
            status  # OPEN or CLOSE
        ))
        
        conn.commit()
        conn.close()
        
        print(f"Order {order['id']} saved with status: {status}")


    # update order status: use when need to close order
    def update_order_status(self, order_id, new_status):
        """Update order status to OPEN or CLOSE"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE orders 
            SET status = ? 
            WHERE order_id = ?
        ''', (new_status, order_id))
        
        conn.commit()
        conn.close()
        print(f"Order {order_id} status updated to: {new_status}")


    # get variable from database
    def get_variable_from_db(self, var_name="variable", default_value=100):
        """
        Get variable value from database. If variables table doesn't exist or no variable record,
        create it with default value and return default value.
        
        Args:
            var_name (str): The name of the variable (e.g., "score", "level", "counter")
            default_value (any): Default value if variable doesn't exist
            db_file (str): The name of the SQLite database file.
        
        Returns:
            any: Current value of the variable
        """
        import sqlite3
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create variables table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS variables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            var_name TEXT NOT NULL UNIQUE,
            var_value TEXT NOT NULL
        )
        ''')
        
        # Check if variable exists
        cursor.execute('SELECT var_value FROM variables WHERE var_name = ?', (var_name,))
        result = cursor.fetchone()
        
        if result is None:
            # No variable record, insert default value
            cursor.execute('INSERT INTO variables (var_name, var_value) VALUES (?, ?)', 
                        (var_name, str(default_value)))
            conn.commit()
            variable_value = default_value
            print(f"Variable '{var_name}' created with default value: {variable_value}")
        else:
            # Try to convert back to original type if possible
            value_str = result[0]
            try:
                # Try to convert to int
                variable_value = int(value_str)
            except ValueError:
                try:
                    # Try to convert to float
                    variable_value = float(value_str)
                except ValueError:
                    # Keep as string
                    variable_value = value_str
        
        conn.close()
        return variable_value


    # set variable in database
    def set_variable_in_db(self, var_name="variable", new_value=100):
        """
        Update variable value in database for a specific variable name.
        
        Args:
            var_name (str): The name of the variable (e.g., "score", "level", "counter")
            new_value (any): New value to set (will be stored as string)
            db_file (str): The name of the SQLite database file.
        
        Returns:
            any: The new variable value that was set
        """
        import sqlite3
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create variables table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS variables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            var_name TEXT NOT NULL UNIQUE,
            var_value TEXT NOT NULL
        )
        ''')
        
        # Update or insert variable
        cursor.execute('''
        INSERT OR REPLACE INTO variables (var_name, var_value) VALUES (?, ?)
        ''', (var_name, str(new_value)))
        
        conn.commit()
        conn.close()
        
        # print(f"Variable '{var_name}' updated to: {new_value}")
        return new_value


    # load open positions
    def load_open_positions(self, market=None):
        """
        Load all open positions from orders table where status is 'OPEN'.
        
        Args:
            market (str, optional): Filter by market (e.g., 'BTC-USDT')
        
        Returns:
            list: List of dictionaries containing open positions
        """
        import sqlite3
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Check if orders table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("⚠️ Orders table does not exist. Creating it now...")
            # Create orders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY,
                    order_type TEXT,
                    market TEXT,
                    price REAL,
                    amount REAL,
                    total_order_price REAL,
                    client_order_id TEXT,
                    created_at TEXT,
                    status TEXT
                )
            ''')
            conn.commit()
            print("✓ Orders table created successfully.")
            conn.close()
            return []  # Return empty list since no positions exist
        
        if market:
            cursor.execute('''
            SELECT order_id, order_type, market, price, amount, total_order_price, client_order_id, created_at, status
            FROM orders
            WHERE status = 'OPEN' AND market = ?
            ORDER BY created_at DESC
            ''', (market,))
        else:
            cursor.execute('''
            SELECT order_id, order_type, market, price, amount, total_order_price, client_order_id, created_at, status
            FROM orders
            WHERE status = 'OPEN'
            ORDER BY created_at DESC
            ''')
        
        positions_data = cursor.fetchall()
        conn.close()
        
        # Convert each position to dictionary
        positions = []
        for pos in positions_data:
            position_dict = {
                'order_id': pos[0],
                'order_type': pos[1],
                'market': pos[2],
                'price': pos[3],
                'amount': pos[4],
                'total_order_price': pos[5],
                'client_order_id': pos[6],
                'created_at': pos[7],
                'status': pos[8]
            }
            positions.append(position_dict)
        
        return positions


    # order id --> status=CLOSE in database
    def close_order_in_db(self, client_order_id, status="CLOSE"):
        """
        Close an order in database by updating its status to CLOSE.
        
        Args:
            client_order_id (str): The client order ID of the order to close
            status (str): The status to set (default: "CLOSE")
        
        Returns:
            bool: True if order was found and updated, False otherwise
        """
        import sqlite3
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # First check if order exists
        cursor.execute('''
        SELECT order_id, client_order_id, status 
        FROM orders 
        WHERE client_order_id = ?
        ''', (client_order_id,))
        
        order = cursor.fetchone()
        
        if order is None:
            print(f"Order with client_order_id '{client_order_id}' not found.")
            conn.close()
            return False
        
        # Update the status to CLOSE
        cursor.execute('''
        UPDATE orders 
        SET status = ?
        WHERE client_order_id = ?
        ''', (status, client_order_id))
        
        conn.commit()
        conn.close()
        
        # print(f"Order {order[0]} (client_order_id: {client_order_id}) status updated to: {status}")
        return True


# # TEST
# db_engine = DataBaseEngine(db_file='database.db')
# db_engine.close_order_in_db(client_order_id="order00004")
# positions = db_engine.load_open_positions()