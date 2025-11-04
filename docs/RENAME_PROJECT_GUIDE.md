# 🔄 Hướng Dẫn Đổi Tên Project

**Tác giả**: Trần Trọng Hiếu  
**Date**: October 23, 2025

---

##  Tên Mới Đề Xuất

### Top 3 Recommendations:

1. **`ML-SuperTrend-Pro-MT5`**  (Best Choice)
   - Professional, clear evolution
   - Keeps core identity
   - SEO-friendly

2. **`SuperTrend-ICT-MT5`**
   - Highlights ICT features
   - Unique positioning
   - Clear differentiation

3. **`Thales-SuperTrend-MT5`**
   - Personal branding
   - Memorable
   - Shows ownership

---

## 📋 Files Cần Update

### 1. **setup.py**
```python
# OLD:
name='ml-supertrend-mt5',

# NEW:
name='ml-supertrend-pro-mt5',  # or your chosen name
```

### 2. **README.md**
```markdown
# OLD:
# 🤖 ML-SuperTrend-MT5

# NEW:
# 🤖 ML-SuperTrend-Pro-MT5
Enhanced Machine Learning Trading Bot for MetaTrader 5
```

### 3. **pyproject.toml** (if exists)
```toml
[project]
name = "ml-supertrend-pro-mt5"
```

### 4. **MANIFEST.in**
Check if package name referenced

### 5. **docs/** (All documentation)
- README.md
- QUICKSTART.md
- All guides with project name

### 6. **Import Statements** (If package name changes)
```python
# OLD:
from ml_supertrend_mt5 import ...

# NEW:
from ml_supertrend_pro_mt5 import ...
```

---

##  Step-by-Step Process

### Phase 1: Decide on Name 

**My Top Pick:** `ML-SuperTrend-Pro-MT5`

**Reasoning:**
-  Professional
-  Shows enhancement ("Pro")
-  Maintains recognition
-  Clear purpose
-  Good for marketing

**Alternative Names (Vote!):**

A. `ML-SuperTrend-Pro-MT5` (Professional)
B. `SuperTrend-ICT-MT5` (Feature-focused)
C. `Thales-SuperTrend-MT5` (Personal brand)
D. `QuantumTrader-MT5` (Completely new)
E. Keep `ML-SuperTrend-MT5` (No change)

---

### Phase 2: Update Package Files

#### Step 1: Update setup.py

**File:** `setup.py`

**Change:**
```python
setup(
    name='ml-supertrend-pro-mt5',  # Updated
    version='2.0.0',  # Bump major version for rebrand
    author='Trần Trọng Hiếu',
    author_email='your-email@example.com',
    description='Enhanced ML SuperTrend Trading Bot with ICT/SMC strategies',
    long_description=long_description,
    # ... rest unchanged
)
```

#### Step 2: Update Package Directory (If needed)

**Only if you want package imports to change:**

```bash
# Rename package directory
mv ml_supertrend_mt5/ ml_supertrend_pro_mt5/

# Update all imports in codebase
```

** WARNING:** This breaks backward compatibility!

**Recommendation:** Keep package name same, only change display name.

---

### Phase 3: Update Documentation

#### Files to Update:

1. **README.md**
   - Title
   - Project description
   - Installation instructions
   - All references

2. **docs/README.md**
   - Project name
   - Links

3. **docs/QUICKSTART.md**
   - Examples with new name

4. **All other docs/**
   - Search & replace project name

#### Automated Update:

```powershell
# Search for old name
git grep -l "ML-SuperTrend-MT5" | grep -v ".git"

# Will list all files needing update
```

---

### Phase 4: Update GitHub Repository

#### On GitHub.com:

1. **Rename Repository:**
   - Go to: https://github.com/thales1020/ML-SuperTrend-MT5/settings
   - Scroll to "Repository name"
   - Change to: `ML-SuperTrend-Pro-MT5`
   - Click "Rename"

2. **Update Description:**
   ```
   Enhanced ML SuperTrend Trading Bot for MT5 with ICT/SMC strategies and advanced customization
   ```

3. **Update Topics:**
   ```
   metatrader5, trading-bot, machine-learning, algorithmic-trading,
   supertrend, ict-trading, smc, forex, pro-trading
   ```

#### Update Local Remote:

```powershell
# GitHub redirects automatically, but update anyway:
git remote set-url origin https://github.com/thales1020/ML-SuperTrend-Pro-MT5.git
```

---

### Phase 5: Update Configs & Scripts

#### 1. **config/config.json**
Check if project name referenced

#### 2. **scripts/** 
Check all scripts for hardcoded names

#### 3. **.gitignore**
Usually no project name

#### 4. **requirements.txt**
Usually no project name

---

### Phase 6: Test Everything

```powershell
# 1. Test installation
pip install -e .

# 2. Test imports
python -c "import ml_supertrend_mt5; print('OK')"

# 3. Test scripts
python scripts/runners/run_supertrend.py --help

# 4. Test backtest
python scripts/analysis/run_backtest.py --symbol EURUSDm

# 5. Check docs build (if using Sphinx)
cd docs && make html
```

---

### Phase 7: Commit & Push

```powershell
# Stage all changes
git add -A

# Commit with clear message
git commit -m "refactor: Rebrand project to ML-SuperTrend-Pro-MT5

- Update setup.py with new name and v2.0.0
- Update all documentation and README files
- Update repository references
- Maintain backward compatibility for imports
- Reflect enhanced features (ICT/SMC, customization)

BREAKING CHANGE: Project renamed from ML-SuperTrend-MT5 to ML-SuperTrend-Pro-MT5"

# Push
git push origin main
```

---

##  Marketing & Branding Updates

### After Renaming:

1. **Create Logo/Banner**
   - Use Canva or Figma
   - Include "Pro" badge
   - Professional design

2. **Update Social Media**
   - LinkedIn post announcing rebrand
   - Twitter thread
   - Dev.to article

3. **Create Tagline**
   ```
   "ML-SuperTrend-Pro-MT5: Where Machine Learning Meets Professional Trading"
   "Advanced MT5 Trading Bot with ICT/SMC Intelligence"
   "Professional-Grade Algorithmic Trading, Simplified"
   ```

4. **Update README Header**
   ```markdown
   <div align="center">
   
   #  ML-SuperTrend-Pro-MT5
   
   **Professional Machine Learning Trading Bot for MetaTrader 5**
   
   *Enhanced with ICT/SMC Strategies | Fully Customizable | Production-Ready*
   
   [![Author](https://img.shields.io/badge/Author-thales1020-blue)](https://github.com/thales1020)
   [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
   [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
   
   </div>
   ```

---

##  Important Considerations

### Backward Compatibility

**If you want to keep old imports working:**

```python
# In ml_supertrend_mt5/__init__.py (create if needed)
import warnings

warnings.warn(
    "Package 'ml_supertrend_mt5' has been renamed to 'ml_supertrend_pro_mt5'. "
    "Please update your imports. Old name will be deprecated in v3.0.0",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything
from ml_supertrend_pro_mt5 import *
```

### PyPI Publishing (Future)

**If planning to publish:**

```bash
# Check name availability
pip search ml-supertrend-pro-mt5

# Reserve name by publishing stub
```

---

##  Impact Analysis

### Low Impact (Safe to change):
-  Repository name on GitHub
-  README titles
-  Documentation
-  setup.py display name (if keeping package name same)

### Medium Impact:
-  setup.py package name (affects pip install)
-  Package directory name
-  Some config files

### High Impact (Avoid):
-  Package import paths (breaks user code)
-  API endpoints (if any)
-  Database schemas (N/A for this project)

---

##  Recommended Approach

### **Soft Rebrand** (Khuyến Nghị) 

**Change:**
-  GitHub repo name: `ML-SuperTrend-Pro-MT5`
-  README title
-  Documentation
-  Marketing materials
-  setup.py display name

**Keep:**
-  Package name: `ml_supertrend_mt5` (in code)
-  Import paths
-  Backward compatibility

**Result:**
- New identity & branding
- No breaking changes
- Easy transition
- Best of both worlds!

---

##  Checklist

### Pre-Rename:
- [ ] Backup everything: `git tag v1.0.0-pre-rename`
- [ ] Decide final name
- [ ] Get feedback (if team project)
- [ ] Plan announcement

### Rename Process:
- [ ] Update setup.py
- [ ] Update README.md
- [ ] Update all docs/
- [ ] Test imports
- [ ] Test scripts
- [ ] Update GitHub repo name
- [ ] Update remote URL

### Post-Rename:
- [ ] Commit & push
- [ ] Create release: v2.0.0
- [ ] Announce on social media
- [ ] Update portfolio/resume
- [ ] Celebrate! 

---

## 💬 Questions to Consider

Before you decide, answer these:

1. **Will you publish on PyPI?**
   - Yes  Choose unique name
   - No  Less critical

2. **Do you have users already?**
   - Yes  Soft rebrand (keep imports)
   - No  Free to fully rename

3. **How much different from original?**
   - 50-70%  Keep similar name
   - 95%+  (Your case) New name OK!

4. **Future plans?**
   - Personal project  Personal branding OK
   - Commercial  Professional name better
   - Open-source community  Clear & descriptive

---

##  My Final Recommendation

**For Trần Trọng Hiếu (@thales1020):**

### **Option: Soft Rebrand to `ML-SuperTrend-Pro-MT5`**

**Reasoning:**
1. You have 95-98% original code  Deserves new identity
2. Added major features (ICT/SMC)  "Pro" justified
3. Personal project  Can rebrand freely
4. No existing users  No breaking changes concern
5. Better for portfolio/resume  Shows progression

**Implementation:**
- Change GitHub repo name 
- Update all documentation 
- Keep package name same (optional) 
- Bump to v2.0.0 
- Create announcement 

**Timeline:** 1-2 hours of work

**Benefit:** Strong personal brand + clear differentiation

---

**What do you think? Should we:**
- A. Rename to `ML-SuperTrend-Pro-MT5` (soft rebrand)
- B. Rename to `SuperTrend-ICT-MT5` (feature-focused)
- C. Rename to `Thales-SuperTrend-MT5` (personal brand)
- D. Keep `ML-SuperTrend-MT5` (no change)

Tell me your preference and I'll implement it! 
