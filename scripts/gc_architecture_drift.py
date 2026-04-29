"""
GC: Architecture drift detection (Phase 6).
Collects all import relationships in src/ and sends them to Claude
to check for soft violations of ARCHITECTURE.md principles.
Run monthly.
Requires: ANTHROPIC_API_KEY environment variable.
"""
import ast
import pathlib
import sys

try:
    import anthropic
except ImportError:
    print("anthropic not found. Install with: pip install anthropic")
    sys.exit(1)


def extract_imports(path: pathlib.Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def format_imports(imports_map: dict) -> str:
    lines = []
    for file, imports in imports_map.items():
        if imports:
            lines.append(f"{file}: {', '.join(imports)}")
    return "\n".join(lines)


def main():
    arch_doc_path = pathlib.Path("docs/ARCHITECTURE.md")
    if not arch_doc_path.exists():
        print("docs/ARCHITECTURE.md not found — skipping drift check")
        sys.exit(0)

    arch_doc = arch_doc_path.read_text(encoding="utf-8")

    imports_map = {}
    src_dir = pathlib.Path("src")
    if src_dir.exists():
        for f in src_dir.rglob("*.py"):
            imports_map[str(f)] = extract_imports(f)

    if not imports_map:
        print("No Python files found in src/ — skipping drift check")
        sys.exit(0)

    print("Sending import map to Claude for drift analysis...")

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": f"""架构规范：
{arch_doc}

当前 src/ 的 import 依赖关系：
{format_imports(imports_map)}

识别所有违反架构规范中"禁止依赖"规则的 import 关系。
对每条违规，格式为：[文件路径] 违反了 [规则描述] 因为 [原因]
如果全部合规，仅输出：✅ No drift detected
"""
        }]
    )

    result = msg.content[0].text
    print(result)

    if "No drift detected" not in result and "PASSED" not in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
