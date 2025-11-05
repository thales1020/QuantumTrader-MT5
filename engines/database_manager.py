"""
Database Manager - Lưu trữ và quản lý dữ liệu trading
======================================================

Lưu trữ:
- Orders: Tất cả lệnh đã đặt
- Fills: Lịch sử khớp lệnh
- Positions: Vị thế hiện tại và đã đóng
- Account History: Biến động tài khoản

Sử dụng SQLite + SQLAlchemy ORM

Author: QuantumTrader Team
Version: 2.0.0  
Date: November 2025
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime
from typing import List, Dict, Optional
import logging
import enum


Base = declarative_base()


# Enums for database
class OrderTypeDB(enum.Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderSideDB(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatusDB(enum.Enum):
    PENDING = "PENDING"
    PARTIAL_FILLED = "PARTIAL_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


# Database Models
class OrderDB(Base):
    """Bảng lưu trữ orders"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Order details
    symbol = Column(String(20), nullable=False, index=True)
    order_type = Column(SQLEnum(OrderTypeDB), nullable=False)
    side = Column(SQLEnum(OrderSideDB), nullable=False)
    quantity = Column(Float, nullable=False)
    
    # Prices
    limit_price = Column(Float, nullable=True)
    stop_price = Column(Float, nullable=True)
    avg_fill_price = Column(Float, default=0.0)
    
    # Status
    status = Column(SQLEnum(OrderStatusDB), nullable=False, index=True)
    filled_quantity = Column(Float, default=0.0)
    remaining_quantity = Column(Float)
    
    # Time tracking
    created_time = Column(DateTime, nullable=False, index=True)
    filled_time = Column(DateTime, nullable=True)
    cancelled_time = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    rejection_reason = Column(Text, nullable=True)
    cancelled_reason = Column(Text, nullable=True)
    strategy_name = Column(String(100), nullable=True, index=True)
    
    # Relationships
    fills = relationship("FillDB", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order {self.order_id}: {self.side.value} {self.quantity} {self.symbol} @ {self.status.value}>"


class FillDB(Base):
    """Bảng lưu trữ fills (khớp lệnh)"""
    __tablename__ = 'fills'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fill_id = Column(String(50), unique=True, nullable=False, index=True)
    order_id = Column(String(50), ForeignKey('orders.order_id'), nullable=False, index=True)
    
    # Fill details
    fill_time = Column(DateTime, nullable=False, index=True)
    fill_price = Column(Float, nullable=False)
    fill_volume = Column(Float, nullable=False)
    commission = Column(Float, default=0.0)
    
    # Fill type
    is_partial = Column(Boolean, default=False)
    remaining_volume = Column(Float)
    
    # Market data at fill
    market_price = Column(Float)
    bid = Column(Float)
    ask = Column(Float)
    volume = Column(Integer)
    
    # Relationship
    order = relationship("OrderDB", back_populates="fills")
    
    def __repr__(self):
        return f"<Fill {self.fill_id}: {self.fill_volume} @ {self.fill_price:.5f}>"


class PositionDB(Base):
    """Bảng lưu trữ positions"""
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    position_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Position details
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(SQLEnum(OrderSideDB), nullable=False)
    quantity = Column(Float, nullable=False)
    
    # Prices
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    
    # SL/TP
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    
    # Status
    is_open = Column(Boolean, default=True, index=True)
    
    # P&L
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    
    # Costs
    total_commission = Column(Float, default=0.0)
    total_swap = Column(Float, default=0.0)
    spread_cost = Column(Float, default=0.0)
    
    # Time tracking
    open_time = Column(DateTime, nullable=False, index=True)
    close_time = Column(DateTime, nullable=True)
    days_held = Column(Integer, default=0)
    
    # Metadata
    exit_reason = Column(String(100), nullable=True)
    strategy_name = Column(String(100), nullable=True, index=True)
    
    def __repr__(self):
        status = "OPEN" if self.is_open else "CLOSED"
        return f"<Position {self.position_id}: {self.side.value} {self.quantity} {self.symbol} [{status}]>"


class AccountHistoryDB(Base):
    """Bảng lưu trữ lịch sử tài khoản"""
    __tablename__ = 'account_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Snapshot time
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Account metrics
    balance = Column(Float, nullable=False)
    equity = Column(Float, nullable=False)
    margin_used = Column(Float, default=0.0)
    free_margin = Column(Float)
    margin_level = Column(Float, default=0.0)
    
    # Position counts
    num_positions = Column(Integer, default=0)
    num_pending_orders = Column(Integer, default=0)
    
    # Daily P&L
    daily_pnl = Column(Float, default=0.0)
    daily_return_pct = Column(Float, default=0.0)
    
    # Cumulative
    total_realized_pnl = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    total_commission_paid = Column(Float, default=0.0)
    
    # Drawdown
    drawdown_usd = Column(Float, default=0.0)
    drawdown_pct = Column(Float, default=0.0)
    
    def __repr__(self):
        return f"<AccountSnapshot {self.timestamp}: Balance=${self.balance:.2f}, Equity=${self.equity:.2f}>"


class TradeDB(Base):
    """Bảng lưu trữ trades (completed roundtrips)"""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_id = Column(Integer, nullable=False, index=True)
    
    # Trade details
    symbol = Column(String(20), nullable=False, index=True)
    direction = Column(String(10), nullable=False)  # LONG/SHORT
    
    # Entry/Exit
    entry_time = Column(DateTime, nullable=False, index=True)
    exit_time = Column(DateTime, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=False)
    lot_size = Column(Float, nullable=False)
    
    # P&L breakdown
    gross_pnl = Column(Float, nullable=False)
    commission = Column(Float, default=0.0)
    swap = Column(Float, default=0.0)
    spread_cost = Column(Float, default=0.0)
    slippage = Column(Float, default=0.0)
    net_pnl = Column(Float, nullable=False, index=True)
    
    # Metrics
    pips = Column(Float)
    duration_hours = Column(Float)
    exit_reason = Column(String(100))
    
    # Running totals
    balance_after = Column(Float)
    equity_after = Column(Float)
    drawdown_pct = Column(Float, default=0.0)
    
    # Metadata
    strategy_name = Column(String(100), nullable=True, index=True)
    
    def __repr__(self):
        return f"<Trade #{self.trade_id}: {self.direction} {self.symbol} P&L=${self.net_pnl:.2f}>"


class DatabaseManager:
    """
    Quản lý database cho paper trading và backtesting
    
    Chức năng:
    1. Lưu orders và fills
    2. Track positions
    3. Log account history
    4. Query và analysis
    """
    
    def __init__(self, db_path: str = "data/trading.db"):
        """
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.logger = logging.getLogger('DatabaseManager')
        
        # Create tables
        Base.metadata.create_all(self.engine)
        self.logger.info(f"✅ Database initialized: {db_path}")
    
    def save_order(self, order) -> int:
        """
        Lưu order vào database
        
        Args:
            order: Order object from order_matching_engine
        
        Returns:
            order.id (database ID)
        """
        session = self.Session()
        
        try:
            # Convert to DB model
            order_db = OrderDB(
                order_id=order.order_id,
                symbol=order.symbol,
                order_type=OrderTypeDB[order.order_type.name],
                side=OrderSideDB[order.side.name],
                quantity=order.quantity,
                limit_price=order.limit_price,
                stop_price=order.stop_price,
                avg_fill_price=order.avg_fill_price,
                status=OrderStatusDB[order.status.name],
                filled_quantity=order.filled_quantity,
                remaining_quantity=order.remaining_quantity,
                created_time=order.created_time,
                expires_at=order.expires_at,
                rejection_reason=order.rejection_reason,
                cancelled_reason=order.cancelled_reason
            )
            
            session.add(order_db)
            session.commit()
            
            order_id = order_db.id
            self.logger.debug(f"💾 Saved order: {order.order_id}")
            
            return order_id
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to save order: {e}")
            raise
        finally:
            session.close()
    
    def update_order(self, order) -> bool:
        """Update existing order"""
        session = self.Session()
        
        try:
            order_db = session.query(OrderDB).filter_by(order_id=order.order_id).first()
            
            if not order_db:
                self.logger.warning(f"Order {order.order_id} not found for update")
                return False
            
            # Update fields
            order_db.status = OrderStatusDB[order.status.name]
            order_db.filled_quantity = order.filled_quantity
            order_db.remaining_quantity = order.remaining_quantity
            order_db.avg_fill_price = order.avg_fill_price
            
            if order.status == OrderStatusDB.FILLED:
                order_db.filled_time = datetime.now()
            elif order.status == OrderStatusDB.CANCELLED:
                order_db.cancelled_time = datetime.now()
                order_db.cancelled_reason = order.cancelled_reason
            
            session.commit()
            self.logger.debug(f"📝 Updated order: {order.order_id}")
            
            return True
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to update order: {e}")
            return False
        finally:
            session.close()
    
    def save_fill(self, fill, strategy_name: str = None) -> int:
        """Lưu fill vào database"""
        session = self.Session()
        
        try:
            fill_db = FillDB(
                fill_id=fill.fill_id,
                order_id=fill.order_id,
                fill_time=fill.fill_time,
                fill_price=fill.fill_price,
                fill_volume=fill.fill_volume,
                commission=fill.commission,
                is_partial=fill.is_partial,
                remaining_volume=fill.remaining_volume,
                market_price=fill.market_price,
                bid=fill.bid,
                ask=fill.ask,
                volume=fill.volume
            )
            
            session.add(fill_db)
            session.commit()
            
            fill_id = fill_db.id
            self.logger.debug(f"💾 Saved fill: {fill.fill_id}")
            
            return fill_id
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to save fill: {e}")
            raise
        finally:
            session.close()
    
    def save_position(self, position, strategy_name: str = None) -> int:
        """Lưu position vào database"""
        session = self.Session()
        
        try:
            pos_db = PositionDB(
                position_id=position.position_id,
                symbol=position.symbol,
                side=OrderSideDB.BUY if position.direction == 1 else OrderSideDB.SELL,
                quantity=position.lot_size,
                entry_price=position.entry_price,
                current_price=position.current_price,
                stop_loss=position.stop_loss,
                take_profit=position.take_profit,
                is_open=True,
                unrealized_pnl=position.unrealized_pnl,
                total_commission=position.total_commission,
                total_swap=position.total_swap,
                spread_cost=position.spread_cost,
                open_time=position.open_time,
                days_held=position.days_held,
                strategy_name=strategy_name
            )
            
            session.add(pos_db)
            session.commit()
            
            pos_id = pos_db.id
            self.logger.debug(f"💾 Saved position: {position.position_id}")
            
            return pos_id
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to save position: {e}")
            raise
        finally:
            session.close()
    
    def close_position(self, position_id: str, exit_price: float, exit_reason: str):
        """Update position as closed"""
        session = self.Session()
        
        try:
            pos = session.query(PositionDB).filter_by(position_id=position_id).first()
            
            if not pos:
                self.logger.warning(f"Position {position_id} not found")
                return False
            
            pos.is_open = False
            pos.exit_price = exit_price
            pos.close_time = datetime.now()
            pos.exit_reason = exit_reason
            
            session.commit()
            self.logger.debug(f"🔒 Closed position: {position_id}")
            
            return True
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to close position: {e}")
            return False
        finally:
            session.close()
    
    def save_account_snapshot(self, account_info: Dict) -> int:
        """Lưu account snapshot"""
        session = self.Session()
        
        try:
            snapshot = AccountHistoryDB(
                timestamp=datetime.now(),
                balance=account_info.get('balance', 0),
                equity=account_info.get('equity', 0),
                margin_used=account_info.get('margin_used', 0),
                free_margin=account_info.get('free_margin', 0),
                margin_level=account_info.get('margin_level', 0),
                num_positions=account_info.get('num_positions', 0),
                num_pending_orders=account_info.get('num_pending_orders', 0),
                total_realized_pnl=account_info.get('total_realized_pnl', 0)
            )
            
            session.add(snapshot)
            session.commit()
            
            return snapshot.id
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to save account snapshot: {e}")
            raise
        finally:
            session.close()
    
    def save_trade(self, trade_record) -> int:
        """Lưu completed trade"""
        session = self.Session()
        
        try:
            trade = TradeDB(
                trade_id=trade_record.trade_id,
                symbol=trade_record.symbol,
                direction=trade_record.direction,
                entry_time=trade_record.entry_time,
                exit_time=trade_record.exit_time,
                entry_price=trade_record.entry_price,
                exit_price=trade_record.exit_price,
                lot_size=trade_record.lot_size,
                gross_pnl=trade_record.gross_pnl,
                commission=trade_record.commission,
                swap=trade_record.swap,
                spread_cost=trade_record.spread_cost,
                slippage=trade_record.slippage,
                net_pnl=trade_record.net_pnl,
                pips=trade_record.pips,
                duration_hours=trade_record.duration_hours,
                exit_reason=trade_record.exit_reason,
                balance_after=trade_record.balance_after,
                equity_after=trade_record.equity_after,
                drawdown_pct=trade_record.drawdown_pct
            )
            
            session.add(trade)
            session.commit()
            
            return trade.id
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to save trade: {e}")
            raise
        finally:
            session.close()
    
    # Query methods
    def get_all_orders(self, status: Optional[str] = None) -> List[OrderDB]:
        """Get all orders, optionally filtered by status"""
        session = self.Session()
        
        try:
            query = session.query(OrderDB)
            
            if status:
                query = query.filter_by(status=OrderStatusDB[status])
            
            orders = query.order_by(OrderDB.created_time.desc()).all()
            return orders
            
        finally:
            session.close()
    
    def get_order_by_id(self, order_id: str) -> Optional[OrderDB]:
        """Get order by order_id"""
        session = self.Session()
        
        try:
            return session.query(OrderDB).filter_by(order_id=order_id).first()
        finally:
            session.close()
    
    def get_open_positions(self) -> List[PositionDB]:
        """Get all open positions"""
        session = self.Session()
        
        try:
            return session.query(PositionDB).filter_by(is_open=True).all()
        finally:
            session.close()
    
    def get_all_trades(self) -> List[TradeDB]:
        """Get all completed trades"""
        session = self.Session()
        
        try:
            return session.query(TradeDB).order_by(TradeDB.exit_time.desc()).all()
        finally:
            session.close()
    
    def get_account_history(self, start_date: Optional[datetime] = None) -> List[AccountHistoryDB]:
        """Get account history"""
        session = self.Session()
        
        try:
            query = session.query(AccountHistoryDB)
            
            if start_date:
                query = query.filter(AccountHistoryDB.timestamp >= start_date)
            
            return query.order_by(AccountHistoryDB.timestamp).all()
            
        finally:
            session.close()
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        session = self.Session()
        
        try:
            total_orders = session.query(OrderDB).count()
            filled_orders = session.query(OrderDB).filter_by(status=OrderStatusDB.FILLED).count()
            total_trades = session.query(TradeDB).count()
            open_positions = session.query(PositionDB).filter_by(is_open=True).count()
            
            return {
                'total_orders': total_orders,
                'filled_orders': filled_orders,
                'total_trades': total_trades,
                'open_positions': open_positions
            }
            
        finally:
            session.close()


# Example usage
if __name__ == "__main__":
    """
    Test Database Manager
    """
    logging.basicConfig(level=logging.INFO)
    
    # Initialize database
    db = DatabaseManager("data/test_trading.db")
    
    # Get statistics
    stats = db.get_statistics()
    print(f"Database stats: {stats}")
    
    # Query orders
    orders = db.get_all_orders()
    print(f"Total orders in DB: {len(orders)}")
