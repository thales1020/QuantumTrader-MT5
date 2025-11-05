# Supabase Database ERD (Entity Relationship Diagram)

## Visual Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SUPABASE DATABASE SCHEMA                             │
│                     QuantumTrader MT5 Paper Trading                         │
└─────────────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────┐
│           ORDERS                 │
├──────────────────────────────────┤
│ PK  id (BIGSERIAL)              │
│ UK  order_id (VARCHAR)          │◄──────┐
│     symbol (VARCHAR)            │       │
│     order_type (VARCHAR)        │       │
│     side (VARCHAR)              │       │  1:N Relationship
│     quantity (DECIMAL)          │       │  (One order → Many fills)
│     limit_price (DECIMAL)       │       │
│     stop_price (DECIMAL)        │       │
│     avg_fill_price (DECIMAL)    │       │
│     status (VARCHAR)            │       │
│     filled_quantity (DECIMAL)   │       │
│     remaining_quantity (DECIMAL)│       │
│     created_time (TIMESTAMPTZ)  │       │
│     filled_time (TIMESTAMPTZ)   │       │
│     cancelled_time (TIMESTAMPTZ)│       │
│     expires_at (TIMESTAMPTZ)    │       │
│     rejection_reason (TEXT)     │       │
│     cancelled_reason (TEXT)     │       │
│     strategy_name (VARCHAR)     │       │
│     created_at (TIMESTAMPTZ)    │       │
│     updated_at (TIMESTAMPTZ)    │       │
└──────────────────────────────────┘       │
                                           │
                                           │
                                           │
┌──────────────────────────────────┐       │
│            FILLS                 │       │
├──────────────────────────────────┤       │
│ PK  id (BIGSERIAL)              │       │
│ UK  fill_id (VARCHAR)           │       │
│ FK  order_id (VARCHAR)          │───────┘
│     fill_time (TIMESTAMPTZ)     │
│     fill_price (DECIMAL)        │
│     fill_volume (DECIMAL)       │
│     commission (DECIMAL)        │
│     is_partial (BOOLEAN)        │
│     remaining_volume (DECIMAL)  │
│     market_price (DECIMAL)      │
│     bid (DECIMAL)               │
│     ask (DECIMAL)               │
│     volume (INTEGER)            │
│     created_at (TIMESTAMPTZ)    │
└──────────────────────────────────┘


┌──────────────────────────────────┐
│          POSITIONS               │
├──────────────────────────────────┤
│ PK  id (BIGSERIAL)              │
│ UK  position_id (VARCHAR)       │
│     symbol (VARCHAR)            │
│     side (VARCHAR)              │
│     quantity (DECIMAL)          │
│     entry_price (DECIMAL)       │
│     current_price (DECIMAL)     │
│     exit_price (DECIMAL)        │
│     stop_loss (DECIMAL)         │
│     take_profit (DECIMAL)       │
│     is_open (BOOLEAN)           │
│     unrealized_pnl (DECIMAL)    │
│     realized_pnl (DECIMAL)      │
│     total_commission (DECIMAL)  │
│     total_swap (DECIMAL)        │
│     spread_cost (DECIMAL)       │
│     open_time (TIMESTAMPTZ)     │
│     close_time (TIMESTAMPTZ)    │
│     days_held (INTEGER)         │
│     exit_reason (VARCHAR)       │
│     strategy_name (VARCHAR)     │
│     created_at (TIMESTAMPTZ)    │
│     updated_at (TIMESTAMPTZ)    │
└──────────────────────────────────┘
         │
         │ When position closes
         │ → Creates trade record
         ▼
┌──────────────────────────────────┐
│           TRADES                 │
│    (Completed Roundtrips)        │
├──────────────────────────────────┤
│ PK  id (BIGSERIAL)              │
│     trade_id (INTEGER)          │
│     symbol (VARCHAR)            │
│     direction (VARCHAR)         │
│     entry_time (TIMESTAMPTZ)    │
│     exit_time (TIMESTAMPTZ)     │
│     entry_price (DECIMAL)       │
│     exit_price (DECIMAL)        │
│     lot_size (DECIMAL)          │
│     gross_pnl (DECIMAL)         │
│     commission (DECIMAL)        │
│     swap (DECIMAL)              │
│     spread_cost (DECIMAL)       │
│     slippage (DECIMAL)          │
│     net_pnl (DECIMAL)           │
│     pips (DECIMAL)              │
│     duration_hours (DECIMAL)    │
│     exit_reason (VARCHAR)       │
│     balance_after (DECIMAL)     │
│     equity_after (DECIMAL)      │
│     drawdown_pct (DECIMAL)      │
│     strategy_name (VARCHAR)     │
│     created_at (TIMESTAMPTZ)    │
└──────────────────────────────────┘


┌──────────────────────────────────┐
│       ACCOUNT_HISTORY            │
│    (Account Snapshots)           │
├──────────────────────────────────┤
│ PK  id (BIGSERIAL)              │
│     timestamp (TIMESTAMPTZ)     │
│     balance (DECIMAL)           │
│     equity (DECIMAL)            │
│     margin_used (DECIMAL)       │
│     free_margin (DECIMAL)       │
│     margin_level (DECIMAL)      │
│     num_positions (INTEGER)     │
│     num_pending_orders (INTEGER)│
│     daily_pnl (DECIMAL)         │
│     daily_return_pct (DECIMAL)  │
│     total_realized_pnl (DECIMAL)│
│     total_trades (INTEGER)      │
│     total_commission_paid (DEC) │
│     drawdown_usd (DECIMAL)      │
│     drawdown_pct (DECIMAL)      │
│     created_at (TIMESTAMPTZ)    │
└──────────────────────────────────┘
```

## Relationships

### 1. ORDERS ← FILLS (One-to-Many)
```
┌─────────┐     1      N    ┌──────┐
│ ORDERS  │◄───────────────►│FILLS │
└─────────┘                 └──────┘
  order_id ══════════════ order_id (FK)
```

**Type:** One-to-Many (CASCADE DELETE)  
**Constraint:** `FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE`  
**Business Logic:**
- One order can have multiple fills (partial fills)
- When order is deleted, all fills are automatically deleted
- Fill must belong to an existing order

### 2. POSITIONS → TRADES (Logical, Not FK)
```
┌───────────┐              ┌────────┐
│ POSITIONS │──┐           │ TRADES │
└───────────┘  │  Close    └────────┘
   is_open=T   │  Position
               │  Creates
               └──► Trade Record
```

**Type:** Logical Relationship (No FK constraint)  
**Business Logic:**
- When position closes (is_open = FALSE) → Creates trade record
- Position tracks real-time P&L (unrealized_pnl)
- Trade records final results (realized_pnl, net_pnl)
- No FK to allow flexible data management

### 3. ACCOUNT_HISTORY (Independent)
```
┌──────────────────┐
│ ACCOUNT_HISTORY  │  ← Periodic snapshots
└──────────────────┘     No FK relationships
```

**Type:** Independent Time-Series  
**Business Logic:**
- Periodic snapshots of account state
- Tracks equity curve over time
- No direct relationships with other tables
- Used for performance analysis

## Indexes

### ORDERS Table
```sql
idx_orders_order_id      → order_id         (Fast lookups)
idx_orders_symbol        → symbol           (Filter by symbol)
idx_orders_status        → status           (Filter by status)
idx_orders_created_time  → created_time ↓   (Sort by time)
idx_orders_strategy      → strategy_name    (Group by strategy)
```

### FILLS Table
```sql
idx_fills_fill_id        → fill_id          (Fast lookups)
idx_fills_order_id       → order_id         (JOIN with orders)
idx_fills_fill_time      → fill_time ↓      (Sort by time)
```

### POSITIONS Table
```sql
idx_positions_position_id → position_id     (Fast lookups)
idx_positions_symbol      → symbol          (Filter by symbol)
idx_positions_is_open     → is_open         (Filter open/closed)
idx_positions_open_time   → open_time ↓     (Sort by time)
idx_positions_strategy    → strategy_name   (Group by strategy)
```

### TRADES Table
```sql
idx_trades_trade_id      → trade_id         (Fast lookups)
idx_trades_symbol        → symbol           (Filter by symbol)
idx_trades_exit_time     → exit_time ↓      (Sort by time)
idx_trades_net_pnl       → net_pnl ↓        (Sort by profit)
idx_trades_strategy      → strategy_name    (Group by strategy)
idx_trades_direction     → direction        (Filter LONG/SHORT)
```

### ACCOUNT_HISTORY Table
```sql
idx_account_history_timestamp → timestamp ↓  (Time-series queries)
```

## Views (Aggregated Data)

### 1. open_positions_summary
```sql
CREATE VIEW open_positions_summary AS
SELECT 
    symbol,
    COUNT(*) as num_positions,
    SUM(quantity) as total_quantity,
    SUM(unrealized_pnl) as total_unrealized_pnl,
    AVG(entry_price) as avg_entry_price
FROM positions
WHERE is_open = TRUE
GROUP BY symbol;
```

**Usage:** Quick overview of open positions by symbol

### 2. daily_performance
```sql
CREATE VIEW daily_performance AS
SELECT 
    DATE(exit_time) as trade_date,
    COUNT(*) as num_trades,
    COUNT(CASE WHEN net_pnl > 0 THEN 1 END) as winning_trades,
    SUM(net_pnl) as daily_pnl,
    SUM(commission) as daily_commission,
    AVG(net_pnl) as avg_trade_pnl
FROM trades
GROUP BY DATE(exit_time);
```

**Usage:** Daily P&L summary

### 3. symbol_performance
```sql
CREATE VIEW symbol_performance AS
SELECT 
    symbol,
    COUNT(*) as num_trades,
    COUNT(CASE WHEN net_pnl > 0 THEN 1 END) as wins,
    ROUND(wins / COUNT(*) * 100, 2) as win_rate_pct,
    SUM(net_pnl) as total_pnl,
    AVG(net_pnl) as avg_pnl,
    MAX(net_pnl) as best_trade,
    MIN(net_pnl) as worst_trade
FROM trades
GROUP BY symbol;
```

**Usage:** Performance metrics per trading symbol

## Data Flow

```
┌────────────────────────────────────────────────────────────────┐
│                        TRADING WORKFLOW                        │
└────────────────────────────────────────────────────────────────┘

1. ORDER SUBMISSION
   ┌─────────┐
   │ ORDERS  │ ← New order submitted
   └────┬────┘   (status: PENDING)
        │
        ▼
2. ORDER MATCHING
   ┌──────┐
   │FILLS │ ← Market data matches order
   └──────┘   (partial or full fill)
        │
        ▼
3. POSITION CREATION
   ┌───────────┐
   │ POSITIONS │ ← Fill creates/updates position
   └─────┬─────┘   (is_open: TRUE)
         │
         │ Position tracks in real-time:
         │ - unrealized_pnl
         │ - current_price
         │ - stop_loss / take_profit
         │
         ▼
4. POSITION CLOSE
   ┌───────────┐
   │ POSITIONS │ ← SL/TP hit or manual close
   └─────┬─────┘   (is_open: FALSE)
         │
         ▼
5. TRADE RECORD
   ┌────────┐
   │ TRADES │ ← Complete roundtrip saved
   └────────┘   (entry + exit + costs + P&L)
         │
         ▼
6. ACCOUNT SNAPSHOT
   ┌──────────────────┐
   │ ACCOUNT_HISTORY  │ ← Periodic snapshots
   └──────────────────┘   (balance, equity, drawdown)
```

## Real-time Features

### Tables with Real-time Enabled

```
┌────────────┐  📡 Real-time    ┌──────────────┐
│   TRADES   │──────────────────►│ Subscribers  │
└────────────┘  WebSocket       └──────────────┘
                                 - VPS bot
┌────────────┐  📡 Real-time    - Laptop monitor
│ POSITIONS  │──────────────────►- Mobile app
└────────────┘  WebSocket       - Web dashboard
```

**Enabled via:**
```sql
ALTER PUBLICATION supabase_realtime ADD TABLE trades;
ALTER PUBLICATION supabase_realtime ADD TABLE positions;
```

**Usage:**
```python
# Subscribe to new trades
db.subscribe_to_trades(callback)

# Subscribe to position updates  
db.subscribe_to_positions(callback)
```

## Triggers

### Auto-Update Timestamp

```sql
CREATE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Applied to:
CREATE TRIGGER update_orders_updated_at 
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_positions_updated_at 
    BEFORE UPDATE ON positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## Data Types Summary

| Column Type | PostgreSQL Type | Range/Notes |
|------------|----------------|-------------|
| **IDs** | BIGSERIAL | Auto-increment, 1 to 9.2 quintillion |
| **Prices** | DECIMAL(18, 8) | 10 decimal places, precise for forex |
| **Quantities** | DECIMAL(18, 8) | Up to 999,999,999.99999999 lots |
| **Timestamps** | TIMESTAMPTZ | Timezone-aware, UTC stored |
| **Percentages** | DECIMAL(18, 4) | e.g., 1.2500% = 1.2500 |
| **Enums** | VARCHAR + CHECK | Validated: BUY/SELL, LONG/SHORT, etc. |
| **Status** | BOOLEAN | TRUE/FALSE for is_open |

## Security (Optional)

### Row Level Security (RLS)

```sql
-- Enable RLS (commented out by default)
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE fills ENABLE ROW LEVEL SECURITY;
ALTER TABLE positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE account_history ENABLE ROW LEVEL SECURITY;

-- Policy example: Allow authenticated users
CREATE POLICY "Allow all for authenticated users" ON orders
    FOR ALL USING (auth.role() = 'authenticated');
```

**Note:** RLS is optional. For single-user paper trading, not required.

## Query Performance Tips

### 1. Use Indexes
```sql
-- Fast: Uses idx_trades_symbol
SELECT * FROM trades WHERE symbol = 'EURUSD';

-- Slow: No index on duration_hours
SELECT * FROM trades WHERE duration_hours > 24;
```

### 2. Limit Results
```sql
-- Good: Limited results
SELECT * FROM trades ORDER BY exit_time DESC LIMIT 100;

-- Bad: Fetches all records
SELECT * FROM trades;
```

### 3. Use Views for Aggregations
```sql
-- Fast: Pre-aggregated view
SELECT * FROM symbol_performance;

-- Slower: On-the-fly aggregation
SELECT symbol, COUNT(*), AVG(net_pnl) FROM trades GROUP BY symbol;
```

### 4. Date Filtering
```sql
-- Fast: Index on timestamp
SELECT * FROM account_history 
WHERE timestamp >= '2025-01-01'::timestamptz;

-- Fast: Recent data
SELECT * FROM trades 
WHERE exit_time >= CURRENT_DATE - INTERVAL '7 days';
```

## Database Statistics

### Estimated Row Sizes

| Table | Columns | Avg Row Size | 1000 Records |
|-------|---------|--------------|--------------|
| orders | 19 | ~250 bytes | ~250 KB |
| fills | 12 | ~150 bytes | ~150 KB |
| positions | 23 | ~300 bytes | ~300 KB |
| trades | 24 | ~320 bytes | ~320 KB |
| account_history | 17 | ~200 bytes | ~200 KB |

### Storage Estimates

**Scenario: Active paper trading (1 year)**
- ~10,000 orders → 2.5 MB
- ~15,000 fills → 2.3 MB
- ~5,000 positions → 1.5 MB
- ~5,000 trades → 1.6 MB
- ~365 daily snapshots → 73 KB

**Total: ~8 MB/year**

**Supabase FREE Plan: 500 MB** → Enough for 60+ years of data! 🎉

---

**Last Updated:** November 2025  
**Version:** 2.0.1  
**Author:** QuantumTrader Team
