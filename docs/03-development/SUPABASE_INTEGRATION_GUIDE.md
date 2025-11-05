# Supabase Integration Guide

Complete guide to setting up and using Supabase cloud database for QuantumTrader MT5 paper trading system.

## Table of Contents
1. [Why Supabase?](#why-supabase)
2. [Setup Instructions](#setup-instructions)
3. [Database Schema](#database-schema)
4. [Configuration](#configuration)
5. [Migration from SQLite](#migration-from-sqlite)
6. [Real-time Features](#real-time-features)
7. [Usage Examples](#usage-examples)
8. [Troubleshooting](#troubleshooting)

---

## Why Supabase?

### Benefits over SQLite

| Feature | SQLite | Supabase |
|---------|--------|----------|
| **Location** | Local file | Cloud PostgreSQL |
| **Multi-device** | ❌ No | ✅ Yes |
| **Real-time** | ❌ No | ✅ Yes |
| **Backup** | Manual | ✅ Automatic |
| **Dashboard** | ❌ No | ✅ Web UI |
| **Scalability** | Limited | ✅ High |
| **Team Access** | ❌ No | ✅ Yes |
| **Cost** | Free | ✅ FREE (500MB) |

### Use Cases

✅ **Perfect for:**
- Running bot on VPS, monitoring from laptop
- Multi-device access to trading data
- Real-time notifications on new trades
- Cloud backup and disaster recovery
- Team collaboration on same dataset
- Production deployment

⚠️ **Consider SQLite if:**
- Offline-only usage
- Privacy concerns (local data only)
- Very simple single-machine setup

---

## Setup Instructions

### Step 1: Create Supabase Project

1. **Sign up** at [https://supabase.com](https://supabase.com)
   - Free plan: 500MB database + 5GB storage
   - No credit card required

2. **Create new project:**
   - Click "New Project"
   - Choose organization (or create new)
   - Project name: `quantumtrader-mt5`
   - Database password: Generate strong password (save it!)
   - Region: Choose closest to your VPS/location
   - Click "Create new project"
   - Wait 2-3 minutes for provisioning

3. **Wait for setup** to complete (green checkmark appears)

### Step 2: Run SQL Schema

1. **Open SQL Editor:**
   - In Supabase dashboard, click "SQL Editor" in sidebar
   - Click "New Query"

2. **Copy schema:**
   - Open `database/supabase_schema.sql` from this project
   - Copy entire content

3. **Execute:**
   - Paste into SQL Editor
   - Click "Run" or press Ctrl+Enter
   - Wait for success message (should create 5 tables + views)

4. **Verify tables:**
   - Click "Database" > "Tables" in sidebar
   - You should see:
     * `orders`
     * `fills`
     * `positions`
     * `trades`
     * `account_history`

### Step 3: Enable Real-time

1. **Go to Database > Replication:**
   - In Supabase dashboard
   - Click "Replication" tab

2. **Enable tables:**
   - Find `trades` table → Toggle ON
   - Find `positions` table → Toggle ON
   - (Optional) Enable `orders` and `fills`

3. **Verify:**
   - Green checkmark should appear
   - Status: "Realtime enabled"

### Step 4: Get API Credentials

1. **Open Settings > API:**
   - In Supabase dashboard
   - Click "Settings" (gear icon)
   - Click "API"

2. **Copy credentials:**
   - **Project URL:** `https://xxxxx.supabase.co`
   - **anon public key:** Long string starting with `eyJ...`
   - ⚠️ DO NOT use service_role key (not needed)

3. **Save securely:**
   - These are safe to use in client code
   - Row Level Security protects your data

### Step 5: Configure QuantumTrader

1. **Copy config template:**
   ```powershell
   copy config\supabase.example.json config\supabase.json
   ```

2. **Edit `config/supabase.json`:**
   ```json
   {
     "database": {
       "backend": "supabase",
       "supabase": {
         "url": "https://your-project-ref.supabase.co",
         "anon_key": "paste-your-anon-key-here"
       }
     }
   }
   ```

3. **Save file** (never commit to git - already in .gitignore)

### Step 6: Install Dependencies

```powershell
pip install supabase
```

Or if using requirements.txt:
```powershell
pip install -r requirements.txt
```

---

## Database Schema

### Tables Overview

```sql
orders            -- All order submissions
├── fills         -- Order execution details (foreign key: order_id)
├── positions     -- Open and closed positions
├── trades        -- Completed roundtrip trades
└── account_history -- Account snapshots over time
```

### Table Details

#### 1. Orders Table
Stores all order submissions (pending, filled, cancelled, rejected).

**Key Columns:**
- `order_id` (VARCHAR): Unique order identifier
- `symbol` (VARCHAR): Trading symbol (e.g., EURUSD)
- `order_type` (VARCHAR): MARKET, LIMIT, STOP, STOP_LIMIT
- `side` (VARCHAR): BUY or SELL
- `quantity` (DECIMAL): Order size in lots
- `status` (VARCHAR): PENDING, FILLED, CANCELLED, REJECTED
- `created_time` (TIMESTAMPTZ): When order was submitted

**Indexes:**
- Primary: `order_id`
- Fast queries on: `symbol`, `status`, `created_time`

#### 2. Fills Table
Records each order execution (supports partial fills).

**Key Columns:**
- `fill_id` (VARCHAR): Unique fill identifier
- `order_id` (VARCHAR): Links to orders table
- `fill_price` (DECIMAL): Execution price
- `fill_volume` (DECIMAL): Filled quantity
- `commission` (DECIMAL): Commission paid
- `is_partial` (BOOLEAN): True if partial fill

**Relationship:**
- One order → Many fills (for partial executions)

#### 3. Positions Table
Tracks open and closed positions.

**Key Columns:**
- `position_id` (VARCHAR): Unique position ID
- `symbol` (VARCHAR): Trading symbol
- `entry_price` (DECIMAL): Average entry price
- `current_price` (DECIMAL): Latest price
- `is_open` (BOOLEAN): True if position open
- `unrealized_pnl` (DECIMAL): Current floating P&L
- `realized_pnl` (DECIMAL): Locked P&L after close
- `total_commission` (DECIMAL): All commission paid
- `stop_loss`, `take_profit` (DECIMAL): SL/TP levels

**Real-time Enabled:** ✅ Subscribe to position updates

#### 4. Trades Table
Completed trading roundtrips (entry + exit).

**Key Columns:**
- `trade_id` (INTEGER): Sequential trade number
- `symbol` (VARCHAR): Trading symbol
- `direction` (VARCHAR): LONG or SHORT
- `entry_time`, `exit_time` (TIMESTAMPTZ): Trade timespan
- `gross_pnl` (DECIMAL): P&L before costs
- `commission`, `swap`, `spread_cost`, `slippage` (DECIMAL): Cost breakdown
- `net_pnl` (DECIMAL): Final profit/loss
- `exit_reason` (VARCHAR): Why trade closed

**Real-time Enabled:** ✅ Subscribe to new trades

#### 5. Account History Table
Periodic account snapshots for equity curve.

**Key Columns:**
- `timestamp` (TIMESTAMPTZ): Snapshot time
- `balance` (DECIMAL): Account balance
- `equity` (DECIMAL): Balance + unrealized P&L
- `margin_used` (DECIMAL): Used margin
- `drawdown_pct` (DECIMAL): Current drawdown %
- `total_trades` (INTEGER): Cumulative trade count

### Views

Three helpful views are auto-created:

1. **`open_positions_summary`** - Grouped open positions by symbol
2. **`daily_performance`** - Daily P&L and win rate
3. **`symbol_performance`** - Statistics per trading symbol

---

## Configuration

### Minimal Config

```json
{
  "database": {
    "backend": "supabase",
    "supabase": {
      "url": "https://xxxxx.supabase.co",
      "anon_key": "your-anon-key"
    }
  }
}
```

### Full Config (with fallback)

```json
{
  "database": {
    "backend": "supabase",
    
    "supabase": {
      "url": "https://xxxxx.supabase.co",
      "anon_key": "your-anon-key"
    },
    
    "sqlite_fallback": {
      "enabled": true,
      "db_path": "data/paper_trading.db"
    }
  },
  
  "paper_trading": {
    "broker_api": {
      "use_supabase": true,
      "auto_update_interval": 1.0
    },
    
    "realtime": {
      "enabled": true,
      "subscribe_to_trades": true,
      "subscribe_to_positions": true
    }
  }
}
```

### Environment Variables (Alternative)

For production/VPS, use environment variables instead:

```powershell
# Set environment variables
$env:SUPABASE_URL = "https://xxxxx.supabase.co"
$env:SUPABASE_KEY = "your-anon-key"
```

Then in code:
```python
import os
config = SupabaseConfig(
    url=os.getenv('SUPABASE_URL'),
    key=os.getenv('SUPABASE_KEY')
)
```

---

## Migration from SQLite

If you have existing SQLite data, migrate to Supabase:

### Automatic Migration

```powershell
# Run migration tool
python scripts/migrate_to_supabase.py
```

**Interactive prompts:**
1. SQLite database path (default: `data/paper_trading.db`)
2. Supabase config path (default: `config/supabase.json`)
3. Confirm migration

**Output example:**
```
📊 MIGRATION SUMMARY
================================================================================
✅ ORDERS               Total:    150 | Migrated:    150 | Failed:      0
✅ FILLS                Total:    200 | Migrated:    200 | Failed:      0
✅ POSITIONS            Total:     80 | Migrated:     80 | Failed:      0
✅ TRADES               Total:     75 | Migrated:     75 | Failed:      0
✅ ACCOUNT_HISTORY      Total:    500 | Migrated:    500 | Failed:      0
================================================================================
TOTAL RECORDS:           1005
SUCCESSFULLY MIGRATED:   1005
FAILED:                  0
================================================================================
```

### Manual Migration

1. **Export from SQLite:**
   ```python
   from engines.database_manager import DatabaseManager
   
   db = DatabaseManager("data/paper_trading.db")
   trades = db.get_all_trades()
   ```

2. **Import to Supabase:**
   ```python
   from engines.supabase_database import SupabaseDatabase, SupabaseConfig
   
   config = SupabaseConfig(url="...", key="...")
   supabase_db = SupabaseDatabase(config)
   
   for trade in trades:
       supabase_db.save_trade(trade)
   ```

### Verify Migration

Check in Supabase Dashboard:
1. Go to "Database" > "Tables"
2. Click on `trades` table
3. Verify record count matches SQLite

---

## Real-time Features

### Subscribe to New Trades

Get notified instantly when trades close:

```python
from engines.supabase_database import SupabaseDatabase, SupabaseConfig

# Setup
config = SupabaseConfig(url="...", key="...")
db = SupabaseDatabase(config)

# Define callback
def on_new_trade(trade_data: dict):
    symbol = trade_data['symbol']
    pnl = trade_data['net_pnl']
    print(f"🎯 New trade closed: {symbol} | P&L: ${pnl:.2f}")
    
    # Send notification
    if pnl > 100:
        send_telegram_alert(f"Big win! ${pnl}")

# Subscribe
db.subscribe_to_trades(on_new_trade)

# Keep running
while True:
    time.sleep(1)
```

### Subscribe to Position Updates

Monitor position P&L in real-time:

```python
def on_position_update(position_data: dict):
    symbol = position_data['symbol']
    unrealized_pnl = position_data['unrealized_pnl']
    
    print(f"📊 {symbol} P&L: ${unrealized_pnl:.2f}")
    
    # Alert on drawdown
    if unrealized_pnl < -500:
        send_alert(f"⚠️ Large loss on {symbol}!")

db.subscribe_to_positions(on_position_update)
```

### Multi-Device Setup

**Scenario:** Bot on VPS, monitoring from laptop

**VPS (Trading Bot):**
```python
# Main trading bot runs here
api = PaperTradingBrokerAPI(use_supabase=True)
api.start_auto_update()

# Trades are saved to Supabase cloud
```

**Laptop (Monitor):**
```python
# Just subscribe to real-time updates
db = SupabaseDatabase(config)

def show_trade(trade):
    print(f"VPS closed trade: {trade}")

db.subscribe_to_trades(show_trade)
# Now you see trades instantly as VPS executes them!
```

---

## Usage Examples

### Basic CRUD Operations

```python
from engines.supabase_database import SupabaseDatabase, SupabaseConfig

# Connect
config = SupabaseConfig(
    url="https://xxxxx.supabase.co",
    key="your-anon-key"
)
db = SupabaseDatabase(config)

# Save order
order_data = {
    'order_id': 'ORD-001',
    'symbol': 'EURUSD',
    'order_type': 'MARKET',
    'side': 'BUY',
    'quantity': 0.1,
    'status': 'PENDING'
}
saved_order = db.save_order(order_data)
print(f"Order saved: {saved_order['id']}")

# Get all orders
orders = db.get_all_orders()
print(f"Total orders: {len(orders)}")

# Get trades for specific symbol
eurusd_trades = db.get_trades_by_symbol('EURUSD')
print(f"EURUSD trades: {len(eurusd_trades)}")

# Get open positions
open_positions = db.get_open_positions()
for pos in open_positions:
    print(f"{pos['symbol']}: ${pos['unrealized_pnl']:.2f}")
```

### Analytics

```python
# Get performance summary
stats = db.get_performance_summary()

print(f"Total Trades: {stats['total_trades']}")
print(f"Win Rate: {stats['win_rate']:.2f}%")
print(f"Net P&L: ${stats['net_pnl']:.2f}")
print(f"Avg Win: ${stats['avg_win']:.2f}")
print(f"Avg Loss: ${stats['avg_loss']:.2f}")
print(f"Profit Factor: {stats['profit_factor']:.2f}")

# Get statistics by symbol
symbol_stats = db.get_statistics(symbol='EURUSD')
print(f"EURUSD Win Rate: {symbol_stats['win_rate']:.2f}%")
```

### Paper Trading Integration

```python
from engines.paper_trading_broker_api import PaperTradingBrokerAPI

# Use Supabase instead of SQLite
api = PaperTradingBrokerAPI(
    initial_balance=10000.0,
    use_supabase=True,  # ← Enable Supabase
    supabase_config=config
)

# Start auto-update (saves to cloud)
api.start_auto_update()

# Submit order
order = api.submit_order(
    symbol='EURUSD',
    order_type='MARKET',
    side='BUY',
    quantity=0.1
)

# Data is automatically saved to Supabase!
```

---

## Troubleshooting

### Connection Errors

**Problem:** `ConnectionError: Could not connect to Supabase`

**Solutions:**
1. Check internet connection
2. Verify URL is correct (`https://xxxxx.supabase.co`)
3. Verify anon key is copied correctly
4. Check Supabase project status (dashboard)
5. Try VPN if firewall blocks Supabase

### Authentication Errors

**Problem:** `AuthError: Invalid API key`

**Solutions:**
1. Copy anon key again (full string)
2. DO NOT use service_role key
3. Check for extra spaces in config
4. Regenerate key in Supabase dashboard if needed

### Real-time Not Working

**Problem:** Subscriptions don't trigger

**Solutions:**
1. Enable Realtime in Dashboard > Database > Replication
2. Check table is enabled for realtime
3. Verify callback function is correct
4. Check network allows WebSocket connections
5. Add error handling to callback

### Migration Fails

**Problem:** Migration tool errors

**Solutions:**
1. Verify schema is created (run SQL first)
2. Check SQLite file exists
3. Ensure no duplicate data
4. Run migration in smaller batches
5. Check logs for specific errors

### Performance Issues

**Problem:** Slow queries

**Solutions:**
1. Check indexes are created (see schema)
2. Add more indexes if needed:
   ```sql
   CREATE INDEX idx_custom ON trades(symbol, exit_time);
   ```
3. Use connection pooling
4. Enable query caching
5. Upgrade Supabase plan if needed

### Data Not Syncing

**Problem:** Changes don't appear on other devices

**Solutions:**
1. Check internet connection both devices
2. Refresh browser if using dashboard
3. Verify both devices use same project
4. Check row-level security policies
5. Force reload: `db.client.postgrest.reload()`

---

## Advanced Features

### Custom Queries

```python
# Raw SQL query
result = db.client.rpc('custom_function', {'param': 'value'}).execute()

# Complex filter
high_profit_trades = db.client.table('trades') \
    .select('*') \
    .gte('net_pnl', 100) \
    .order('exit_time', desc=True) \
    .limit(10) \
    .execute()
```

### Batch Operations

```python
# Insert multiple trades
trades_batch = [
    {'trade_id': 1, 'symbol': 'EURUSD', ...},
    {'trade_id': 2, 'symbol': 'GBPUSD', ...},
]
db.client.table('trades').insert(trades_batch).execute()
```

### Export to Excel

```python
import pandas as pd

# Get all trades
trades = db.get_all_trades()

# Convert to DataFrame
df = pd.DataFrame(trades)

# Export
df.to_excel('trades_export.xlsx', index=False)
```

---

## Next Steps

After setup:

1. ✅ Verify tables in Supabase dashboard
2. ✅ Test connection with Python script
3. ✅ Migrate existing data (if any)
4. ✅ Update PaperTradingBrokerAPI to use Supabase
5. ✅ Test real-time subscriptions
6. ✅ Deploy to VPS with Supabase config
7. ✅ Monitor from multiple devices
8. (Optional) Build web dashboard
9. (Optional) Add Telegram alerts
10. (Optional) Set up automated backups

---

## Support

**Supabase Docs:** https://supabase.com/docs  
**Supabase Status:** https://status.supabase.com  
**Python Client:** https://github.com/supabase-community/supabase-py

**QuantumTrader Issues:** File issues on GitHub repository

---

**Last Updated:** November 2025  
**Version:** 2.0.0  
**Author:** QuantumTrader Team
