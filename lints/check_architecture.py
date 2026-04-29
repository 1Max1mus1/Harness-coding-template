"""
Architecture constraint checker.
Reads docs/ARCHITECTURE.md forbidden rules and enforces them via AST analysis.
Add project-specific checks in the CUSTOM CHECKS section below.
"""
import ast
import sys
import pathlib

VIOLATIONS = []


def add_violation(path, lineno, message):
    VIOLATIONS.append(f"{path}:{lineno} — {message}")


# ---------------------------------------------------------------------------
# Built-in checks (based on harness-template defaults)
# ---------------------------------------------------------------------------

def check_no_http_in_services(path: pathlib.Path):
    """services/ must not import HTTP frameworks."""
    FORBIDDEN_PREFIXES = ["fastapi", "starlette", "flask", "django", "aiohttp"]
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module = getattr(node, "module", "") or ""
            names = [alias.name for alias in getattr(node, "names", [])]
            all_names = [module] + names
            for name in all_names:
                for prefix in FORBIDDEN_PREFIXES:
                    if name.startswith(prefix):
                        add_violation(
                            path, node.lineno,
                            f"services/ 层禁止导入 HTTP 框架 '{prefix}'"
                        )


def check_no_db_in_api(path: pathlib.Path):
    """api/routers must not import db layer directly."""
    # Adjust 'src.db' to match your project's DB module path
    FORBIDDEN_DB_MODULES = ["src.db", "database", "sqlalchemy", "sqlite3", "psycopg2"]
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module = getattr(node, "module", "") or ""
            names = [alias.name for alias in getattr(node, "names", [])]
            all_names = [module] + names
            for name in all_names:
                for forbidden in FORBIDDEN_DB_MODULES:
                    if name.startswith(forbidden):
                        add_violation(
                            path, node.lineno,
                            f"api/ 层禁止直接导入 DB 模块 '{forbidden}'，请通过 services/ 访问"
                        )


# ---------------------------------------------------------------------------
# CUSTOM CHECKS — 根据你的 ARCHITECTURE.md 在这里添加项目专属规则
# ---------------------------------------------------------------------------
# 示例：
# def check_models_no_business_logic(path: pathlib.Path):
#     """models/ must not import services/."""
#     ...


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_checks():
    services_dir = pathlib.Path("src/services")
    api_dir = pathlib.Path("src/api")

    if services_dir.exists():
        for f in services_dir.rglob("*.py"):
            check_no_http_in_services(f)

    if api_dir.exists():
        for f in api_dir.rglob("*.py"):
            check_no_db_in_api(f)

    # Add calls to custom check functions here


if __name__ == "__main__":
    run_checks()
    if VIOLATIONS:
        print(f"\n❌ Architecture violations found ({len(VIOLATIONS)}):\n")
        for v in VIOLATIONS:
            print(f"  {v}")
        sys.exit(1)
    else:
        print("✅ Architecture constraints passed (0 violations)")
