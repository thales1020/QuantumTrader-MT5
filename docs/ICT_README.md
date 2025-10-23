# ICT Trading Bot - Inner Circle Trader Strategy

## 📚 Chiến Lược ICT (Inner Circle Trader)

Bot này sử dụng các khái niệm trading nâng cao từ ICT (Michael J. Huddleston):

### 🎯 **Các Thành Phần Chính:**

#### 1. **Order Blocks (OB)** 📦
- **Bullish Order Block**: Nến giảm cuối cùng trước một đợt tăng mạnh
- **Bearish Order Block**: Nến tăng cuối cùng trước một đợt giảm mạnh
- Đây là vùng mà tổ chức/smart money đã đặt lệnh
- Giá thường quay lại test Order Block trước khi tiếp tục xu hướng

#### 2. **Fair Value Gaps (FVG)** 🔲
- **Imbalance/Gap** trong giá do giao dịch nhanh
- **Bullish FVG**: Khoảng trống giữa high của nến n-2 và low của nến n
- **Bearish FVG**: Khoảng trống giữa low của nến n-2 và high của nến n
- Giá có xu hướng quay lại "fill" các gap này

#### 3. **Liquidity Sweeps** 💧
- **Buy Side Liquidity (BSL)**: Stop loss của sellers ở trên đỉnh gần nhất
- **Sell Side Liquidity (SSL)**: Stop loss của buyers ở dưới đáy gần nhất
- Smart money thường "sweep liquidity" (đánh stop loss) trước khi đảo chiều
- **Bullish Sweep**: Giá chạm đáy → đảo chiều tăng
- **Bearish Sweep**: Giá chạm đỉnh → đảo chiều giảm

#### 4. **Market Structure** 📈📉
- **Higher Highs (HH) + Higher Lows (HL)** = Uptrend
- **Lower Highs (LH) + Lower Lows (LL)** = Downtrend
- **BOS (Break of Structure)**: Phá vỡ cấu trúc → tiếp tục xu hướng
- **CHoCH (Change of Character)**: Thay đổi xu hướng

---

## 🔧 **Cách Bot Hoạt Động:**

### **Tín Hiệu MUA (BUY):**
Cần ít nhất **2/4 điều kiện**:
1. ✅ Market structure đang uptrend (HH + HL)
2. ✅ Giá chạm vào Bullish Order Block
3. ✅ Giá trong vùng Bullish FVG
4. ✅ Có Bullish Liquidity Sweep (giá đánh SSL rồi đảo chiều)

### **Tín Hiệu BÁN (SELL):**
Cần ít nhất **2/4 điều kiện**:
1. ✅ Market structure đang downtrend (LH + LL)
2. ✅ Giá chạm vào Bearish Order Block
3. ✅ Giá trong vùng Bearish FVG
4. ✅ Có Bearish Liquidity Sweep (giá đánh BSL rồi đảo chiều)

---

## 📊 **Quản Lý Lệnh:**

### **Stop Loss (SL):**
- Đặt **dưới Order Block** (nếu BUY)
- Đặt **trên Order Block** (nếu SELL)
- Backup: 1.5x ATR nếu không có Order Block

### **Take Profit (TP):**
- Risk/Reward ratio **2:1** (mặc định)
- TP = SL distance × RR ratio

### **Position Sizing:**
- Dựa trên % risk mỗi trade (mặc định 1%)
- Tự động tính lot size dựa trên khoảng cách SL

---

## 🚀 **Cách Sử Dụng:**

### **1. Chạy Bot:**
```bash
python run_ict_bot.py --account demo --symbol EURUSDm --interval 60
```

### **2. Parameters:**
```
--account demo/live    : Loại tài khoản
--symbol EURUSDm       : Cặp tiền
--interval 60          : Chu kỳ check (giây)
--log-level INFO       : Mức log
```

### **3. Config File (config.json):**
```json
{
  "symbols": {
    "EURUSDm": {
      "enabled": true,
      "timeframe": "M15",      // Khung thời gian
      "risk_percent": 1.0,     // Risk mỗi trade
      "sl_multiplier": 1.5,    // SL backup
      "tp_multiplier": 2.0     // RR ratio
    }
  }
}
```

---

## ⚙️ **Tùy Chỉnh Chiến Lược:**

Trong file `core/ict_bot.py`, bạn có thể chỉnh:

```python
Config(
    lookback_candles=20,          # Số nến tìm Order Blocks
    fvg_min_size=0.0005,          # Kích thước FVG tối thiểu
    liquidity_sweep_pips=5.0,     # Pips để xác định sweep
    rr_ratio=2.0,                 # Risk/Reward ratio
    use_market_structure=True,    # Bật/tắt Market Structure
    use_order_blocks=True,        # Bật/tắt Order Blocks
    use_fvg=True,                 # Bật/tắt FVG
    use_liquidity_sweeps=True     # Bật/tắt Liquidity Sweeps
)
```

---

## 📈 **So Sánh với SuperTrend Bot:**

| Feature | SuperTrend Bot | ICT Bot |
|---------|---------------|---------|
| **Indicators** | SuperTrend + ATR + K-means | Order Blocks + FVG + Liquidity |
| **Complexity** | Trung bình | Cao |
| **Timeframe** | M15-M30 | M15-H1 |
| **Philosophy** | Trend Following | Smart Money Concepts |
| **Entry** | Multiple SuperTrend consensus | ICT concepts confluence |
| **Best For** | Trending markets | Range + Trend markets |

---

## 💡 **Lời Khuyên:**

### **Timeframe tốt nhất:**
- **M15-M30**: Scalping/Day trading
- **H1-H4**: Swing trading
- **D1**: Position trading

### **Symbols phù hợp:**
- ✅ **Major Forex**: EURUSD, GBPUSD, USDJPY
- ✅ **Indices**: US30, NAS100
- ⚠️ **Gold**: Cần adjust parameters (volatile)

### **Điều kiện thị trường:**
- 🟢 **Tốt nhất**: London + New York session
- 🟡 **OK**: Asian session có tin tức
- 🔴 **Tránh**: Low volatility, holidays

---

## 🎓 **Học Thêm về ICT:**

1. **Order Blocks**: https://www.youtube.com/watch?v=XXX
2. **Fair Value Gaps**: https://www.youtube.com/watch?v=XXX
3. **Liquidity Concepts**: https://www.youtube.com/watch?v=XXX
4. **Market Structure**: https://www.youtube.com/watch?v=XXX

---

## ⚠️ **Disclaimer:**

- Bot này chỉ cho mục đích **GIÁO DỤC**
- **LUÔN TEST trên DEMO** trước khi dùng live
- ICT strategy cần **kinh nghiệm** để hiểu rõ
- **KHÔNG BẢO ĐẢM** lợi nhuận
- Trading có **RỦI RO** - chỉ trade với tiền bạn có thể mất

---

## 📞 **Support:**

- GitHub: https://github.com/xPOURY4/ML-SuperTrend-MT5
- Issues: https://github.com/xPOURY4/ML-SuperTrend-MT5/issues

---

**Happy Trading! 🚀📈**
