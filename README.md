# harness-template

Harness Engineering 项目模板。基于 [Harness Engineering SOP](docs/) 构建，
覆盖从 Phase 0（项目宪法）到 Phase 7（Meta-Learning Loop）的完整工作流。

## 如何使用这个模板

### 1. 克隆模板

在 GitHub 点击 **"Use this template"** 按钮，或用 CLI：

```bash
gh repo create my-project --template your-username/harness-template
cd my-project
```

### 2. 填写四份核心文件（Phase 0，约 2 小时）

按顺序填写，每份文件内有填写指引（以 `#` 开头的注释行）：

| 文件 | 用途 | 用 Claude 生成的 Prompt |
|------|------|------------------------|
| [docs/INTENT.md](docs/INTENT.md) | 项目宪法：做什么、为谁做、完成标准 | "帮我把以下产品想法写成 INTENT.md 模板格式：[你的想法]" |
| [docs/STACK.md](docs/STACK.md) | 技术栈合约 + FORBIDDEN 清单 | "基于我们的技术选型对话，生成 STACK.md" |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 系统边界 + 禁止依赖矩阵 | "基于以下系统设计，生成 ARCHITECTURE.md，重点写禁止部分" |
| [AGENTS.md](AGENTS.md) | Agent 导航地图（只写指针） | "基于以上三份文档，生成 AGENTS.md 导航地图" |

### 3. 生成项目专属 Linter（Phase 2）

把 `docs/ARCHITECTURE.md` 的"禁止"部分发给 Claude：

```
根据以下架构约束，在 lints/check_architecture.py 的 CUSTOM CHECKS 区域
添加对应的 Python AST 检查函数：

[粘贴 ARCHITECTURE.md 的禁止依赖部分]

要求：每条违规输出 [文件:行号] 违规描述
```

### 4. 安装 pre-commit hooks

```bash
pip install pre-commit
pre-commit install
```

### 5. 验证 Harness 就绪

```bash
python lints/check_all.py        # 所有约束检查通过
git commit --allow-empty -m "chore: verify harness setup"
git push                          # CI pipeline 绿灯
```

---

## 目录结构

```
harness-template/
├── AGENTS.md                        ← Agent 导航地图（填写后使用）
├── docs/
│   ├── INTENT.md                   ← 项目宪法（必须最先填）
│   ├── STACK.md                    ← 技术栈合约
│   ├── ARCHITECTURE.md             ← 系统边界与禁止依赖
│   └── decisions/
│       └── 000-template.md         ← ADR 模板（复制后填写）
├── lints/
│   ├── check_all.py                ← 统一入口（CI 和本地都用这个）
│   ├── check_architecture.py       ← 架构约束（添加项目专属规则）
│   ├── check_no_print.py           ← 禁止裸 print()
│   └── ai_review.py                ← Claude AI 架构审查（CI Layer 4）
├── scripts/
│   ├── smoke_test.py               ← 部署后验证（填写核心端点）
│   ├── gc_docs_freshness.py        ← 每周：文档鲜度检查
│   ├── gc_architecture_drift.py    ← 每月：架构漂移检测
│   ├── gc_dead_code.py             ← 每月：死代码清理
│   ├── gc_update_agents_md.py      ← pre-commit：同步 AGENTS.md 导航
│   ├── metrics_collect.py          ← CI：记录 DORA 指标
│   └── weekly_retrospective.py     ← 每周：AI 瓶颈分析
├── metrics/                         ← DORA 指标数据（JSONL，gitignore 可选）
├── .pre-commit-config.yaml          ← 本地 git hooks
└── .github/
    ├── pull_request_template.md     ← PR 自检清单
    └── workflows/
        └── ci.yml                   ← 四层门禁 CI Pipeline
```

---

## 每日工作流

```bash
# 开发前：写 Task Spec（见 docs/ARCHITECTURE.md 里的格式说明）
# 开发中：Claude Code 读 AGENTS.md 自动工作

# 每次提交前
python lints/check_all.py
pytest src/tests/ -v

# 每日收尾
python scripts/gc_docs_freshness.py        # 检查文档是否跟上代码
grep -r "NEEDS_DECISION" src/ --include="*.py"  # 不过夜积累
```

## 周期性维护

| 频率 | 脚本 | 用途 |
|------|------|------|
| 每周 | `python scripts/weekly_retrospective.py` | AI 分析本周工程瓶颈 |
| 每周 | `python scripts/gc_docs_freshness.py` | 文档鲜度检查 |
| 每月 | `python scripts/gc_architecture_drift.py` | 架构漂移检测 |
| 每月 | `python scripts/gc_dead_code.py` | 死代码清理列表 |
| 每季 | Harness 成熟度 Checklist（见 SOP Phase 7-4） | 全面体检 |

---

## 环境变量（在 GitHub Secrets 里配置）

| 变量 | 用途 | 需要时机 |
|------|------|---------|
| `ANTHROPIC_API_KEY` | AI Review + 周报分析 + 架构漂移检测 | CI Layer 4 就绪时 |
| `DATABASE_URL` | 集成测试连接 DB | Phase 4 集成测试 |
| `DEPLOYMENT_URL` | Smoke tests | Phase 5 部署后 |

---

## 成功标准

- **Harness 就绪**：一个新的 Claude Code session，仅凭仓库里的文件，能完成中等复杂度的 Task Spec
- **CI 门禁生效**：>80% 的架构违规被自动拦截，人工 review 只讨论设计问题
- **长期健康**：文档与代码 lag 不超过 1 周，每周有 AI 生成的改进建议
