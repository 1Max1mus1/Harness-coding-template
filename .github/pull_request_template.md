## 变更摘要
<!-- 1-2 句话描述这个 PR 做了什么 -->


## 对应 INTENT.md 验收条件
<!-- 这个 PR 实现了 docs/INTENT.md 里的哪条完成标准？ -->
- [ ] 实现了验收条件：[复制对应条目]

## Agent 自检清单
<!-- 提交前必须全部打勾 -->
- [ ] `python lints/check_all.py` 全部通过 ✅
- [ ] `pytest` 全部通过 ✅
- [ ] 无新增 FORBIDDEN 依赖（见 docs/STACK.md）✅
- [ ] 所有新函数/组件有类型注解 ✅
- [ ] 无 TODO/FIXME 残留（NEEDS_DECISION 除外）✅

## 架构影响
<!-- 回答以下问题，如无变化请写"无" -->
- 改动了哪些模块边界？
- 是否修改了 Pydantic Schema / API contract？（如是，是否同步更新了 docs/api/？）
- 是否引入了新的外部依赖？（如是，是否更新了 docs/STACK.md？）

## 需要人工决策的点
<!-- 列出代码里所有 [NEEDS_DECISION] 标注，或写"无" -->
- 无
