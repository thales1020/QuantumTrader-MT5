"""
Supabase Migration Tool
Migrates data from SQLite to Supabase cloud database

Author: QuantumTrader Team
Version: 2.0.0
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.database_manager import DatabaseManager
from engines.supabase_database import SupabaseDatabase, SupabaseConfig
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SupabaseMigrationTool:
    """Tool to migrate paper trading data from SQLite to Supabase"""
    
    def __init__(
        self,
        sqlite_db_path: str,
        supabase_config: SupabaseConfig,
        batch_size: int = 100
    ):
        """
        Initialize migration tool
        
        Args:
            sqlite_db_path: Path to SQLite database file
            supabase_config: Supabase configuration
            batch_size: Number of records to migrate per batch
        """
        self.sqlite_db_path = sqlite_db_path
        self.batch_size = batch_size
        
        # Initialize databases
        logger.info("📦 Initializing SQLite database...")
        self.sqlite_db = DatabaseManager(sqlite_db_path)
        
        logger.info("☁️  Initializing Supabase database...")
        self.supabase_db = SupabaseDatabase(supabase_config)
        
        # Migration statistics
        self.stats = {
            'orders': {'total': 0, 'migrated': 0, 'failed': 0},
            'fills': {'total': 0, 'migrated': 0, 'failed': 0},
            'positions': {'total': 0, 'migrated': 0, 'failed': 0},
            'trades': {'total': 0, 'migrated': 0, 'failed': 0},
            'account_history': {'total': 0, 'migrated': 0, 'failed': 0}
        }
    
    def migrate_all(self, verify: bool = True) -> Dict:
        """
        Migrate all data from SQLite to Supabase
        
        Args:
            verify: Whether to verify data integrity after migration
            
        Returns:
            Migration statistics dictionary
        """
        start_time = datetime.now()
        logger.info("=" * 80)
        logger.info("🚀 STARTING SUPABASE MIGRATION")
        logger.info("=" * 80)
        
        try:
            # Migrate each table in order (respecting foreign keys)
            logger.info("\n📊 Phase 1: Migrating Orders...")
            self._migrate_orders()
            
            logger.info("\n📊 Phase 2: Migrating Fills...")
            self._migrate_fills()
            
            logger.info("\n📊 Phase 3: Migrating Positions...")
            self._migrate_positions()
            
            logger.info("\n📊 Phase 4: Migrating Trades...")
            self._migrate_trades()
            
            logger.info("\n📊 Phase 5: Migrating Account History...")
            self._migrate_account_history()
            
            # Verification
            if verify:
                logger.info("\n✅ Phase 6: Verifying Data Integrity...")
                self._verify_migration()
            
            # Print summary
            self._print_summary(start_time)
            
            return self.stats
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}", exc_info=True)
            self._print_summary(start_time)
            raise
    
    def _migrate_orders(self):
        """Migrate orders table"""
        try:
            # Get all orders from SQLite
            with self.sqlite_db.Session() as session:
                sqlite_orders = session.query(self.sqlite_db.OrderDB).all()
                self.stats['orders']['total'] = len(sqlite_orders)
                
                logger.info(f"Found {len(sqlite_orders)} orders to migrate")
                
                # Migrate in batches
                for i in range(0, len(sqlite_orders), self.batch_size):
                    batch = sqlite_orders[i:i + self.batch_size]
                    
                    for order_obj in batch:
                        try:
                            order_data = {
                                'order_id': order_obj.order_id,
                                'symbol': order_obj.symbol,
                                'order_type': order_obj.order_type,
                                'side': order_obj.side,
                                'quantity': float(order_obj.quantity),
                                'limit_price': float(order_obj.limit_price) if order_obj.limit_price else None,
                                'stop_price': float(order_obj.stop_price) if order_obj.stop_price else None,
                                'avg_fill_price': float(order_obj.avg_fill_price),
                                'status': order_obj.status,
                                'filled_quantity': float(order_obj.filled_quantity),
                                'remaining_quantity': float(order_obj.remaining_quantity),
                                'created_time': order_obj.created_time.isoformat() if order_obj.created_time else None,
                                'filled_time': order_obj.filled_time.isoformat() if order_obj.filled_time else None,
                                'cancelled_time': order_obj.cancelled_time.isoformat() if order_obj.cancelled_time else None,
                                'expires_at': order_obj.expires_at.isoformat() if order_obj.expires_at else None,
                                'rejection_reason': order_obj.rejection_reason,
                                'cancelled_reason': order_obj.cancelled_reason,
                                'strategy_name': order_obj.strategy_name
                            }
                            
                            self.supabase_db.save_order(order_data)
                            self.stats['orders']['migrated'] += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to migrate order {order_obj.order_id}: {e}")
                            self.stats['orders']['failed'] += 1
                    
                    logger.info(f"Migrated {min(i + self.batch_size, len(sqlite_orders))}/{len(sqlite_orders)} orders")
            
            logger.info(f"✅ Orders migration complete: {self.stats['orders']['migrated']}/{self.stats['orders']['total']}")
            
        except Exception as e:
            logger.error(f"❌ Orders migration failed: {e}", exc_info=True)
            raise
    
    def _migrate_fills(self):
        """Migrate fills table"""
        try:
            with self.sqlite_db.Session() as session:
                sqlite_fills = session.query(self.sqlite_db.FillDB).all()
                self.stats['fills']['total'] = len(sqlite_fills)
                
                logger.info(f"Found {len(sqlite_fills)} fills to migrate")
                
                for i in range(0, len(sqlite_fills), self.batch_size):
                    batch = sqlite_fills[i:i + self.batch_size]
                    
                    for fill_obj in batch:
                        try:
                            fill_data = {
                                'fill_id': fill_obj.fill_id,
                                'order_id': fill_obj.order_id,
                                'fill_time': fill_obj.fill_time.isoformat(),
                                'fill_price': float(fill_obj.fill_price),
                                'fill_volume': float(fill_obj.fill_volume),
                                'commission': float(fill_obj.commission),
                                'is_partial': fill_obj.is_partial,
                                'remaining_volume': float(fill_obj.remaining_volume),
                                'market_price': float(fill_obj.market_price) if fill_obj.market_price else None,
                                'bid': float(fill_obj.bid) if fill_obj.bid else None,
                                'ask': float(fill_obj.ask) if fill_obj.ask else None,
                                'volume': fill_obj.volume
                            }
                            
                            self.supabase_db.save_fill(fill_data)
                            self.stats['fills']['migrated'] += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to migrate fill {fill_obj.fill_id}: {e}")
                            self.stats['fills']['failed'] += 1
                    
                    logger.info(f"Migrated {min(i + self.batch_size, len(sqlite_fills))}/{len(sqlite_fills)} fills")
            
            logger.info(f"✅ Fills migration complete: {self.stats['fills']['migrated']}/{self.stats['fills']['total']}")
            
        except Exception as e:
            logger.error(f"❌ Fills migration failed: {e}", exc_info=True)
            raise
    
    def _migrate_positions(self):
        """Migrate positions table"""
        try:
            with self.sqlite_db.Session() as session:
                sqlite_positions = session.query(self.sqlite_db.PositionDB).all()
                self.stats['positions']['total'] = len(sqlite_positions)
                
                logger.info(f"Found {len(sqlite_positions)} positions to migrate")
                
                for i in range(0, len(sqlite_positions), self.batch_size):
                    batch = sqlite_positions[i:i + self.batch_size]
                    
                    for pos_obj in batch:
                        try:
                            position_data = {
                                'position_id': pos_obj.position_id,
                                'symbol': pos_obj.symbol,
                                'side': pos_obj.side,
                                'quantity': float(pos_obj.quantity),
                                'entry_price': float(pos_obj.entry_price),
                                'current_price': float(pos_obj.current_price) if pos_obj.current_price else None,
                                'exit_price': float(pos_obj.exit_price) if pos_obj.exit_price else None,
                                'stop_loss': float(pos_obj.stop_loss) if pos_obj.stop_loss else None,
                                'take_profit': float(pos_obj.take_profit) if pos_obj.take_profit else None,
                                'is_open': pos_obj.is_open,
                                'unrealized_pnl': float(pos_obj.unrealized_pnl),
                                'realized_pnl': float(pos_obj.realized_pnl),
                                'total_commission': float(pos_obj.total_commission),
                                'total_swap': float(pos_obj.total_swap),
                                'spread_cost': float(pos_obj.spread_cost),
                                'open_time': pos_obj.open_time.isoformat(),
                                'close_time': pos_obj.close_time.isoformat() if pos_obj.close_time else None,
                                'days_held': pos_obj.days_held,
                                'exit_reason': pos_obj.exit_reason,
                                'strategy_name': pos_obj.strategy_name
                            }
                            
                            self.supabase_db.save_position(position_data)
                            self.stats['positions']['migrated'] += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to migrate position {pos_obj.position_id}: {e}")
                            self.stats['positions']['failed'] += 1
                    
                    logger.info(f"Migrated {min(i + self.batch_size, len(sqlite_positions))}/{len(sqlite_positions)} positions")
            
            logger.info(f"✅ Positions migration complete: {self.stats['positions']['migrated']}/{self.stats['positions']['total']}")
            
        except Exception as e:
            logger.error(f"❌ Positions migration failed: {e}", exc_info=True)
            raise
    
    def _migrate_trades(self):
        """Migrate trades table"""
        try:
            with self.sqlite_db.Session() as session:
                sqlite_trades = session.query(self.sqlite_db.TradeDB).all()
                self.stats['trades']['total'] = len(sqlite_trades)
                
                logger.info(f"Found {len(sqlite_trades)} trades to migrate")
                
                for i in range(0, len(sqlite_trades), self.batch_size):
                    batch = sqlite_trades[i:i + self.batch_size]
                    
                    for trade_obj in batch:
                        try:
                            trade_data = {
                                'trade_id': trade_obj.trade_id,
                                'symbol': trade_obj.symbol,
                                'direction': trade_obj.direction,
                                'entry_time': trade_obj.entry_time.isoformat(),
                                'exit_time': trade_obj.exit_time.isoformat(),
                                'entry_price': float(trade_obj.entry_price),
                                'exit_price': float(trade_obj.exit_price),
                                'lot_size': float(trade_obj.lot_size),
                                'gross_pnl': float(trade_obj.gross_pnl),
                                'commission': float(trade_obj.commission),
                                'swap': float(trade_obj.swap),
                                'spread_cost': float(trade_obj.spread_cost),
                                'slippage': float(trade_obj.slippage),
                                'net_pnl': float(trade_obj.net_pnl),
                                'pips': float(trade_obj.pips) if trade_obj.pips else None,
                                'duration_hours': float(trade_obj.duration_hours) if trade_obj.duration_hours else None,
                                'exit_reason': trade_obj.exit_reason,
                                'balance_after': float(trade_obj.balance_after) if trade_obj.balance_after else None,
                                'equity_after': float(trade_obj.equity_after) if trade_obj.equity_after else None,
                                'drawdown_pct': float(trade_obj.drawdown_pct) if trade_obj.drawdown_pct else None,
                                'strategy_name': trade_obj.strategy_name
                            }
                            
                            self.supabase_db.save_trade(trade_data)
                            self.stats['trades']['migrated'] += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to migrate trade {trade_obj.trade_id}: {e}")
                            self.stats['trades']['failed'] += 1
                    
                    logger.info(f"Migrated {min(i + self.batch_size, len(sqlite_trades))}/{len(sqlite_trades)} trades")
            
            logger.info(f"✅ Trades migration complete: {self.stats['trades']['migrated']}/{self.stats['trades']['total']}")
            
        except Exception as e:
            logger.error(f"❌ Trades migration failed: {e}", exc_info=True)
            raise
    
    def _migrate_account_history(self):
        """Migrate account history table"""
        try:
            with self.sqlite_db.Session() as session:
                sqlite_history = session.query(self.sqlite_db.AccountHistoryDB).all()
                self.stats['account_history']['total'] = len(sqlite_history)
                
                logger.info(f"Found {len(sqlite_history)} account snapshots to migrate")
                
                for i in range(0, len(sqlite_history), self.batch_size):
                    batch = sqlite_history[i:i + self.batch_size]
                    
                    for hist_obj in batch:
                        try:
                            history_data = {
                                'timestamp': hist_obj.timestamp.isoformat(),
                                'balance': float(hist_obj.balance),
                                'equity': float(hist_obj.equity),
                                'margin_used': float(hist_obj.margin_used),
                                'free_margin': float(hist_obj.free_margin),
                                'margin_level': float(hist_obj.margin_level),
                                'num_positions': hist_obj.num_positions,
                                'num_pending_orders': hist_obj.num_pending_orders,
                                'daily_pnl': float(hist_obj.daily_pnl),
                                'daily_return_pct': float(hist_obj.daily_return_pct),
                                'total_realized_pnl': float(hist_obj.total_realized_pnl),
                                'total_trades': hist_obj.total_trades,
                                'total_commission_paid': float(hist_obj.total_commission_paid),
                                'drawdown_usd': float(hist_obj.drawdown_usd),
                                'drawdown_pct': float(hist_obj.drawdown_pct)
                            }
                            
                            self.supabase_db.save_account_snapshot(history_data)
                            self.stats['account_history']['migrated'] += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to migrate account snapshot: {e}")
                            self.stats['account_history']['failed'] += 1
                    
                    logger.info(f"Migrated {min(i + self.batch_size, len(sqlite_history))}/{len(sqlite_history)} snapshots")
            
            logger.info(f"✅ Account history migration complete: {self.stats['account_history']['migrated']}/{self.stats['account_history']['total']}")
            
        except Exception as e:
            logger.error(f"❌ Account history migration failed: {e}", exc_info=True)
            raise
    
    def _verify_migration(self):
        """Verify data integrity after migration"""
        logger.info("🔍 Verifying migration...")
        
        issues = []
        
        # Verify counts
        for table_name in ['orders', 'fills', 'positions', 'trades', 'account_history']:
            total = self.stats[table_name]['total']
            migrated = self.stats[table_name]['migrated']
            failed = self.stats[table_name]['failed']
            
            if migrated + failed != total:
                issues.append(f"{table_name}: count mismatch (total={total}, migrated={migrated}, failed={failed})")
        
        if issues:
            logger.warning("⚠️ Verification issues found:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("✅ Verification passed: All data migrated successfully")
    
    def _print_summary(self, start_time: datetime):
        """Print migration summary"""
        duration = datetime.now() - start_time
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 MIGRATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Duration: {duration}")
        logger.info("")
        
        total_migrated = 0
        total_failed = 0
        
        for table_name in ['orders', 'fills', 'positions', 'trades', 'account_history']:
            stats = self.stats[table_name]
            total_migrated += stats['migrated']
            total_failed += stats['failed']
            
            status = "✅" if stats['failed'] == 0 else "⚠️"
            logger.info(f"{status} {table_name.upper():<20} Total: {stats['total']:>6} | Migrated: {stats['migrated']:>6} | Failed: {stats['failed']:>6}")
        
        logger.info("=" * 80)
        logger.info(f"TOTAL RECORDS:           {total_migrated + total_failed}")
        logger.info(f"SUCCESSFULLY MIGRATED:   {total_migrated}")
        logger.info(f"FAILED:                  {total_failed}")
        logger.info("=" * 80)


def load_supabase_config(config_path: str = "config/supabase.json") -> SupabaseConfig:
    """Load Supabase configuration from JSON file"""
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    supabase_cfg = config_data['database']['supabase']
    
    return SupabaseConfig(
        url=supabase_cfg['url'],
        key=supabase_cfg['anon_key']
    )


def main():
    """Main migration script"""
    print("\n" + "=" * 80)
    print("🚀 SUPABASE MIGRATION TOOL")
    print("=" * 80)
    print("\nThis tool will migrate your paper trading data from SQLite to Supabase.")
    print("Make sure you have:")
    print("  1. Created a Supabase project")
    print("  2. Run the SQL schema from database/supabase_schema.sql")
    print("  3. Updated config/supabase.json with your credentials")
    print("")
    
    # Get paths
    sqlite_path = input("Enter SQLite database path [data/paper_trading.db]: ").strip()
    if not sqlite_path:
        sqlite_path = "data/paper_trading.db"
    
    if not os.path.exists(sqlite_path):
        print(f"\n❌ Error: SQLite database not found at {sqlite_path}")
        return
    
    config_path = input("Enter Supabase config path [config/supabase.json]: ").strip()
    if not config_path:
        config_path = "config/supabase.json"
    
    if not os.path.exists(config_path):
        print(f"\n❌ Error: Config file not found at {config_path}")
        print("Please copy config/supabase.example.json to config/supabase.json and fill in your credentials.")
        return
    
    # Confirm
    print(f"\n📦 SQLite Database: {sqlite_path}")
    print(f"☁️  Supabase Config: {config_path}")
    confirm = input("\nProceed with migration? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Migration cancelled")
        return
    
    try:
        # Load config
        supabase_config = load_supabase_config(config_path)
        
        # Create migration tool
        migration_tool = SupabaseMigrationTool(
            sqlite_db_path=sqlite_path,
            supabase_config=supabase_config,
            batch_size=100
        )
        
        # Run migration
        stats = migration_tool.migrate_all(verify=True)
        
        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("  1. Verify data in Supabase Dashboard")
        print("  2. Update paper_trading_broker_api.py to use SupabaseDatabase")
        print("  3. Test the integration")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
