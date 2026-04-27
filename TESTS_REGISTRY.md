# Test Registry

This file documents all test files and their purposes.

| File | Lines | Purpose |
|------|-------|---------|
| test_audit_fixes.py | 886 | Verifies all code audit fixes (exception handling, XSS protection, context management) |
| test_architecture.py | 499 | Architecture layer separation and dependency injection |
| test_architecture_integrity.py | 942 | Comprehensive architecture integrity checks (42 tests) |
| test_architecture_patterns.py | 201 | Architecture principles verification |
| test_arch_audit_fixes.py | 207 | Architectural fixes verification (DRY, KISS, YAGNI, SRP) |
| test_arch_fixes.py | 129 | Architecture changes verification |
| test_audit_fixes.py | 886 | Core audit fixes - exceptions, sanitization, provider errors |
| test_batch01_fixes.py | 246 | Batch 01 fixes (issues 0001-0020) |
| test_batch03_fixes.py | 388 | Batch 03 fixes |
| test_call_from_thread_fix.py | 399 | Thread call fix verification |
| test_code_audit_fixes.py | 317 | Code audit fixes + verification tests merged |
| test_critical.py | 653 | Critical issues from audit report |
| test_fixes.py | 229 | General code fixes verification |
| test_new_audit_fixes.py | 433 | New audit fixes (trim, lock, cleanup) |
| test_textual_reactive.py | 62 | Textual reactive attributes |
| test_timeout_fixes.py | 184 | Timeout fixes verification |
| test_ui_nomatches_handling.py | 140 | UI error handling |
| test_architecture_refactor.py | 172 | Architectural refactoring verification |

**Total: 18 test files, 6218 lines, 371 tests**

Last updated: 2026-04-27

## Audit Results (2026-04-27)

- ✅ All 371 tests passing
- ✅ No duplicate tests found
- ✅ No empty tests (all have assertions)
- ✅ No orphaned tests (all import project modules)
- ✅ Ruff formatting applied
- ✅ Import sorting fixed
- ⚠️ 42 remaining lint warnings (mostly type annotations - see pyproject.toml exclusions)