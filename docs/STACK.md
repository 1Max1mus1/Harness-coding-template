# docs/STACK.md
# 填写指引：每个选型写明"为什么选这个而不是那个"。
# 写完后删除所有以 # 开头的注释行。
# FORBIDDEN 区块是最重要的部分——Agent 最需要知道不能用什么。

## Frontend
# 示例：React + Vite + TypeScript
技术：[填写]
版本：[填写]
理由：[为什么选这个，不选其他]

## Backend
# 示例：FastAPI + Pydantic
技术：[填写]
版本：[填写]
理由：[为什么选这个，不选其他]

## Database
# 示例：SQLite (dev) → Supabase/PostgreSQL (prod)
技术：[填写]
版本：[填写]
理由：[为什么选这个，迁移路径是什么]

## 部署
# 示例：Vercel (前端) + Railway (后端) + Supabase (DB)
前端部署：[填写]
后端部署：[填写]
理由：[为什么选这个组合]

## LLM / AI（如适用）
# 示例：Anthropic Claude claude-sonnet-4-6 via API
模型：[填写]
SDK：[填写]
理由：[为什么选这个]

## 禁止（FORBIDDEN）
# 这是最关键的部分。明确列出不允许引入的模式、框架、做法。
# Agent 违反这些规则时，lints/ 脚本会自动拦截。
- 不得引入 [禁止的框架/模式]
- 不得在 [禁止的层] 直接调用 [禁止的依赖]
- 不得使用 [禁止的模式，如：class components，ORM 以外的 DB 抽象]
- 不得硬编码环境变量（必须通过 config.py / .env 注入）
