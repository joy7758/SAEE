# SAEE Pilot Dataset Quality Control v0.1

状态：`rules_only_not_executed`。质量规则不等于质量结果。

## Structural checks

- 每个记录通过对应 JSON Schema；
- 所有必需字段存在，未声明字段被拒绝；
- identifier 在其命名空间唯一且格式稳定；
- `episode_id`、`task_id`、trace、bundle 和 annotation 引用一致；
- 时间使用 RFC 3339，摘要使用声明算法的规范语法；
- 数据来源枚举与批准的 manifest 一致。

## Evidence consistency checks

- resource receipt ref 能解析到同一 episode 的明确对象；
- authorization 的 action、scope 与有效时间关系可检查；
- human oversight 的 action、scope 和时序可检查；
- execution effect 与 action/resource 的 causal link 两端存在；
- trace observation 不得自动充当 receipt、authorization 或 causal evidence；
- 对缺失关系保留显式缺失，不补造默认值。

## Annotation quality

- 每个主标注单位由两名标注者独立处理；
- 记录原始标签、缺失集合、错误关系集合与信心值；
- 分歧必须复核，未解决分歧进入独立 adjudication；
- 保留初标和裁决，不静默覆盖；
- pilot 报告一致性、分歧率和裁决率，未达码本目标时停止主评估。

## Leakage prevention

标注者不得看到：

- evaluator 输出或 reason codes；
- expected/reference label；
- 其他标注者的答案；
- scenario 文件中的 condition expectation；
- 会直接暴露类别的文件名或目录名。

数据准备者应生成 annotator view 与 evaluator view 两个分离清单，并用随机、不含标签语义的 episode 标识。主评估前冻结泄漏检查；发现泄漏的记录必须隔离并按预注册规则处理。

## Quality report boundary

未来 quality report 必须同时给出失败数、排除数、未决数和修改历史。v0.1 没有数据，因此没有结构通过率、标注一致性或质量得分。

