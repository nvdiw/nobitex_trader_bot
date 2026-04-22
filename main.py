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
from database_engine import DataBaseEngine
from nobitex_requests import Nobitex
from order_code import increment_order_code

# environment process
# Load environment variables from .env file
load_dotenv()
# Get NOBITEX_API_KEY from environment
NOBITEX_API_KEY = os.getenv('NOBITEX_API_KEY')

SYMBOL = "BTCUSDT"
symbol = "btc"
market_symbol = "BTC-USDT"
db_file='database.db'

default_balance = 100.0

nobitex = Nobitex(NOBITEX_API_KEY)
db_engine = DataBaseEngine(db_file)

@dataclass
class BotState_limbian_strategy:
    # settings:
    balance: float = db_engine.get_balance_from_db(balance_state="balance", default_balance=default_balance)  # 100
    first_balance: float = db_engine.get_balance_from_db(balance_state="first_balance", default_balance=default_balance)  # 100
    symbol_change_pct: float = 0.06
    more_symbol_change_pct: float = 0.05
    trade_amount_percent: float = 0.10
    max_open_trades: int = 10

    # variables
    last_price_entry: float = db_engine.get_variable_from_db(var_name='last_price_entry', default_value=0.0)
    order_code: str = db_engine.get_variable_from_db(var_name='order_code', default_value="order00001")

BOT_STATE = BotState_limbian_strategy()



# main limbian_strategy
def limbian_strategy(state):
    # get symbol data and save on database
    current_ts, past_ts = get_current_and_past_timestamps(days_ago=1)
    symbol_ohlcv_data = nobitex.get_market_history_symbol_nobitex(symbol= SYMBOL, fromm= past_ts, to= current_ts)
    db_engine.database_process_symbol_data(data=symbol_ohlcv_data, symbol=SYMBOL)

    # last candle data
    open_time_candle = timestamp_to_datetime(symbol_ohlcv_data["t"][-2])
    close_time_candle = timestamp_to_datetime(symbol_ohlcv_data["t"][-1])
    open_price_candle = symbol_ohlcv_data["o"][-2]
    high_price_candle = symbol_ohlcv_data["h"][-2]
    low_price_candle = symbol_ohlcv_data["l"][-2]
    close_price_candle = symbol_ohlcv_data["c"][-2]
    volume_candle = symbol_ohlcv_data["v"][-2]

    if state.last_price_entry <= close_price_candle:
        state.last_price_entry = close_price_candle
        db_engine.set_variable_in_db(var_name='last_price_entry', new_value=close_price_candle)



    # ===================== OPEN LONG =====================
    if (close_price_candle <= state.last_price_entry * (1 - state.symbol_change_pct)) and (len(open_positions) < state.max_open_trades):

        state.last_price_entry = close_price_candle
        db_engine.set_variable_in_db(var_name='last_price_entry', new_value=close_price_candle)

        # price process for open long
        orderbook_data = nobitex.get_orderbook_symbol_nobitex(symbol= SYMBOL)
        last_asks_order = float(orderbook_data["asks"][0][0])

        # amount process for open long
        if state.balance >= state.first_balance * state.trade_amount_percent:
            order_cost = state.first_balance * state.trade_amount_percent
        else:
            order_cost = state.balance
        amount = order_cost / last_asks_order

        # ---- open long in nobitex ----
        open_long_data = nobitex.set_order_symbol_nobitex(type= "buy", execution="limit", symbol=symbol, amount= amount, price= last_asks_order, id= state.order_code)
        time.sleep(1)
        # success
        if open_long_data['status'] == "ok":
            # order code +1 number
            state.order_code = increment_order_code(state.order_code)
            db_engine.set_variable_in_db(var_name='order_code', new_value=state.order_code)
            # balance decrease
            state.balance -= order_cost
            db_engine.set_balance_in_db(balance_state="balance", new_value=state.balance)
            # print
            print(f"BUY order set: {open_long_data["order"]["srcCurrency"]} price: {open_long_data["order"]["price"]} order_size: {open_long_data["order"]["amount"]} | {open_long_data["order"]["totalOrderPrice"]}$")
            # inset opened positions in database
            db_engine.save_order_to_db(open_long_data, status= "OPEN")
        
        else:
            print("Your Open_Order Failed")

        open_long_data = None
    # ======================================================

    
    open_positions = db_engine.load_open_positions(market=market_symbol)


    # ===================== CLOSE LONG =====================
    for p in open_positions:
        if p['price'] * (1 + state.symbol_change_pct + state.more_symbol_change_pct) <= close_price_candle:
            # price process for close long
            orderbook_data = nobitex.get_orderbook_symbol_nobitex(symbol= SYMBOL)
            last_bids_order = float(orderbook_data["bids"][0][0])

            # amount process for close long
            amount = p['amount']

            # ---- close long in nobitex ----
            close_long_data = nobitex.set_order_symbol_nobitex(type= "sell", execution="limit", symbol=symbol, amount= amount, price= last_bids_order, id= state.order_code)
            time.sleep(1)
            # success
            if close_long_data['status'] == "ok":
                # order code +1 number
                state.order_code = increment_order_code(state.order_code)
                db_engine.set_variable_in_db(var_name='order_code', new_value=state.order_code)
                # balance increase
                state.balance += close_long_data["order"]["totalOrderPrice"]
                db_engine.set_balance_in_db(balance_state="balance", new_value=state.balance)
                # print
                print(f"SELL order set: {close_long_data["order"]["srcCurrency"]} price: {close_long_data["order"]["price"]} order_size: {close_long_data["order"]["amount"]} | {close_long_data["order"]["totalOrderPrice"]}$")
                # CLOSE opened positions in database
                db_engine.close_order_in_db(client_order_id= p['client_order_id'], status= "CLOSE")
                # Remove From open_positions
                open_positions.remove(p)
            else:
                print("Your CLOSE_Order Failed")

            close_long_data = None
    # ======================================================

# ==== MIAN ====
def main(state):
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run trading strategy')
    parser.add_argument('--test', action='store_true',
                       help='Run strategy once immediately without time schedule')
    args = parser.parse_args()

    # checking for "can be / can't be" trade
    nobitex_balance = float(nobitex.symbol_wallet_balance_nobitex(symbol= "usdt"))
    if state.balance <= nobitex_balance:
        print(f"Bot needs {state.balance} $ and you have {round(nobitex_balance, 2)} $ so bot can trade")
    else: 
        print(f"Bot needs {state.balance} $ and you have {round(nobitex_balance, 2)} $ so bot can't trade")
        return

    if args.test:
        # Test mode: run once immediately
        limbian_strategy(BOT_STATE)
    else:
        # Normal mode: run at 0, 15, 30, 45 minutes
        print("Scheduled mode: Running strategy every 15 minutes at 0, 15, 30, 45")
        
        while True:
            now = datetime.now()
            minute = now.minute
            
            # Check if current minute is 0, 15, 30, or 45
            if minute in [0, 15, 30, 45]:
                # Check if second is 0 to run exactly at the start of minute
                if now.second == 1:
                    limbian_strategy(BOT_STATE)
                    time.sleep(1)  # Sleep 1 second to avoid running multiple times
            time.sleep(0.5)  # Check every 0.5 seconds


if __name__ == "__main__":
    main(BOT_STATE)