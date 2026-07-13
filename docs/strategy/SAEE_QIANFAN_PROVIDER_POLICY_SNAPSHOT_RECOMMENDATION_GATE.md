# SAEE Qianfan Provider Policy Snapshot Recommendation Gate
# SAEE 千帆供应商政策快照推荐门

## Recommendation question

If a customer asks whether SAEE may use Baidu Qianfan as a bounded external
agent host, would we recommend a machine-readable policy snapshot before any
commercial data is sent?

如果客户询问 SAEE 是否可以把百度千帆作为受控外部智能体宿主，是否推荐在
发送任何商业数据前先生成机器可读的政策快照？

## Verdict

`recommend`

Recommend this snapshot for technical and retrieval review only. It records
official document locations, observed clauses, and unresolved retention/DPA
questions. It does not provide legal advice, sign a DPA, approve production,
or authorize customer data to be sent to Qianfan.

## Design check

- Strengthened subsystems: Global Sensing and Evolutionary Archive / Rollback
  Immune System by making provider-policy facts and uncertainty retrievable.
- Keeps the Qianfan bridge bounded to sanitized fixtures and user-supplied
  credentials; no new network path or tool is introduced.
- Preserves the rule that provider policy text is evidence for review, not a
  production or legal truth surface.

## Evidence boundary

| Item | Result |
| --- | --- |
| Official agreement catalog located | `true` |
| Special-agreement data-use clauses captured | `true` |
| Explicit retention period verified | `false` |
| DPA completed | `false` |
| Privacy/legal review completed | `false` |
| Production provider approval | `false` |

## Final decision

Proceed with a dated, source-linked policy snapshot for agent retrieval. Keep
the provider-data blocker open until an authorized owner completes retention,
cross-border/data-processing, security, and DPA review.
