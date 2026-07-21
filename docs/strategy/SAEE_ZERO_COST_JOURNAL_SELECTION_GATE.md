# SAEE 真实零费用期刊选择门

Status（状态）: `constitutional_mandatory`

Authority（权威）:
`docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md#第十一章学术期刊真实性与零费用发表门禁`

## Gate Result

只有同时满足下列条件的目标才可进入 manuscript preparation、portal draft、upload 或
final submission：

```text
venue_type=peer_reviewed_scholarly_journal
real_journal_verification_required=true
mandatory_author_cost=0
cost_evidence_source=official
unknown_cost_policy=stop_and_reject_venue
payment_authorized=false
author_budget_for_mandatory_publication_fees=0
paid_fallback_allowed=false
```

Author directive reconfirmed on 2026-07-19（作者于 2026-07-19 再次确认）:

> 只选择真实、可核验的同行评审学术期刊，并且必须存在作者侧强制费用为零的正常发表路线。
> 作者没有支付 APC、投稿费、版面费、注册费或其他强制发表费用的预算。

该约束是 venue-selection stop rule（期刊选择停止规则），不是录用后再讨论的付款偏好。
任何付费路线都不得作为“先投稿再说”的 fallback（后备路线）。

## Required Evidence

- 出版商或学会的官方期刊页面；
- 可核验的 ISSN / eISSN；
- 官方 peer-review policy、editorial board 和 publication ethics；
- 可持续访问的卷期或文章归档；
- 官方 author guidelines；
- 官方 fee / open-access 页面；
- 核验日期和明确选择的零费用路线。

## Eligible Routes

- subscription / traditional route，且不收 mandatory APC、submission fee、page
  charge、mandatory color charge 或其他强制作者费用；
- diamond open access，且作者强制费用为零；
- hybrid journal 仅当作者可明确选择免费的 traditional route 时合格。

## Automatic Rejection

以下任一条件命中即输出 `VENUE_NOT_ELIGIBLE` 或 `COST_GATE_FAILED` 并停止：

- conference、workshop、poster、Late-Breaking Abstract、magazine、blog 或 preprint
  repository；
- fully open access 且 mandatory APC；
- mandatory submission fee、page charge、color charge 或 registration fee；
- 只能依赖尚未书面批准的 waiver 才可能免费；
- 费用未知、官方页面冲突或录用后才披露费用；
- 期刊身份、同行评审或归档信息无法从官方来源核验。

## Truth Separation

```text
venue_cost_screened != package_ready
package_ready != portal_draft
portal_draft != uploaded
uploaded != submitted
submitted != accepted
accepted != published
published != doi_assigned
```

本门禁不授权投稿，不授权付款，也不把任何本地 package、draft、upload 或 acceptance
记录升级为 published 或 externally validated。

## ALIFE 2026 Decision

`lb120` 的外部门户证据是 `Accept (Confirmed)`，但它属于 Late-Breaking Abstract /
poster conference route。作者于 2026-07-19 决定不注册、不付款、不继续展示。当前必须
记录为：

```text
external_portal_status=Accept (Confirmed)
author_participation_status=abandoned_before_registration
conference_registration_completed=false
registration_payment_made=false
external_withdrawal_completed=false
author_route_decision=FINAL_ABANDONED
route_reactivation_allowed=false_without_new_explicit_author_instruction
```

`author_route_decision=FINAL_ABANDONED` 表示作者不再注册、不付款、不参会、不展示；
它不伪造 Linklings 已经完成外部撤回。若以后获得门户撤回或主办方确认，才可把
`external_withdrawal_completed` 更新为 `true`。

## Current AIJ Eligibility Verification

截至 2026-07-19，`Artificial Intelligence`（AIJ）通过本门禁：

```text
official_journal_name=Artificial Intelligence
publisher=Elsevier
online_issn=1872-7921
print_issn=0004-3702
peer_review=single_anonymized_minimum_two_independent_reviewers
selected_route=subscription
official_subscription_publication_fee=0
optional_open_access_apc_usd=4050
optional_paid_oa_selected=false
mandatory_author_cost=0
venue_eligible=true
verification_date=2026-07-19
```

详细官方证据与提交前复核规则见
`paper_reconstructability_readiness/AIJ_VENUE_AND_COST_VERIFICATION.md`。
