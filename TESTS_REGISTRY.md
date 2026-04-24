# Test Suite Registry

## Overview
Total test files: 20 (after cleanup)

## Test Files Inventory

| File | Purpose | Coverage |
|------|---------|----------|
| `conftest.py` | Shared pytest fixtures | Helpers |
| `__init__.py` | Tests package init | - |
| `test_architecture.py` | Layer separation, DI | Architecture |
| `test_architecture_integrity.py` | SOLID, ProviderError | Architecture |
| `test_architecture_patterns.py` | Separation of concerns | Architecture |
| `test_architecture_refactor.py` | YAGNI, KISS fixes | Architecture |
| `test_arch_audit_fixes.py` | DRY, SRP fixes | Architecture |
| `test_arch_fixes.py` | Module boundaries | Architecture |
| `test_audit_fixes.py` | Exception handling | Code quality |
| `test_batch01_fixes.py` | Issues 0001-0020 | Verification |
| `test_batch03_fixes.py` | Issues 0041-0048 | Verification |
| `test_call_from_thread_fix.py` | call_from_thread fix | UI |
| `test_code_audit_fixes.py` | Code audit fixes | Verification |
| `test_code_audit_fixes_verification.py` | Fix verification | Verification |
| `test_critical.py` | Critical fixes | Integration |
| `test_fixes.py` | General fixes | Verification |
| `test_new_audit_fixes.py` | New audit fixes | Verification |
| `test_audit_fixes_verification.py` | Audit verification | Verification |
| `test_textual_reactive.py` | Textual reactive | UI |
| `test_timeout_fixes.py` | Timeout handling | Network |
| `test_ui_nomatches_handling.py` | NoMatches handling | UI |

## Last Updated
2026-04-24