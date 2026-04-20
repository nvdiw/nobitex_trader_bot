import requests
import json
from datetime import datetime
import time
import argparse
from dataclasses import dataclass, field
import os
from dotenv import load_dotenv

# my codes :
from time_engine import get_current_and_past_timestamps, timestamp_to_datetime
from database_engine import database_process_symbol_data, get_balance_from_db
from nobitex_requests import get_market_history_symbol_nobitex

# environment process
# Load environment variables from .env file
load_dotenv()
# Get NOBITEX_API_KEY from environment
NOBITEX_API_KEY = os.getenv('NOBITEX_API_KEY')

symbol = "BTCUSDT"
db_file='database.db'

open_positions = []

@dataclass
class BotState_limbian_strategy:
    # settings:
    balance: float = 100
    symbol_change_pct: float = 0.06
    more_symbol_change_pct: float = 0.05
    max_open_trades: int = 10

    # variables
    last_price_entry: float = 0.0

BOT_STATE = BotState_limbian_strategy()


# main limbian_strategy
def limbian_strategy(state):
    # setting:


    current_ts, past_ts = get_current_and_past_timestamps(days_ago=1)
    symbol_ohlcv_data = get_market_history_symbol_nobitex(symbol= symbol, fromm= past_ts, to= current_ts)

    last_open_time_candle = timestamp_to_datetime(symbol_ohlcv_data["t"][-2])
    last_close_time_candle = timestamp_to_datetime(symbol_ohlcv_data["t"][-1])
    last_open_price_candle = symbol_ohlcv_data["o"][-2]
    last_high_price_candle = symbol_ohlcv_data["h"][-2]
    last_low_price_candle = symbol_ohlcv_data["l"][-2]
    last_close_price_candle = symbol_ohlcv_data["c"][-2]
    last_volume_candle = symbol_ohlcv_data["v"][-2]

    balance = get_balance_from_db(db_file=db_file, default_balance=state.balance)

    if state.last_price_entry <= last_close_price_candle:
        state.last_price_entry = last_close_price_candle

    # ===================== OPEN LONG =====================
    # if (last_close_price_candle <= state.last_price_entry * (1 - state.symbol_change_pct)) and (len(open_positions) < state.max_open_trades):
        # ---- open long in nobitex ----

        # success
        
        # inset opened positions in database

    database_process_symbol_data(data=symbol_ohlcv_data, db_file=db_file, symbol=symbol)


# ==== MIAN ====
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run trading strategy')
    parser.add_argument('--test', action='store_true',
                       help='Run strategy once immediately without time schedule')
    args = parser.parse_args()

    if args.test:
        # Test mode: run once immediately
        print("Test mode: Running strategy once...")
        limbian_strategy(BOT_STATE)
        print("Strategy execution completed.")
    else:
        # Normal mode: run at 0, 15, 30, 45 minutes
        print("Scheduled mode: Running strategy every 15 minutes at 0, 15, 30, 45")
        print("Waiting for next scheduled time...")
        
        while True:
            now = datetime.now()
            minute = now.minute
            
            # Check if current minute is 0, 15, 30, or 45
            if minute in [0, 15, 30, 45]:
                # Check if second is 0 to run exactly at the start of minute
                if now.second == 0:
                    limbian_strategy(BOT_STATE)
                    time.sleep(1)  # Sleep 1 second to avoid running multiple times
            time.sleep(0.5)  # Check every 0.5 seconds


if __name__ == "__main__":
    main()