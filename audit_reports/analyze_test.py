#!/usr/bin/env python3
"""
Static analysis of a test file to detect issues.
"""

import ast
import sys
import os


def analyze_test_file(filepath):
    """Analyze a test file and return a list of issues."""
    issues = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        issues.append(f"Error reading file: {e}")
        return issues

    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        issues.append(f"Syntax error: {e}")
        return issues

    # Find all test functions
    test_functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            test_functions.append(node)

    if not test_functions:
        issues.append("No test functions found")
        return issues

    for func in test_functions:
        # Check for empty test function (no statements or only pass/docstring)
        if len(func.body) == 0:
            issues.append(f"Empty test function: {func.name}")
            continue

        # Check if the function body only contains a pass statement or docstring
        if len(func.body) == 1:
            if isinstance(func.body[0], ast.Pass):
                issues.append(f"Test function with only pass: {func.name}")
                continue
            if isinstance(func.body[0], ast.Expr) and isinstance(func.body[0].value, ast.Str):
                issues.append(f"Test function with only docstring: {func.name}")
                continue

        # Check for assertions
        has_assert = False
        for node in ast.walk(func):
            if isinstance(node, ast.Assert):
                has_assert = True
                break

        if not has_assert:
            # Check for pytest.raises or other assertion-like constructs
            # For simplicity, we'll just note no assert found
            issues.append(f"Test function with no assertions: {func.name}")

        # Check for constant pass/fail (hard to do statically, skip for now)

    # Check for duplicate test function names
    func_names = [f.name for f in test_functions]
    if len(func_names) != len(set(func_names)):
        from collections import Counter

        duplicates = [name for name, count in Counter(func_names).items() if count > 1]
        issues.append(f"Duplicate test function names: {', '.join(duplicates)}")

    return issues


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_test.py <test_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)

    issues = analyze_test_file(filepath)
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("No issues found")
