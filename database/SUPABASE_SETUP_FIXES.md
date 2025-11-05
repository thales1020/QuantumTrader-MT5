# Supabase Setup - Common Fixes

## Issue: IMMUTABLE Function Error

**Error Message:**
```
ERROR: 42P17: functions in index expression must be marked IMMUTABLE
```

**Cause:**
- PostgreSQL requires functions in default values to be IMMUTABLE
- `NOW()` is STABLE, not IMMUTABLE
- Use `CURRENT_TIMESTAMP` instead

**Fix Applied:**
✅ Changed all `DEFAULT NOW()` to `DEFAULT CURRENT_TIMESTAMP`
✅ Updated trigger function to use `CURRENT_TIMESTAMP`

**Status:** Fixed in `supabase_schema.sql` v2.0.1

---

## How to Apply Fixed Schema

### Option 1: Fresh Install (Recommended)

If you haven't run the schema yet:

```sql
-- In Supabase SQL Editor, run the updated schema
-- Copy entire content from database/supabase_schema.sql
-- Paste and execute
```

### Option 2: Already Created Tables

If you already ran the old schema and got errors:

```sql
-- 1. Drop existing trigger function
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- 2. Recreate with CURRENT_TIMESTAMP
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 3. Recreate triggers
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE
    ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_positions_updated_at BEFORE UPDATE
    ON positions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Option 3: Complete Reset

If you want to start fresh:

```sql
-- ⚠️ WARNING: This deletes all data!

-- Drop all tables
DROP TABLE IF EXISTS account_history CASCADE;
DROP TABLE IF EXISTS trades CASCADE;
DROP TABLE IF EXISTS positions CASCADE;
DROP TABLE IF EXISTS fills CASCADE;
DROP TABLE IF EXISTS orders CASCADE;

-- Drop function
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- Now run the full schema from database/supabase_schema.sql
```

---

## Verification

After applying the fix, verify:

```sql
-- Check tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- Should show:
-- account_history
-- fills
-- orders
-- positions
-- trades

-- Check trigger function exists
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_name = 'update_updated_at_column';

-- Should show:
-- update_updated_at_column
```

---

## Testing

Run the test script:

```powershell
python scripts/test_supabase.py
```

Expected output:
```
✅ PASSED    Connection
✅ PASSED    Order Operations
✅ PASSED    Trade Operations
✅ PASSED    Position Operations
✅ PASSED    Account History
✅ PASSED    Statistics
✅ PASSED    Real-time
```

---

## Other Common Issues

### Issue: Tables Not Found

**Error:** `relation "orders" does not exist`

**Solution:**
```sql
-- Run the full schema
-- Copy from database/supabase_schema.sql
```

### Issue: Real-time Not Working

**Error:** Subscriptions don't trigger

**Solution:**
1. Go to Database → Replication
2. Enable `trades` table
3. Enable `positions` table
4. Save

### Issue: Connection Failed

**Error:** `ConnectionError: Could not connect to Supabase`

**Solution:**
1. Check internet connection
2. Verify URL in config: `https://xxxxx.supabase.co`
3. Verify anon key (not service_role key)
4. Check Supabase project is active

### Issue: Permission Denied

**Error:** `permission denied for table`

**Solution:**
```sql
-- Grant permissions (run in SQL Editor)
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon;
```

---

## Schema Version History

### v2.0.1 (Current)
- ✅ Fixed: Changed `NOW()` to `CURRENT_TIMESTAMP`
- ✅ Fixed: IMMUTABLE function error
- Status: Production ready

### v2.0.0 (Initial)
- ❌ Issue: Used `NOW()` in defaults
- ❌ Issue: Trigger function not IMMUTABLE
- Status: Deprecated

---

## Support

If you still have issues:

1. **Check Supabase Status:** https://status.supabase.com
2. **Review logs:** Supabase Dashboard → Logs
3. **Test connection:** `python scripts/test_supabase.py`
4. **Check documentation:** `docs/SUPABASE_INTEGRATION_GUIDE.md`

---

**Last Updated:** November 2025  
**Schema Version:** 2.0.1  
**Status:** ✅ Fixed and Ready
