-- QuantumTrader MT5 - Supabase Database Schema
-- Version: 2.0.0
-- Date: November 2025
--
-- Run this SQL in Supabase SQL Editor to create all tables

-- ============================================
-- 1. ORDERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS orders (
    id BIGSERIAL PRIMARY KEY,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Order details
    symbol VARCHAR(20) NOT NULL,
    order_type VARCHAR(20) NOT NULL CHECK (order_type IN ('MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT')),
    side VARCHAR(10) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    quantity DECIMAL(18, 8) NOT NULL CHECK (quantity > 0),
    
    -- Prices
    limit_price DECIMAL(18, 8),
    stop_price DECIMAL(18, 8),
    avg_fill_price DECIMAL(18, 8) DEFAULT 0.0,
    
    -- Status
    status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'PARTIAL_FILLED', 'FILLED', 'CANCELLED', 'REJECTED', 'EXPIRED')),
    filled_quantity DECIMAL(18, 8) DEFAULT 0.0,
    remaining_quantity DECIMAL(18, 8),
    
    -- Time tracking
    created_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    filled_time TIMESTAMPTZ,
    cancelled_time TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    
    -- Metadata
    rejection_reason TEXT,
    cancelled_reason TEXT,
    strategy_name VARCHAR(100),
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for orders
CREATE INDEX idx_orders_order_id ON orders(order_id);
CREATE INDEX idx_orders_symbol ON orders(symbol);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_time ON orders(created_time DESC);
CREATE INDEX idx_orders_strategy ON orders(strategy_name);

-- Auto update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE
    ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 2. FILLS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS fills (
    id BIGSERIAL PRIMARY KEY,
    fill_id VARCHAR(50) UNIQUE NOT NULL,
    order_id VARCHAR(50) NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    
    -- Fill details
    fill_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fill_price DECIMAL(18, 8) NOT NULL,
    fill_volume DECIMAL(18, 8) NOT NULL CHECK (fill_volume > 0),
    commission DECIMAL(18, 8) DEFAULT 0.0,
    
    -- Fill type
    is_partial BOOLEAN DEFAULT FALSE,
    remaining_volume DECIMAL(18, 8),
    
    -- Market data at fill
    market_price DECIMAL(18, 8),
    bid DECIMAL(18, 8),
    ask DECIMAL(18, 8),
    volume INTEGER,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fills
CREATE INDEX idx_fills_fill_id ON fills(fill_id);
CREATE INDEX idx_fills_order_id ON fills(order_id);
CREATE INDEX idx_fills_fill_time ON fills(fill_time DESC);

-- ============================================
-- 3. POSITIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS positions (
    id BIGSERIAL PRIMARY KEY,
    position_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Position details
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    quantity DECIMAL(18, 8) NOT NULL CHECK (quantity > 0),
    
    -- Prices
    entry_price DECIMAL(18, 8) NOT NULL,
    current_price DECIMAL(18, 8),
    exit_price DECIMAL(18, 8),
    
    -- SL/TP
    stop_loss DECIMAL(18, 8),
    take_profit DECIMAL(18, 8),
    
    -- Status
    is_open BOOLEAN DEFAULT TRUE,
    
    -- P&L
    unrealized_pnl DECIMAL(18, 8) DEFAULT 0.0,
    realized_pnl DECIMAL(18, 8) DEFAULT 0.0,
    
    -- Costs
    total_commission DECIMAL(18, 8) DEFAULT 0.0,
    total_swap DECIMAL(18, 8) DEFAULT 0.0,
    spread_cost DECIMAL(18, 8) DEFAULT 0.0,
    
    -- Time tracking
    open_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    close_time TIMESTAMPTZ,
    days_held INTEGER DEFAULT 0,
    
    -- Metadata
    exit_reason VARCHAR(100),
    strategy_name VARCHAR(100),
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for positions
CREATE INDEX idx_positions_position_id ON positions(position_id);
CREATE INDEX idx_positions_symbol ON positions(symbol);
CREATE INDEX idx_positions_is_open ON positions(is_open);
CREATE INDEX idx_positions_open_time ON positions(open_time DESC);
CREATE INDEX idx_positions_strategy ON positions(strategy_name);

CREATE TRIGGER update_positions_updated_at BEFORE UPDATE
    ON positions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 4. TRADES TABLE (Completed Roundtrips)
-- ============================================
CREATE TABLE IF NOT EXISTS trades (
    id BIGSERIAL PRIMARY KEY,
    trade_id INTEGER NOT NULL,
    
    -- Trade details
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('LONG', 'SHORT')),
    
    -- Entry/Exit
    entry_time TIMESTAMPTZ NOT NULL,
    exit_time TIMESTAMPTZ NOT NULL,
    entry_price DECIMAL(18, 8) NOT NULL,
    exit_price DECIMAL(18, 8) NOT NULL,
    lot_size DECIMAL(18, 8) NOT NULL CHECK (lot_size > 0),
    
    -- P&L breakdown
    gross_pnl DECIMAL(18, 8) NOT NULL,
    commission DECIMAL(18, 8) DEFAULT 0.0,
    swap DECIMAL(18, 8) DEFAULT 0.0,
    spread_cost DECIMAL(18, 8) DEFAULT 0.0,
    slippage DECIMAL(18, 8) DEFAULT 0.0,
    net_pnl DECIMAL(18, 8) NOT NULL,
    
    -- Metrics
    pips DECIMAL(18, 4),
    duration_hours DECIMAL(18, 2),
    exit_reason VARCHAR(100),
    
    -- Running totals
    balance_after DECIMAL(18, 8),
    equity_after DECIMAL(18, 8),
    drawdown_pct DECIMAL(18, 4) DEFAULT 0.0,
    
    -- Metadata
    strategy_name VARCHAR(100),
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for trades
CREATE INDEX idx_trades_trade_id ON trades(trade_id);
CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_trades_exit_time ON trades(exit_time DESC);
CREATE INDEX idx_trades_net_pnl ON trades(net_pnl DESC);
CREATE INDEX idx_trades_strategy ON trades(strategy_name);
CREATE INDEX idx_trades_direction ON trades(direction);

-- ============================================
-- 5. ACCOUNT HISTORY TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS account_history (
    id BIGSERIAL PRIMARY KEY,
    
    -- Snapshot time
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Account metrics
    balance DECIMAL(18, 8) NOT NULL,
    equity DECIMAL(18, 8) NOT NULL,
    margin_used DECIMAL(18, 8) DEFAULT 0.0,
    free_margin DECIMAL(18, 8),
    margin_level DECIMAL(18, 4) DEFAULT 0.0,
    
    -- Position counts
    num_positions INTEGER DEFAULT 0,
    num_pending_orders INTEGER DEFAULT 0,
    
    -- Daily P&L
    daily_pnl DECIMAL(18, 8) DEFAULT 0.0,
    daily_return_pct DECIMAL(18, 4) DEFAULT 0.0,
    
    -- Cumulative
    total_realized_pnl DECIMAL(18, 8) DEFAULT 0.0,
    total_trades INTEGER DEFAULT 0,
    total_commission_paid DECIMAL(18, 8) DEFAULT 0.0,
    
    -- Drawdown
    drawdown_usd DECIMAL(18, 8) DEFAULT 0.0,
    drawdown_pct DECIMAL(18, 4) DEFAULT 0.0,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for account_history
CREATE INDEX idx_account_history_timestamp ON account_history(timestamp DESC);
-- Note: DATE(timestamp) index removed - use timestamp index with date filtering instead
-- Example query: WHERE timestamp >= CURRENT_DATE AND timestamp < CURRENT_DATE + INTERVAL '1 day'

-- ============================================
-- 6. ENABLE ROW LEVEL SECURITY (Optional)
-- ============================================
-- Uncomment below to enable RLS
-- This restricts access to authenticated users only

-- ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE fills ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE positions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE account_history ENABLE ROW LEVEL SECURITY;

-- Create policies (example for authenticated users)
-- CREATE POLICY "Allow all for authenticated users" ON orders
--     FOR ALL USING (auth.role() = 'authenticated');

-- CREATE POLICY "Allow all for authenticated users" ON fills
--     FOR ALL USING (auth.role() = 'authenticated');

-- CREATE POLICY "Allow all for authenticated users" ON positions
--     FOR ALL USING (auth.role() = 'authenticated');

-- CREATE POLICY "Allow all for authenticated users" ON trades
--     FOR ALL USING (auth.role() = 'authenticated');

-- CREATE POLICY "Allow all for authenticated users" ON account_history
--     FOR ALL USING (auth.role() = 'authenticated');

-- ============================================
-- 7. ENABLE REALTIME (Important!)
-- ============================================
-- Run this in Supabase SQL Editor to enable real-time subscriptions

-- For trades table (most important)
ALTER PUBLICATION supabase_realtime ADD TABLE trades;

-- For positions table
ALTER PUBLICATION supabase_realtime ADD TABLE positions;

-- For orders table (optional)
-- ALTER PUBLICATION supabase_realtime ADD TABLE orders;

-- For fills table (optional)
-- ALTER PUBLICATION supabase_realtime ADD TABLE fills;

-- ============================================
-- 8. HELPFUL VIEWS
-- ============================================

-- View: Open Positions Summary
CREATE OR REPLACE VIEW open_positions_summary AS
SELECT 
    symbol,
    COUNT(*) as num_positions,
    SUM(quantity) as total_quantity,
    SUM(unrealized_pnl) as total_unrealized_pnl,
    AVG(entry_price) as avg_entry_price
FROM positions
WHERE is_open = TRUE
GROUP BY symbol
ORDER BY total_unrealized_pnl DESC;

-- View: Daily Performance
CREATE OR REPLACE VIEW daily_performance AS
SELECT 
    DATE(exit_time) as trade_date,
    COUNT(*) as num_trades,
    COUNT(CASE WHEN net_pnl > 0 THEN 1 END) as winning_trades,
    SUM(net_pnl) as daily_pnl,
    SUM(commission) as daily_commission,
    AVG(net_pnl) as avg_trade_pnl
FROM trades
GROUP BY DATE(exit_time)
ORDER BY trade_date DESC;

-- View: Symbol Performance
CREATE OR REPLACE VIEW symbol_performance AS
SELECT 
    symbol,
    COUNT(*) as num_trades,
    COUNT(CASE WHEN net_pnl > 0 THEN 1 END) as wins,
    ROUND(COUNT(CASE WHEN net_pnl > 0 THEN 1 END)::NUMERIC / COUNT(*)::NUMERIC * 100, 2) as win_rate_pct,
    SUM(net_pnl) as total_pnl,
    AVG(net_pnl) as avg_pnl,
    MAX(net_pnl) as best_trade,
    MIN(net_pnl) as worst_trade
FROM trades
GROUP BY symbol
ORDER BY total_pnl DESC;

-- ============================================
-- 9. SAMPLE QUERIES
-- ============================================

-- Get today's trades
-- SELECT * FROM trades WHERE DATE(exit_time) = CURRENT_DATE ORDER BY exit_time DESC;

-- Get open positions with unrealized P&L
-- SELECT * FROM positions WHERE is_open = TRUE ORDER BY unrealized_pnl DESC;

-- Get pending orders
-- SELECT * FROM orders WHERE status = 'PENDING' ORDER BY created_time DESC;

-- Get account equity curve
-- SELECT timestamp, equity, balance, drawdown_pct FROM account_history ORDER BY timestamp;

-- Get win rate by strategy
-- SELECT 
--     strategy_name,
--     COUNT(*) as trades,
--     ROUND(COUNT(CASE WHEN net_pnl > 0 THEN 1 END)::NUMERIC / COUNT(*)::NUMERIC * 100, 2) as win_rate
-- FROM trades
-- GROUP BY strategy_name;

-- ============================================
-- SETUP COMPLETE!
-- ============================================
-- After running this script:
-- 1. Go to Supabase Dashboard > Database > Replication
-- 2. Enable Realtime for 'trades' and 'positions' tables
-- 3. Get your project URL and anon key from Settings > API
-- 4. Update your config.json with Supabase credentials
-- ============================================
