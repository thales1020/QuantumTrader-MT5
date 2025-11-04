#  Hướng Dẫn Tạo Repository Mới Trên GitHub Của Bạn

**Tác giả**: Trần Trọng Hiếu  
**GitHub**: @thales1020  
**Ngày**: 23 tháng 10, 2025

---

##  Mục Tiêu

Tạo repository mới trên **GitHub cá nhân** (@thales1020) và push toàn bộ code ML-SuperTrend-MT5 lên đó.

---

## 📋 Bước 1: Tạo Repository Mới Trên GitHub

### Option A: Qua GitHub Website (Dễ nhất)

1. **Đăng nhập GitHub** với account **@thales1020**

2. **Tạo Repository Mới**:
   - Vào: https://github.com/new
   - Hoặc click nút **[+]** ở góc trên bên phải  **New repository**

3. **Điền thông tin**:
   ```
   Repository name:     ML-SuperTrend-MT5
   Description:         Machine Learning Enhanced SuperTrend Trading Bot for MetaTrader 5
   Visibility:           Public (hoặc Private nếu muốn)
   
    KHÔNG tick: Initialize with README
    KHÔNG tick: Add .gitignore
    KHÔNG tick: Choose a license
   
   (Vì chúng ta đã có rồi!)
   ```

4. **Click "Create repository"**

5. **Copy URL** của repo mới:
   ```
   https://github.com/thales1020/ML-SuperTrend-MT5.git
   ```

### Option B: Qua GitHub CLI (Nhanh hơn)

```bash
# Cài GitHub CLI nếu chưa có: https://cli.github.com/

# Login
gh auth login

# Tạo repo
gh repo create ML-SuperTrend-MT5 --public --source=. --remote=origin-thales

# Đây sẽ tự động tạo repo và thêm remote
```

---

## 📋 Bước 2: Chuẩn Bị Local Repository

### 2.1: Kiểm Tra Git Status

```powershell
# Xem current status
git status

# Xem current remotes
git remote -v
```

**Hiện tại bạn có:**
```
origin  https://github.com/xPOURY4/ML-SuperTrend-MT5.git (fetch)
origin  https://github.com/xPOURY4/ML-SuperTrend-MT5.git (push)
```

### 2.2: Option A - Thay Đổi Origin (Khuyến Nghị)

**Nếu bạn muốn THAY THẾ hoàn toàn xPOURY4 bằng thales1020:**

```powershell
# Xóa remote cũ
git remote remove origin

# Thêm remote mới (thales1020)
git remote add origin https://github.com/thales1020/ML-SuperTrend-MT5.git

# Verify
git remote -v
```

**Kết quả:**
```
origin  https://github.com/thales1020/ML-SuperTrend-MT5.git (fetch)
origin  https://github.com/thales1020/ML-SuperTrend-MT5.git (push)
```

### 2.3: Option B - Giữ Cả Hai Remotes

**Nếu bạn muốn GIỮ CẢ HAI (xPOURY4 và thales1020):**

```powershell
# Đổi tên remote cũ
git remote rename origin origin-xpoury4

# Thêm remote mới làm origin chính
git remote add origin https://github.com/thales1020/ML-SuperTrend-MT5.git

# Verify
git remote -v
```

**Kết quả:**
```
origin              https://github.com/thales1020/ML-SuperTrend-MT5.git (fetch)
origin              https://github.com/thales1020/ML-SuperTrend-MT5.git (push)
origin-xpoury4      https://github.com/xPOURY4/ML-SuperTrend-MT5.git (fetch)
origin-xpoury4      https://github.com/xPOURY4/ML-SuperTrend-MT5.git (push)
```

---

## 📋 Bước 3: Commit Attribution Files

```powershell
# Stage tất cả thay đổi (attribution files)
git add -A

# Commit với message rõ ràng
git commit -m "docs: Add professional attribution and author information

- Update LICENSE with full name (Trần Trọng Hiếu)
- Add NOTICE file with community attribution
- Update README with author section and badges
- Create comprehensive ATTRIBUTION.md
- Add AUTHOR_INFO.md explaining repo structure
- Document 95-98% original code ownership
- Link personal GitHub (@thales1020)

This establishes clear ownership and professional attribution
while respecting the open-source community that inspired the work."
```

---

## 📋 Bước 4: Push Lên GitHub Mới

### 4.1: Push Lần Đầu (với -u)

```powershell
# Push và set upstream
git push -u origin main

# Hoặc nếu branch là master
git push -u origin master
```

**Giải thích:**
- `-u` (hoặc `--set-upstream`): Set default remote cho branch
- `origin`: Remote name
- `main`: Branch name

### 4.2: Xử Lý Lỗi Nếu Có

**Lỗi 1: Authentication Failed**
```powershell
# Windows: Dùng Git Credential Manager
# Sẽ mở browser để login

# Hoặc dùng Personal Access Token
# Tạo token tại: https://github.com/settings/tokens
# Chọn scopes: repo, workflow
```

**Lỗi 2: Protected Branch**
```bash
# GitHub Settings  Branches  Edit protection rules
# Hoặc push vào branch khác trước
git push -u origin main:dev
```

**Lỗi 3: Large Files**
```bash
# Check file sizes
git ls-files | xargs ls -lh

# If needed, use Git LFS
git lfs track "*.whl"
git add .gitattributes
git commit -m "Add Git LFS tracking"
```

---

## 📋 Bước 5: Verify Trên GitHub

### 5.1: Kiểm Tra Trên Web

Vào: https://github.com/thales1020/ML-SuperTrend-MT5

**Check:**
-  Tất cả files đã up
-  README hiển thị đúng
-  LICENSE file có
-  Commit history preserved

### 5.2: Update Repository Settings

**Vào Settings của repo mới:**

1. **Description & Topics**:
   ```
   Description: Machine Learning Enhanced SuperTrend Trading Bot for MetaTrader 5
   Website: (nếu có)
   Topics: metatrader5, trading-bot, machine-learning, algorithmic-trading, 
           python, supertrend, ict-trading, forex-trading
   ```

2. **Features**:
   -  Issues
   -  Discussions (optional)
   -  Wikis (có docs/ rồi)
   -  Projects (chưa cần)

3. **Social Preview**:
   - Upload một banner/logo nếu có

---

## 📋 Bước 6: Update Documentation

### 6.1: Update README.md (đã làm rồi )

Đã có:
```markdown
[![Author](https://img.shields.io/badge/Author-thales1020-blue)](https://github.com/thales1020)

## 👨‍ Author
**Trần Trọng Hiếu**
-  Personal GitHub: [@thales1020](https://github.com/thales1020)
```

### 6.2: Update Links (nếu cần)

**Nếu bạn chọn Option A (thay thế hoàn toàn):**

```markdown
# Before:
Project Link: https://github.com/xPOURY4/ML-SuperTrend-MT5

# After:
Project Link: https://github.com/thales1020/ML-SuperTrend-MT5
```

**Tạo file để update links:**
```powershell
# Tôi sẽ tạo file này cho bạn
```

---

## 📋 Bước 7: Future Workflow

### Từ Giờ Push Như Thế Nào?

**Nếu chọn Option A (chỉ thales1020):**
```bash
git add .
git commit -m "Your message"
git push  # Sẽ tự động push lên thales1020
```

**Nếu chọn Option B (cả hai):**
```bash
git add .
git commit -m "Your message"
git push origin main           # Push lên thales1020 (chính)
git push origin-xpoury4 main   # Push lên xPOURY4 (backup)
```

---

## 📋 Bước 8: Cleanup (Optional)

### Nếu Không Cần xPOURY4 Nữa

**Archive repo cũ:**
1. Vào https://github.com/xPOURY4/ML-SuperTrend-MT5/settings
2. Scroll xuống "Danger Zone"
3. Click "Archive this repository"
4. Hoặc "Delete this repository" (cẩn thận!)

**Add redirect notice:**
Tạo file README trong xPOURY4 repo:
```markdown
# 🔀 This repository has moved!

This project is now maintained at:
https://github.com/thales1020/ML-SuperTrend-MT5

Please update your bookmarks and clones.
```

---

##  Checklist

- [ ] **Bước 1**: Tạo repo mới trên GitHub (@thales1020)
- [ ] **Bước 2**: Chọn Option A hoặc B cho remotes
- [ ] **Bước 3**: Commit attribution files
- [ ] **Bước 4**: Push lên repo mới
- [ ] **Bước 5**: Verify trên GitHub
- [ ] **Bước 6**: Update settings & description
- [ ] **Bước 7**: Test push/pull
- [ ] **Bước 8**: (Optional) Cleanup xPOURY4 repo

---

##  Recommended Option: Option A

**Tại sao?**
-  Đơn giản hơn
-  Rõ ràng ownership
-  Một repo chính thức
-  Dễ maintain

**Khi nào dùng Option B?**
- Muốn sync với xPOURY4 (collaboration)
- Backup trên nhiều repos
- Contributing back to xPOURY4

---

##  Quick Commands (Copy-Paste)

### Nếu Chưa Tạo Repo (GitHub CLI):
```bash
gh repo create ML-SuperTrend-MT5 --public --description "Machine Learning Enhanced SuperTrend Trading Bot for MetaTrader 5"
```

### Setup Remote (Option A):
```bash
git remote remove origin
git remote add origin https://github.com/thales1020/ML-SuperTrend-MT5.git
```

### Commit & Push:
```bash
git add -A
git commit -m "docs: Add professional attribution"
git push -u origin main
```

### Verify:
```bash
git remote -v
git log --oneline -5
```

---

## ❓ Troubleshooting

### Q: Authentication failed?
**A**: 
```bash
# Windows: Git Credential Manager sẽ pop up
# Hoặc tạo Personal Access Token:
# https://github.com/settings/tokens

# Set token:
git remote set-url origin https://YOUR_TOKEN@github.com/thales1020/ML-SuperTrend-MT5.git
```

### Q: Large files error?
**A**:
```bash
# Check size
ls -lh data/

# Use Git LFS for files > 50MB
git lfs install
git lfs track "*.whl"
git add .gitattributes
```

### Q: Push bị rejected?
**A**:
```bash
# Pull first
git pull origin main --allow-unrelated-histories

# Then push
git push origin main
```

---

##  Done!

Sau khi hoàn thành:

1.  Repo mới trên https://github.com/thales1020/ML-SuperTrend-MT5
2.  Full code + history
3.  Attribution đầy đủ
4.  Ready để share/promote

**Next steps:**
- Share on LinkedIn/Twitter
- Add to portfolio
- Continue development
- Get users & feedback

---

**Bạn cần tôi giúp phần nào?**

A. Tạo repo (GitHub CLI commands)
B. Setup remotes (Option A or B)
C. Handle errors
D. All of above
