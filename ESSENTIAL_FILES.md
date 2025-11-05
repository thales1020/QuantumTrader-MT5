# Essential Files Only - Quick Reference

Nếu project quá lớn, chỉ cần quan tâm những files này:

## 🎯 Core Files (Bắt buộc)

### Configuration
```
config/config.json          ← Cài đặt bot (QUAN TRỌNG NHẤT!)
```

### Quick Start
```
START_HERE.md              ← Điểm bắt đầu (đọc đầu tiên)
QUICK_SCRIPTS.md           ← Commands hàng ngày
```

### Essential Scripts
```
examples/quick_backtest.py           ← Backtest nhanh
scripts/test_deployed_bots.py        ← Paper trading
scripts/dashboard.py                 ← Monitor
scripts/check_data.py                ← Check data
```

---

## 📁 Essential Folders

### 1. examples/ (CHẠY ĐỂ HỌC)
```
examples/
├── quick_backtest.py       ← BẮT ĐẦU TỪ ĐÂY
├── backtest_supertrend_v2.py
└── use_cases/
    ├── use_case_1_conservative.py  ← Strategy an toàn
    └── use_case_2_scalping.py      ← Strategy tích cực
```

### 2. scripts/ (TOOLS)
```
scripts/
├── test_deployed_bots.py   ← Paper trading
├── dashboard.py            ← Monitor
├── create_strategy.py      ← Tạo strategy
└── check_data.py          ← Verify data
```

### 3. config/ (SETTINGS)
```
config/
├── config.json            ← Cài đặt chính
└── config.example.json    ← Template
```

### 4. reports/ (RESULTS)
```
reports/
└── backtest_*.xlsx        ← Kết quả backtest ở đây
```

---

## 🚫 Có thể Ignore (Không cần quan tâm)

### For Non-Developers
```
tests/                     ← Testing code (skip it!)
engines/                   ← Internal engine (skip it!)
database/                  ← Database code (skip it!)
ml_supertrend_mt5.egg-info/ ← Package info (skip it!)
__pycache__/              ← Python cache (skip it!)
.pytest_cache/            ← Test cache (skip it!)
htmlcov/                  ← Coverage reports (skip it!)
```

### Documentation (Chỉ đọc khi cần)
```
docs/07-project-history/   ← History (không cần)
docs/05-architecture/      ← Architecture (nâng cao)
docs/06-technical-specs/   ← Specs (nâng cao)
```

---

## 📊 File Size Reference

| File/Folder | Quan trọng? | Khi nào cần? |
|-------------|-------------|--------------|
| **config/config.json** | ⭐⭐⭐⭐⭐ | Mỗi ngày |
| **START_HERE.md** | ⭐⭐⭐⭐⭐ | Khi lạc đường |
| **QUICK_SCRIPTS.md** | ⭐⭐⭐⭐⭐ | Mỗi ngày |
| **examples/** | ⭐⭐⭐⭐ | Học & test |
| **scripts/** | ⭐⭐⭐⭐ | Tools hữu ích |
| **reports/** | ⭐⭐⭐⭐ | Xem kết quả |
| **docs/01-getting-started/** | ⭐⭐⭐ | Người mới |
| **docs/02-user-guides/** | ⭐⭐⭐ | Khi cần guide |
| **tests/** | ⭐ | Developers only |
| **engines/** | ⭐ | Developers only |

---

## 💡 Minimalist Approach

### Chỉ cần 3 files này cho 90% công việc:

1. **config/config.json**
   - Cấu hình bot
   - Thay đổi settings
   - Adjust risk

2. **QUICK_SCRIPTS.md**
   - Copy commands
   - Chạy ngay
   - Không cần hiểu code

3. **reports/**
   - Xem kết quả
   - Track performance
   - Make decisions

**Thế thôi!**

---

## 🎯 Focus Strategy

### Week 1-2: The Essentials
**Only learn:**
- How to run backtest
- How to read results
- How to adjust config

**Files to know:**
- `examples/quick_backtest.py`
- `config/config.json`
- `reports/`

**Ignore everything else!**

---

### Week 3-4: Paper Trading
**Only add:**
- How to paper trade
- How to monitor

**New files:**
- `scripts/test_deployed_bots.py`
- `scripts/dashboard.py`

**Still ignore everything else!**

---

### Month 2+: Advanced (Optional)
**If you want more:**
- Create custom strategies
- Explore other scripts

**New files:**
- `scripts/create_strategy.py`
- `SCRIPTS_INDEX.md`

**Still don't need to read source code!**

---

## 🔍 Quick File Finder

**"Tôi muốn..."**

| Task | File |
|------|------|
| Backtest | `examples/quick_backtest.py` |
| Paper trade | `scripts/test_deployed_bots.py` |
| Monitor | `scripts/dashboard.py` |
| Change settings | `config/config.json` |
| Create strategy | `scripts/create_strategy.py` |
| Check data | `scripts/check_data.py` |
| See results | `reports/` folder |
| Get help | `START_HERE.md` |
| Find commands | `QUICK_SCRIPTS.md` |
| Find all scripts | `SCRIPTS_INDEX.md` |

---

## 📝 Bookmark These

**Top 5 files to bookmark:**

1. `START_HERE.md` - When lost
2. `QUICK_SCRIPTS.md` - Daily commands
3. `config/config.json` - Bot settings
4. `ESSENTIAL_FILES.md` - This file
5. `examples/quick_backtest.py` - First script to run

**Copy this path for quick access:**
```
c:\github\ML-SuperTrend-MT5\START_HERE.md
c:\github\ML-SuperTrend-MT5\QUICK_SCRIPTS.md
c:\github\ML-SuperTrend-MT5\config\config.json
c:\github\ML-SuperTrend-MT5\ESSENTIAL_FILES.md
```

---

## 🎓 Learning Path (Minimalist)

### Day 1 (15 minutes)
1. Read `START_HERE.md` (5 min)
2. Run `python examples/quick_backtest.py` (5 min)
3. Check `reports/` (5 min)

**Done! You understand the basics.**

---

### Week 1 (1 hour total)
1. Run backtest 3-4 times
2. Try different configs
3. Learn to read reports

**Done! You can backtest like a pro.**

---

### Week 2-4 (2 hours total)
1. Try paper trading
2. Monitor daily
3. Adjust based on results

**Done! You're ready for live (if metrics are good).**

---

## 🚨 Red Flags (Dấu hiệu làm quá nhiều)

❌ **Stop if:**
- Reading source code in `core/`, `engines/`
- Trying to understand all tests
- Reading all documentation
- Exploring all 60+ scripts

✅ **Instead:**
- Use what works
- Copy-paste commands
- Focus on results
- Ignore the rest

---

## 💪 You Don't Need To:

- ❌ Understand all code
- ❌ Read all docs
- ❌ Know all scripts
- ❌ Be a Python expert
- ❌ Understand ML algorithms
- ❌ Know system architecture

## ✅ You Only Need To:

- ✅ Run backtest
- ✅ Read results
- ✅ Adjust config
- ✅ Monitor performance
- ✅ Make informed decisions

**That's it!**

---

## 🎯 Final Word

**Project size:** 60+ scripts, 80+ docs, 1000+ files

**What you need:** 3-5 scripts, 2-3 docs, 5-10 files

**Ratio:** ~1% of project for 90% of value

**Don't let size intimidate you. Focus on what matters.**

---

**When overwhelmed, come back to this file.**

**Remember: Less is more. Start small, stay focused.**

---

**Created:** November 5, 2025  
**Purpose:** Simplify overwhelming project  
**For:** Traders, not developers
