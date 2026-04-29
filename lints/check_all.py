"""
Unified lint entry point. Runs all checks and reports a combined summary.
Usage: python lints/check_all.py
Exit code 1 if any check fails.
"""
import subprocess
import sys
import pathlib

CHECKS = [
    ("Architecture constraints", ["python", "lints/check_architecture.py"]),
    ("No bare print()",          ["python", "lints/check_no_print.py"]),
    # Add new check scripts here as you create them:
    # ("My custom check",        ["python", "lints/check_custom.py"]),
]

passed = []
failed = []

for name, cmd in CHECKS:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        passed.append(name)
        print(f"✅ {name}")
    else:
        failed.append(name)
        print(f"❌ {name}")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

print(f"\n{'='*50}")
print(f"Passed: {len(passed)}/{len(CHECKS)}  |  Failed: {len(failed)}/{len(CHECKS)}")

if failed:
    print("\nFailed checks:")
    for f in failed:
        print(f"  • {f}")
    sys.exit(1)
else:
    print("All checks passed ✅")
