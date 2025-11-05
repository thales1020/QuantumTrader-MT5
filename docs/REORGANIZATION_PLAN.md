# Documentation Reorganization Plan

## Current State
- **80+ files** in single `docs/` folder
- Hard to find specific documentation
- No clear structure or navigation

## Proposed Structure

```
docs/
├── README.md                          # Main index (keep)
├── QUICKSTART.md                      # Quick start guide (keep)
├── CHANGELOG.md                       # Version history (keep)
├── CONTRIBUTING.md                    # How to contribute (keep)
├── FAQ.md                            # Common questions (keep)
│
├── 01-getting-started/               # NEW: User onboarding
│   ├── README.md
│   ├── installation.md
│   ├── quickstart.md
│   ├── video-tutorials.md
│   └── migration-guide.md
│
├── 02-user-guides/                   # NEW: How to use features
│   ├── README.md
│   ├── crypto-trading-guide.md
│   ├── customization-guide.md
│   ├── vps-deployment-guide.md
│   ├── mt5-vps-deployment.md
│   └── mt5-vps-info-update.md
│
├── 03-development/                   # NEW: Developer docs
│   ├── README.md
│   ├── project-scope.md
│   ├── technology-stack.md
│   ├── plugin-system.md
│   ├── plugin-quick-start.md
│   ├── strategy-templates.md
│   └── supabase-integration-guide.md
│
├── 04-testing/                       # NEW: Testing documentation
│   ├── README.md
│   ├── testing-index.md
│   ├── test-plan.md
│   ├── test-requirements.md
│   ├── api-testing-guide.md
│   ├── api-quick-reference.md
│   ├── for-tester-read-first.md
│   ├── tester-prompt.md
│   ├── quick-tester-prompt.md
│   ├── test-execution-reports/
│   │   ├── tester-1-report.md
│   │   ├── tester-2-report.md
│   │   └── tester-3-report.md
│   └── bug-fixes/
│       ├── bug-fixes-summary.md
│       └── bug-fixes-tester3.md
│
├── 05-architecture/                  # NEW: System design
│   ├── README.md
│   ├── uml/
│   │   ├── README.md
│   │   ├── uml-documentation-summary.md
│   │   ├── uml-usecase-diagram.md
│   │   ├── uml-process-view.md
│   │   ├── diagrams/                (from uml_diagrams/)
│   │   ├── view-uml-diagrams.md
│   │   └── export-diagrams-guide.md
│   ├── paper-trading-system.md
│   ├── backtest-architecture.md
│   ├── plugin-system.md
│   └── supabase-erd.md
│
├── 06-technical-specs/               # NEW: Technical details
│   ├── README.md
│   ├── performance.md
│   ├── optimization-summary.md
│   ├── backtest-memory-leak-fix.md
│   ├── backtest-reliability-analysis.md
│   └── breakeven-sl-feature.md
│
├── 07-project-history/               # NEW: Archive
│   ├── README.md
│   ├── phases/
│   │   ├── phase-1/
│   │   │   ├── phase1-progress.md
│   │   │   ├── phase-1-deployment-complete.md
│   │   │   ├── phase-1.4-complete.md
│   │   │   ├── phase-1.4-final-summary.md
│   │   │   ├── phase-1.4-review-index.md
│   │   │   ├── phase-1.4-validation-results.md
│   │   │   ├── phase-1.4-visual-comparison.md
│   │   │   ├── phase-1.5-complete.md
│   │   │   ├── phase-1.5-final-summary.md
│   │   │   ├── phase-1.5-plan.md
│   │   │   ├── phase-1.5-review-index.md
│   │   │   ├── phase-1.5-validation-results.md
│   │   │   └── phase-1.5-visual-summary.md
│   │   ├── phase-2/
│   │   │   ├── phase-2-checklist.md
│   │   │   └── phase-2-complete.md
│   │   ├── phase-3/
│   │   │   └── phase-3-complete.md
│   │   └── phase-4/
│   │       ├── phase-4-plan.md
│   │       └── phase-4-complete.md
│   ├── refactoring/
│   │   ├── ict-bot-refactoring.md
│   │   ├── dual-orders-implementation.md
│   │   ├── dual-orders-changes.md
│   │   ├── import-changes-summary.md
│   │   └── code-quality/
│   │       ├── code-quality-improvement-plan.md
│   │       └── code-quality-fix-1-paper-trading.md
│   ├── cleanup/
│   │   ├── cleanup-analysis.md
│   │   ├── cleanup-results.md
│   │   ├── file-organization-analysis.md
│   │   └── backtest-validation-results.md
│   ├── rebrand/
│   │   ├── rebrand-complete.md
│   │   ├── rebrand-final-steps.md
│   │   ├── rename-project-guide.md
│   │   └── setup-new-github-repo.md
│   └── attribution/
│       ├── attribution.md
│       ├── attribution-summary.md
│       ├── attribution-complete.md
│       ├── attribution-final.md
│       ├── attribution-checklist.md
│       ├── attribution-best-practices.md
│       └── author-info.md
│
├── 08-project-management/            # NEW: PM docs
│   ├── README.md
│   ├── project-review.md
│   ├── project-evaluation.md
│   ├── post-launch-checklist.md
│   └── break-time.md
│
├── 09-reference/                     # NEW: Bot-specific guides
│   ├── README.md
│   ├── ict-readme.md
│   └── examples/                    (keep existing)
│
└── archive/                          # NEW: Deprecated/old docs
    ├── find-png-files.md
    └── list_diagrams.ps1

```

## File Mapping

### Keep in Root
- README.md
- QUICKSTART.md → Link to 01-getting-started/
- CHANGELOG.md
- CONTRIBUTING.md
- FAQ.md

### Move to 01-getting-started/
- VIDEO_TUTORIALS.md → video-tutorials.md
- MIGRATION_GUIDE.md → migration-guide.md

### Move to 02-user-guides/
- CRYPTO_TRADING_GUIDE.md → crypto-trading-guide.md
- CUSTOMIZATION_GUIDE.md → customization-guide.md
- VPS_DEPLOYMENT_GUIDE.md → vps-deployment-guide.md
- MT5_VPS_DEPLOYMENT.md → mt5-vps-deployment.md
- MT5_VPS_INFO_UPDATE.md → mt5-vps-info-update.md

### Move to 03-development/
- PROJECT_SCOPE.md → project-scope.md
- TECHNOLOGY_STACK.md → technology-stack.md
- PLUGIN_SYSTEM.md → plugin-system.md
- PLUGIN_QUICK_START.md → plugin-quick-start.md
- STRATEGY_TEMPLATES.md → strategy-templates.md
- SUPABASE_INTEGRATION_GUIDE.md → supabase-integration-guide.md

### Move to 04-testing/
- TESTING_INDEX.md → testing-index.md
- TEST_PLAN.md → test-plan.md
- TEST_REQUIREMENTS.md → test-requirements.md
- API_TESTING_GUIDE.md → api-testing-guide.md
- API_QUICK_REFERENCE.md → api-quick-reference.md
- FOR_TESTER_READ_FIRST.md → for-tester-read-first.md
- TESTER_PROMPT.md → tester-prompt.md
- QUICK_TESTER_PROMPT.md → quick-tester-prompt.md
- BUG_FIXES_SUMMARY.md → bug-fixes/bug-fixes-summary.md
- BUG_FIXES_TESTER3.md → bug-fixes/bug-fixes-tester3.md

### Move to 05-architecture/
- UML_DOCUMENTATION_SUMMARY.md → uml/uml-documentation-summary.md
- UML_USECASE_DIAGRAM.md → uml/uml-usecase-diagram.md
- UML_PROCESS_VIEW.md → uml/uml-process-view.md
- VIEW_UML_DIAGRAMS.md → uml/view-uml-diagrams.md
- EXPORT_DIAGRAMS_GUIDE.md → uml/export-diagrams-guide.md
- uml_diagrams/ → uml/diagrams/
- PAPER_TRADING_SYSTEM.md → paper-trading-system.md
- NEW_BACKTEST_ARCHITECTURE.md → backtest-architecture.md
- SUPABASE_ERD.md → supabase-erd.md

### Move to 06-technical-specs/
- PERFORMANCE.md → performance.md
- OPTIMIZATION_SUMMARY.md → optimization-summary.md
- BACKTEST_MEMORY_LEAK_FIX.md → backtest-memory-leak-fix.md
- BACKTEST_RELIABILITY_ANALYSIS.md → backtest-reliability-analysis.md
- BREAKEVEN_SL_FEATURE.md → breakeven-sl-feature.md

### Move to 07-project-history/
All PHASE_* files → phases/phase-X/
All ATTRIBUTION_* files → attribution/
All refactoring docs → refactoring/
All cleanup docs → cleanup/
All rebrand docs → rebrand/

### Move to 08-project-management/
- PROJECT_REVIEW.md → project-review.md
- PROJECT_EVALUATION.md → project-evaluation.md
- POST_LAUNCH_CHECKLIST.md → post-launch-checklist.md
- BREAK_TIME.md → break-time.md

### Move to 09-reference/
- ICT_README.md → ict-readme.md
- examples/ (keep)

### Move to archive/
- FIND_PNG_FILES.md
- list_diagrams.ps1

## Benefits

1. **Clear Navigation**: Numbered folders show reading order
2. **Easy Discovery**: Files grouped by purpose
3. **Scalable**: Can add more docs to each category
4. **Professional**: Industry-standard structure
5. **Maintainable**: Clear where new docs belong

## Implementation Steps

1. Create folder structure
2. Move files with git mv (preserve history)
3. Update internal links
4. Create README.md in each folder
5. Update root README.md with new navigation
6. Test all links

## Estimated Time
- Structure creation: 5 min
- Moving files: 10 min
- Creating READMEs: 15 min
- Updating links: 20 min
- Testing: 10 min
**Total: ~60 minutes**
