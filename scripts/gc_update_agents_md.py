"""
GC: Auto-maintain AGENTS.md navigation section (Phase 6).
Scans docs/ and updates the "必须读" file list in AGENTS.md.
Safe to run in pre-commit hook.
"""
import pathlib
import re
import sys


def get_first_description_line(f: pathlib.Path) -> str:
    """Return the first non-heading, non-empty, non-comment line (max 60 chars)."""
    try:
        for line in f.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("<!--"):
                return stripped[:60]
    except Exception:
        pass
    return ""


def build_nav_section(docs_dir: pathlib.Path) -> str:
    lines = ["## 开始任何任务前，必须读\n"]
    priority_files = ["INTENT.md", "STACK.md", "ARCHITECTURE.md"]

    # Priority files first
    for name in priority_files:
        f = docs_dir / name
        if f.exists():
            desc = get_first_description_line(f)
            lines.append(f"- {f}  ← {desc}" if desc else f"- {f}")

    # Then decisions/ and api/ subdirectories
    for subdir in ["decisions", "api"]:
        subdir_path = docs_dir / subdir
        if subdir_path.exists():
            for f in sorted(subdir_path.glob("*.md")):
                desc = get_first_description_line(f)
                entry = f"- {f}  ← {desc}" if desc else f"- {f}"
                lines.append(entry)

    return "\n".join(lines) + "\n"


def main():
    agents_md = pathlib.Path("AGENTS.md")
    docs_dir = pathlib.Path("docs")

    if not agents_md.exists():
        print("AGENTS.md not found — skipping update")
        sys.exit(0)

    if not docs_dir.exists():
        print("docs/ not found — skipping update")
        sys.exit(0)

    nav_section = build_nav_section(docs_dir)
    content = agents_md.read_text(encoding="utf-8")

    updated = re.sub(
        r"## 开始任何任务前，必须读\n.*?(?=\n##|\Z)",
        nav_section,
        content,
        flags=re.DOTALL
    )

    if updated != content:
        agents_md.write_text(updated, encoding="utf-8")
        print("✅ AGENTS.md navigation section updated")
    else:
        print("✅ AGENTS.md navigation section is already up to date")


if __name__ == "__main__":
    main()
