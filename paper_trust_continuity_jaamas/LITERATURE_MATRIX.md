# Literature and Standards Matrix

Snapshot date: 2026-07-17

This is a scoped synthesis matrix, not a systematic-review dataset. It records
the literature families required to ground a Viewpoint and to distinguish the
proposed agenda from adjacent work.

| Cluster | Representative sources | What the cluster establishes | Remaining question used by this paper |
| --- | --- | --- | --- |
| Computational trust and reputation | Sabater and Sierra; Pinyol and Sabater-Mir; Braga et al. | Rich models exist for estimating whether an agent or partner should be relied upon. | How should previously established reliance be reinterpreted after identity, evidence, delegation, or state changes? |
| Trust maintenance and temporal logic | Khosravifar et al.; Drawel et al. | Trust assessments can be updated as behavior changes, and trust relations can be expressed and verified using temporal logic. | Does claim-ground applicability across heterogeneous evidence sources require a distinct interpretation task, or can these methods already answer it? |
| Trust transfer and repair | Diab and Demiris; Kox et al. | Trust-related experience can be transferred across similar tasks, and human trust can be repaired after agent violations. | How does transfer or repair differ from deciding whether prior declared evidence still covers a current bounded claim? |
| Delegation chains | Hu; Baqueta and Tacla | Trust-aware delegation, recursive sub-delegation, and delegation-chain formation are established research problems. | Which recorded scope and evidence remain applicable after later decomposition, re-delegation, or environmental change? |
| Mutable language-model-agent identity | Hu, Rong, and Van Kleek | Persistent-identity assumptions behind reputation are undermined by mutable models, prompts, tools, memories, and composite agents. | Which observable bindings are sufficient for a claim-scoped continuity judgment without inventing a persistent personal essence? |
| Contract-based multi-agent verification | Dewes and Dimitrova | Quantitative assume-guarantee contracts can support compositional design and verification of local and shared requirements. | Is continuity interpretation merely another contract property, or does it require claim-ground applicability across evidence sources not represented in the contract? |
| Agentic trust, risk, and security management | Raza et al. | Agentic multi-agent trust, risk, security, lifecycle governance, explainability, and evaluation already form a broad research space. | Does continuity add a measurable decision problem, or should it remain a subproblem inside this broader lifecycle framework? |
| Message and agent trust management | He et al. | Inter-agent message trustworthiness and accumulated agent-level trust can be assessed and used in trust-aware action policies. | How does message or agent trustworthiness differ from whether earlier declared grounds still cover a later bounded claim? |
| Trace-to-logic assurance | Paduraru et al. | Message-action traces can support interpretable rule induction and deviation signals under contract-first governance. | Can the same trace and contract methods answer continuity questions at equal or lower cost? |
| Reliable-autonomy assurance | Fisher et al.; Abbass et al. | Autonomous systems need evidence-backed assurance, verification, and certification arguments. | How can assurance grounds be kept temporally scoped as the system evolves and crosses organizational boundaries? |
| Responsibility and accountability | Grossi et al.; Yazdanpanah et al.; Sloan and Ajmeri; Constantinescu and Kaptein | Responsibility depends on organizational roles, commitments, interactions, and evidence. | How can responsibility-relevant evidence remain connected across repeated delegation and long-running execution? |
| Long-horizon agent evaluation | Park et al.; Huang et al.; Ma et al.; Xu et al. | Long and multi-turn tasks expose planning, partial observability, collaboration, and evaluation limitations that final success rates hide. | How should evaluations track whether the grounds for continuing remain valid, not merely whether a final task was completed? |
| Provenance and transparent statements | W3C PROV; SCITT RFC 9943 | Provenance and append-only signed-statement transparency support traceability and auditability. | What claim does a traceable or transparent artifact support now, under current scope and time? |
| Observability | OpenTelemetry specification | Traces, metrics, logs, context, and resources can be collected and propagated. | When are observed signals adequate and still applicable to a current trust claim? |
| Workload identity | SPIFFE specification | Workload identity can be issued and cryptographically verified across heterogeneous environments. | How should identity assertions be interpreted when their temporal accuracy, scope, or meaning changes? |
| Agent interoperability | Model Context Protocol; Agent2Agent Protocol | Agents can discover tools and peers, exchange information, and manage asynchronous long-running tasks. | How can connection and task-lifecycle evidence be composed without treating interoperability as continuing trust? |
| Risk management | NIST AI Risk Management Framework | Risk management is continuous, contextual, and socio-technical. | Which continuity interpretations improve specific continue, pause, re-confirm, or review decisions? |
| Legal record keeping and oversight | Regulation (EU) 2024/1689 | Certain high-risk AI systems are subject to scoped logging, documentation, transparency, oversight, and retention duties. | How can continuity research avoid converting context-specific legal duties into universal agent requirements or expanded surveillance? |

## Most Closely Related Work

1. Fisher et al. provide the closest assurance-oriented roadmap in the target
   journal. This paper differs by centering the temporal validity of trust
   grounds across multi-agent changes, rather than certification of an
   autonomous system as such.
2. Pinyol and Sabater-Mir and Braga et al. synthesize computational trust and
   reputation models. This paper does not propose another trust score; it asks
   when the evidence and assumptions underlying a bounded reliance claim remain
   applicable.
3. Yazdanpanah et al. provide a responsibility research agenda. This paper
   treats responsibility as one consumer of continuity evidence and keeps
   interpretation separate from authority and final responsibility allocation.
4. AgentBoard, MLAgentBench, and TheAgentCompany move evaluation toward
   multi-turn and consequential tasks. This paper focuses on the continuity of
   trust grounds during those tasks rather than capability or completion alone.
5. W3C PROV, OpenTelemetry, SPIFFE, SCITT, MCP, and A2A provide composable
   evidence sources and interoperability mechanisms. The proposed category does
   not replace them.
6. Khosravifar et al. and Drawel et al. are the closest temporal-trust
   predecessors. The manuscript must not claim that maintaining or formally
   reasoning about trust over time is new.
7. Diab and Demiris and Kox et al. cover trust transfer and repair. The
   manuscript's narrower object is the continuing applicability of declared
   grounds, not transfer of a trust level or restoration of a human attitude.
8. Hu and Baqueta and Tacla establish delegation as a trust problem and model
   delegation chains. The manuscript contributes no claim of priority over
   delegation-chain research.
9. Hu, Rong, and Van Kleek provide the strongest identity-continuity precursor
   for language-model agents. The proposed identity dimension adopts this
   problem rather than claiming to discover it.
10. Dewes and Dimitrova provide a strong formal-contract baseline. If a
    continuity question can be expressed and verified as an ordinary contract
    property, a separate category is unnecessary.
11. Raza et al. provide the closest recent broad review of trust, risk, and
    security management in language-model-based multi-agent systems. The
    manuscript must show a narrower operational unit than that umbrella.
12. He et al. provide a direct message- and agent-level trust-management
    baseline. The manuscript must not relabel message trustworthiness as
    continuity.
13. Paduraru et al. provide a direct trace-based assurance baseline. The
    manuscript must test whether claim-ground applicability adds decision value
    beyond deviation detection and contract-first trace analysis.

## Source-Quality Rule

The manuscript prioritizes journal articles, archival conference proceedings,
accepted papers, standards, and official protocol specifications. Unaccepted
preprints and withdrawn submissions are excluded from the core argument.
Current protocol versions and journal requirements must be rechecked
immediately before submission.

The exact phrase `trust continuity` is not treated as novel or proprietary.
The paper's proposed construct is the narrower claim-ground-transition
relation called `trust continuity interpretation`, whose incremental value
must be tested against the adjacent methods above.
