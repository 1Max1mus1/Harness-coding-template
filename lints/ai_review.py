"""
AI-powered architecture review for CI.
Sends git diff + ARCHITECTURE.md to Claude and checks for violations.
Requires: ANTHROPIC_API_KEY environment variable.
Usage: python lints/ai_review.py [--base-branch main]
"""
import subprocess
import sys
import pathlib
import argparse

try:
    import anthropic
except ImportError:
    print("anthropic package not found. Install with: pip install anthropic")
    sys.exit(1)


def get_diff(base_branch: str) -> str:
    result = subprocess.run(
        ["git", "diff", f"{base_branch}...HEAD"],
        capture_output=True, text=True
    )
    return result.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-branch", default="main")
    args = parser.parse_args()

    arch_doc_path = pathlib.Path("docs/ARCHITECTURE.md")
    if not arch_doc_path.exists():
        print("⚠️  docs/ARCHITECTURE.md not found — skipping AI review")
        sys.exit(0)

    arch_doc = arch_doc_path.read_text(encoding="utf-8")
    diff = get_diff(args.base_branch)

    if not diff.strip():
        print("✅ No diff found — skipping AI review")
        sys.exit(0)

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=(
            "你是一个严格的架构审查员。"
            "只报告代码 diff 中违反架构文档规则的问题。"
            "不报告风格、命名、性能建议等非架构问题。"
        ),
        messages=[{
            "role": "user",
            "content": f"""架构文档：
{arch_doc}

代码 diff（最多 4000 字符）：
{diff[:4000]}

检查这个 diff 是否违反了架构文档中的规则。
每条违规格式：[文件名:行号] 违规描述
如无违规，只输出：✅ PASSED
"""
        }]
    )

    result = msg.content[0].text
    print(result)

    if "PASSED" not in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
