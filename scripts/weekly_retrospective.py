"""
Weekly retrospective: AI-powered engineering bottleneck analysis (Phase 7).
Reads DORA metrics + CI failure history and asks Claude for improvement suggestions.
Run every week (or after notable incidents).
Requires: ANTHROPIC_API_KEY environment variable.
"""
import json
import pathlib
import sys
from datetime import datetime

try:
    import anthropic
except ImportError:
    print("anthropic not found. Install with: pip install anthropic")
    sys.exit(1)


def load_jsonl(path: pathlib.Path, last_n: int = 20) -> list[dict]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    records = []
    for line in lines:
        line = line.strip()
        if line:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return records[-last_n:]


def load_text(path: pathlib.Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "(not found)"


def main():
    print(f"Weekly Retrospective — {datetime.utcnow().strftime('%Y-%m-%d')}\n")

    deployments = load_jsonl(pathlib.Path("metrics/deployments.jsonl"))
    ci_failures = load_jsonl(pathlib.Path("metrics/ci_failures.jsonl"))
    lint_violations = load_jsonl(pathlib.Path("metrics/violations.jsonl"))

    arch_doc = load_text(pathlib.Path("docs/ARCHITECTURE.md"))

    if not deployments and not ci_failures and not lint_violations:
        print("No metrics data found in metrics/. Run deployments first to collect data.")
        sys.exit(0)

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=(
            "你是一个工程效能分析师，专门分析 AI 辅助开发团队的瓶颈。"
            "基于数据给出具体、可执行的建议，每条建议必须指定：改哪个文件 / 怎么改 / 预期效果。"
        ),
        messages=[{
            "role": "user",
            "content": f"""本周工程数据：

部署记录（最近 {len(deployments)} 条）：
{json.dumps(deployments, ensure_ascii=False, indent=2)}

CI 失败记录（最近 {len(ci_failures)} 条）：
{json.dumps(ci_failures, ensure_ascii=False, indent=2)}

Linter 违规记录（最近 {len(lint_violations)} 条）：
{json.dumps(lint_violations, ensure_ascii=False, indent=2)}

当前架构文档摘要：
{arch_doc[:1500]}

请分析：
1. 本周最大的工程瓶颈是什么？
2. 哪些违规或失败是反复出现的模式？（可能意味着 Harness 有漏洞）
3. 给出 3 条具体的 Harness 改进建议，每条必须包含：
   - 改哪个文件（docs/ARCHITECTURE.md / lints/ / AGENTS.md 等）
   - 具体怎么改（新增什么规则 / 修改什么描述）
   - 预期效果（减少哪类违规 / 提升哪个指标）
"""
        }]
    )

    print(msg.content[0].text)


if __name__ == "__main__":
    main()
