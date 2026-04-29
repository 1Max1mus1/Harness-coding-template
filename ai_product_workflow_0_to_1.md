# 从 0 到 1 用 AI 做产品——完整工作流

> **核心前提**：前三个阶段的投入决定后两个阶段的效率。  
> 跳过 Phase 1-3 直接写代码，你会在 Phase 4 花 3 倍时间返工。

---

## 目录

- [SOP 复用方法对比](#sop-复用方法对比)
- [Phase 1：思路结晶](#phase-1思路结晶)
- [Phase 2：架构决策](#phase-2架构决策)
- [Phase 3：Harness 搭建](#phase-3harness-搭建)
- [Phase 4：AI 辅助开发](#phase-4ai-辅助开发)
- [Phase 5：部署与上线](#phase-5部署与上线)
- [工具全景图](#工具全景图)
- [时间预估与成功标准](#时间预估与成功标准)

---

## SOP 复用方法对比

在开始做新产品之前，先解决"如何让 Harness Engineering SOP 在下一个项目里自动生效"的问题。三种方案各有适用场景，建议两套并行。

### 方案 A：Claude Project + Project Instructions（规划层）

在 Claude.ai 创建一个专门的 Project（比如命名为"Product Dev"），把 SOP 的浓缩版（500-800 字）粘贴进 Project Instructions。

**效果**：每次在这个 Project 里开对话，Claude 天然在 Harness Engineering 语境里工作。你说"帮我设计 API"，它会主动问"INTENT.md 写了吗、STACK.md 里有什么约束"，而不是直接给你一个通用方案。

**适合场景**：阶段一和二（思路结晶、架构决策），以及任何需要和 Claude 对话讨论的场景。

**Project Instructions 浓缩版模板：**

```
你是我的产品开发伙伴，我们遵循 Harness Engineering 方法论。

核心原则：
1. 文档先于代码。任何开发任务开始前，INTENT.md / STACK.md / ARCHITECTURE.md 必须就绪。
2. 约束机器化。架构规则写成 linter 脚本，不靠人工 review 执行。
3. 障碍是信号。Agent 卡住 = Harness 有漏洞，修 Harness，不帮 Agent 绕过。

工作文件结构：
- docs/INTENT.md      ← 项目意图和机器可验证的完成标准
- docs/STACK.md       ← 技术栈合约（含 FORBIDDEN 区块）
- docs/ARCHITECTURE.md ← 系统边界和禁止依赖模式
- lints/              ← 架构约束脚本（CI 自动执行）
- AGENTS.md           ← Agent 导航地图（100行封顶，只写指针）

每次我描述新功能需求，你先问我：
1. 这对应 INTENT.md 里的哪条验收标准？
2. STACK.md 里有没有相关约束？
3. 最小的 Task Spec 是什么？
```

### 方案 B：Git Template Repo（执行层）

把 P0 阶段的所有文件做成一个 GitHub Template Repository，每次新项目 `Use this template` 克隆，Claude Code 在这个仓库里工作时天然就在 Harness 框架里。

**Template Repo 应包含的文件：**

```
harness-template/
├── AGENTS.md                    ← 模板版，含占位符
├── docs/
│   ├── INTENT.md               ← 空模板，含填写指引
│   ├── STACK.md                ← 空模板，含常见选项
│   ├── ARCHITECTURE.md         ← 空模板，含示例禁止模式
│   └── decisions/
│       └── 000-template.md     ← ADR 模板
├── lints/
│   ├── check_architecture.py   ← 基础版，可扩展
│   ├── check_no_print.py
│   └── check_all.py            ← 统一入口
├── scripts/
│   ├── smoke_test.py           ← 骨架，待填充
│   ├── gc_docs_freshness.py
│   └── weekly_retrospective.py
├── .pre-commit-config.yaml     ← 已配置好
├── .github/
│   ├── pull_request_template.md
│   └── workflows/
│       └── ci.yml              ← 四层门禁模板
└── README.md                   ← 如何使用这个模板
```

### 方案对比总结

| 维度 | Project Instructions | Git Template | Skill 文件 |
|------|---------------------|-------------|-----------|
| 覆盖场景 | 对话规划阶段 | 编码执行阶段 | 文件生成任务 |
| 生效方式 | 自动注入每次对话 | Claude Code 自动读 AGENTS.md | Claude 扫描触发 |
| 维护成本 | 极低 | 低（更新模板一次） | 中 |
| 推荐优先级 | ⭐⭐⭐ | ⭐⭐⭐ | 可选 |

**结论：Project Instructions + Git Template 双轨并行，覆盖产品开发全生命周期。**

---

## Phase 1：思路结晶

**时长**：1-3 天  
**目标**：把脑子里模糊的"感觉不错"，逼迫它变成一个可被质疑、可被验证的具体规格。  
**核心工具**：Claude（对话）

### 步骤 1-1：压力测试想法

把初始想法告诉 Claude，让它用两个视角轮流质问你。不要一开始就让 Claude 帮你完善，先让它挑战你。

**Prompt 模板：**

```
我有一个产品想法：[你的想法]

请分别用两个视角质问我：

视角1——最挑剔的用户：
- 为什么要用这个而不是 [Notion/Excel/现有工具]？
- 哪里具体好用，给我一个实际使用场景？
- 我为什么要在意这个产品而不是忽略它？

视角2——最懒的开发者：
- 最简单的 MVP 版本是什么？
- 哪些功能是核心？哪些是我以为用户需要但其实不需要的？
- 如果只能做一件事，是哪一件？

每个视角给我 3-5 个尖锐的问题，不要给答案。
```

逐一回答这些问题，你会发现很多没想清楚的地方。这些暴露出来的空白就是你需要在开始写代码前解决的。

### 步骤 1-2：提炼核心价值主张

经过压力测试后，让 Claude 帮你把想法压缩。

**Prompt 模板：**

```
基于我们的对话，帮我把这个产品的核心价值提炼成：
1. 一句话的价值主张（格式：[目标用户] 用 [产品名] 来 [做什么]，因为 [现有方案的核心痛点]）
2. 三条"明确不做什么"（scope 边界，防止功能蔓延）
3. 最小 MVP 的功能列表（最多 5 个功能，排序）
```

这一句话的价值主张就是 INTENT.md 的第一行，也是整个项目的北极星。

### 步骤 1-3：生成 PRD 草稿

**Prompt 模板：**

```
根据以下信息，帮我生成一份轻量 PRD 草稿：

核心价值主张：[上一步的结果]
目标用户：[描述]
MVP 功能列表：[上一步的结果]
明确不做的事：[上一步的结果]

PRD 格式：
1. 产品概述（3-5句）
2. 目标用户画像（1-2个典型用户）
3. 用户故事（每个 MVP 功能对应 1 个，格式：作为[用户]，我想要[功能]，以便[价值]）
4. 功能规格（每个功能的输入/输出/边界条件）
5. 成功指标（可量化，上线后如何判断成功）
6. 明确超出范围的功能
```

**重点**：review PRD 草稿时，重点看"功能规格"和"成功指标"部分。任何模糊的地方都要追问 Claude 直到它变成具体的、可测试的描述。

### 步骤 1-4：写 INTENT.md

把以上所有输出整理成 INTENT.md，这是你项目的宪法。

```markdown
# docs/INTENT.md

## 核心价值主张
[一句话]

## 目标用户
[1-2句描述]

## MVP 功能范围
1. [功能一]
2. [功能二]
3. [功能三]

## 明确不做
- [超出范围的功能1]
- [超出范围的功能2]

## 完成标准（机器可验证）
- [ ] [具体的 API 端点 + 响应时间]
- [ ] [具体的用户操作 + 预期结果]
- [ ] [具体的性能指标]

## 成功指标（上线后）
- [可量化的指标]
```

**阶段产出：**
- 通过压力测试的核心价值主张
- 草稿 PRD（含用户故事 + 功能规格 + 成功指标）
- INTENT.md 初始版本

---

## Phase 2：架构决策

**时长**：半天到一天  
**目标**：在第一行代码出现之前，把技术路线锁定。  
**核心工具**：Claude（对话）

### 步骤 2-1：技术栈选型对话

不要问"什么技术栈最好"，要问"对我这个具体情况最好的是什么"。

**Prompt 模板：**

```
帮我做技术栈选型，给出推荐和理由。

我的情况：
- 产品类型：[SaaS / 工具 / API 服务 / 其他]
- 预期用户量（第一个月）：[数量级]
- 我熟悉的技术：[你的技术背景]
- 上线时间压力：[几周内]
- 部署预算：[免费 / 低成本 / 无限制]
- 是否需要 LLM：[是/否，如是，用途是]

我最关心的 tradeoff：
1. 数据库：[你的选项]，怎么选？
2. 部署架构：[你的选项]，怎么选？
3. [其他你不确定的选项]

对于每个问题，请明确给出"对我这个情况，推荐X而不是Y，原因是A/B/C"，不要泛泛介绍每种技术。
```

### 步骤 2-2：系统设计 review

把你设计的系统架构（哪怕只是文字描述）让 Claude 挑战，而不是设计。

**Prompt 模板：**

```
这是我设计的系统架构：
[你的架构描述，包括：模块划分 / 数据流 / 关键依赖]

请找出三个最可能出问题的地方：
1. 哪里最容易出性能瓶颈？
2. 哪里最可能在 MVP 阶段变成技术债？
3. 哪里的设计假设最脆弱（一旦假设不成立就要大改）？

每个问题给出：问题描述 + 为什么这里危险 + 一个低成本的预防方案
```

### 步骤 2-3：数据库 Schema 设计

**Prompt 模板：**

```
根据以下 PRD 和用户故事，帮我设计数据库 schema：

[粘贴 INTENT.md 的功能规格部分]

要求：
1. 用 SQL DDL 格式输出
2. 每张表加注释说明用途
3. 标出主键、外键、索引
4. 说明哪些字段是 MVP 必需的，哪些是可以后加的
5. 指出任何可能导致后期 migration 很痛苦的设计决策
```

### 步骤 2-4：写 STACK.md 和 ARCHITECTURE.md

**Prompt 模板（STACK.md）：**

```
基于我们的选型对话，帮我生成 STACK.md 文件。

格式要求：
- 每个技术选项写明：技术名 + 版本 + 选择理由
- 必须有 FORBIDDEN 区块，列出不允许引入的模式
- 用 markdown 格式
```

**Prompt 模板（ARCHITECTURE.md）：**

```
基于以下系统设计，帮我生成 ARCHITECTURE.md 文件：

[你的系统架构描述]
[数据库 schema]

格式要求：
1. 系统边界：用文字描述数据流向，并列出"禁止"的数据流
2. 模块职责：每个模块的职责 + 禁止行为（重点写禁止）
3. 关键决策：每个重要架构决策 + 理由
4. 禁止依赖矩阵：哪些模块不得导入哪些模块
```

**阶段产出：**
- STACK.md（技术栈合约）
- ARCHITECTURE.md 初始版
- 数据库 schema（SQL DDL）

---

## Phase 3：Harness 搭建

**时长**：半天  
**目标**：P0-P2 全部就绪，第一个 linter 脚本跑通，pre-commit hook 安装完毕。  
**核心工具**：Claude（文件生成）+ Claude Code（执行）

### 步骤 3-1：从 Template Repo 克隆

```bash
# 在 GitHub 点击 "Use this template" 或
gh repo create my-project --template your-username/harness-template
cd my-project
```

### 步骤 3-2：填写模板文件

用 Claude 根据 Phase 1-2 的产出填充所有模板文件。

**Prompt 模板：**

```
我有以下文档：
[粘贴 INTENT.md]
[粘贴 STACK.md]
[粘贴 ARCHITECTURE.md]

帮我：
1. 填写 AGENTS.md（基于这三份文档，生成导航地图）
2. 生成对应的 lints/check_architecture.py（检查 ARCHITECTURE.md 里的禁止依赖规则）
3. 生成 .github/pull_request_template.md
```

### 步骤 3-3：生成 Linter 脚本

**关键操作**：把 ARCHITECTURE.md 里的"禁止"部分单独发给 Claude，让它生成对应的 Python AST 检查脚本。

**Prompt 模板：**

```
根据以下架构约束，生成对应的 Python linter 脚本：

[粘贴 ARCHITECTURE.md 的 "禁止" 部分]

要求：
- 用 Python ast 模块做静态分析
- 每条违规输出：[文件路径:行号] 违规描述
- 有违规时 sys.exit(1)
- 全通过时输出 ✅ 和通过的检查数量
- 脚本放在 lints/check_architecture.py
```

### 步骤 3-4：验证 Harness 就绪

```bash
# 安装 pre-commit
pip install pre-commit
pre-commit install

# 验证 linter 运行正常
python lints/check_architecture.py

# 验证 CI 配置语法正确
# （推一个空 commit 到 GitHub 检查 Actions）
git commit --allow-empty -m "test: verify CI setup"
git push
```

**阶段产出：**
- 完整的 Harness 文件结构
- 跑通的 pre-commit hooks
- CI Pipeline 就绪（GitHub Actions）

---

## Phase 4：AI 辅助开发

**时长**：主要编码阶段，每个 Feature 半天到一天  
**目标**：在 Harness 约束里高效产出代码，同时保持文档和代码同步。  
**核心工具**：Claude Code + Cursor/Windsurf + v0.dev

### 工具分工

| 工具 | 负责场景 | 不适合场景 |
|------|---------|-----------|
| Claude Code | 复杂多文件变更、重构、读 AGENTS.md 的任意任务 | 快速单文件小改动 |
| Cursor Composer | 日常单文件编辑、前后端联动的中型改动 | 需要读大量上下文的重构 |
| v0.dev / Lovable | UI 组件初始生成、Landing Page | 业务逻辑、API 设计 |
| Claude（对话） | 架构决策、调试根因分析、代码 review | 直接写代码 |

### 步骤 4-1：功能开发前——写 Task Spec

每个 Feature 开始前，先写 Task Spec，再给 AI 执行。这是整个工作流里最容易被跳过、但最有价值的一步。

**Task Spec 标准格式：**

```markdown
## Context（Agent 开始前必须读）
- docs/INTENT.md
- docs/ARCHITECTURE.md
- docs/api/[相关端点].md （如果有）
- src/[相关模块]/README.md

## 任务描述
实现 [具体函数/组件/API endpoint]。

输入：[精确的类型描述]
输出：[精确的类型描述]
副作用：[数据库写入/外部 API 调用/等]

## 验收标准（机器可验证）
- [ ] [具体的测试条件1]
- [ ] [具体的测试条件2]
- [ ] lints/check_architecture.py 通过
- [ ] 相关 pytest 通过

## 禁止
- [本任务中不允许的做法]
- [不得修改的文件]
```

### 步骤 4-2：测试先行（Test-as-Spec）

对每个新功能，先让 Claude 写测试，再写实现。测试文件就是最精确的任务规格。

**Prompt 模板：**

```
根据以下 Task Spec，先写测试文件，不要写实现：

[粘贴 Task Spec]

测试要求：
1. 测试命名用业务语言（test_returns_valid_schema，而不是 test_func_1）
2. 每个测试类加文档注释说明"这个测试类测的是什么规格"
3. 覆盖：正常路径 + 边界条件 + 错误路径
4. 不要 mock 业务逻辑，只 mock 外部依赖（DB/LLM/HTTP）
```

review 测试文件，确认它准确描述了你要的行为。然后：

```
好，测试文件确认正确。现在实现让这些测试通过的代码。
严格遵守 docs/ARCHITECTURE.md 的约束，完成后运行 lints/ 自检。
```

### 步骤 4-3：UI 开发策略

UI 组件分两类处理：

**结构性 UI（布局/页面框架）**：用 v0.dev 生成初始版，在自然语言里描述完整的 UI 结构。复制生成的 React 组件到项目，再用 Cursor 调整样式和逻辑。

**v0.dev 高效 Prompt 格式：**
```
[组件类型]，具有以下功能：
- [功能点1]
- [功能点2]
样式风格：[minimal/modern/...]
技术栈：React + TypeScript + Tailwind CSS
不要使用外部 UI 库（只用 Tailwind）
```

**数据驱动 UI（图表/复杂交互）**：直接用 Claude Code，给它 API response schema，让它生成对应的 React 组件。比 v0.dev 更适合有复杂数据绑定的场景。

### 步骤 4-4：调试工作流

遇到 bug 时，不要直接说"帮我修这个 bug"，用两步法。

**两步调试 Prompt：**

第一步：
```
以下是错误日志和相关代码：
[错误信息]
[相关代码]

给我三个最可能的根因，按概率从高到低排序。
每个根因说明：为什么你认为是这个原因 + 如何验证。
不要修代码，只分析原因。
```

第二步（你选择最可能的根因后）：
```
我认为是原因2。
请针对这个原因生成修复方案，要求：
1. 改动范围最小化
2. 加一个测试覆盖这个 bug 场景
3. 说明为什么这个修复不会引入新问题
```

### 步骤 4-5：每日收尾 checklist

每天开发结束时执行：

```bash
# 1. 跑完整测试
pytest src/tests/ -v

# 2. 跑架构检查
python lints/check_architecture.py

# 3. 检查文档是否跟上代码
python scripts/gc_docs_freshness.py

# 4. 检查是否有 NEEDS_DECISION 标注积压
grep -r "NEEDS_DECISION" src/ --include="*.py"
```

有 NEEDS_DECISION 的，当天决策并补写对应 ADR，不过夜积累。

### 步骤 4-6：障碍处理协议

Agent 卡住或反复出错时，按这个决策树处理：

```
Agent 卡住？先问：

1. 是文档缺失吗？
   → 补写对应 docs/ 文档，让 Agent 重读后重试
   → 不要在 prompt 里重复解释，文档才是正确的地方

2. 是约束冲突吗？（规则A和规则B互相矛盾）
   → 写 ADR 解决冲突
   → 更新 ARCHITECTURE.md

3. 是工具缺失吗？
   → 写这个工具的 Task Spec，让 Agent 实现
   → 不要手动帮 Agent 绕过

4. 是任务粒度太粗吗？
   → 把任务拆成更小的 Task Spec

⚠️ 永远不要做的事：
手动帮 Agent 写代码来解决它卡住的问题。
每次 Agent 卡住 = Harness 的一个 bug。修 Harness。
```

**阶段产出：**
- 每个 Feature 有对应测试 + 实现
- 文档与代码保持同步
- 所有 lints 通过，CI 绿灯

---

## Phase 5：部署与上线

**时长**：半天到一天  
**目标**：产品可访问，有基础监控，部署流程自动化。  
**核心工具**：Claude（生成配置文件）+ Vercel + Railway + Supabase

### 推荐部署架构（React + FastAPI + Supabase）

```
用户
 ↓
Vercel（前端，自动 CI/CD）
 ↓ API 请求
Railway（FastAPI 后端，Docker 容器）
 ↓ 数据库读写
Supabase（PostgreSQL，行级安全，Realtime）
```

**为什么这个组合：**
- Vercel：零配置部署 React，自动 preview deployments，免费额度够用
- Railway：Docker 原生，环境变量管理干净，日志好用，比 Heroku 稳
- Supabase：托管 PostgreSQL + 自动生成 REST API + Auth，避免自己维护 DB

### 步骤 5-1：生成 Dockerfile

**Prompt 模板：**

```
帮我生成一个生产级别的 FastAPI Dockerfile：

技术栈：
- Python [版本]
- FastAPI + uvicorn
- 依赖文件：requirements.txt

要求：
1. 多阶段构建（builder + production）
2. 非 root 用户运行
3. 健康检查端点（GET /health）
4. 环境变量通过 ENV 注入，不硬编码
5. 生产环境用 uvicorn --workers 2

额外：同时生成一个 docker-compose.yml 用于本地开发，
包含：app 服务 + postgres 服务（替代 Supabase 本地调试用）
```

### 步骤 5-2：生成 CI/CD Workflow

**Prompt 模板：**

```
帮我生成 GitHub Actions workflow，实现：

触发条件：push 到 main 分支

流程：
1. 运行 lints/check_architecture.py
2. 运行 pytest（排除 perf/ 目录）
3. 构建 Docker 镜像
4. 推送到 Railway（用 Railway CLI Action）
5. 部署成功后运行 scripts/smoke_test.py
6. Smoke test 失败则触发 Railway 回滚

我的环境变量：
- RAILWAY_TOKEN（Railway CLI token）
- DEPLOYMENT_URL（Railway 部署的 URL）
- DATABASE_URL（Supabase 连接串）
```

### 步骤 5-3：完善 Smoke Tests

在 `scripts/smoke_test.py` 里补充针对你产品核心功能的验证：

```python
# scripts/smoke_test.py
import httpx, sys, os

BASE_URL = os.environ["DEPLOYMENT_URL"]

def smoke_test():
    client = httpx.Client(base_url=BASE_URL, timeout=15)

    tests = [
        # 1. 基础健康检查
        lambda: assert_status(client.get("/health"), 200, "Health check"),

        # 2. Auth 端点可用
        lambda: assert_status(
            client.post("/auth/signup", json={"email": "smoke@test.com", "password": "test1234"}),
            [200, 400],  # 400 表示用户已存在，也算通过
            "Auth signup"
        ),

        # 3. 核心业务 API 可用（替换为你的核心端点）
        lambda: assert_core_api(client),
    ]

    for test in tests:
        test()

    print("✅ All smoke tests passed")

def assert_status(response, expected, name):
    if isinstance(expected, list):
        assert response.status_code in expected, f"{name} failed: {response.status_code}"
    else:
        assert response.status_code == expected, f"{name} failed: {response.status_code}"

def assert_core_api(client):
    # 替换为你的核心 API 验证
    r = client.post("/api/[your-endpoint]", json={"test": True})
    assert r.status_code == 200, f"Core API failed: {r.status_code}"
    data = r.json()
    assert "[expected_key]" in data, "Core API response schema invalid"

if __name__ == "__main__":
    try:
        smoke_test()
    except (AssertionError, Exception) as e:
        print(f"❌ Smoke test failed: {e}")
        sys.exit(1)
```

### 步骤 5-4：基础监控设置（上线当天）

| 工具 | 用途 | 配置时间 |
|------|------|---------|
| UptimeRobot（免费） | 每 5 分钟 ping /health，挂了发邮件 | 5 分钟 |
| Railway 内置日志 | 查看 API 日志和错误 | 零配置 |
| Supabase Dashboard | 查看 DB 查询性能和慢查询 | 零配置 |
| Vercel Analytics（免费） | 前端页面性能和流量 | 一键开启 |

**上线当天必须验证：**
```
[ ] /health 端点返回 200
[ ] Smoke tests 全部通过
[ ] UptimeRobot 监控已设置
[ ] 环境变量全部正确（没有 localhost 或 dev 的值）
[ ] 错误日志格式是结构化 JSON（便于后续分析）
```

**阶段产出：**
- 产品可访问（有公开 URL）
- 自动化 CI/CD（push to main → 自动部署）
- 基础监控就绪

---

## 工具全景图

### 按开发阶段

```
Phase 1 思路结晶     → Claude（Project Instructions 模式）
Phase 2 架构决策     → Claude（Project Instructions 模式）
Phase 3 Harness搭建  → Claude + Claude Code
Phase 4 功能开发     → Claude Code（主力）+ Cursor（日常）+ v0.dev（UI）
Phase 5 部署上线     → Claude（配置生成）+ Vercel + Railway
```

### 按任务类型

```
需要思考/决策        → Claude 对话（Project Instructions 模式）
复杂多文件变更       → Claude Code
日常单文件编辑       → Cursor / Windsurf
UI 组件初始生成      → v0.dev / Lovable
Landing Page        → v0.dev
调试根因分析         → Claude 对话（两步法）
配置文件生成         → Claude 对话
数据分析 / 图表      → Claude（Artifacts）
```

### 工具使用的反模式（避免这些）

- 用 Claude Code 从零生成复杂 UI：慢且质量差，用 v0.dev
- 用 v0.dev 生成业务逻辑：它不读你的 ARCHITECTURE.md，约束全失效
- 在 prompt 里重复解释架构背景：这些背景应该在 `docs/` 里，让 Agent 去读
- 一次性给 Agent 一个超大任务：拆成 Task Spec，每次一个功能点

---

## 时间预估与成功标准

### 时间预估（一人独立开发，中等复杂度 SaaS）

| 阶段 | 时间 | 关键输出 |
|------|------|---------|
| Phase 1 思路结晶 | 1-3 天 | INTENT.md + PRD |
| Phase 2 架构决策 | 0.5-1 天 | STACK.md + ARCHITECTURE.md + Schema |
| Phase 3 Harness 搭建 | 0.5 天 | 完整 Harness 文件结构 + CI 绿灯 |
| Phase 4 开发（每个 Feature） | 0.5-1 天 | 测试 + 实现 + 文档同步 |
| Phase 5 部署 | 0.5-1 天 | 线上可访问 + 监控就绪 |
| **MVP 总计** | **4-6 周** | 可用产品 |

### 各阶段就绪标准

**Phase 1-2 就绪**：一个陌生人读完 INTENT.md + STACK.md + ARCHITECTURE.md 后，能描述清楚这个产品做什么、用什么技术、哪些是禁止的。

**Phase 3 就绪**：一个新的 Claude Code session，仅凭仓库里的文件，能完成一个中等复杂度的 Task Spec 而不需要你在 prompt 里解释背景。

**Phase 4 进行中**：超过 80% 的架构违规被 CI 自动拦截，人工 review 只讨论设计问题，不检查格式和约束。

**Phase 5 就绪**：push to main → 自动测试 → 自动部署 → 自动 smoke test，全程无需手动操作。

### 最重要的一个数字

**每天花在"帮 Agent 写代码"上的时间。**

这个数字应该从第一周的高（还在摸索）持续下降，到第三四周趋近于零。如果这个数字没有下降，说明 Harness 某个环节有漏洞——回到 Phase 3 找原因，不要硬撑着继续写代码。
