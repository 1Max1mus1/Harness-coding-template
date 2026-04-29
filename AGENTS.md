# AGENTS.md
# [PROJECT_NAME] — Agent 导航地图
# 100 行封顶。只写指针，规则在 docs/ 里。

## 开始任何任务前，必须读
1. docs/INTENT.md        ← 项目意图和机器可验证的完成标准
2. docs/STACK.md         ← 技术栈合约（不得绕过）
3. docs/ARCHITECTURE.md  ← 系统边界和禁止模式

## 约束（机器强制执行，非人工审查）
→ 见 lints/ 目录。CI 自动拦截违规。
→ 本地运行：python lints/check_all.py

## PR 提交前，必须
- [ ] python lints/check_all.py 全部通过
- [ ] pytest 全部通过
- [ ] 确认没有 TODO/FIXME 残留（NEEDS_DECISION 例外）
- [ ] 在 PR 描述里引用对应的 INTENT.md 验收条件

## 遇到不确定时
→ 查 docs/，找不到则在代码里标注 # [NEEDS_DECISION: 描述]
→ 永远不要自行假设技术选型
→ 不要在 AGENTS.md 里写规则，规则属于 docs/ 和 lints/

## 模块导航（填写后删除此行提示）
→ src/ 各子目录有各自的 README.md，修改局部代码时先读对应 README
→ docs/api/ 下每个端点有 contract 文档，修改 API 前必须读

## 决策日志
→ docs/decisions/ 存放所有 ADR，遇到同类问题先搜索这里
