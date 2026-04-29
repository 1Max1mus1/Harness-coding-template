# Harness Engineering AI Coding SOP

> **核心哲学**：你不再是代码的作者，你是 Agent 工作环境的架构师。  
> 传统 AI 编程：描述需求 → AI 写代码 → 你 review → 反复修改  
> Harness Engineering：设计环境 → AI 在环境里工作 → 环境拒绝错误 → AI 自我修正

---

## 目录

- [Phase 0：Pre-flight — 项目意图声明与环境搭建](#phase-0pre-flight--项目意图声明与环境搭建)
- [Phase 1：Context Engineering — 构建 Agent 知识库](#phase-1context-engineering--构建-agent-知识库)
- [Phase 2：Constraint Architecture — 构建约束机器](#phase-2constraint-architecture--构建约束机器)
- [Phase 3：Agent-First Dev Loop — 核心构建循环](#phase-3agent-first-dev-loop--核心构建循环)
- [Phase 4：CI Harness — 自动化反馈门禁](#phase-4ci-harness--自动化反馈门禁)
- [Phase 5：Observability — 可观测性与持续验证](#phase-5observability--可观测性与持续验证)
- [Phase 6：Anti-Entropy — 熵减与垃圾回收](#phase-6anti-entropy--熵减与垃圾回收)
- [Phase 7：Meta-Learning Loop — 闭环进化与 SOP 自改进](#phase-7meta-learning-loop--闭环进化与-sop-自改进)
- [整体逻辑链与落地路径](#整体逻辑链与落地路径)

---

## Phase 0：Pre-flight — 项目意图声明与环境搭建

这是整个 SOP 的地基阶段，目标是在第一行代码出现之前，把项目的"宪法"写清楚。没有这层，Agent 的每一次决策都是在消耗你的 review 注意力。

### 步骤 0-1：写 INTENT.md

用三个不可逃避的问题锁定项目边界：这个系统做什么、目标用户是谁、完成标准是什么。完成标准必须是机器可验证的形式，比如"POST /api/paths 在 3 秒内返回 200"而不是"性能良好"。这份文件是 Agent 在启动任何任务前都必须读的。它的价值不在于详细，而在于"强制让你在项目开始时把模糊想法变成具体约束"。

```markdown
# docs/INTENT.md

## 项目意图
本系统是一个 AI 驱动的学习路径生成器，
接收技能目标 → 输出知识依赖图。

## 目标用户
自学开发者，无结构化课程背景。

## 完成标准（Agent 可验证）
- [ ] POST /api/paths 在 3s 内返回 200
- [ ] 知识图谱节点 >= 5，边具有方向性
- [ ] 前端 Lighthouse Performance >= 85
- [ ] 所有测试通过，lints 零报错
```

### 步骤 0-2：冻结技术栈，写 STACK.md

每个技术选型都要写明"为什么选这个而不是那个"。一旦写入，Agent 不得自行引入新框架或切换库。最重要的部分是"FORBIDDEN"区块，明确列出禁止引入的模式。Agent 最需要的不是你告诉它用什么，而是告诉它不能用什么。

```markdown
# docs/STACK.md

## Frontend: React + Vite + TypeScript
理由：TS 类型在 Agent 生成代码时可自动验证

## Backend: FastAPI + Pydantic
理由：Pydantic schema 可直接注入 Agent context

## Database: SQLite (dev) → Supabase (prod)
理由：本地零配置，生产有行级安全

## 禁止（FORBIDDEN）
- 不得引入 ORM 以外的数据库抽象层
- 不得使用 class components（仅 hooks）
- 不得在 route handler 里直接调用 DB
```

### 步骤 0-3：初始化仓库骨架

按 Harness 三段式目录约定建立结构。把 `lints/` 和 `docs/` 和 `src/` 放在同一层级，视为一等公民。`docs/` 是 Agent 的操作系统，`lints/` 是约束的物理实体，`src/` 才是代码本身。

```
your-project/
├── AGENTS.md          ← 100行以内，纯目录
├── docs/
│   ├── INTENT.md      ← Agent 宪法
│   ├── STACK.md       ← 技术栈合约
│   ├── ARCHITECTURE.md
│   ├── decisions/     ← ADR 决策日志
│   └── api/           ← API contract 文档
├── src/
│   ├── api/           ← FastAPI routers
│   ├── services/      ← 业务逻辑
│   ├── models/        ← Pydantic schemas
│   └── tests/
├── frontend/
└── lints/             ← 自定义 linter 脚本
```

### 步骤 0-4：写 AGENTS.md v0（目录版，约 100 行封顶）

AGENTS.md 是 Agent 的导航地图，不是规则手册。它只做一件事：告诉 Agent 去哪里找真正的知识。不要把规则写在 AGENTS.md 里，规则属于 `docs/` 和 `lints/`。AGENTS.md 只是目录。

```markdown
# AGENTS.md

## 开始任何任务前，必须读
1. docs/INTENT.md       ← 项目意图和完成标准
2. docs/STACK.md        ← 技术栈约束（不得绕过）
3. docs/ARCHITECTURE.md ← 系统边界和禁止模式

## 约束（机器强制执行，非人工审查）
→ 见 lints/ 目录。CI 自动拦截违规。

## PR 提交前，必须
- [ ] 运行 python lints/check_all.py
- [ ] 确认没有 TODO/FIXME 残留
- [ ] 在 PR 描述里引用对应的 INTENT.md 验收条件

## 遇到不确定时
→ 查 docs/，找不到则在 PR 里标 [NEEDS_DECISION]
→ 永远不要自行假设技术选型
```

> **核心洞见**：Phase 0 花 2 小时建好这四份文件，相当于给 Agent 装了导航系统。没有这层，Agent 的每次决策都在消耗你的 review 注意力。

---

## Phase 1：Context Engineering — 构建 Agent 知识库

Agent 的输出上限等于它的 Context 质量上限。这个阶段的目标是把所有"人类默认知道但从未写下来"的上下文，结构化地存入 `docs/`，让 Agent 不需要靠猜测来填补空白。

### 步骤 1-1：写 ARCHITECTURE.md（设计意图文档）

这是整个 docs/ 体系里最重要的文档。核心价值不在于描述系统是什么，而在于描述"为什么这么设计"和"什么是明确禁止的"。系统边界的数据流向、关键架构决策的理由、模块间的禁止依赖关系——这三块是骨架。"既有规则又有理由"的写法比单纯写规则强 10 倍，因为 Agent 理解理由后才能在边缘情况下做出正确判断。

```markdown
# docs/ARCHITECTURE.md

## 系统边界（数据流向）
Browser → FastAPI Router → Service Layer → DB
禁止：Router 直接操作 DB
禁止：前端绕过 API 直连后端

## 关键决策
1. 所有 API 响应必须是 Pydantic BaseModel 实例
   原因：类型安全 + 自动 OpenAPI 文档
2. Service 层不导入任何 HTTP 依赖
   原因：可独立单元测试

## 模块边界（禁止跨层依赖）
api/      → services/ ✓
api/      → models/   ✓
services/ → models/   ✓
services/ → api/      ✗ FORBIDDEN
models/   → services/ ✗ FORBIDDEN
```

### 步骤 1-2：API Contract 文档（每个端点一份）

在 `docs/api/` 目录下，每个 API 端点对应一份 markdown 文件，包含完整的请求/响应 schema、所有可能的错误码、副作用说明。Agent 修改 API 时必须先读对应文档，修改完后必须同步更新文档。这让 API contract 从"代码里隐含的知识"变成"明确的、可追踪的合约"。

```markdown
# docs/api/POST_paths.md

## 端点：POST /api/paths

### 请求
{
  "goal": "string",        // 学习目标，5-200字
  "depth": "basic|full",  // 图谱深度
  "exclude": ["string"]   // 排除的知识点
}

### 响应 200
{
  "nodes": [{"id": "uuid", "name": "str", "level": int}],
  "edges": [{"from": "uuid", "to": "uuid"}]
}

### 错误码
- 422: goal 为空或超长
- 503: LLM 服务不可用（重试 3 次后）
```

### 步骤 1-3：决策日志（ADR 模式）

每个重要技术决策写一份轻量的 ADR（Architecture Decision Record），格式是背景 + 决定 + 后果。存在 `docs/decisions/` 目录下，用编号命名。后果部分要特别写清楚"Agent 必须知道的影响"。当 Agent 遇到同类问题时会读这些 ADR，避免重复踩同样的坑。

```markdown
# docs/decisions/001-use-streaming-response.md

## 状态：已采纳
## 日期：2025-03

## 背景
LLM 生成知识图谱需要 8-15 秒，
直接等待会导致前端 timeout。

## 决定
使用 FastAPI StreamingResponse 配合 Server-Sent Events。

## 后果（Agent 必须知道）
- 所有 /api/paths 相关测试需 mock streaming
- 禁止在 streaming route 里用 await 阻塞调用
```

### 步骤 1-4：模块 README 模式

每个 `src/` 子目录放一个 README.md，说明这个模块的职责边界、禁止行为、对外接口规范。比全局 ARCHITECTURE.md 更精准，Agent 修改局部代码时会自动读到最相关的上下文。这是"Just-in-Time Context"的实践：把正确的知识放在正确的位置，让 Agent 在需要时自然读到。

```markdown
# src/services/README.md

## 职责
- 编排 LLM 调用和 DB 操作
- 实现业务规则（不包含 HTTP 细节）

## 禁止
- 不导入 fastapi、Request、Response 等 HTTP 类
- 不直接读取环境变量（通过 config.py 注入）
- 不抛出 HTTP 异常（抛 Domain Exception，由 router 层转译）

## 对外接口
所有公开函数必须有 Pydantic 类型注解
```

> **核心洞见**：衡量 Context 质量的标准：一个新 Agent（无任何历史上下文）能否仅凭 `docs/` 完成一个中等复杂度的 PR？做不到就继续补文档。

---

## Phase 2：Constraint Architecture — 构建约束机器

规则如果靠人工 review 来执行，就会在 Agent 的输出速度面前失效。这个阶段把所有架构约束变成机器可执行的代码，让 CI 在 30 秒内拦截任何违规。

### 步骤 2-1：自定义 Linter（架构约束脚本）

用 Python 脚本检查最重要的架构规则，存在 `lints/` 目录下。核心思路是用 Python 的 `ast` 模块解析代码的抽象语法树，检查 import 关系是否违反了模块边界规则。CI 第一步就运行这些脚本，失败则阻断后续所有流程。

```python
# lints/check_architecture.py
import ast, sys, pathlib

VIOLATIONS = []

def check_service_imports(path):
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith('fastapi'):
                    VIOLATIONS.append(
                        f"{path}:{node.lineno} — Service 层禁止导入 fastapi"
                    )

for f in pathlib.Path("src/services").rglob("*.py"):
    check_service_imports(f)

if VIOLATIONS:
    for v in VIOLATIONS:
        print(f"❌ {v}")
    sys.exit(1)

print("✅ Architecture constraints passed")
```

### 步骤 2-2：Schema 验证门禁

后端所有 API 响应必须通过 Pydantic 验证，前端所有 API 调用必须通过 Zod 验证。把"类型一致性"从约定变成物理约束。FastAPI 的 `response_model` 参数会在运行时自动验证响应，类型错误直接 500，而不是悄悄传递错误数据给前端。

```python
# src/models/path_models.py
from pydantic import BaseModel, Field
from uuid import UUID

class PathNode(BaseModel):
    id: UUID
    name: str = Field(min_length=1, max_length=100)
    level: int = Field(ge=0, le=5)

class PathEdge(BaseModel):
    from_node: UUID = Field(alias="from")
    to_node: UUID = Field(alias="to")

class PathResponse(BaseModel):
    nodes: list[PathNode]
    edges: list[PathEdge]
    model_config = {"populate_by_name": True}

# Router 层使用：
# @router.post("/paths", response_model=PathResponse)
```

### 步骤 2-3：架构测试（用 pytest 测模块边界）

写一类特殊的测试，不测业务逻辑，只测"模块边界有没有被违反"。这类测试非常快（纯静态分析），放在 CI 的最早阶段，违规立即被发现。

```python
# src/tests/test_architecture.py
import ast, pathlib, pytest

@pytest.mark.parametrize("service_file",
    list(pathlib.Path("src/services").glob("*.py")))
def test_service_no_http_imports(service_file):
    """Service 层不得导入 HTTP 框架"""
    tree = ast.parse(service_file.read_text())
    forbidden = ["fastapi", "starlette", "flask"]
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module = getattr(node, 'module', '') or ''
            names = [a.name for a in getattr(node, 'names', [])]
            for f in forbidden:
                assert not module.startswith(f), \
                    f"{service_file}: forbidden import '{f}'"
```

### 步骤 2-4：Pre-commit Hook 配置

把最快的 lints 注册为 git hook，让 Agent 在 `git commit` 时就被拦截，而不是等到远程 CI。这是最快的反馈回路：本地 30 秒拦截 vs CI 5 分钟拦截。

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: architecture-check
        name: Architecture constraints
        entry: python lints/check_architecture.py
        language: system
        pass_filenames: false

      - id: no-print-statements
        name: No print() in src/
        entry: python lints/check_no_print.py
        language: system
        pass_filenames: false

# 安装：pre-commit install
```

> **核心洞见**：约束的价值 = 它拦截违规的速度。Pre-commit < 30s，CI < 2min，PR review 是最后防线。把尽可能多的规则推向更前面。

---

## Phase 3：Agent-First Dev Loop — 核心构建循环

这是 Harness Engineering 的核心执行循环。关键转变：你不再写代码，你写任务规格和验收标准，然后评估 Agent 的输出是否符合 Harness 的约束。你的产出从"代码"变成"清晰的任务规格"。

### 步骤 3-1：任务分解协议（Task Spec 格式）

每个给 Agent 的任务必须包含四个部分：Context（Agent 开始前必须读的文件列表）、任务描述（输入/输出的精确规格）、验收标准（机器可验证的 checklist）、禁止项（本任务中明确不允许的做法）。

```markdown
## Context（Agent 必须读的文件）
- docs/INTENT.md
- docs/ARCHITECTURE.md
- docs/api/POST_paths.md
- src/models/path_models.py

## 任务
实现 src/services/path_service.py 中的
generate_path(goal: str) -> PathResponse 函数。

## 验收标准
- [ ] 返回类型必须是 PathResponse（Pydantic 验证通过）
- [ ] nodes 数量 >= 3
- [ ] 每个 edge 的 from/to 都必须存在于 nodes 中
- [ ] 函数无 fastapi 导入（架构测试会验证）

## 禁止
- 不得硬编码任何知识点
- 不得修改 PathResponse schema
```

### 步骤 3-2：Prompt 工程（Agent 激活最佳状态）

给 Claude Code 的最优 prompt 结构分三段：首先注入约束文档（让 Agent 读 ARCHITECTURE.md、STACK.md、对应模块的 README.md），然后描述具体任务，最后要求 Agent 在提交前执行自检清单。把约束文档放在 prompt 的最前面，而不是最后面。

```
你是一个严格遵守项目约束的工程师。

在开始前，读以下文件：
1. docs/ARCHITECTURE.md（特别是"禁止"部分）
2. docs/STACK.md（技术栈合约）
3. src/services/README.md（本层职责边界）

任务：[在这里描述具体任务]

完成后，在提交前自检：
1. python lints/check_architecture.py 是否通过？
2. pytest src/tests/test_architecture.py 是否通过？
3. 新增代码是否有完整的类型注解？
4. 是否引入了 STACK.md 里禁止的依赖？

如果有任何不确定，在代码里标注
# [NEEDS_DECISION: 描述不确定的地方]
不要自行假设。
```

### 步骤 3-3：PR 工作流（Agent 自我 review）

用 PR 模板强制要求每个 PR 包含：对应的 INTENT.md 验收条件、Agent 自检清单（lints 通过、测试通过、无 FORBIDDEN 依赖）、架构影响说明、NEEDS_DECISION 标注。这个模板让 Agent 在提交前做强制性的自我 review，减少大约 80% 的低级架构违规。

```markdown
# .github/pull_request_template.md

## 变更摘要
[1-2句描述做了什么]

## 对应 INTENT.md 验收条件
- [ ] 本 PR 实现了哪条验收标准？

## Agent 自检清单
- [ ] python lints/check_architecture.py ✅
- [ ] pytest 全部通过 ✅
- [ ] 无新增 FORBIDDEN 依赖 ✅
- [ ] 所有新函数有类型注解 ✅

## 架构影响
- 改动了哪些模块边界？（如无请写"无"）
- 是否修改了 Pydantic schema？

## 需要人工决策的点
[如有不确定，标注 NEEDS_DECISION 项]
```

### 步骤 3-4：障碍处理协议（Agent 卡住时的决策树）

当 Agent 反复卡在同一个问题上，按优先级检查四种情况并对应处理。最重要的原则：永远不要帮 Agent 写代码来绕过障碍。每次障碍都是 Harness 的一个 bug，答案是修复 Harness。

```
Agent 卡住了？按顺序检查：

1. 文档缺失？
   → 补写对应 docs/ 文档，让 Agent 重读后重试

2. 约束冲突？（规则A和规则B互相矛盾）
   → 写一份 ADR 解决冲突，更新 ARCHITECTURE.md

3. 工具缺失？（Agent 需要某个能力但没有）
   → 写这个工具的 spec，让 Agent 来实现这个工具

4. 任务分解粒度太粗？
   → 把任务拆成更小的 Task Spec

⚠️ 永远不要做的事：
帮 Agent 写代码来绕过障碍。
每次障碍 = Harness 的一个 bug。
```

> **核心洞见**：Dev Loop 的核心度量：你每天在"帮 Agent 写代码"上花的时间。这个数字应该持续下降，被替代的时间应该花在强化 Harness（写文档、写约束）上。

---

## Phase 4：CI Harness — 自动化反馈门禁

CI 是 Harness 的第一道机械防线。这个阶段的目标是让人工 review 只关注"这个设计好不好"，而不是"这里少了个类型注解"。所有机械性的检查都应该由 CI 完成。

### 步骤 4-1：四层门禁 CI Pipeline 设计

按速度从快到慢设计四层门禁，每层失败都阻断后续层，实现"快速失败"。

```yaml
# .github/workflows/ci.yml
name: Harness CI
on: [push, pull_request]

jobs:
  # 层 1：约束检查（< 30s）
  constraints:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python lints/check_architecture.py
      - run: python lints/check_no_print.py

  # 层 2：单元测试（< 2min）
  unit-tests:
    needs: constraints
    steps:
      - run: pytest src/tests/unit/ -v --tb=short

  # 层 3：集成测试（< 5min）
  integration-tests:
    needs: unit-tests
    steps:
      - run: pytest src/tests/integration/ -v

  # 层 4：AI Code Review（异步，不阻断）
  ai-review:
    needs: constraints
    steps:
      - run: python lints/ai_review.py
```

### 步骤 4-2：AI Code Review Agent

用 Claude API 在 CI 里做架构合规性检查。脚本提取本次 PR 的 git diff，连同 ARCHITECTURE.md 一起发给 Claude，要求它只报告架构违规，每条违规注明文件名和行号。如果输出中没有"PASSED"字样则 exit 1。这不替代人工 review，但能在 2 分钟内发现大多数架构违规。

```python
# lints/ai_review.py
import subprocess, anthropic

diff = subprocess.check_output(
    ["git", "diff", "main...HEAD"], text=True
)
arch_doc = open("docs/ARCHITECTURE.md").read()

client = anthropic.Anthropic()
msg = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1000,
    messages=[{
        "role": "user",
        "content": f"""
架构文档：
{arch_doc}

代码 diff：
{diff[:4000]}

检查这个 diff 是否违反了架构文档中的规则。
只报告违规，不报告风格问题。
每条违规格式：[文件名:行号] 违规描述
如无违规，只输出：✅ PASSED
"""
    }]
)
result = msg.content[0].text
print(result)
if "PASSED" not in result:
    exit(1)
```

### 步骤 4-3：测试即规格（Test-as-Spec 模式）

测试文件同时扮演三个角色：行为规格（描述这个模块应该做什么）、Agent 的验收标准（Agent 拿到测试就知道要实现什么）、回归测试（防止未来的 Agent 破坏现有功能）。测试命名要用业务语言，Agent 读到这样的测试，就能直接推断出函数需要做什么。

```python
# src/tests/unit/test_path_service.py
"""
这个文件同时是：
1. path_service 的行为规格
2. Agent 实现时的验收标准
3. 回归测试
"""
class TestGeneratePath:
    """生成知识路径的规格"""

    def test_returns_valid_schema(self):
        """必须返回通过 Pydantic 验证的 PathResponse"""
        result = generate_path("learn Python basics")
        assert isinstance(result, PathResponse)

    def test_minimum_nodes(self):
        """知识图必须有至少 3 个节点"""
        result = generate_path("learn Python basics")
        assert len(result.nodes) >= 3

    def test_edges_reference_valid_nodes(self):
        """每条边的两端都必须是存在的节点"""
        result = generate_path("learn Python basics")
        node_ids = {n.id for n in result.nodes}
        for edge in result.edges:
            assert edge.from_node in node_ids
            assert edge.to_node in node_ids
```

### 步骤 4-4：Branch Protection 配置

在 GitHub 设置 Branch Protection Rules，要求所有 CI checks 必须通过才能合并到 main，并禁止 bypass（包括管理员）。这让约束从"建议"变成"不可逃脱的规则"，对所有提交者（包括 Agent）一视同仁。

```
GitHub Branch Protection 配置：
Settings → Branches → Add rule

Required status checks:
  ✅ constraints
  ✅ unit-tests
  ✅ integration-tests

Rules:
  [x] Require status checks to pass
  [x] Require branches to be up to date
  [x] Do not allow bypassing the above settings
```

> **核心洞见**：好的 CI 是"零人工干预拦截率"最大化。目标：人工 review 时，看到的是"这个设计好不好"，而不是"这里少了个类型注解"。

---

## Phase 5：Observability — 可观测性与持续验证

Agent 写的代码进了生产，你的眼睛必须比以往更亮。这个阶段建立结构化的可观测性体系，让系统行为对人和 Agent 都可见、可追踪、可分析。

### 步骤 5-1：结构化日志 Schema

所有日志必须是机器可解析的 JSON 格式，包含固定字段（endpoint、duration_ms、status_code、request_id、timestamp）。结构化日志的价值在于：Agent 可以通过分析日志来定位它自己写的代码的问题，而不需要人类帮它 grep 文本日志。

```python
# src/utils/logger.py
import structlog, time

log = structlog.get_logger()

def log_api_call(endpoint: str, duration_ms: float,
                 status: int, user_id: str = None):
    log.info(
        "api_call",
        endpoint=endpoint,
        duration_ms=round(duration_ms, 2),
        status_code=status,
        user_id=user_id,
        timestamp=time.time()
    )

# 输出格式（机器可解析）：
# {"event":"api_call","endpoint":"/api/paths",
#  "duration_ms":1243.5,"status_code":200}
```

### 步骤 5-2：性能基准断言（Benchmark Tests）

关键路径的性能要求写成 pytest 测试。Agent 优化代码时如果导致性能倒退，CI 会立即报错。这把性能 SLA 从"口头承诺"变成"机器强制执行的约束"。

```python
# src/tests/perf/test_benchmarks.py
import time, pytest

class TestPerformanceBudgets:
    """性能预算（这些是 SLA，不是目标）"""

    def test_path_generation_under_5s(self):
        """知识路径生成必须在 5s 内完成"""
        start = time.time()
        result = generate_path("learn Python basics")
        duration = time.time() - start
        assert duration < 5.0, \
            f"Path generation took {duration:.2f}s, budget is 5.0s"

    def test_db_query_under_100ms(self):
        """DB 查询必须在 100ms 内"""
        from src.db import get_recent_paths
        start = time.time()
        get_recent_paths(limit=10)
        assert (time.time() - start) < 0.1
```

### 步骤 5-3：错误边界和告警规则

定义什么算"异常"，以及异常时系统该做什么（自动重试 vs 告警 vs 降级），把这些决策写进代码而不是靠人工判断。使用 tenacity 库实现指数退避重试。

```python
# src/services/path_service.py
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

log = structlog.get_logger()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True
)
async def _call_llm(prompt: str) -> str:
    """LLM 调用失败自动重试（最多3次，指数退避）"""
    ...

async def generate_path(goal: str) -> PathResponse:
    try:
        raw = await _call_llm(build_prompt(goal))
        return parse_and_validate(raw)
    except Exception as e:
        log.error("path_generation_failed",
            goal=goal[:50], error=str(e),
            alert=True  # 触发告警系统
        )
        raise
```

### 步骤 5-4：部署验证（Smoke Tests）

每次部署后自动运行 Smoke Test，验证健康检查端点可用、核心 API 可用、响应数据符合 schema。任何失败触发自动回滚。这把"Agent 部署的代码是否真正可用"变成一个自动化的是/否判断。

```python
# scripts/smoke_test.py
import httpx, sys, os

BASE_URL = os.environ["DEPLOYMENT_URL"]

def smoke_test():
    client = httpx.Client(base_url=BASE_URL, timeout=10)

    # 1. 健康检查
    r = client.get("/health")
    assert r.status_code == 200, f"Health check failed: {r.status_code}"

    # 2. 核心 API 可用
    r = client.post("/api/paths", json={
        "goal": "smoke test", "depth": "basic"
    })
    assert r.status_code == 200, f"Core API failed: {r.status_code}"

    # 3. Schema 验证
    data = r.json()
    assert "nodes" in data and len(data["nodes"]) > 0

    print("✅ All smoke tests passed")

if __name__ == "__main__":
    try:
        smoke_test()
    except AssertionError as e:
        print(f"❌ Smoke test failed: {e}")
        sys.exit(1)
```

> **核心洞见**：可观测性的最高境界：Agent 能通过读日志和监控来诊断它自己写的代码的问题，而不需要人类帮它 debug。

---

## Phase 6：Anti-Entropy — 熵减与垃圾回收

系统随时间自然腐化：文档过期、架构漂移、死代码堆积、决策失忆。这是 Harness 面临的最大长期威胁，因为 Agent 会越来越依赖越来越过期的文档做出越来越偏离原始意图的决策。

### 步骤 6-1：文档鲜度检查 Agent（每周运行）

比较 `docs/api/` 下每份 API 文档的修改时间与对应代码文件的修改时间。如果代码文件在过去 24 小时内有更新但文档超过 1 天没更新，就标记为 stale 并生成 issue。以 cron job 形式每周运行一次。

```python
# scripts/gc_docs_freshness.py
import pathlib

def check_doc_freshness():
    stale = []
    for doc in pathlib.Path("docs/api").glob("*.md"):
        code_files = list(pathlib.Path("src/api").glob(
            f"*{doc.stem.split('_')[-1].lower()}*"
        ))
        if not code_files:
            continue
        doc_mtime = doc.stat().st_mtime
        code_mtime = max(f.stat().st_mtime for f in code_files)
        if code_mtime > doc_mtime + 86400:
            stale.append({
                "doc": str(doc),
                "days_behind": int((code_mtime - doc_mtime) / 86400)
            })
    return stale

stale = check_doc_freshness()
if stale:
    print("⚠️ Stale documentation detected:")
    for s in stale:
        print(f"  {s['doc']} is {s['days_behind']} days behind")
```

### 步骤 6-2：架构约束漂移检测（每月运行）

收集整个代码库的 import 依赖关系，发给 Claude API，让它对照 ARCHITECTURE.md 检查是否有新的依赖模式违反了架构原则。这检测的是那些没有被具体 linter 规则覆盖、但整体上偏离了架构意图的"软违规"。

```python
# scripts/gc_architecture_drift.py
import pathlib, anthropic

arch_doc = pathlib.Path("docs/ARCHITECTURE.md").read_text()
imports_map = {}
for f in pathlib.Path("src").rglob("*.py"):
    imports_map[str(f)] = extract_imports(f)

client = anthropic.Anthropic()
msg = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1500,
    messages=[{
        "role": "user",
        "content": f"""
架构规范：{arch_doc}
当前 import 依赖关系：{format_imports(imports_map)}

识别所有违反架构规范的依赖关系。
格式：[文件] 违反了 [规则] 因为 [原因]
如果全部合规，输出：✅ No drift detected
"""
    }]
)
print(msg.content[0].text)
```

### 步骤 6-3：死代码清理（每月运行）

使用 `vulture` 库检测未使用的代码，生成 `CLEANUP_NEEDED.md` 文档，而不是直接删除。死代码的危害不只是浪费空间，更重要的是它会污染 Agent 的 Context，让 Agent 可能去调用不再维护的函数。

```python
# scripts/gc_dead_code.py
import subprocess

result = subprocess.run(
    ["vulture", "src/",
     "--min-confidence", "80",
     "--exclude", "src/tests/"],
    capture_output=True, text=True
)

if result.stdout:
    print("⚠️ Potential dead code found:")
    print(result.stdout)

    with open("CLEANUP_NEEDED.md", "w") as f:
        f.write("# Dead Code Cleanup Needed\n\n")
        f.write("由 gc_dead_code.py 自动检测\n\n")
        f.write("```\n" + result.stdout + "\n```\n")
        f.write("\n指令：审查以上条目，确认后删除")

# 安装：pip install vulture
```

### 步骤 6-4：AGENTS.md 自动维护

扫描 `docs/` 目录结构，用正则更新 AGENTS.md 里的文件导航列表，保证 Agent 的导航地图始终准确。可以在 pre-commit hook 里触发。

```python
# scripts/gc_update_agents_md.py
import pathlib, re

def get_first_line(f):
    lines = f.read_text().splitlines()
    for line in lines:
        if line.strip() and not line.startswith('#'):
            return line.strip()[:50]
    return ""

docs_files = list(pathlib.Path("docs").rglob("*.md"))
nav_section = "## 开始任何任务前，必须读\n"

for f in sorted(docs_files):
    if f.name == "AGENTS.md":
        continue
    nav_section += f"- {f}  ← {get_first_line(f)}\n"

agents_md = pathlib.Path("AGENTS.md").read_text()
updated = re.sub(
    r"## 开始任何任务前.*?(?=\n##)",
    nav_section + "\n",
    agents_md, flags=re.DOTALL
)
pathlib.Path("AGENTS.md").write_text(updated)
print("✅ AGENTS.md navigation updated")
```

> **核心洞见**：Garbage Collection 的目标是让 Harness 的质量随时间上升而不是衰减。每个月花 2 小时运行 GC，比 6 个月后重写文档要省力得多。

---

## Phase 7：Meta-Learning Loop — 闭环进化与 SOP 自改进

这是 Harness Engineering 的最顶层能力：让整个系统学习自己的弱点，并自动提出改进方案。AI 在这个阶段不只是写代码的工具，而是改进整个工程体系的合作者。

### 步骤 7-1：DORA Metrics 收集

每次部署后自动记录四个核心 DORA 指标：部署频率（每周部署次数）、变更前置时间（从 PR 创建到部署完成的分钟数）、变更失败率（失败部署占总部署的比例）、MTTR（从失败到恢复服务的时间）。这四个数字是 Harness 健康状况的体检报告。

```python
# scripts/metrics_collect.py
import json, datetime, pathlib

def record_deployment(success: bool, duration_min: float):
    metrics_file = pathlib.Path("metrics/deployments.jsonl")
    metrics_file.parent.mkdir(exist_ok=True)

    record = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "success": success,
        "lead_time_minutes": duration_min,
        "week": datetime.date.today().isocalendar()[1]
    }

    with open(metrics_file, "a") as f:
        f.write(json.dumps(record) + "\n")

# DORA 4 指标：
# Deployment Frequency : 每周部署次数
# Lead Time            : PR → 生产的时间（分钟）
# Change Failure Rate  : 失败部署占比
# MTTR                 : 从失败到恢复的时间
```

### 步骤 7-2：AI 瓶颈分析（每周回顾）

把本周的 DORA 数据、CI 失败日志、linter 违规历史整合后发给 Claude API，要求它识别最大的工程瓶颈、分析反复出现的违规模式，并给出三条具体的 Harness 改进建议（每条建议要指定改哪个文件、怎么改、预期效果）。这把"每周回顾"从人工脑力劳动变成 5 分钟的自动化流程。

```python
# scripts/weekly_retrospective.py
import json, pathlib, anthropic

deployments = load_weekly_metrics("metrics/deployments.jsonl")
ci_failures = load_ci_failures("metrics/ci_failures.jsonl")
lint_violations = load_lint_history("metrics/violations.jsonl")

client = anthropic.Anthropic()
msg = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2000,
    messages=[{
        "role": "user",
        "content": f"""
本周工程数据：
- 部署：{deployments}
- CI 失败：{ci_failures}
- Linter 违规：{lint_violations}

分析：
1. 最大的工程瓶颈是什么？
2. 哪些违规是反复出现的模式？
3. 给出 3 条具体的 Harness 改进建议
   （每条要指定：改哪个文件 / 怎么改 / 预期效果）
"""
    }]
)
print(msg.content[0].text)
```

### 步骤 7-3：SOP 自改进协议

定义四个触发 SOP 审查的条件，每种触发条件都对应一个明确的修复动作，并且修复动作永远由 Agent 来实现，而不是人工直接修改。

```
SOP 改进触发条件：

1. 同一类 linter 违规连续 3 周出现
   → 可能是约束描述不清楚，或文档指针错误
   → 动作：更新 AGENTS.md / docs/ 相关文档

2. CI 失败率 > 20%（周平均）
   → 可能是约束太严格或测试太脆
   → 动作：审查 lints/ 和 tests/ 的合理性

3. Agent 频繁标注 [NEEDS_DECISION]
   → 某类决策没有文档化
   → 动作：写新的 ADR + 更新 ARCHITECTURE.md

4. MTTR > 30 分钟
   → Smoke Tests 可能不够覆盖关键路径
   → 动作：扩充 scripts/smoke_test.py

# 改进动作：永远让 Agent 来写改进方案
# 你负责 review 和 merge
```

### 步骤 7-4：Harness 成熟度 Checklist（季度自评）

四个维度的 checklist，每个季度用它做一次全面体检，找到 Harness 最薄弱的环节。

```markdown
## Harness 成熟度 Checklist

### Context Engineering（知识质量）
[ ] INTENT.md 包含机器可验证的完成标准
[ ] ARCHITECTURE.md 包含禁止模式（不只是描述）
[ ] 所有 API 端点有 contract 文档
[ ] 所有模块有 README.md

### Constraint Architecture（约束覆盖率）
[ ] 依赖方向由 linter 强制执行
[ ] Schema 验证覆盖所有 API 边界
[ ] Pre-commit hooks 在本地运行
[ ] CI 所有 checks 阻断 merge

### Feedback Loops（反馈速度）
[ ] Pre-commit < 30s
[ ] CI unit tests < 2min
[ ] AI code review 在 CI 中运行
[ ] 部署后有 smoke tests

### Anti-Entropy（长期健康度）
[ ] 每周有文档鲜度检查
[ ] 每月有架构漂移检测
[ ] DORA 指标被记录和分析
[ ] SOP 在过去 3 个月有更新
```

> **核心洞见**：Harness Engineering 的终态：你的主要工作是作为系统的架构师，而不是代码的作者。AI 写代码，AI 审代码，AI 分析问题，你决定系统该往哪走。

---

## 整体逻辑链与落地路径

### 核心循环

```
P0 环境宣言 → P1 知识注入 → P2 约束机器 → P3 构建循环
     ↑                                              ↓
P7 Meta-Learning ← P6 熵减 GC ← P5 可观测 ← P4 CI门禁
```

### 三大核心原则

**原则一：文档是 Context，不是 Comment**  
`docs/` 是 Agent 的操作系统，每次它"犯错"，答案不是多解释，而是升级文档或 linter。

**原则二：约束先于自由**  
在 Agent-first 工作流里，架构约束必须机械化执行，不能靠 review 来兜底。规则如果只存在于人脑里，就等于不存在。

**原则三：失败是信号，不是终点**  
Agent 卡住 = Harness 有漏洞，永远通过强化 Harness 来解决，而不是帮 Agent 写代码。

### 建议落地时间线

| 阶段 | 时间 | 重点 |
|------|------|------|
| 第一周 | 4-6 小时 | 完成 P0 全部：INTENT.md + STACK.md + AGENTS.md + 目录骨架 |
| 第二周 | 4-6 小时 | P1 写 ARCHITECTURE.md + P2 写前两个 linter |
| 第三周 | 持续 | P3 开始用 Task Spec 格式给 Claude Code 任务 |
| 第四周起 | 持续 | P4 CI 接入，性能基准测试 |
| 每月 | 2 小时 | P6 GC 脚本运行，文档同步 |
| 每周 | 30 分钟 | P7 weekly_retrospective.py 运行，阅读 AI 分析结果 |

### 成功标准

- **P0-P2 就绪**：一个新的 Claude Code session，仅凭 `docs/` 能完成中等复杂度的 PR
- **P3-P4 就绪**：超过 80% 的架构违规在 CI 里被自动拦截，人工 review 只讨论设计问题
- **P5-P6 就绪**：系统的任何异常在 5 分钟内可定位，文档与代码的 lag 不超过 1 周
- **P7 就绪**：每周有 AI 生成的工程改进建议，SOP 每季度有可追踪的更新记录
