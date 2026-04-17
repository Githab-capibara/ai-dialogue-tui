#!/usr/bin/env python3
"""
Run analysis on all test files and collect results.
"""

import subprocess


def run_analysis_on_file(test_file):
    """Run the analysis script on a single test file."""
    result = subprocess.run(
        ["python3", "audit_reports/analyze_test.py", test_file],
        capture_output=True,
        text=True,
        cwd="/home/d/ai-dialogue-tui",
    )
    return result.stdout, result.stderr, result.returncode


def main():
    # Read the list of test files
    with open("audit_reports/test_files.txt", "r") as f:
        test_files = [line.strip() for line in f if line.strip()]

    all_issues = {}

    for test_file in test_files:
        print(f"Analyzing {test_file}...")
        stdout, stderr, returncode = run_analysis_on_file(test_file)
        if returncode != 0:
            print(f"Error analyzing {test_file}: {stderr}")
            all_issues[test_file] = [f"Analysis error: {stderr}"]
        else:
            issues = []
            for line in stdout.split("\n"):
                if line.startswith("  - "):
                    issues.append(line[4:])
            all_issues[test_file] = issues

    # Write the report
    with open("audit_reports/analysis_report.txt", "w") as f:
        f.write("TEST ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        for test_file, issues in all_issues.items():
            f.write(f"File: {test_file}\n")
            if issues:
                f.write("  Issues found:\n")
                for issue in issues:
                    f.write(f"    - {issue}\n")
            else:
                f.write("  No issues found\n")
            f.write("\n")

    print("Analysis complete. Report written to audit_reports/analysis_report.txt")


if __name__ == "__main__":
    main()
