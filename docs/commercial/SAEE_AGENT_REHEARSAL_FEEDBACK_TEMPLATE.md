# SAEE 智能体演练匿名反馈模板 v0.1

状态：`blank_no_feedback`。禁止填写姓名、邮箱、公司名称、联系方式、真实日志、
生产 Trace、凭据、客户数据或可识别自由文本。

## Session Boundary

- `anonymous_session_id`：无含义本地编号
- `consent_confirmed`：yes / no
- `synthetic_material_only`：必须 yes
- `recording_created`：必须 no
- `customer_data_received`：必须 no

## Role Category

- agent_platform_team
- evaluation_or_red_team
- governance_or_risk
- other_non_identifying

## Before Demo

- `problem_recognition`：recognized / not_recognized / unclear
- `current_rehearsal_exists`：yes / partial / no / unclear
- 当前上线评审阶段：只记录无识别性的类别摘要

## After Demo

- `rehearsal_workflow_fit`：fit / partial / no_fit / unclear
- `evidence_output_value`：useful / partial / not_useful / unclear
- `scenario_relevance`：high / mixed / low / unclear
- `integration_feasibility`：feasible / conditional / infeasible / unclear
- `most_useful_component`：scenario / trace / evidence_gap / benchmark / mcp / none / unclear
- `missing_capability_categories`：adapter / environment / tool / memory / policy / report / trust / other_non_identifying
- `adoption_barrier_categories`：data_boundary / integration / trust / ownership / methodology / cost_unknown / other_non_identifying
- `follow_up_protocol_interest`：yes / no / unclear

## Boundary Confirmation

- 未讨论或承诺价格、合同或 Pilot：yes / no
- 未提交真实 Agent、日志、凭据或客户数据：yes / no
- 未作安全、合规、法律或上线批准：yes / no
- 未把兴趣解释为购买意愿：yes / no

## Session Result

- `valid_protocol_session`：yes / no
- `stop_reason_category`：none / consent / data_boundary / overclaim_request / facilitator_boundary / other_non_identifying

模板保持空白，直到人工批准单次访谈。
