# 🔒 Breakeven Stop Loss Feature

## Tổng quan

Tính năng **Move SL to Breakeven** tự động di chuyển Stop Loss của Order 2 (Main RR) về giá entry khi Order 1 (RR 1:1) đạt Take Profit.

##  Lợi ích

1. **Bảo vệ lợi nhuận**: Sau khi Order 1 đạt TP (RR 1:1), trade đã có lãi  Di chuyển SL về breakeven để bảo vệ
2. **Không rủi ro**: Order 2 sẽ không bị lỗ nếu giá quay đầu
3. **Tâm lý thoải mái**: Biết rằng trade không thể lỗ, cho phép để Order 2 chạy đến TP cao hơn
4. **Tối ưu Risk/Reward**: Giữ được tiềm năng lợi nhuận lớn từ Order 2 mà không lo rủi ro

##  Cách hoạt động

### Quy trình tự động:

1. **Mở 2 lệnh đồng thời**:
   - Order 1: TP = Entry + Risk × 1.0 (RR 1:1)
   - Order 2: TP = Entry + Risk × RR_Ratio (ví dụ: RR 2:1)
   - Cả 2 có cùng SL ban đầu

2. **Giám sát Order 1**:
   - Bot kiểm tra liên tục xem Order 1 còn mở không
   - Nếu Order 1 đóng (hit TP)  Kích hoạt bước 3

3. **Di chuyển SL Order 2**:
   - Tự động modify SL của Order 2 = Entry Price
   - Order 2 giờ ở trạng thái "risk-free" (không rủi ro)
   - Để Order 2 chạy đến TP2

### Ví dụ cụ thể:

####  **BUY Trade:**
```
Entry  = 1.0850
SL     = 1.0800  (Risk = 50 pips)
TP1    = 1.0900  (+50 pips, RR 1:1) ← Order 1
TP2    = 1.0950  (+100 pips, RR 2:1) ← Order 2

Khi giá đạt 1.0900:
 Order 1 đóng với +50 pips lãi
🔄 Order 2: SL di chuyển từ 1.0800  1.0850 (breakeven)
 Order 2 tiếp tục chạy đến TP2 = 1.0950 mà không lo rủi ro
```

####  **SELL Trade:**
```
Entry  = 1.0850
SL     = 1.0900  (Risk = 50 pips)
TP1    = 1.0800  (-50 pips, RR 1:1) ← Order 1
TP2    = 1.0750  (-100 pips, RR 2:1) ← Order 2

Khi giá đạt 1.0800:
 Order 1 đóng với +50 pips lãi
🔄 Order 2: SL di chuyển từ 1.0900  1.0850 (breakeven)
 Order 2 tiếp tục chạy đến TP2 = 1.0750 mà không lo rủi ro
```

##  Cấu hình

### Trong code:

**ICT Bot** (`core/ict_bot.py`):
```python
config = Config(
    symbol="EURUSD",
    risk_percent=1.0,
    rr_ratio=2.0,
    move_sl_to_breakeven=True  # ← Bật tính năng
)
```

**SuperTrend Bot** (`core/supertrend_bot.py`):
```python
config = Config(
    symbol="EURUSD",
    risk_percent=1.0,
    tp_multiplier=3.0,
    sl_multiplier=2.0,
    move_sl_to_breakeven=True  # ← Bật tính năng
)
```

### Trong config file (`config/config.json`):

```json
{
  "ict_bot": {
    "symbol": "EURUSD",
    "risk_percent": 1.0,
    "rr_ratio": 2.0,
    "move_sl_to_breakeven": true
  },
  "supertrend_bot": {
    "symbol": "EURUSD",
    "risk_percent": 1.0,
    "move_sl_to_breakeven": true
  }
}
```

##  Log Messages

Khi tính năng hoạt động, bạn sẽ thấy các log sau:

```
 Order 1 (RR 1:1) closed! Moving Order 2's SL to breakeven...
 SL modified for ticket 123456: 1.08000  1.08500
 Order 2 now at BREAKEVEN (SL = Entry = 1.08500)
🔒 Trade is now RISK-FREE! Letting profits run to TP2=1.09500
```

## 🎲 Các kịch bản

### Kịch bản 1: Order 1 hit TP, Order 2 hit TP
```
Entry = 100.00, SL = 99.00, Risk = 1.00

Order 1: TP = 101.00 (RR 1:1)
Order 2: TP = 102.00 (RR 2:1)

Kết quả:
 Order 1: +1.00 (đóng tại 101.00)
 Order 2: +2.00 (SL moved to 100.00, đóng tại 102.00)
 Tổng: +3.00 (= Risk × 3)
```

### Kịch bản 2: Order 1 hit TP, giá quay đầu hit SL của Order 2
```
Entry = 100.00, SL = 99.00, Risk = 1.00

Order 1: TP = 101.00 (RR 1:1)
Order 2: TP = 102.00 (RR 2:1)

Kết quả:
 Order 1: +1.00 (đóng tại 101.00)
🔄 Order 2: SL moved to 100.00
 Order 2: +0.00 (giá quay đầu, đóng tại breakeven 100.00)
 Tổng: +1.00 (= Risk × 1) ← Vẫn lãi!
```

### Kịch bản 3: Cả 2 order hit SL (trước khi Order 1 hit TP)
```
Entry = 100.00, SL = 99.00, Risk = 1.00

Giá không đạt TP1, quay đầu hit SL

Kết quả:
 Order 1: -1.00
 Order 2: -1.00
 Tổng: -2.00 (= Risk × 2)
```

## 🔑 Điểm chính

 **Tự động hóa hoàn toàn**: Không cần can thiệp thủ công

 **Bật/Tắt linh hoạt**: Sử dụng `move_sl_to_breakeven = True/False`

 **Áp dụng cho cả 2 bot**: ICT Bot và SuperTrend Bot

 **Bảo vệ lợi nhuận**: Sau khi Order 1 chốt lời, Order 2 không thể lỗ

 **Tối ưu RR**: Giữ được tiềm năng lợi nhuận lớn từ Order 2

##  Khi nào nên dùng?

###  Nên dùng khi:
- Muốn bảo vệ lợi nhuận sau khi đã có RR 1:1
- Trade theo trend mạnh, muốn để lợi nhuận chạy
- Tâm lý lo sợ giá quay đầu sau khi có lãi
- Muốn tối ưu hóa risk/reward

###  Có thể không dùng khi:
- Chiến lược scalping (đóng lệnh nhanh)
- Không muốn can thiệp vào SL ban đầu
- Trading range-bound markets (giá đi ngang)

##  Notes

1. **Không áp dụng trailing stop**: Tính năng này chỉ di chuyển SL về breakeven 1 lần, không trailing liên tục
2. **Chỉ kiểm tra khi có position**: Bot chỉ check khi `current_trade` tồn tại
3. **Backward compatible**: Nếu tắt feature (`move_sl_to_breakeven=False`), bot hoạt động như cũ
4. **MT5 API**: Sử dụng `TRADE_ACTION_SLTP` để modify SL

##  Troubleshooting

### Lỗi: "Failed to modify SL"
- Kiểm tra kết nối MT5
- Đảm bảo position còn mở
- Kiểm tra SL level hợp lệ (không quá gần giá hiện tại)

### SL không tự động di chuyển
- Kiểm tra `move_sl_to_breakeven = True`
- Xem log để đảm bảo Order 1 đã đóng
- Kiểm tra `ticket1` và `ticket2` được lưu đúng

### Log không hiện thông báo
- Đảm bảo log level = INFO hoặc DEBUG
- Kiểm tra file log: `ict_bot.log` hoặc `supertrend_bot.log`

---

**Tác giả**: xPOURY4  
**Ngày tạo**: October 21, 2025  
**Version**: 1.0.0
