# 🚀 START HERE - QuantumTrader-MT5

**Cảm thấy overwhelmed? Bắt đầu từ đây!**

---

## ⚡ Bạn muốn làm gì hôm nay?

### 1️⃣ Tôi muốn chạy backtest
```bash
python examples/quick_backtest.py
```
✅ **Xong!** Kết quả sẽ ở folder `reports/`

---

### 2️⃣ Tôi muốn paper trading (test không rủi ro)
```bash
python scripts/test_deployed_bots.py
```
✅ **Xong!** Bot sẽ chạy với tiền ảo

---

### 3️⃣ Tôi muốn xem dashboard
```bash
python scripts/dashboard.py
```
✅ **Xong!** Mở browser để monitor

---

### 4️⃣ Tôi muốn tạo strategy mới
```bash
python scripts/create_strategy.py
```
✅ **Xong!** Follow hướng dẫn trên màn hình

---

### 5️⃣ Tôi muốn chạy live trading
⚠️ **CHẬM LẠI!** Trước khi live trading:

**Checklist bắt buộc:**
- [ ] Đã backtest ít nhất 6 tháng data? → `python examples/quick_backtest.py`
- [ ] Đã paper trading ít nhất 1 tháng? → `python scripts/test_deployed_bots.py`
- [ ] Win rate > 50%? → Xem reports/
- [ ] Hiểu rõ rủi ro? → Đọc `docs/02-user-guides/crypto-trading-guide.md`

✅ **Nếu TẤT CẢ checklist đã xong:**
```bash
python scripts/live_trade_ict_audusd.py
```

---

## 📚 Tôi bị lạc trong project

### Chỉ cần nhớ 3 file này:

| File | Mục đích |
|------|----------|
| **[QUICK_SCRIPTS.md](QUICK_SCRIPTS.md)** | Copy-paste commands nhanh |
| **[SCRIPTS_INDEX.md](SCRIPTS_INDEX.md)** | Tất cả 60+ scripts có gì |
| **[docs/README.md](docs/README.md)** | Navigation tất cả documentation |

---

## 🗂️ Cấu trúc project (đơn giản hóa)

```
QuantumTrader-MT5/
│
├─ 📄 START_HERE.md          ← BẠN ĐANG Ở ĐÂY
├─ 📄 QUICK_SCRIPTS.md       ← Commands hàng ngày
├─ 📄 SCRIPTS_INDEX.md       ← Catalog đầy đủ
│
├─ 📁 examples/              ← CHẠY ĐỂ HỌC
│   ├─ quick_backtest.py     ← Bắt đầu từ đây
│   ├─ backtest_*.py         ← Các loại backtest
│   └─ use_cases/            ← 5 scenarios thực tế
│
├─ 📁 scripts/               ← TOOLS HỮU ÍCH
│   ├─ dashboard.py          ← Monitor trading
│   ├─ create_strategy.py    ← Tạo strategy mới
│   └─ test_deployed_bots.py ← Paper trading
│
├─ 📁 core/                  ← ĐỪNG ĐỘNG VÀO
│   └─ (code core của bot)
│
├─ 📁 docs/                  ← ĐỌC KHI CẦN
│   ├─ 01-getting-started/   ← Hướng dẫn cơ bản
│   ├─ 02-user-guides/       ← Guides chi tiết
│   └─ README.md             ← Navigation đầy đủ
│
├─ 📁 tests/                 ← CHỈ CHO DEVELOPERS
├─ 📁 config/                ← CẤU HÌNH BOT
└─ 📁 reports/               ← KẾT QUẢ BACKTEST
```

---

## 🎯 Workflow đơn giản nhất

### Beginner (Tuần 1-2)
```bash
# Ngày 1: Backtest
python examples/quick_backtest.py

# Ngày 2-7: Đọc kết quả, điều chỉnh config
# (edit config/config.json)

# Ngày 8-14: Paper trading
python scripts/test_deployed_bots.py
```

### Intermediate (Tuần 3-4)
```bash
# Tạo strategy riêng
python scripts/create_strategy.py

# Test strategy
python examples/quick_backtest.py

# Monitor
python scripts/dashboard.py
```

### Advanced (Tháng 2+)
```bash
# Live trading (sau khi tự tin)
python scripts/live_trade_ict_audusd.py
```

---

## ❓ FAQ - Câu hỏi thường gặp

### Q: Tôi phải bắt đầu từ đâu?
**A:** Chạy `python examples/quick_backtest.py` ngay bây giờ!

### Q: File nào quan trọng nhất?
**A:** 
- `config/config.json` - Cấu hình bot
- `examples/quick_backtest.py` - Test đầu tiên
- `QUICK_SCRIPTS.md` - Reference hàng ngày

### Q: Tôi không cần tất cả features
**A:** Đúng rồi! Chỉ dùng những gì cần:
- **Chỉ backtest?** → `examples/` folder
- **Chỉ paper trade?** → `scripts/test_deployed_bots.py`
- **Chỉ live trade?** → `scripts/live_trade_ict_audusd.py`

### Q: Folder nào có thể ignore?
**A:** Nếu không phải developer, ignore:
- `tests/` - Testing code
- `engines/` - Internal code
- `database/` - Database internals
- `ml_supertrend_mt5.egg-info/` - Package info

### Q: Tôi chỉ muốn copy-paste commands
**A:** Mở `QUICK_SCRIPTS.md` - tất cả commands ở đó!

### Q: Project quá lớn, tôi nên làm gì?
**A:** **Bạn không cần biết 100% project!** Chỉ cần:
1. Biết chạy backtest (1 command)
2. Biết paper trading (1 command)
3. Biết xem dashboard (1 command)
4. Biết đọc `QUICK_SCRIPTS.md`

**Thế thôi!** 90% còn lại là optional.

---

## 🚨 Khi gặp vấn đề

### Lỗi khi chạy script?
```bash
# 1. Check Python environment
python --version

# 2. Activate venv
venv\Scripts\activate

# 3. Reinstall dependencies
pip install -r requirements.txt

# 4. Try again
python examples/quick_backtest.py
```

### Bot không hoạt động?
```bash
# Check data
python scripts/check_data.py

# Debug signals
python scripts/debug_signals.py
```

### Cần help nhanh?
1. Mở `QUICK_SCRIPTS.md` - tìm task bạn muốn
2. Copy command
3. Paste vào terminal
4. Done!

---

## 💡 Pro Tips

### Tip 1: Bookmark 3 files này
- `START_HERE.md` (file này)
- `QUICK_SCRIPTS.md`
- `config/config.json`

### Tip 2: Chỉ cần nhớ 3 commands
```bash
python examples/quick_backtest.py        # Backtest
python scripts/test_deployed_bots.py     # Paper trade
python scripts/dashboard.py              # Monitor
```

### Tip 3: Ignore những gì không cần
❌ Không cần đọc:
- Source code trong `core/`, `engines/`
- Test files trong `tests/`
- Documentation details trong `docs/07-project-history/`

✅ Chỉ cần:
- Run scripts
- Đọc results
- Adjust config

### Tip 4: Làm việc theo template
```bash
# Morning routine
1. python scripts/dashboard.py          # Check status
2. Check reports/                       # Review results
3. Adjust config if needed

# Weekly routine
1. python examples/quick_backtest.py    # Test new config
2. Review performance
3. Decide to continue or adjust

# Monthly routine
1. Review all reports/
2. Calculate total P&L
3. Adjust strategy if needed
```

---

## 🎓 Học project theo level

### Level 0: Absolute Beginner (Ngày 1)
**Mục tiêu:** Chạy được backtest đầu tiên
```bash
python examples/quick_backtest.py
```
**Thời gian:** 10 phút

---

### Level 1: User (Tuần 1)
**Mục tiêu:** Hiểu cách bot hoạt động
- [ ] Chạy backtest thành công
- [ ] Đọc report hiểu được win rate, profit
- [ ] Biết config cơ bản trong `config/config.json`

**Commands cần biết:**
```bash
python examples/quick_backtest.py
python scripts/dashboard.py
```

---

### Level 2: Advanced User (Tuần 2-4)
**Mục tiêu:** Tự tin paper trading
- [ ] Chạy paper trading 1 tuần
- [ ] Monitor dashboard hàng ngày
- [ ] Điều chỉnh config để optimize

**Commands cần biết:**
```bash
python scripts/test_deployed_bots.py
python scripts/dashboard.py
python scripts/check_data.py
```

---

### Level 3: Power User (Tháng 2+)
**Mục tiêu:** Tạo strategy riêng
- [ ] Tạo strategy từ template
- [ ] Backtest strategy riêng
- [ ] So sánh strategies

**Commands cần biết:**
```bash
python scripts/create_strategy.py
python scripts/validate_templates.py
python scripts/test_strategy_examples.py
```

---

### Level 4: Trader (Tháng 3+)
**Mục tiêu:** Live trading có kiểm soát
- [ ] Win rate ổn định >50%
- [ ] Hiểu rõ risk management
- [ ] Có plan stop-loss rõ ràng

**Commands cần biết:**
```bash
python scripts/live_trade_ict_audusd.py
python scripts/dashboard.py  # Monitor 24/7
```

---

## 📊 Metrics quan trọng

Chỉ cần theo dõi 5 số này:

1. **Win Rate** - % thắng (>50% là good)
2. **Profit Factor** - Lãi/lỗ ratio (>1.5 là good)
3. **Max Drawdown** - Lỗ tối đa (càng thấp càng tốt)
4. **Average Win** - Lãi trung bình mỗi lệnh
5. **Average Loss** - Lỗ trung bình mỗi lệnh

**Tất cả có trong reports/ sau mỗi backtest!**

---

## 🎯 Action Plan Hôm Nay

### ✅ Checklist cho người mới (30 phút)

**Bước 1** (5 phút): Setup
```bash
cd c:\github\ML-SuperTrend-MT5
venv\Scripts\activate
```

**Bước 2** (10 phút): Backtest đầu tiên
```bash
python examples/quick_backtest.py
```

**Bước 3** (10 phút): Xem kết quả
- Mở folder `reports/`
- Tìm file Excel mới nhất
- Xem win rate, profit

**Bước 4** (5 phút): Bookmark files
- `START_HERE.md` (file này)
- `QUICK_SCRIPTS.md`
- `config/config.json`

**Xong!** Bạn đã hiểu 80% project!

---

## 🔥 Cheat Sheet - Copy This!

```bash
# ====================
# DAILY COMMANDS
# ====================

# Activate environment (luôn chạy đầu tiên)
venv\Scripts\activate

# Backtest
python examples/quick_backtest.py

# Paper trading
python scripts/test_deployed_bots.py

# Dashboard
python scripts/dashboard.py

# Check data
python scripts/check_data.py

# Debug
python scripts/debug_signals.py

# ====================
# WEEKLY COMMANDS
# ====================

# Create new strategy
python scripts/create_strategy.py

# Test all strategies
python scripts/test_strategy_examples.py

# ====================
# MONTHLY COMMANDS
# ====================

# Full test suite
python -m pytest tests/

# Generate UML
python scripts/generate_uml.py

# ====================
# EMERGENCY
# ====================

# Stop all trading
# → Close MetaTrader 5 terminal

# Reset environment
pip install -r requirements.txt --force-reinstall
```

---

## 🎁 Bonus: Aliases cho PowerShell

Thêm vào PowerShell profile để command ngắn hơn:

```powershell
# Mở: notepad $PROFILE
# Paste:

function bt { python examples/quick_backtest.py }
function pt { python scripts/test_deployed_bots.py }
function db { python scripts/dashboard.py }
function cs { python scripts/create_strategy.py }

# Reload: . $PROFILE

# Giờ chỉ cần gõ:
bt  # backtest
pt  # paper trade
db  # dashboard
cs  # create strategy
```

---

## 🌟 Remember

> **"You don't need to understand everything. You just need to know what you need, when you need it."**

**Project này có 60+ scripts, nhưng bạn chỉ cần 3-5 scripts cho daily use.**

**Còn lại? Đó là công cụ khi bạn cần mở rộng.**

---

## 📞 Next Steps

Sau khi đọc file này:

1. ✅ **Chạy backtest đầu tiên** → `python examples/quick_backtest.py`
2. ✅ **Bookmark file này** → Để quay lại khi cần
3. ✅ **Mở QUICK_SCRIPTS.md** → Khi cần command cụ thể
4. ✅ **Start small, grow gradually** → Không cần rush!

---

**Good luck! 🚀**

---

**Last Updated:** November 5, 2025  
**For:** Solo traders feeling overwhelmed  
**TL;DR:** Run `python examples/quick_backtest.py` now!
