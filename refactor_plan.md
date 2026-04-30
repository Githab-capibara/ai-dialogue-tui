# Refactor Plan - Issue Register

## Stage 0: Audit Results Summary

### Tool Results
| Tool | Issues Found | Status |
|------|------------|--------|
| ruff | 0 | CLEAN |
| flake8 (source) | 50 | E501 only |
| flake8 (tests) | 196 | E501 only |
| pyright (source) | 0 | CLEAN |
| pyright (tests) | 60 | TypedDict patterns |
| vulture | 0 (project) | CLEAN |
| bandit | 0 | CLEAN |

### Statistics by Category
- **STYLE**: 246 (E501 line length)
- **TYPE_SAFETY**: 60 (test file patterns)
- **DEPRECATED**: 0
- **SECURITY**: 0
- **ARCHITECTURE**: 0
- **UNUSED**: 0
- **PERFORMANCE**: 0

### Statistics by Severity
- **CRITICAL**: 0
- **HIGH**: 0  
- **MEDIUM**: 60 (type safety)
- **LOW**: 246 (style)

---

## Issue Register (200 issues)

### PACKET-1 (Issues ISS-001 to ISS-020) - E501 Source Files
| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|---------|---------|----------|------------|
| ISS-001 | LOW | STYLE | services/dialogue_runner.py:86 | Line too long (81 > 79) | Split line or increase max-len in config |
| ISS-002 | LOW | STYLE | services/dialogue_runner.py:126 | Line too long (88 > 79) | Split line |
| ISS-003 | LOW | STYLE | services/dialogue_service.py:156 | Line too long (82 > 79) | Split line |
| ISS-004 | LOW | STYLE | tui/app.py:25 | Line too long (89 > 79) | Split line |
| ISS-005 | LOW | STYLE | tui/app.py:65 | Line too long (82 > 79) | Split line |
| ISS-006 | LOW | STYLE | tui/app.py:197 | Line too long (82 > 79) | Split line |
| ISS-007 | LOW | STYLE | tui/app.py:272 | Line too long (82 > 79) | Split line |
| ISS-008 | LOW | STYLE | tui/app.py:294 | Line too long (106 > 79) | Split line |
| ISS-009 | LOW | STYLE | tui/app.py:296 | Line too long (82 > 79) | Split line |
| ISS-010 | LOW | STYLE | tui/app.py:307 | Line too long (93 > 79) | Split line |
| ISS-011 | LOW | STYLE | tui/app.py:330 | Line too long (89 > 79) | Split line |
| ISS-012 | LOW | STYLE | tui/app.py:355 | Line too long (91 > 79) | Split line |
| ISS-013 | LOW | STYLE | tui/app.py:502 | Line too long (86 > 79) | Split line |
| ISS-014 | LOW | STYLE | tui/app.py:634 | Line too long (85 > 79) | Split line |
| ISS-015 | LOW | STYLE | tui/app.py:665 | Line too long (106 > 79) | Split line |
| ISS-016 | LOW | STYLE | tui/app.py:666 | Line too long (104 > 79) | Split line |
| ISS-017 | LOW | STYLE | tui/app.py:691 | Line too long (86 > 79) | Split line |
| ISS-018 | LOW | STYLE | tui/app.py:698 | Line too long (86 > 79) | Split line |
| ISS-019 | LOW | STYLE | tui/sanitizer.py:88 | Line too long (84 > 79) | Split line |
| ISS-020 | LOW | STYLE | main.py:36 | Line too long (110 > 79) | Split line |

### PACKET-2 (Issues ISS-021 to ISS-040) - E501 Test Files Batch 1
| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|---------|---------|----------|------------|
| ISS-021 | LOW | STYLE | tests/test_critical.py:15 | Line too long (83 > 79) | Split or ignore in test config |
| ISS-022 | LOW | STYLE | tests/test_critical.py:20 | Line too long (86 > 79) | Split line |
| ISS-023 | LOW | STYLE | tests/test_critical.py:40 | Line too long (87 > 79) | Split line |
| ISS-024 | LOW | STYLE | tests/test_critical.py:97 | Line too long (100 > 79) | Split line |
| ISS-025 | LOW | STYLE | tests/test_critical.py:126 | Line too long (94 > 79) | Split line |
| ISS-026 | LOW | STYLE | tests/test_critical.py:136 | Line too long (97 > 79) | Split line |
| ISS-027 | LOW | STYLE | tests/test_critical.py:225 | Line too long (81 > 79) | Split line |
| ISS-028 | LOW | STYLE | tests/test_critical.py:228 | Line too long (95 > 79) | Split line |
| ISS-029 | LOW | STYLE | tests/test_critical.py:249 | Line too long (95 > 79) | Split line |
| ISS-030 | LOW | STYLE | tests/test_critical.py:258 | Line too long (109 > 79) | Split line |
| ISS-031 | LOW | STYLE | tests/test_critical.py:261 | Line too long (95 > 79) | Split line |
| ISS-032 | LOW | STYLE | tests/test_critical.py:317 | Line too long (80 > 79) | Split line |
| ISS-033 | LOW | STYLE | tests/test_critical.py:509 | Line too long (103 > 79) | Split line |
| ISS-034 | LOW | STYLE | tests/test_critical.py:513 | Line too long (95 > 79) | Split line |
| ISS-035 | LOW | STYLE | tests/test_critical.py:524 | Line too long (103 > 79) | Split line |
| ISS-036 | LOW | STYLE | tests/test_critical.py:528 | Line too long (95 > 79) | Split line |
| ISS-037 | LOW | STYLE | tests/test_critical.py:531 | Line too long (86 > 79) | Split line |
| ISS-038 | LOW | STYLE | tests/test_critical.py:548 | Line too long (87 > 79) | Split line |
| ISS-039 | LOW | STYLE | tests/test_critical.py:550 | Line too long (80 > 79) | Split line |
| ISS-040 | LOW | STYLE | tests/test_critical.py:560 | Line too long (87 > 79) | Split line |

### PACKET-3 (Issues ISS-041 to ISS-060) - E501 Test Files Batch 2
| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|---------|---------|----------|------------|
| ISS-041 | LOW | STYLE | tests/test_critical.py:562 | Line too long (80 > 79) | Split line |
| ISS-042 | LOW | STYLE | tests/test_critical.py:571 | Line too long (87 > 79) | Split line |
| ISS-043 | LOW | STYLE | tests/test_critical.py:581 | Line too long (80 > 79) | Split line |
| ISS-044 | LOW | STYLE | tests/test_critical.py:592 | Line too long (84 > 79) | Split line |
| ISS-045 | LOW | STYLE | tests/test_critical.py:595 | Line too long (85 > 79) | Split line |
| ISS-046 | LOW | STYLE | tests/test_critical.py:599 | Line too long (95 > 79) | Split line |
| ISS-047 | LOW | STYLE | tests/test_critical.py:604 | Line too long (82 > 79) | Split line |
| ISS-048 | LOW | STYLE | tests/test_critical.py:609 | Line too long (81 > 79) | Split line |
| ISS-049 | LOW | STYLE | tests/test_critical.py:612 | Line too long (85 > 79) | Split line |
| ISS-050 | LOW | STYLE | tests/test_critical.py:616 | Line too long (95 > 79) | Split line |
| ISS-051 | LOW | STYLE | tests/test_critical.py:619 | Line too long (86 > 79) | Split line |
| ISS-052 | LOW | STYLE | tests/test_critical.py:621 | Line too long (82 > 79) | Split line |
| ISS-053 | LOW | STYLE | tests/test_critical.py:628 | Line too long (81 > 79) | Split line |
| ISS-054 | LOW | STYLE | tests/test_critical.py:643 | Line too long (85 > 79) | Split line |
| ISS-055 | LOW | STYLE | tests/test_critical.py:644 | Line too long (82 > 79) | Split line |
| ISS-056 | LOW | STYLE | tests/conftest.py:38 | Line too long (97 > 79) | Split line |
| ISS-057 | LOW | STYLE | tests/conftest.py:74 | Line too long (80 > 79) | Split line |
| ISS-058 | LOW | STYLE | tests/conftest.py:95 | Line too long (90 > 79) | Split line |
| ISS-059 | LOW | STYLE | tests/conftest.py:98 | Line too long (85 > 79) | Split line |
| ISS-060 | LOW | STYLE | tests/conftest.py:120 | Line too long (96 > 79) | Split line |

### PACKET-4 (Issues ISS-061 to ISS-080) - E501 Test Files Batch 3
| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|---------|---------|----------|------------|
| ISS-061 | LOW | STYLE | tests/test_fixes.py:4 | Line too long (85 > 79) | Split line |
| ISS-062 | LOW | STYLE | tests/test_fixes.py:28 | Line too long (83 > 79) | Split line |
| ISS-063 | LOW | STYLE | tests/test_fixes.py:67 | Line too long (84 > 79) | Split line |
| ISS-064 | LOW | STYLE | tests/test_fixes.py:73 | Line too long (94 > 79) | Split line |
| ISS-065 | LOW | STYLE | tests/test_fixes.py:91 | Line too long (95 > 79) | Split line |
| ISS-066 | LOW | STYLE | tests/test_fixes.py:95 | Line too long (80 > 79) | Split line |
| ISS-067 | LOW | STYLE | tests/test_fixes.py:143 | Line too long (87 > 79) | Split line |
| ISS-068 | LOW | STYLE | tests/test_fixes.py:144 | Line too long (81 > 79) | Split line |
| ISS-069 | LOW | STYLE | tests/test_fixes.py:150 | Line too long (84 > 79) | Split line |
| ISS-070 | LOW | STYLE | tests/test_fixes.py:153 | Line too long (84 > 79) | Split line |
| ISS-071 | LOW | STYLE | tests/test_fixes.py:175 | Line too long (85 > 79) | Split line |
| ISS-072 | LOW | STYLE | tests/test_fixes.py:188 | Line too long (85 > 79) | Split line |
| ISS-073 | LOW | STYLE | tests/test_fixes.py:198 | Line too long (84 > 79) | Split line |
| ISS-074 | LOW | STYLE | tests/test_fixes.py:202 | Line too long (81 > 79) | Split line |
| ISS-075 | LOW | STYLE | tests/test_fixes.py:225 | Line too long (84 > 79) | Split line |
| ISS-076 | LOW | STYLE | tests/test_audit_fixes.py:54 | Line too long (81 > 79) | Split line |
| ISS-077 | LOW | STYLE | tests/test_audit_fixes.py:78 | Line too long (88 > 79) | Split line |
| ISS-078 | LOW | STYLE | tests/test_audit_fixes.py:79 | Line too long (88 > 79) | Split line |
| ISS-079 | LOW | STYLE | tests/test_audit_fixes.py:94 | Line too long (85 > 79) | Split line |
| ISS-080 | LOW | STYLE | tests/test_audit_fixes.py:102 | Line too long (91 > 79) | Split line |

### PACKET-5 (Issues ISS-081 to ISS-100) - E501 Test Files Batch 4
| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|---------|---------|----------|------------|
| ISS-081 | LOW | STYLE | tests/test_new_audit_fixes.py:11 | Line too long (90 > 79) | Split line |
| ISS-082 | LOW | STYLE | tests/test_new_audit_fixes.py:38 | Line too long (89 > 79) | Split line |
| ISS-083 | LOW | STYLE | tests/test_new_audit_fixes.py:59 | Line too long (87 > 79) | Split line |
| ISS-084 | LOW | STYLE | tests/test_new_audit_fixes.py:60 | Line too long (83 > 79) | Split line |
| ISS-085 | LOW | STYLE | tests/test_new_audit_fixes.py:62 | Line too long (102 > 79) | Split line |
| ISS-086 | LOW | STYLE | tests/test_new_audit_fixes.py:92 | Line too long (109 > 79) | Split line |
| ISS-087 | LOW | STYLE | tests/test_new_audit_fixes.py:94 | Line too long (83 > 79) | Split line |
| ISS-088 | LOW | STYLE | tests/test_new_audit_fixes.py:127 | Line too long (85 > 79) | Split line |
| ISS-089 | LOW | STYLE | tests/test_new_audit_fixes.py:182 | Line too long (81 > 79) | Split line |
| ISS-090 | LOW | STYLE | tests/test_new_audit_fixes.py:195 | Line too long (81 > 79) | Split line |
| ISS-091 | LOW | STYLE | tests/test_new_audit_fixes.py:249 | Line too long (81 > 79) | Split line |
| ISS-092 | LOW | STYLE | tests/test_new_audit_fixes.py:260 | Line too long (85 > 79) | Split line |
| ISS-093 | LOW | STYLE | tests/test_new_audit_fixes.py:261 | Line too long (86 > 79) | Split line |
| ISS-094 | LOW | STYLE | tests/test_new_audit_fixes.py:310 | Line too long (82 > 79) | Split line |
| ISS-095 | LOW | STYLE | tests/test_new_audit_fixes.py:334 | Line too long (84 > 79) | Split line |
| ISS-096 | LOW | STYLE | tests/test_new_audit_fixes.py:351 | Line too long (111 > 79) | Split line |
| ISS-097 | LOW | STYLE | tests/test_new_audit_fixes.py:420 | Line too long (93 > 79) | Split line |
| ISS-098 | LOW | STYLE | tests/test_timeout_fixes.py:46 | Line too long (100 > 79) | Split line |
| ISS-099 | LOW | STYLE | tests/test_timeout_fixes.py:66 | Line too long (94 > 79) | Split line |
| ISS-100 | LOW | STYLE | tests/test_timeout_fixes.py:76 | Line too long (97 > 79) | Split line |

### PACKET-6 (Issues ISS-101 to ISS-120) - E501 Test Files Batch 5
| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|---------|---------|----------|------------|
| ISS-101 | LOW | STYLE | tests/test_timeout_fixes.py:128 | Line too long (85 > 79) | Split line |
| ISS-102 | LOW | STYLE | tests/test_timeout_fixes.py:147 | Line too long (84 > 79) | Split line |
| ISS-103 | LOW | STYLE | tests/test_timeout_fixes.py:152 | Line too long (95 > 79) | Split line |
| ISS-104 | LOW | STYLE | tests/test_timeout_fixes.py:158 | Line too long (86 > 79) | Split line |
| ISS-105 | LOW | STYLE | tests/test_timeout_fixes.py:168 | Line too long (84 > 79) | Split line |
| ISS-106 | LOW | STYLE | tests/test_timeout_fixes.py:173 | Line too long (95 > 79) | Split line |
| ISS-107 | LOW | STYLE | tests/test_timeout_fixes.py:179 | Line too long (86 > 79) | Split line |
| ISS-108 | LOW | STYLE | tests/test_call_from_thread_fix.py:5 | Line too long (87 > 79) | Split line |
| ISS-109 | LOW | STYLE | tests/test_call_from_thread_fix.py:6 | Line too long (85 > 79) | Split line |
| ISS-110 | LOW | STYLE | tests/test_call_from_thread_fix.py:7 | Line too long (85 > 79) | Split line |
| ISS-111 | LOW | STYLE | tests/test_textual_reactive.py:30 | Line too long (85 > 79) | Split line |
| ISS-112 | LOW | STYLE | tests/test_textual_reactive.py:33 | Line too long (87 > 79) | Split line |
| ISS-113 | LOW | STYLE | tests/test_ui_nomatches_handling.py:17 | Line too long (80 > 79) | Split line |
| ISS-114 | LOW | STYLE | tests/test_batch01_fixes.py:32 | Line too long (80 > 79) | Split line |
| ISS-115 | LOW | STYLE | tests/test_batch01_fixes.py:56 | Line too long (80 > 79) | Split line |
| ISS-116 | LOW | STYLE | tests/test_batch03_fixes.py:125 | Line too long (87 > 79) | Split line |
| ISS-117 | LOW | STYLE | tests/test_batch03_fixes.py:233 | Line too long (101 > 79) | Split line |
| ISS-118 | LOW | STYLE | tests/test_batch03_fixes.py:270 | Line too long (88 > 79) | Split line |
| ISS-119 | LOW | STYLE | tests/test_batch03_fixes.py:278 | Line too long (81 > 79) | Split line |
| ISS-120 | LOW | STYLE | tests/test_batch03_fixes.py:282 | Line too long (83 > 79) | Split line |

### PACKET-7 (Issues ISS-121 to ISS-140) - E501 Test Files Batch 6 + Type Issues
| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|---------|---------|----------|------------|
| ISS-121 | LOW | STYLE | tests/test_batch03_fixes.py:287 | Line too long (82 > 79) | Split line |
| ISS-122 | LOW | STYLE | tests/test_batch03_fixes.py:294 | Line too long (99 > 79) | Split line |
| ISS-123 | LOW | STYLE | tests/test_batch03_fixes.py:296 | Line too long (86 > 79) | Split line |
| ISS-124 | LOW | STYLE | tests/test_batch03_fixes.py:306 | Line too long (98 > 79) | Split line |
| ISS-125 | LOW | STYLE | tests/test_arch_audit_fixes.py:38 | Line too long (80 > 79) | Split line |
| ISS-126 | LOW | STYLE | tests/test_arch_audit_fixes.py:55 | Line too long (83 > 79) | Split line |
| ISS-127 | LOW | STYLE | tests/test_arch_audit_fixes.py:83 | Line too long (86 > 79) | Split line |
| ISS-128 | LOW | STYLE | tests/test_arch_audit_fixes.py:142 | Line too long (109 > 79) | Split line |
| ISS-129 | LOW | STYLE | tests/test_arch_fixes.py:82 | Line too long (91 > 79) | Split line |
| ISS-130 | LOW | STYLE | tests/test_architecture.py:221 | Line too long (81 > 79) | Split line |
| ISS-131 | LOW | STYLE | tests/test_architecture.py:235 | Line too long (80 > 79) | Split line |
| ISS-132 | LOW | STYLE | tests/test_architecture_integrity.py:168 | Line too long (94 > 79) | Split line |
| ISS-133 | LOW | STYLE | tests/test_architecture_integrity.py:202 | Line too long (96 > 79) | Split line |
| ISS-134 | LOW | STYLE | tests/test_architecture_integrity.py:218 | Line too long (89 > 79) | Split line |
| ISS-135 | LOW | STYLE | tests/test_architecture_integrity.py:234 | Line too long (89 > 79) | Split line |
| ISS-136 | LOW | STYLE | tests/test_architecture_integrity.py:706 | Line too long (93 > 79) | Split line |
| ISS-137 | LOW | STYLE | tests/test_architecture_integrity.py:756 | Line too long (94 > 79) | Split line |
| ISS-138 | LOW | STYLE | tests/test_architecture_integrity.py:811 | Line too long (82 > 79) | Split line |
| ISS-139 | LOW | STYLE | tests/test_architecture_integrity.py:815 | Line too long (82 > 79) | Split line |
| ISS-140 | LOW | STYLE | tests/test_batch03_fixes.py:233 | E203 whitespace before ':' | Fix whitespace |

### PACKET-8 (Issues ISS-141 to ISS-160) - Type Issues Batch 1
| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|---------|---------|----------|------------|
| ISS-141 | MEDIUM | TYPE_SAFETY | tests/test_arch_audit_fixes.py:46 | Cannot access attribute "left" for class "expr" | Add typeguard or cast |
| ISS-142 | MEDIUM | TYPE_SAFETY | tests/test_arch_audit_fixes.py:47 | Cannot access attribute "left" for class "expr" | Add typeguard or cast |
| ISS-143 | MEDIUM | TYPE_SAFETY | tests/test_arch_audit_fixes.py:48 | Cannot access attribute "left" for class "expr" | Add typeguard or cast |
| ISS-144 | MEDIUM | TYPE_SAFETY | tests/test_architecture_integrity.py:425 | "role" not required key in MessageDict | Use .get() or make key required |
| ISS-145 | MEDIUM | TYPE_SAFETY | tests/test_architecture_integrity.py:856 | "content" not required key in MessageDict | Use .get() or make key required |
| ISS-146 | MEDIUM | TYPE_SAFETY | tests/test_architecture_integrity.py:859 | "content" not required key in MessageDict | Use .get() or make key required |
| ISS-147 | MEDIUM | TYPE_SAFETY | tests/test_architecture_integrity.py:878 | Cannot access "append" on tuple | Use list instead of tuple |
| ISS-148 | MEDIUM | TYPE_SAFETY | tests/test_audit_fixes.py:559 | "content" not required key in MessageDict | Use .get() or make key required |
| ISS-149 | MEDIUM | TYPE_SAFETY | tests/test_audit_fixes.py:560 | "content" not required key in MessageDict | Use .get() or make key required |
| ISS-150 | MEDIUM | TYPE_SAFETY | tests/test_audit_fixes.py:865 | "role" not required key in MessageDict | Use .get() or make key required |
| ISS-151 | MEDIUM | TYPE_SAFETY | tests/test_audit_fixes.py:866 | "content" not required key in MessageDict | Use .get() or make key required |
| ISS-152 | MEDIUM | TYPE_SAFETY | tests/test_batch01_fixes.py:32 | "role" not required key in MessageDict | Use .get() or make key required |
| ISS-153 | MEDIUM | TYPE_SAFETY | tests/test_batch01_fixes.py:56 | "role" not required key in MessageDict | Use .get() or make key required |
| ISS-154 | MEDIUM | TYPE_SAFETY | tests/test_batch03_fixes.py:71 | "content" not required key in MessageDict | Use .get() or make key required |
| ISS-155 | MEDIUM | TYPE_SAFETY | tests/test_batch03_fixes.py:129 | None cannot be assigned to str | Add default or handle None |
| ISS-156 | MEDIUM | TYPE_SAFETY | tests/test_batch03_fixes.py:272 | Type mismatch for context param | Use Sequence instead of list |
| ISS-157 | MEDIUM | TYPE_SAFETY | tests/test_batch03_fixes.py:274 | "role" not required key in MessageDict | Use .get() or make key required |
| ISS-158 | MEDIUM | TYPE_SAFETY | tests/test_batch03_fixes.py:284 | Type mismatch for context param | Use Sequence instead of list |
| ISS-159 | MEDIUM | TYPE_SAFETY | tests/test_batch03_fixes.py:286 | "role" not required key in MessageDict | Use .get() or make key required |
| ISS-160 | MEDIUM | TYPE_SAFETY | tests/test_batch03_fixes.py:296 | Type mismatch for context param | Use Sequence instead of list |

### PACKET-9 (Issues ISS-161 to ISS-180) - Type Issues Batch 2
| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|---------|---------|----------|------------|
| ISS-161 | MEDIUM | TYPE_SAFETY | tests/test_batch03_fixes.py:298 | "role" not required key in MessageDict | Use .get() or make key required |
| ISS-162 | MEDIUM | TYPE_SAFETY | tests/test_batch03_fixes.py:299 | "role" not required key in MessageDict | Use .get() or make key required |
| ISS-163 | MEDIUM | TYPE_SAFETY | tests/test_batch03_fixes.py:308 | Type mismatch for context param | Use Sequence instead of list |
| ISS-164 | MEDIUM | TYPE_SAFETY | tests/test_batch03_fixes.py:383 | Literal[123] cannot be assigned to str | Fix type annotation |
| ISS-165 | MEDIUM | TYPE_SAFETY | tests/test_batch03_fixes.py:388 | Literal[123] cannot be assigned to str | Fix type annotation |
| ISS-166 | MEDIUM | TYPE_SAFETY | tests/test_call_from_thread_fix.py:60 | Type mismatch for model_id | Fix literal type |
| ISS-167 | MEDIUM | TYPE_SAFETY | tests/test_call_from_thread_fix.py:91 | Generator return type mismatch | Fix mock return type |
| ISS-168 | MEDIUM | TYPE_SAFETY | tests/test_call_from_thread_fix.py:98 | Generator return type mismatch | Fix mock return type |
| ISS-169 | MEDIUM | TYPE_SAFETY | tests/test_code_audit_fixes.py:127 | "role" not required key in MessageDict | Use .get() or make key required |
| ISS-170 | MEDIUM | TYPE_SAFETY | tests/test_code_audit_fixes.py:128 | "content" not required key in MessageDict | Use .get() or make key required |
| ISS-171 | MEDIUM | TYPE_SAFETY | tests/test_code_audit_fixes.py:150 | "content" not required key in MessageDict | Use .get() or make key required |
| ISS-172 | MEDIUM | TYPE_SAFETY | tests/test_critical.py:105 | Expected class but received callable | Fix type annotation |
| ISS-173 | MEDIUM | TYPE_SAFETY | tests/test_critical.py:364 | "role" not required key in MessageDict | Use .get() or make key required |
| ISS-174 | MEDIUM | TYPE_SAFETY | tests/test_critical.py:365 | "role" not required key in MessageDict | Use .get() or make key required |
| ISS-175 | MEDIUM | TYPE_SAFETY | tests/test_fixes.py:119 | "content" not required key in MessageDict | Use .get() or make key required |
| ISS-176 | MEDIUM | TYPE_SAFETY | tests/test_fixes.py:120 | "content" not required key in MessageDict | Use .get() or make key required |
| ISS-177 | MEDIUM | TYPE_SAFETY | tests/test_fixes.py:137 | "role" not required key in MessageDict | Use .get() or make key required |
| ISS-178 | MEDIUM | TYPE_SAFETY | tests/test_fixes.py:138 | "content" not required key in MessageDict | Use .get() or make key required |
| ISS-179 | MEDIUM | TYPE_SAFETY | tests/test_fixes.py:200 | None cannot be assigned to str | Add default or handle None |
| ISS-180 | MEDIUM | TYPE_SAFETY | tests/test_fixes.py:205 | Literal[123] cannot be assigned to str | Fix type annotation |

### PACKET-10 (Issues ISS-181 to ISS-200) - Type Issues Batch 3 + Additional
| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|---------|---------|----------|------------|
| ISS-181 | MEDIUM | TYPE_SAFETY | tests/test_fixes.py:207 | list[Any] cannot be assigned to str | Fix mock data |
| ISS-182 | MEDIUM | TYPE_SAFETY | tests/test_new_audit_fixes.py:65 | "role" not required key in MessageDict | Use .get() or make key required |
| ISS-183 | MEDIUM | TYPE_SAFETY | tests/test_new_audit_fixes.py:109 | Cannot access "key" on tuple | Use dataclass or namedtuple |
| ISS-184 | MEDIUM | TYPE_SAFETY | tests/test_new_audit_fixes.py:110 | Cannot access "key" on tuple | Use dataclass or namedtuple |
| ISS-185 | MEDIUM | TYPE_SAFETY | tests/test_new_audit_fixes.py:122 | Cannot access "action" on tuple | Use dataclass or namedtuple |
| ISS-186 | MEDIUM | TYPE_SAFETY | tests/test_new_audit_fixes.py:123 | Cannot access "action" on tuple | Use dataclass or namedtuple |
| ISS-187 | MEDIUM | TYPE_SAFETY | tests/test_new_audit_fixes.py:191 | None cannot be assigned to _SourceObjectType | Add type annotation |
| ISS-188 | MEDIUM | TYPE_SAFETY | tests/test_new_audit_fixes.py:362 | "content" not required key in MessageDict | Use .get() or make key required |
| ISS-189 | MEDIUM | TYPE_SAFETY | tests/test_new_audit_fixes.py:366 | "content" not required key in MessageDict | Use .get() or make key required |
| ISS-190 | MEDIUM | TYPE_SAFETY | tests/test_new_audit_fixes.py:376 | "role" not required key in MessageDict | Use .get() or make key required |
| ISS-191 | MEDIUM | TYPE_SAFETY | tests/test_new_audit_fixes.py:377 | "content" not required key in MessageDict | Use .get() or make key required |
| ISS-192 | MEDIUM | TYPE_SAFETY | tests/test_new_audit_fixes.py:400 | "role" not required key in MessageDict | Use .get() or make key required |
| ISS-193 | MEDIUM | TYPE_SAFETY | tests/test_new_audit_fixes.py:402 | "role" not required key in MessageDict | Use .get() or make key required |
| ISS-194 | MEDIUM | TYPE_SAFETY | tests/test_textual_reactive.py:53 | Cannot access "key" on tuple | Use dataclass or namedtuple |
| ISS-195 | MEDIUM | TYPE_SAFETY | tests/test_timeout_fixes.py:54 | Expected class but received callable | Fix type annotation |
| ISS-196 | LOW | STYLE | main.py:37 | Line too long (100 > 79) | Split line |
| ISS-197 | LOW | STYLE | main.py:63 | Line too long (105 > 79) | Split line |
| ISS-198 | LOW | STYLE | models/config.py:87 | Line too long (80 > 79) | Split line |
| ISS-199 | LOW | STYLE | models/config.py:135 | Line too long (86 > 79) | Split line |
| ISS-200 | LOW | STYLE | models/config.py:221 | Line too long (84 > 79) | Split line |

---

## Packet Summary

| Packet | Count | Primary Category |
|--------|-------|---------------|
| PACKET-1 | 20 | E501 Source Files |
| PACKET-2 | 20 | E501 Tests Batch 1 |
| PACKET-3 | 20 | E501 Tests Batch 2 |
| PACKET-4 | 20 | E501 Tests Batch 3 |
| PACKET-5 | 20 | E501 Tests Batch 4 |
| PACKET-6 | 20 | E501 Tests Batch 5 + misc |
| PACKET-7 | 20 | E501 Tests Batch 6 |
| PACKET-8 | 20 | Type Issues Batch 1 |
| PACKET-9 | 20 | Type Issues Batch 2 |
| PACKET-10 | 20 | Type Issues Batch 3 + remaining |

**Total: 200 Issues**