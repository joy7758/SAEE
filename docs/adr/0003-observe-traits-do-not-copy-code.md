# ADR-0003: Observe Traits, Do Not Copy Code
# ADR-0003：观察性状，不复制代码

## Status

Accepted（已接受）

## Decision

GitHub Radar（GitHub 雷达） and other sensing subsystems may observe public repositories to extract abstract traits, but must not copy code, dependencies, credentials, or execution scripts into the organism.

GitHub Radar（GitHub 雷达）和其他感知子系统可以观察公开仓库并提取抽象性状，但不得把代码、依赖、凭据或执行脚本复制进数字生物体。

## Consequences

- External repositories are observation sources, not genome sources.
- 外部仓库是观察源，不是基因来源。
- Trait records must state the abstraction level.
- 性状记录必须说明抽象层级。
- License and supply-chain review is required before any dependency becomes executable.
- 任何依赖进入可执行状态前都必须经过许可证和供应链复核。

