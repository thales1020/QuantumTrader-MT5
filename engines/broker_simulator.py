"""
Broker Simulator - Giả lập công ty chứng khoán
==============================================

Module này giả lập hoàn toàn chức năng của một broker thực:
- Nhận lệnh từ thuật toán
- Kiểm tra tính hợp lệ (margin, limits)
- Khớp lệnh dựa trên diễn biến thị trường
- Tính toán chi phí giao dịch thực tế
- Từ chối lệnh trong các trường hợp đặc biệt

Author: QuantumTrader Team
Version: 1.0.0
Date: November 2025
"""

import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from enum import Enum
import logging


class OrderType(Enum):
    """Loại lệnh"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderStatus(Enum):
    """Trạng thái lệnh"""
    PENDING = "PENDING"           # Đang chờ
    FILLED = "FILLED"             # Đã khớp
    PARTIAL_FILLED = "PARTIAL"    # Khớp một phần
    REJECTED = "REJECTED"         # Bị từ chối
    CANCELLED = "CANCELLED"       # Đã hủy
    

class RejectionReason(Enum):
    """Lý do từ chối lệnh"""
    INSUFFICIENT_MARGIN = "Insufficient margin"
    MAX_POSITIONS_REACHED = "Maximum positions reached"
    MARKET_CLOSED = "Market is closed"
    INVALID_VOLUME = "Invalid lot size"
    PRICE_TOO_FAR = "Price too far from market"
    LOW_LIQUIDITY = "Insufficient liquidity"
    SPREAD_TOO_WIDE = "Spread too wide"
    BROKER_ERROR = "Broker internal error"
    MAX_SLIPPAGE_EXCEEDED = "Max slippage exceeded"


@dataclass
class BrokerConfig:
    """Cấu hình broker - mô phỏng điều kiện thực tế"""
    
    # === CHI PHÍ GIAO DỊCH ===
    spread_pips: float = 1.5              # Spread trung bình (pips)
    spread_min: float = 0.5               # Spread tối thiểu
    spread_max: float = 5.0               # Spread tối đa (khi thanh khoản thấp)
    commission_per_lot: float = 7.0       # Commission mỗi lot (USD)
    swap_long: float = -5.0               # Swap phí long mỗi ngày (USD/lot)
    swap_short: float = 2.0               # Swap phí short mỗi ngày (USD/lot)
    
    # === XÁC SUẤT THỰC THI ===
    fill_probability: float = 0.95        # Xác suất lệnh được khớp
    rejection_probability: float = 0.05   # Xác suất bị từ chối
    partial_fill_probability: float = 0.1 # Xác suất khớp một phần
    
    # === SLIPPAGE ===
    slippage_pips_min: float = 0.0        # Slippage tối thiểu
    slippage_pips_max: float = 2.0        # Slippage tối đa (market order)
    slippage_pips_avg: float = 0.5        # Slippage trung bình
    sl_slippage_multiplier: float = 2.0   # SL thường slippage nhiều hơn
    tp_slippage_multiplier: float = 0.5   # TP thường slippage ít hơn
    
    # === GIỚI HẠN BROKER ===
    max_positions: int = 200              # Số vị thế tối đa
    max_lot_size: float = 100.0           # Lot size tối đa mỗi lệnh
    min_lot_size: float = 0.01            # Lot size tối thiểu
    max_total_exposure: float = 1000000   # Tổng exposure tối đa (USD)
    margin_call_level: float = 0.5        # Margin call ở 50%
    stop_out_level: float = 0.2           # Stop out ở 20%
    
    # === THANH KHOẢN ===
    min_volume: int = 100                 # Volume tối thiểu để giao dịch
    spread_volume_threshold: int = 500    # Volume < threshold → spread tăng
    
    # === GIỜ GIAO DỊCH ===
    market_open_hour: int = 0             # Thị trường mở 24/7 (forex/crypto)
    market_close_hour: int = 24
    weekend_trading: bool = True          # Crypto: True, Forex: False
    
    # === XÁC SUẤT THEO ĐIỀU KIỆN THỊ TRƯỜNG ===
    high_volatility_reject_prob: float = 0.15  # Reject nhiều hơn khi volatility cao
    low_liquidity_reject_prob: float = 0.20    # Reject nhiều hơn khi thanh khoản thấp


@dataclass
class Order:
    """Lệnh giao dịch"""
    order_id: str
    symbol: str
    order_type: OrderType
    direction: int                  # 1: BUY, -1: SELL
    lot_size: float
    requested_price: float          # Giá yêu cầu
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # Thông tin thực thi
    status: OrderStatus = OrderStatus.PENDING
    filled_price: Optional[float] = None
    filled_volume: float = 0.0
    commission: float = 0.0
    spread_cost: float = 0.0
    slippage: float = 0.0
    
    # Metadata
    created_time: Optional[datetime] = None
    filled_time: Optional[datetime] = None
    rejection_reason: Optional[RejectionReason] = None


@dataclass
class Position:
    """Vị thế đang mở"""
    position_id: str
    symbol: str
    direction: int                  # 1: LONG, -1: SHORT
    lot_size: float
    entry_price: float
    current_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # Chi phí đã trả
    total_commission: float = 0.0
    total_swap: float = 0.0
    spread_cost: float = 0.0
    
    # Thời gian
    open_time: Optional[datetime] = None
    days_held: int = 0
    
    # P&L
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0


class BrokerSimulator:
    """
    Giả lập công ty chứng khoán
    
    Chức năng:
    1. Nhận lệnh từ thuật toán
    2. Kiểm tra tính hợp lệ (margin, limits)
    3. Khớp lệnh theo diễn biến thị trường
    4. Tính toán chi phí thực tế
    5. Quản lý positions và margin
    6. Từ chối lệnh khi cần thiết
    """
    
    def __init__(self, config: BrokerConfig, initial_balance: float = 10000):
        self.config = config
        self.balance = initial_balance
        self.equity = initial_balance
        self.margin_used = 0.0
        self.free_margin = initial_balance
        
        self.positions: Dict[str, Position] = {}
        self.pending_orders: Dict[str, Order] = {}
        self.order_history: List[Order] = []
        self.closed_positions: List[Position] = []
        
        self.logger = logging.getLogger('BrokerSimulator')
        self.order_counter = 0
        
    def submit_order(self, symbol: str, order_type: OrderType, direction: int,
                    lot_size: float, price: float, sl: Optional[float] = None,
                    tp: Optional[float] = None, current_bar: Dict = None) -> Tuple[bool, Optional[Order], Optional[str]]:
        """
        Nhận lệnh từ thuật toán
        
        Returns:
            (success, order, error_message)
        """
        self.order_counter += 1
        order_id = f"ORD_{self.order_counter:06d}"
        
        order = Order(
            order_id=order_id,
            symbol=symbol,
            order_type=order_type,
            direction=direction,
            lot_size=lot_size,
            requested_price=price,
            stop_loss=sl,
            take_profit=tp,
            created_time=datetime.now()
        )
        
        # Bước 1: Kiểm tra tính hợp lệ
        is_valid, rejection_reason = self._validate_order(order, current_bar)
        
        if not is_valid:
            order.status = OrderStatus.REJECTED
            order.rejection_reason = rejection_reason
            self.order_history.append(order)
            self.logger.warning(f"Order {order_id} REJECTED: {rejection_reason.value}")
            return False, order, rejection_reason.value
        
        # Bước 2: Thử khớp lệnh (nếu là market order)
        if order_type == OrderType.MARKET:
            success = self._execute_market_order(order, current_bar)
            if success:
                self.logger.info(f"Order {order_id} FILLED at {order.filled_price:.5f}")
                return True, order, None
            else:
                self.logger.warning(f"Order {order_id} REJECTED: Execution failed")
                return False, order, "Execution failed"
        
        # Bước 3: Lệnh pending (limit, stop)
        self.pending_orders[order_id] = order
        self.logger.info(f"Order {order_id} PENDING")
        return True, order, None
    
    def _validate_order(self, order: Order, current_bar: Dict) -> Tuple[bool, Optional[RejectionReason]]:
        """
        Kiểm tra tính hợp lệ của lệnh - giống broker thật
        """
        # 1. Kiểm tra lot size
        if order.lot_size < self.config.min_lot_size:
            return False, RejectionReason.INVALID_VOLUME
        if order.lot_size > self.config.max_lot_size:
            return False, RejectionReason.INVALID_VOLUME
        
        # 2. Kiểm tra số lượng positions
        if len(self.positions) >= self.config.max_positions:
            return False, RejectionReason.MAX_POSITIONS_REACHED
        
        # 3. Kiểm tra margin
        required_margin = self._calculate_required_margin(order)
        if required_margin > self.free_margin:
            return False, RejectionReason.INSUFFICIENT_MARGIN
        
        # 4. Kiểm tra total exposure
        total_exposure = self._calculate_total_exposure() + (order.lot_size * 100000)
        if total_exposure > self.config.max_total_exposure:
            return False, RejectionReason.MAX_POSITIONS_REACHED
        
        # 5. Kiểm tra giờ giao dịch (nếu cần)
        if current_bar and not self._is_market_open(current_bar['time']):
            return False, RejectionReason.MARKET_CLOSED
        
        # 6. Kiểm tra thanh khoản
        if current_bar and current_bar.get('tick_volume', 1000) < self.config.min_volume:
            return False, RejectionReason.LOW_LIQUIDITY
        
        # 7. Giả lập xác suất từ chối ngẫu nhiên (broker error, network issue, etc)
        rejection_prob = self.config.rejection_probability
        
        # Tăng xác suất từ chối nếu thanh khoản thấp
        if current_bar and current_bar.get('tick_volume', 1000) < self.config.spread_volume_threshold:
            rejection_prob = self.config.low_liquidity_reject_prob
        
        if random.random() < rejection_prob:
            return False, RejectionReason.BROKER_ERROR
        
        return True, None
    
    def _execute_market_order(self, order: Order, current_bar: Dict) -> bool:
        """
        Khớp lệnh market - giả lập thực tế
        """
        # 1. Tính spread hiện tại
        current_spread = self._calculate_current_spread(current_bar)
        
        # 2. Tính slippage
        slippage = self._calculate_slippage(order, current_bar)
        
        # 3. Tính giá thực thi
        base_price = order.requested_price
        
        if order.direction == 1:  # BUY
            # Mua: phải trả ask price = bid + spread
            execution_price = base_price + current_spread + slippage
        else:  # SELL
            # Bán: nhận bid price
            execution_price = base_price - slippage
        
        # 4. Kiểm tra slippage có quá lớn không
        max_slippage = self.config.slippage_pips_max * self._get_point_value(order.symbol)
        if abs(execution_price - base_price) > max_slippage:
            order.status = OrderStatus.REJECTED
            order.rejection_reason = RejectionReason.MAX_SLIPPAGE_EXCEEDED
            return False
        
        # 5. Tính commission
        commission = order.lot_size * self.config.commission_per_lot
        
        # 6. Deduct commission ngay
        self.balance -= commission
        
        # 7. Tạo position
        position_id = f"POS_{order.order_id}"
        position = Position(
            position_id=position_id,
            symbol=order.symbol,
            direction=order.direction,
            lot_size=order.lot_size,
            entry_price=execution_price,
            current_price=execution_price,
            stop_loss=order.stop_loss,
            take_profit=order.take_profit,
            total_commission=commission,
            spread_cost=current_spread * order.lot_size * 100000,  # Contract size
            open_time=datetime.now()
        )
        
        self.positions[position_id] = position
        
        # 8. Update order status
        order.status = OrderStatus.FILLED
        order.filled_price = execution_price
        order.filled_volume = order.lot_size
        order.commission = commission
        order.spread_cost = current_spread * self._get_point_value(order.symbol) * 10
        order.slippage = slippage
        order.filled_time = datetime.now()
        
        self.order_history.append(order)
        
        # 9. Update margin
        self._update_margin()
        
        self.logger.info(f"  Entry: {execution_price:.5f}")
        self.logger.info(f"  Spread: {current_spread:.5f}")
        self.logger.info(f"  Slippage: {slippage:.5f}")
        self.logger.info(f"  Commission: ${commission:.2f}")
        
        return True
    
    def update_positions(self, current_bar: Dict):
        """
        Cập nhật positions theo bar hiện tại
        - Kiểm tra SL/TP
        - Tính swap nếu qua đêm
        - Update unrealized P&L
        """
        if not self.positions:
            return
        
        current_price = current_bar['close']
        current_time = current_bar.get('time', datetime.now())
        
        positions_to_close = []
        
        for pos_id, pos in self.positions.items():
            # Update current price
            pos.current_price = current_price
            
            # Kiểm tra SL/TP hit
            if pos.direction == 1:  # LONG
                # Check SL
                if pos.stop_loss and current_bar['low'] <= pos.stop_loss:
                    # SL hit - có slippage
                    slippage = random.uniform(0, self.config.slippage_pips_max * self.config.sl_slippage_multiplier)
                    exit_price = pos.stop_loss - slippage * self._get_point_value(pos.symbol)
                    positions_to_close.append((pos_id, exit_price, "Stop Loss"))
                    continue
                
                # Check TP
                if pos.take_profit and current_bar['high'] >= pos.take_profit:
                    # TP hit - slippage nhỏ hơn
                    slippage = random.uniform(0, self.config.slippage_pips_max * self.config.tp_slippage_multiplier)
                    exit_price = pos.take_profit - slippage * self._get_point_value(pos.symbol)
                    positions_to_close.append((pos_id, exit_price, "Take Profit"))
                    continue
            
            else:  # SHORT
                # Check SL
                if pos.stop_loss and current_bar['high'] >= pos.stop_loss:
                    slippage = random.uniform(0, self.config.slippage_pips_max * self.config.sl_slippage_multiplier)
                    exit_price = pos.stop_loss + slippage * self._get_point_value(pos.symbol)
                    positions_to_close.append((pos_id, exit_price, "Stop Loss"))
                    continue
                
                # Check TP
                if pos.take_profit and current_bar['low'] <= pos.take_profit:
                    slippage = random.uniform(0, self.config.slippage_pips_max * self.config.tp_slippage_multiplier)
                    exit_price = pos.take_profit + slippage * self._get_point_value(pos.symbol)
                    positions_to_close.append((pos_id, exit_price, "Take Profit"))
                    continue
            
            # Tính swap nếu qua ngày mới
            self._apply_swap(pos, current_time)
            
            # Update unrealized P&L
            pos.unrealized_pnl = self._calculate_position_pnl(pos)
        
        # Close positions that hit SL/TP
        for pos_id, exit_price, reason in positions_to_close:
            self.close_position(pos_id, exit_price, reason)
        
        # Update equity
        self._update_equity()
    
    def close_position(self, position_id: str, exit_price: float, reason: str = "Manual"):
        """
        Đóng position
        """
        if position_id not in self.positions:
            self.logger.warning(f"Position {position_id} not found")
            return
        
        pos = self.positions[position_id]
        
        # 1. Tính commission khi đóng
        exit_commission = pos.lot_size * self.config.commission_per_lot
        self.balance -= exit_commission
        pos.total_commission += exit_commission
        
        # 2. Tính P&L
        price_diff = (exit_price - pos.entry_price) * pos.direction
        
        # Crypto vs Forex
        if 'BTC' in pos.symbol or 'ETH' in pos.symbol:
            # Crypto: direct price difference
            pnl = price_diff * pos.lot_size
        else:
            # Forex: pips to USD
            point = self._get_point_value(pos.symbol)
            pips = price_diff / point
            pip_value = 10.0  # Standard lot pip value
            pnl = pips * pip_value * pos.lot_size
        
        # 3. Trừ tất cả chi phí
        total_costs = pos.total_commission + pos.total_swap
        net_pnl = pnl - total_costs
        
        pos.realized_pnl = net_pnl
        
        # 4. Update balance
        self.balance += pnl  # Gross profit
        
        # 5. Move to closed positions
        self.closed_positions.append(pos)
        del self.positions[position_id]
        
        self.logger.info(f"Position {position_id} CLOSED: {reason}")
        self.logger.info(f"  Exit: {exit_price:.5f}")
        self.logger.info(f"  Gross P&L: ${pnl:.2f}")
        self.logger.info(f"  Costs: ${total_costs:.2f}")
        self.logger.info(f"  Net P&L: ${net_pnl:.2f}")
        
        # 6. Update margin
        self._update_margin()
    
    def _calculate_current_spread(self, current_bar: Dict) -> float:
        """Tính spread hiện tại dựa trên thanh khoản"""
        base_spread = self.config.spread_pips * self._get_point_value("EURUSD")
        
        # Spread tăng khi volume thấp
        volume = current_bar.get('tick_volume', 1000)
        if volume < self.config.spread_volume_threshold:
            spread_multiplier = 1.5 + (self.config.spread_volume_threshold - volume) / 500
            spread_multiplier = min(spread_multiplier, self.config.spread_max / self.config.spread_pips)
            return base_spread * spread_multiplier
        
        return base_spread
    
    def _calculate_slippage(self, order: Order, current_bar: Dict) -> float:
        """Tính slippage dựa trên điều kiện thị trường"""
        point = self._get_point_value(order.symbol)
        
        # Slippage ngẫu nhiên
        avg_slippage = self.config.slippage_pips_avg
        max_slippage = self.config.slippage_pips_max
        
        # Tăng slippage nếu volume thấp
        volume = current_bar.get('tick_volume', 1000)
        if volume < self.config.spread_volume_threshold:
            max_slippage *= 2
        
        slippage_pips = random.uniform(self.config.slippage_pips_min, max_slippage)
        return slippage_pips * point
    
    def _apply_swap(self, position: Position, current_time: datetime):
        """Tính và áp dụng swap phí qua đêm"""
        if not position.open_time:
            return
        
        days_held = (current_time - position.open_time).days
        
        if days_held > position.days_held:
            # Qua ngày mới
            new_days = days_held - position.days_held
            swap_rate = self.config.swap_long if position.direction == 1 else self.config.swap_short
            swap_cost = swap_rate * position.lot_size * new_days
            
            position.total_swap += abs(swap_cost)
            self.balance -= abs(swap_cost)
            position.days_held = days_held
            
            self.logger.info(f"  Swap applied: ${swap_cost:.2f} ({new_days} days)")
    
    def _calculate_position_pnl(self, position: Position) -> float:
        """Tính unrealized P&L"""
        price_diff = (position.current_price - position.entry_price) * position.direction
        
        if 'BTC' in position.symbol or 'ETH' in position.symbol:
            pnl = price_diff * position.lot_size
        else:
            point = self._get_point_value(position.symbol)
            pips = price_diff / point
            pnl = pips * 10.0 * position.lot_size
        
        # Trừ costs
        total_costs = position.total_commission + position.total_swap
        return pnl - total_costs
    
    def _calculate_required_margin(self, order: Order) -> float:
        """Tính margin yêu cầu"""
        # Simplified: 1:100 leverage
        contract_size = 100000
        return (order.lot_size * contract_size) / 100
    
    def _calculate_total_exposure(self) -> float:
        """Tính tổng exposure"""
        total = 0
        for pos in self.positions.values():
            total += pos.lot_size * 100000
        return total
    
    def _update_margin(self):
        """Update margin used và free margin"""
        self.margin_used = sum(
            self._calculate_required_margin(Order(
                order_id="", symbol=pos.symbol, order_type=OrderType.MARKET,
                direction=pos.direction, lot_size=pos.lot_size, requested_price=0
            ))
            for pos in self.positions.values()
        )
        self.free_margin = self.equity - self.margin_used
    
    def _update_equity(self):
        """Update equity"""
        unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        self.equity = self.balance + unrealized_pnl
    
    def _is_market_open(self, current_time: datetime) -> bool:
        """Kiểm tra thị trường có mở không"""
        # Forex: đóng cửa cuối tuần
        if not self.config.weekend_trading:
            if current_time.weekday() >= 5:  # Saturday, Sunday
                return False
        return True
    
    def _get_point_value(self, symbol: str) -> float:
        """Get point value for symbol"""
        if 'JPY' in symbol:
            return 0.01
        return 0.0001
    
    def get_account_info(self) -> Dict:
        """Lấy thông tin tài khoản"""
        return {
            'balance': self.balance,
            'equity': self.equity,
            'margin_used': self.margin_used,
            'free_margin': self.free_margin,
            'margin_level': (self.equity / self.margin_used * 100) if self.margin_used > 0 else 0,
            'num_positions': len(self.positions),
            'total_realized_pnl': sum(p.realized_pnl for p in self.closed_positions)
        }
