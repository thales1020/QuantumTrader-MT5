# 🚀 Quick Reference Card - AI Collaboration

**For:** ML-SuperTrend-MT5 Project  
**Print this and keep nearby!**

---

## 📋 Daily Checklist

### ☀️ Morning (5 minutes)
- [ ] Read `project-state.json`
- [ ] Review yesterday's work log
- [ ] Create today's work log from template
- [ ] Prepare context for AI session

### 🌙 Evening (10 minutes)
- [ ] Complete today's work log
- [ ] Update `project-state.json`
- [ ] Commit changes
- [ ] Create context for tomorrow

---

## 🤖 Starting New AI Session

### Quick Onboarding (Copy-Paste)

```
Working on ML-SuperTrend-MT5 algorithmic trading system.

**Project:** Python 3.11 trading bot with paper trading + backtesting
**Status:** [Check project-state.json]
**Today's goal:** [Your goal]
**Files:** engines/, tests/, docs/

**Context:** [Recent work from last work log]

Ready to start on [specific task].
```

### When to Start New Session?

✅ **Start New If:**
- Chat response >5 seconds
- Agent forgets earlier decisions
- Moving to different feature
- Next day/after 2+ hour break

❌ **Don't Start If:**
- Mid-implementation
- Debugging specific issue
- <30 minutes into session

---

## 📁 Key File Locations

```
Quick Access:
├── Work logs: docs/work-logs/daily/
├── Context: project-state.json
├── Paper trading: engines/paper_trading_broker_api.py
├── Tests: tests/
├── Docs: docs/README.md
└── Config: config/config.json
```

---

## 💬 Common AI Prompts

### Ask for Help
```
Need help with [problem] in [file].

Current code: [snippet]
Error: [error message]
Tried: [what you tried]

Question: [specific question]
```

### Code Review
```
Please review this code:

Purpose: [what it does]
Concerns: [your worries]

[code]

Questions:
1. Edge cases?
2. Performance?
3. Better approach?
```

### End Session
```
Great session!

Completed: [tasks]
Next: [next tasks]
Files changed: [files]

Thanks! Committing now.
```

---

## 📊 Project Stats (Update Weekly)

| Metric | Current | Target |
|--------|---------|--------|
| Test Coverage | 15% | 85% |
| Tests Passing | 17/20 | 100% |
| Documentation | 90 files | - |
| Code Quality | Good | Excellent |

---

## 🎯 Current Sprint Goals

**Week of [Date]:**
1. Goal 1
2. Goal 2
3. Goal 3

---

## 🚨 Emergency Commands

```bash
# Check status
cat project-state.json

# View last log
cat docs/work-logs/daily/$(ls -t docs/work-logs/daily/ | head -1)

# Run tests
pytest tests/ -v

# Check coverage
pytest --cov=engines --cov-report=html
```

---

## 📞 Quick Links

- **Full Workflow:** `docs/work-logs/README.md`
- **Project Brief:** `docs/README.md`
- **Architecture:** `docs/05-architecture/`
- **Testing:** `docs/04-testing/`

---

## 💡 Pro Tips

1. **Update `project-state.json` every hour**
2. **Commit small changes frequently**
3. **Document decisions immediately**
4. **Keep sessions <3 hours**
5. **Copy-paste templates, don't type from scratch**

---

## ⏱️ Time Investment

- Daily logging: 10-15 min
- Weekly review: 30 min
- **ROI:** 2-3x productivity

---

**Keep this card visible while coding!** 📌

**Last Updated:** November 5, 2025
