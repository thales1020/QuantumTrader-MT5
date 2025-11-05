# 📋 Attribution Checklist

##  Tasks to Complete Attribution

Bạn cần điền các thông tin sau để hoàn thành attribution:

### 1. Original Project Information

Tìm và điền vào các files:

#### File: `docs/ATTRIBUTION.md`
- [ ] **Line 7**: Thay `[Original MT5-SuperTrend Repository URL Here]` bằng URL gốc
- [ ] **Line 8**: Thay `[Original Author Name/Handle]` bằng tên/username tác giả gốc
- [ ] **Line 10**: Thay `[Date when you forked]` bằng ngày fork (vd: "January 2024")

#### File: `NOTICE`
- [ ] **Line 6**: Thay `[Original Project Name]` bằng tên project gốc
- [ ] **Line 7**: Thay `[original-author]/[original-repo]` bằng GitHub path gốc
- [ ] **Line 11**: Thay `[Year]` và `[Original Author Name]` bằng thông tin gốc

### 2. Review Modified Files
- [x]  `docs/ATTRIBUTION.md` - Created with placeholders
- [x]  `NOTICE` - Created with placeholders
- [x]  `README.md` - Added attribution notice and link
- [x]  `LICENSE` - Already has your copyright (correct!)

### 3. Verify Information

Hãy kiểm tra lại project gốc và xác nhận:

```bash
# Kiểm tra git history
git log --all --oneline | tail -20

# Xem remote origin
git remote -v

# Kiểm tra fork relationship (nếu có)
gh repo view --json parent
```

### 4. What Information to Find

Bạn cần tìm từ project gốc:

1. **Repository URL**: 
   - Example: `https://github.com/original-author/mt5-supertrend`

2. **Original Author**: 
   - GitHub username hoặc real name
   - Example: `JohnDoe` hoặc `John Doe (@johndoe)`

3. **Original License**: 
   - Kiểm tra LICENSE file của project gốc
   - Nếu cũng là MIT thì OK, nếu khác phải note

4. **Fork Date**: 
   - Khi nào bạn fork/clone project gốc
   - Example: "December 2023" hoặc "Q4 2023"

5. **Original Features**: 
   - List features mà project gốc đã có
   - Để phân biệt với features bạn thêm vào

### 5. Optional but Recommended

- [ ] Contact original author (nếu có thể) để:
  - Inform họ về fork
  - Ask permission (dù MIT cho phép)
  - Share improvements back
  - Build relationship

- [ ] Add badge to README:
  ```markdown
  [![Forked from](https://img.shields.io/badge/Forked%20From-Original--Project-blue)](https://github.com/original/repo)
  ```

- [ ] Add to GitHub:
  - Set repository as "Forked from ..." in GitHub settings (nếu thực sự fork)
  - Add "Original Project" link in About section

### 6. Best Practices Met 

Bạn đã làm đúng các điều sau:

-  Keep MIT License (same as original)
-  Create ATTRIBUTION.md (transparency)
-  Create NOTICE file (legal compliance)
-  Add prominent notice in README
-  List all modifications clearly
-  Maintain copyright notices
-  Document code ownership breakdown

### 7. Legal Compliance Checklist

MIT License requires:

- [x]  Include copy of MIT license  `LICENSE` file exists
- [x]  Include copyright notice  In `LICENSE` and `NOTICE`
- [x]  State modifications  In `ATTRIBUTION.md`
- [x]  Preserve original license  Using same MIT license

##  Example: How to Fill

### Before:
```markdown
- **Repository**: [Original MT5-SuperTrend Repository URL Here]
- **Original Author**: [Original Author Name/Handle]
```

### After:
```markdown
- **Repository**: https://github.com/johndoe/mt5-supertrend-bot
- **Original Author**: John Doe (@johndoe)
- **Original License**: MIT License
- **Fork Date**: December 2023
```

##  Next Steps

1. **Find original project info** (GitHub, git history, etc.)
2. **Fill in all placeholders** in `ATTRIBUTION.md` and `NOTICE`
3. **Commit changes**:
   ```bash
   git add docs/ATTRIBUTION.md NOTICE README.md
   git commit -m "docs: Add proper attribution for original project"
   git push
   ```

4. **(Optional) Contact original author** to inform and thank them

5. **(Optional) Share improvements back** as PR if beneficial

## ❓ FAQ

**Q: Phải credit original author không?**  
A: Yes! MIT license requires it. Và về mặt đạo đức cũng nên làm.

**Q: Có thể thay đổi license không?**  
A: Bạn phải giữ MIT license cho code gốc. Code mới của bạn cũng nên dùng MIT để consistent.

**Q: Phải xin phép original author không?**  
A: MIT license không require, nhưng courtesy thì nên inform họ.

**Q: Nếu không nhớ project gốc thì sao?**  
A: Check git history, README cũ, hoặc ghi "Derived from open-source MT5 SuperTrend implementations"

**Q: Có thể claim là project của mình không?**  
A: Yes! Với 90%+ new code, đây IS your project. Chỉ cần credit phần gốc.

## 📞 Need Help?

Nếu không chắc về legal/attribution issues:

1. Open an issue để discuss
2. Consult with legal advisor (for commercial use)
3. Check GitHub's fork documentation
4. Review OSI license guide

---

**Created**: October 23, 2025  
**Purpose**: Guide for completing project attribution  
**Status**: ⏳ Pending info from you
