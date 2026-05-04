# 🤖 Nobitex Automated Trading Bot

**A production-ready trading bot** connected to [Nobitex](https://nobitex.ir) cryptocurrency exchange.  
Built with modular Python architecture, persistent state management, and scheduled execution.

> 🔍 **Focus:** API integration, database persistence, error handling, and clean code — **not trading strategy details**.

---

## ✨ Key Features

- 🔌 **Real connection to Nobitex API** – market data, orderbook, buy/sell orders  
- 💾 **Persistent state** – balance, last price, order codes, open positions stored in **SQLite**  
- ⏱️ **Scheduled execution** – runs every 15 minutes (at 0, 15, 30, 45)  
- 🧪 **Test mode** – run once immediately with `--test` flag  
- 🔐 **Secure API key** – loaded from `.env` file, never hardcoded  
- 🧩 **Modular design** – separate modules for time handling, database, API requests, order code generation  

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Language** | Python 3.9+ |
| **API & HTTP** | `requests`, custom `Nobitex` wrapper |
| **Database** | SQLite (via custom `DataBaseEngine`) |
| **Configuration** | `python-dotenv`, `argparse` |
| **Data Structures** | `dataclasses` for bot state |
| **Time Handling** | custom `time_engine` (timestamp conversion, date math) |
| **Code Style** | Type hints, docstrings, modular imports |

---

## 🧱 Architecture Overview
nobitex_limbian_bot/
├── main.py # Entry point, scheduling, strategy loop
├── time_engine.py # Timestamp utilities
├── database_engine.py # SQLite CRUD for balances, state, orders, market data
├── nobitex_requests.py # Nobitex API wrapper (REST calls)
├── order_code.py # Auto-increment order ID generator
├── .env # NOBITEX_API_KEY (not committed)
└── database.db # SQLite file (auto-created)


### How it works (engineering view)

1. **Load environment** – reads API key and configuration  
2. **Initialize state** – `BotState_limbian_strategy` (balance, thresholds, etc.) loaded from DB  
3. **Main loop** – runs on schedule (or test mode)  
   - Fetch latest OHLCV data from Nobitex  
   - Update `last_price_entry` in DB  
   - Load open positions from DB  
   - Evaluate conditions (based on price change) → open or close orders  
   - Execute orders via Nobitex API  
   - Update balance, order code, and position status in DB  
4. **Error handling** – basic print statements for failed orders (can be extended to logging)

> ⚠️ The trading logic (entry/exit conditions) is **intentionally not detailed** here – this README focuses on the software engineering aspects.

---

## 📊 Database Schema (exposed by `DataBaseEngine`)

| Table / Purpose | Key fields |
|----------------|-------------|
| `balance` | stores current and initial balance |
| `variables` | key-value store for `last_price_entry`, `order_code` |
| `open_positions` | tracks active orders with status (OPEN/CLOSE) |
| `symbol_data` | historical OHLCV for backtesting (optional) |

All operations are wrapped in the `DataBaseEngine` class, making the main code database-agnostic.

---

## 🚀 Getting Started

### 1. Clone & install dependencies
```bash
git clone https://github.com/nvdiw/nobitex_limbian_bot.git
cd nobitex_limbian_bot
pip install requests python-dotenv

2.Set up environment:
Create a .env file:
add: NOBITEX_API_KEY=your_api_key_here

3. Run the bot:
# Normal mode – runs every 15 minutes
python main.py

# Test mode – runs once immediately
python main.py --test

📈 Example Output (console)
Bot needs 100.0 $ and you have 250.0 $ so bot can trade
BUY order set: BTC price: 35000 order_size: 0.0002857 | 9.99$
SELL order set: BTC price: 35100 order_size: 0.0002857 | 10.02$

📬 Contact & Links

    GitHub: github.com/nvdiw

    Telegram: @nvdiw