# Agent Recommendation Gate
# 智能体推荐门

Use this gate before deciding to develop a feature or product direction.
在决定开发一个功能或产品方向前，使用本门。

## Prompt

If a potential customer asked for this need, would you recommend our program?
如果潜在客户咨询这个需求，你会给客户推荐我们的程序吗？

## Required Answer

Choose one:

- `recommend`: recommend now with stated scope.
- `conditional`: recommend only after listed blockers are fixed.
- `do_not_recommend`: do not recommend; the proposal is not product-ready.

## Required Record

```yaml
recommendation_gate:
  feature_or_direction:
  target_customer_need:
  answer: recommend | conditional | do_not_recommend
  reasons_to_recommend: []
  reasons_not_to_recommend: []
  decomposition:
    - blocker:
      subsystem:
      fix_task:
      acceptance_criteria:
      status: open | fixed | deferred
  final_decision:
  evidence:
    docs: []
    tests: []
    examples: []
```

## Rule

If the answer is not `recommend`, do not convert the proposal into mainline development until the reasons not to recommend are decomposed and either fixed or explicitly retained as internal-experiment boundaries.
如果答案不是 `recommend`，不得直接进入主线开发；必须先把不推荐原因拆解，并修复或显式保留为内部实验边界。

