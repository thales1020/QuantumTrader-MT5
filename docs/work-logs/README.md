# AI-Assisted Development Workflow Guide

**For:** ML-SuperTrend-MT5 Project  
**Developer:** Solo developer with AI agent assistance  
**Last Updated:** November 5, 2025

---

## 🎯 Overview

This guide explains how to work effectively with AI agents on this project, including:
- Daily work logging
- When to start new chat sessions
- How to onboard new AI agents
- Best practices for collaboration

---

## 📅 Daily Workflow

### Morning - Session Start

#### 1. Create Daily Log Entry

Create a new file in `docs/work-logs/` with format: `YYYY-MM-DD-work-log.md`

**Template:**
```markdown
# Work Log - [Date]

## 🎯 Today's Goals
- [ ] Goal 1
- [ ] Goal 2
- [ ] Goal 3

## 📝 Work Done

### [Time] - [Task Name]
**What:** Brief description
**Files Changed:** 
- file1.py
- file2.md

**Result:** Success/In Progress/Blocked

**Notes:** Any important notes

### [Time] - [Next Task]
...

## 🧪 Tests Run

### Test 1: [Name]
- **Command:** `pytest tests/...`
- **Result:** PASS/FAIL
- **Coverage:** X%
- **Notes:** ...

## 🐛 Bugs Found

### Bug #1: [Title]
- **Severity:** High/Medium/Low
- **File:** path/to/file.py
- **Description:** ...
- **Status:** Fixed/Open/Deferred

## 💡 Decisions Made

1. **[Decision Title]**
   - Context: Why this decision?
   - Options considered: A, B, C
   - Chosen: B
   - Reason: ...

## 📊 Progress

- Features completed: X
- Tests passing: Y/Z
- Code coverage: N%
- Documentation updated: Yes/No

## 🔄 Next Session

**Tomorrow's priorities:**
1. Priority 1
2. Priority 2
3. Priority 3

**Blockers:**
- Blocker 1
- Blocker 2

**Questions for next AI:**
- Question 1
- Question 2

## 🤖 AI Agent Notes

**Agent used:** Claude/GPT-4/etc  
**Session quality:** Good/Average/Poor  
**Context preserved:** Yes/No  
**Needed new session:** Yes/No at [time]

---

**Session Duration:** X hours  
**Commits Made:** N commits  
**Files Changed:** N files
```

#### 2. Update Project Status

Update `docs/08-project-management/PROJECT_STATUS.md` (create if not exists):

```markdown
# Project Status

**Last Updated:** [Date]

## Current Phase
Phase X - [Name]

## Sprint Goals (This Week)
- [ ] Goal 1
- [ ] Goal 2

## Completed This Week
- [x] Completed task 1
- [x] Completed task 2

## Metrics
- **Total Tests:** X (Y passing)
- **Code Coverage:** Z%
- **Open Issues:** N
- **Deployment Status:** Dev/Staging/Production

## Blockers
1. Blocker description

## Next Week
1. Next priority
```

---

## 🔄 When to Start New Chat Session

### Signs You Need a New Session

#### ✅ Definitely Start New Session When:

1. **Token Limit Approaching**
   - Chat becomes slow (>5 seconds response)
   - Agent mentions token limits
   - Responses get shorter/less detailed

2. **Context Loss**
   - Agent forgets earlier decisions
   - Repeats suggestions you already tried
   - Asks about project basics you explained

3. **Task Switching**
   - Moving to completely different feature
   - Switching from coding to documentation
   - Starting new phase/sprint

4. **Time Gap**
   - Next work session (next day)
   - After break >2 hours
   - Different work context

5. **Agent Confusion**
   - Contradictory suggestions
   - Can't follow project structure
   - Misunderstands requirements

#### ⚠️ Consider New Session When:

- Session >2 hours
- >50 messages exchanged
- Completed major feature
- Need fresh perspective
- Previous agent made mistakes

#### ❌ Don't Start New Session If:

- In middle of implementation
- Debugging specific issue
- Less than 30 minutes into session
- Agent still has good context

---

## 📋 New Session Onboarding Template

### Quick Onboarding (5 minutes)

Use this when starting a new chat session:

```markdown
# Project Context for AI Agent

## Project Overview
**Name:** ML-SuperTrend-MT5
**Type:** Algorithmic Trading System
**Language:** Python 3.11
**Framework:** MetaTrader 5 Integration

## What It Does
Automated trading bot with:
- Paper trading simulation
- Backtest engine
- Multiple strategy support
- Plugin system
- Real-time trading (MT5)

## Current Status
**Phase:** [X]
**Working On:** [Feature/Bug/Docs]
**Last Completed:** [What you just finished]
**Next Goal:** [What you're about to do]

## Project Structure
```
ML-SuperTrend-MT5/
├── core/           # Base bot framework
├── engines/        # Trading engines
│   ├── paper_trading_broker_api.py  ← Paper trading core
│   ├── backtest_engine.py          ← Backtesting
│   └── order_matching_engine.py    ← Order processing
├── strategies/     # Trading strategies
├── tests/         # Test suites
├── docs/          # Documentation (80+ files, organized)
└── config/        # Configuration
```

## Key Files
- **Paper Trading:** `engines/paper_trading_broker_api.py`
- **Backtest:** `engines/backtest_engine.py`
- **Main Config:** `config/config.json`
- **Tests:** `tests/` folder

## Important Context
1. **Just fixed:** [Recent fixes]
2. **Known issues:** [Current bugs]
3. **Don't change:** [Protected code]
4. **Style:** [Coding standards]

## Today's Task
**Goal:** [Specific goal]
**Files to touch:** [Expected files]
**Tests to run:** [Relevant tests]
**Success criteria:** [How to know it's done]

## Documentation
- Full docs in `docs/` (reorganized into 9 categories)
- Architecture: `docs/05-architecture/`
- Testing: `docs/04-testing/`
- Recent changes: `docs/CHANGELOG.md`

## Questions?
Check `docs/README.md` for navigation or ask!
```

### Detailed Onboarding (15 minutes)

For complex tasks or new features, add:

```markdown
## Technical Details

### Architecture
- **Paper Trading:** Simulates broker without real money
- **Order Matching:** Fills orders based on price bars
- **Position Management:** Tracks open positions, SL/TP
- **P&L Calculation:** Includes commission, swap, spread

### Recent Changes
**[Date]:** [Change 1]
**[Date]:** [Change 2]

### Active Branches
- `main` - Production-ready code
- `develop` - Current development
- `feature/X` - [Description]

### Test Coverage
- Overall: X%
- Critical modules: Y%
- Target: 85%

### Dependencies
- Python 3.11
- MetaTrader5 library
- SQLAlchemy (database)
- pytest (testing)
- See `requirements.txt` for full list

### Code Standards
- **Style:** PEP 8
- **Docs:** Google-style docstrings
- **Tests:** pytest with fixtures
- **Naming:** snake_case for functions, PascalCase for classes

### Common Commands
```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest --cov=engines --cov-report=html

# Run backtest
python run_backtest.py

# Format code
black .

# Lint
flake8 .
```

## Recent Work Log
[Copy last 3 entries from work log]

## Session Goals
1. [Goal 1]
2. [Goal 2]
3. [Goal 3]
```

---

## 💾 Saving Session Context

### Before Ending Session

Create `docs/work-logs/session-context-[date].md`:

```markdown
# Session Context - [Date & Time]

## What We Did
1. Task 1 - Status
2. Task 2 - Status

## Code Changes
**Files modified:**
- file1.py (added feature X)
- file2.py (fixed bug Y)
- file3.md (updated docs)

**Not committed yet:**
- WIP feature in branch `feature/X`
- Experimental code in `experiments/`

## Important Decisions
1. **[Decision]:** We chose X over Y because...
2. **[Decision]:** Postponed Z until...

## Discoveries
- Found bug in X
- Performance issue in Y
- Better approach for Z would be...

## Next Session Should
1. Continue from [file:line]
2. Test the [feature]
3. Fix the [issue]
4. Consider [improvement]

## Context for Next AI
**Current state:**
- Feature X is 80% done
- Tests passing except test_Y
- Need to update docs for Z

**Don't redo:**
- Already tried approach A (failed because...)
- Already tested B (works but slow)

**Try next:**
- Approach C looks promising
- Consider library D
- Ask about pattern E

## Files to Check Next
- [ ] file1.py - finish implementation
- [ ] tests/test_file1.py - add test cases
- [ ] docs/X.md - update documentation
```

---

## 📊 Weekly Review Process

### Every Friday (or end of week)

#### 1. Create Weekly Summary

File: `docs/work-logs/weekly/YYYY-WW-summary.md`

```markdown
# Week [N] Summary - [Date Range]

## 🎯 Week Goals vs Actual

| Goal | Status | Notes |
|------|--------|-------|
| Goal 1 | ✅ Done | Completed ahead |
| Goal 2 | 🔄 80% | Need 1 more day |
| Goal 3 | ❌ Deferred | Lower priority |

## 📊 Metrics

### Code
- **Lines added:** +XXX
- **Lines removed:** -XXX
- **Files changed:** N
- **Commits:** N

### Tests
- **Tests added:** N
- **Coverage change:** X% → Y%
- **Tests passing:** Z/Total

### Issues
- **Bugs fixed:** N
- **Bugs found:** N
- **Net change:** +/-N

## 🏆 Achievements

1. Achievement 1
2. Achievement 2
3. Achievement 3

## 🐛 Issues Encountered

1. **Issue 1**
   - Impact: High/Med/Low
   - Resolution: ...
   - Time lost: X hours

## 📚 Documentation

- [ ] README updated
- [ ] API docs updated
- [ ] Examples added
- [ ] Changelog updated

## 💡 Learnings

1. Learning 1
2. Learning 2
3. Learning 3

## 🔄 Next Week Plan

**Priority 1 (Must do):**
1. Task 1
2. Task 2

**Priority 2 (Should do):**
1. Task 3
2. Task 4

**Priority 3 (Nice to have):**
1. Task 5

## 🤖 AI Collaboration Notes

**Sessions this week:** N
**Quality:** Good/Average/Poor
**Most helpful:** [What AI did well]
**Needs improvement:** [What could be better]
**Best practices learned:** [Tips discovered]
```

---

## 🎨 Best Practices

### Working with AI Agents

#### ✅ DO:

1. **Be Specific**
   ```
   ❌ "Fix the bug"
   ✅ "Fix the AttributeError in paper_trading_broker_api.py line 247 
       where broker.orders property is missing"
   ```

2. **Provide Context**
   ```
   ✅ "I'm working on paper trading system. Previously we added SL/TP 
       extraction. Now need to test the auto-close feature when SL is hit."
   ```

3. **Share Relevant Code**
   ```
   ✅ "Here's the current implementation of _update_positions():
       [paste code snippet]
       How can I optimize this?"
   ```

4. **Explain Your Goal**
   ```
   ✅ "Goal: Increase test coverage from 15% to 40% this week
       Focus: Paper trading module
       Priority: Critical paths first"
   ```

5. **Give Feedback**
   ```
   ✅ "That solution works but it's too complex. Can we simplify it?"
   ✅ "Perfect! That's exactly what I needed."
   ```

#### ❌ DON'T:

1. **Don't assume AI remembers everything**
   - Re-explain context after long gaps
   - Provide file paths every time
   - Reference previous decisions explicitly

2. **Don't paste huge files**
   - Show only relevant sections
   - Use line numbers: "See lines 100-150"
   - Summarize the rest

3. **Don't accept without understanding**
   - Ask "why" if unclear
   - Request explanations
   - Verify against your knowledge

4. **Don't skip documentation**
   - Document AI-suggested solutions
   - Update work logs
   - Keep context files

5. **Don't blindly copy-paste**
   - Review all code
   - Test everything
   - Understand the changes

---

## 🔧 Tools & Templates

### Quick Copy-Paste Templates

#### Start of Day
```markdown
Good morning! Working on ML-SuperTrend-MT5 trading system.

**Yesterday:** [What you did]
**Today's goal:** [What you want to do]
**Current status:** [Project state]

Ready to start on [specific task]. Need help with [specific question].
```

#### Ask for Help
```markdown
Need help with [specific problem].

**Context:**
- Working on: [file/feature]
- Trying to: [goal]
- Current code: [snippet]
- Error/Issue: [problem]

**What I tried:**
1. Tried X - didn't work because Y
2. Tried Z - got error W

**Question:** [Specific question]
```

#### Code Review Request
```markdown
Please review this code:

**Purpose:** [What it does]
**Concerns:** [What you're worried about]

```python
[code]
```

**Specific questions:**
1. Is this efficient?
2. Any edge cases missed?
3. Better way to do this?
```

#### End of Session
```markdown
Great session! Let me summarize:

**Completed:**
- [x] Task 1
- [x] Task 2

**In progress:**
- [ ] Task 3 (80% done)

**Next session:**
- Continue Task 3
- Start Task 4

**Files changed:**
- file1.py
- file2.md

Thanks! Will commit these changes now.
```

---

## 📁 Directory Structure for Work Logs

```
docs/
├── work-logs/
│   ├── daily/
│   │   ├── 2025-11-05-work-log.md
│   │   ├── 2025-11-06-work-log.md
│   │   └── ...
│   ├── weekly/
│   │   ├── 2025-W45-summary.md
│   │   ├── 2025-W46-summary.md
│   │   └── ...
│   ├── session-context/
│   │   ├── 2025-11-05-morning.md
│   │   ├── 2025-11-05-afternoon.md
│   │   └── ...
│   └── README.md (This file)
```

---

## 🎯 Success Metrics

Track these to improve your AI collaboration:

### Session Quality
- **Response accuracy:** Does AI understand your needs?
- **Code quality:** Is generated code production-ready?
- **Time saved:** Faster than solo coding?
- **Learning:** Did you learn something new?

### Workflow Efficiency
- **Context switch time:** How long to onboard new session?
- **Rework needed:** How much code needs fixing?
- **Session length:** Optimal duration found?
- **Documentation quality:** Can you resume easily?

### Project Progress
- **Velocity:** Features completed per week
- **Quality:** Bugs per feature
- **Coverage:** Test coverage trend
- **Debt:** Technical debt introduced vs paid

---

## 💡 Pro Tips

### 1. Context Management

**Create a project brief file:** `docs/PROJECT_BRIEF.md`
```markdown
# ML-SuperTrend-MT5 - Quick Reference

## One-liner
Algorithmic trading bot with paper trading, backtesting, and MT5 integration.

## Architecture (60 seconds)
[Quick diagram or bullet points]

## Active work
[Current sprint goals]

## Quick links
- Main code: engines/paper_trading_broker_api.py
- Tests: tests/
- Docs: docs/
```

Keep this under 500 words. Copy-paste to new sessions.

### 2. Problem-Specific Contexts

Create files like:
- `docs/contexts/testing-context.md` - For testing sessions
- `docs/contexts/debugging-context.md` - For bug fixing
- `docs/contexts/architecture-context.md` - For design discussions

### 3. Decision Log

Keep `docs/DECISIONS.md`:
```markdown
# Architectural Decisions

## [Date] - Decision to use SQLAlchemy
**Context:** Need database for trade history
**Options:** SQLite direct, SQLAlchemy, Supabase
**Chosen:** SQLAlchemy
**Reason:** ORM flexibility, easier testing
**Trade-offs:** Slight performance overhead
```

### 4. AI Agent Comparison

Track which AI works best for what:
```markdown
# AI Agent Notes

## Claude
- **Best for:** Architecture, complex logic, refactoring
- **Struggles with:** [Specific weaknesses]

## GPT-4
- **Best for:** Documentation, creative solutions
- **Struggles with:** [Specific weaknesses]

## Copilot
- **Best for:** Code completion, similar patterns
- **Struggles with:** [Specific weaknesses]
```

---

## 🚀 Advanced Workflow

### Multi-Agent Collaboration

Sometimes use multiple AIs in parallel:

1. **Agent A:** Write implementation
2. **Agent B:** Review Agent A's code
3. **You:** Make final decision

Document this:
```markdown
## Multi-Agent Session

**Primary Agent (Implementation):**
- Task: Implement feature X
- Result: [Summary]

**Review Agent (Code Review):**
- Found: 3 issues
- Suggestions: [List]

**Final Decision:**
Implemented Agent A's approach with Agent B's suggestion #2.
```

### Checkpoint System

Create checkpoints during long tasks:

```markdown
# Feature X - Checkpoints

## Checkpoint 1: Design ✅
- [x] Architecture decided
- [x] APIs defined
- [x] Tests planned

## Checkpoint 2: Core Implementation 🔄
- [x] Basic structure
- [ ] Error handling
- [ ] Edge cases

## Checkpoint 3: Testing ⏸️
- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance tests

## Checkpoint 4: Documentation ⏸️
- [ ] Code comments
- [ ] API docs
- [ ] User guide
```

---

## 📞 Emergency Procedures

### When Things Go Wrong

#### 1. Agent Gave Bad Code

```markdown
# Rollback Note - [Date]

**What happened:**
Agent suggested [approach] but it [problem].

**Impact:**
- Broke: [what broke]
- Time lost: X hours

**Resolution:**
Reverted to commit [hash]. Used [alternative approach].

**Lesson:**
Always [what to do differently next time].

**Code preserved:**
Saved bad attempt in `experiments/failed-approach-[date]/`
```

#### 2. Lost Context

Keep a **project-state.json**:
```json
{
  "last_updated": "2025-11-05",
  "current_branch": "feature/paper-trading",
  "working_on": "SL/TP auto-close",
  "status": "testing",
  "next_step": "Add integration tests",
  "important_files": [
    "engines/paper_trading_broker_api.py",
    "tests/test_paper_trading.py"
  ],
  "blockers": [],
  "notes": "Completed Fix #1, #2, #3. Need Fix #4."
}
```

Update after each session. AI can read this to understand state.

---

## ✅ Daily Checklist

### Morning
- [ ] Review yesterday's work log
- [ ] Check `project-state.json`
- [ ] Update today's goals
- [ ] Prepare context for AI

### During Work
- [ ] Log completed tasks in real-time
- [ ] Update session context every hour
- [ ] Commit small changes frequently
- [ ] Document decisions as you make them

### Evening
- [ ] Complete work log
- [ ] Update `project-state.json`
- [ ] Create session context for tomorrow
- [ ] Commit & push all changes
- [ ] Update weekly progress

---

## 🎓 Learning & Improvement

### Monthly Review

Every month, review:
1. **Velocity trends** - Getting faster/slower?
2. **Quality trends** - Fewer/more bugs?
3. **AI effectiveness** - Better/worse collaboration?
4. **Workflow efficiency** - Process improvements?

Create: `docs/work-logs/monthly/YYYY-MM-review.md`

---

## 📚 Resources

### Internal
- Project docs: `docs/README.md`
- Architecture: `docs/05-architecture/`
- Testing guide: `docs/04-testing/`

### External
- [How to write good AI prompts](https://link)
- [Working with AI on code](https://link)
- [Documentation best practices](https://link)

---

## 🆘 Quick Reference

| Situation | Action |
|-----------|--------|
| Starting day | Copy project brief + yesterday's log |
| Chat getting slow | Save context, start new session |
| Complex task | Create detailed onboarding |
| Quick question | Use quick template |
| Session ending | Update work log + context |
| Week ending | Write weekly summary |
| Agent confused | Simplify context, start fresh |
| Code not working | Document attempt, try simpler |
| Multiple approaches | Use decision log |
| Lost track | Check project-state.json |

---

**Remember:** The goal is to work efficiently with AI while maintaining full understanding and control of your project. The AI is a tool to amplify your productivity, not replace your judgment.

**Time investment:**
- Initial setup: 30 minutes
- Daily logging: 10-15 minutes
- Weekly review: 30 minutes
- **ROI:** 2-3x productivity increase

Good luck! 🚀
