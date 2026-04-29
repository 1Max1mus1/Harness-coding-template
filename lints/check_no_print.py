"""
Forbids bare print() calls in src/.
Use the structured logger (src/utils/logger.py) instead.
Exceptions: files matching ALLOWED_PATTERNS are skipped.
"""
import ast
import sys
import pathlib

ALLOWED_PATTERNS = [
    "src/tests/",
    "src/utils/logger.py",
]

VIOLATIONS = []


def is_allowed(path: pathlib.Path) -> bool:
    path_str = str(path).replace("\\", "/")
    return any(pattern in path_str for pattern in ALLOWED_PATTERNS)


def check_no_print(path: pathlib.Path):
    if is_allowed(path):
        return
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "print":
                VIOLATIONS.append(
                    f"{path}:{node.lineno} — 禁止在 src/ 中使用 print()，请用 structlog/logger"
                )


if __name__ == "__main__":
    src_dir = pathlib.Path("src")
    if src_dir.exists():
        for f in src_dir.rglob("*.py"):
            check_no_print(f)

    if VIOLATIONS:
        print(f"\n❌ print() violations found ({len(VIOLATIONS)}):\n")
        for v in VIOLATIONS:
            print(f"  {v}")
        sys.exit(1)
    else:
        print("✅ No bare print() statements found")
