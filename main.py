API_KEY = "2ee30ea71645ba96e42c1f5b100d0a4bc59b57a9"
import requests
import json
import datetime

# my codes :
from time_engine import get_current_and_past_timestamps, timestamp_to_datetime
from database_engine import database_process_symbol_data, get_balance_from_db
from nobitex_requests import get_market_history_symbol_nobitex

symbol = "BTCUSDT"
db_file='database.db'

# variables:
variable = {}
variable["last_price_entry"] = 0

open_positions = []

# main strategy
def main():
    # setting:
    balance = 100
    symbol_change_pct = 0.06
    more_symbol_change_pct = 0.05
    max_open_trades = 10

    current_ts, past_ts = get_current_and_past_timestamps(days_ago=1)
    symbol_ohlcv_data = get_market_history_symbol_nobitex(symbol= symbol, fromm= past_ts, to= current_ts)

    last_open_time_candle = timestamp_to_datetime(symbol_ohlcv_data["t"][-2])
    last_close_time_candle = timestamp_to_datetime(symbol_ohlcv_data["t"][-1])
    last_open_price_candle = symbol_ohlcv_data["o"][-2]
    last_high_price_candle = symbol_ohlcv_data["h"][-2]
    last_low_price_candle = symbol_ohlcv_data["l"][-2]
    last_close_price_candle = symbol_ohlcv_data["c"][-2]
    last_volume_candle = symbol_ohlcv_data["v"][-2]

    balance = get_balance_from_db(db_file=db_file, default_balance=balance)

    if variable["last_price_entry"] <= last_close_price_candle:
        variable["last_price_entry"] = last_close_price_candle

    # ===================== OPEN LONG =====================
    # if (last_close_price_candle <= variable["last_price_entry"] * (1 - symbol_change_pct)) and (len(open_positions) < max_open_trades):
        # ---- open long in nobitex ----

        # success
        
        # inset opened positions in database

    database_process_symbol_data(data=symbol_ohlcv_data, db_file=db_file, symbol=symbol)

main()