# Multi-Agent Long-Running Trust Infrastructure: A Research Agenda for Trust Continuity Interpretation

**Article type:** Viewpoint

**Author:** Zhang Bin

**Affiliation:** Shanxi Youqibing E-Commerce Co., Ltd., Yuncheng, Shanxi, China

**Corresponding author:** joy7759@gmail.com

**ORCID:** 0009-0002-8861-1481

## Abstract

Autonomous-agent research is moving from short, isolated interactions toward tool-using, long-running, and multi-agent work. This transition creates a problem that is not captured by task success, observability, one-time identity verification, authorization, or conventional trust scores alone: the grounds that justified relying on an agent at one time may no longer support the same claim after changes in identity, evidence, delegation, or task state. We propose **multi-agent long-running trust infrastructure** as a candidate research category and **trust continuity interpretation** as its central analytic function. Trust continuity interpretation asks whether prior trust grounds still support a current, explicitly bounded claim; it produces qualified conclusions, evidence gaps, uncertainty, and re-confirmation conditions rather than authority or a universal score. We organize the agenda around four continuity dimensions: identity, evidence, delegation, and observable state. We then position the category as a composition layer over existing provenance, observability, workload-identity, transparency, tool-connectivity, and agent-interoperability infrastructure, not as a replacement for those systems. Finally, we state falsifiable research questions, baseline comparisons, measurement criteria, and stop conditions. The proposal should be rejected or narrowed if ordinary observability review performs equally well, continuity judgments cannot be annotated reliably, the approach requires inaccessible internal model states, or its costs exceed its decision value. The intended contribution is a rigorous agenda for testing whether temporal trust interpretation is a distinct and useful multi-agent-systems problem.

**Keywords:** autonomous agents; multi-agent systems; trust continuity; evidence; delegation; long-running agents

## 1 Introduction

Research on autonomous agents and multi-agent systems has long examined trust, reputation, commitments, norms, verification, responsibility, and organizational structure. Computational trust models estimate whether one agent should rely on another; reputation mechanisms aggregate experience in open systems; assurance approaches seek evidence that autonomous systems behave reliably; accountability models connect actions to commitments, roles, and responsibility [1-8]. These traditions supply much of the conceptual vocabulary needed for dependable agent systems.

The temporal dimension is not absent from prior work. Computational models maintain trust as behavior changes [23]; temporal logics formalize individual, group, distributed, and propagated trust [24]; human-robot research transfers trust-related experience between tasks [25]; and human-agent research studies trust repair after violations [26]. Agent delegation and delegation-chain formation have also been studied for decades [27, 28]. Most recently, the mutable composition of language-model agents has been argued to undermine the persistent identity assumptions required by reputation mechanisms [29]. Our argument therefore is not that trust over time, delegation, repair, transfer, or identity persistence are newly discovered problems.

Recent work further raises the novelty burden. Quantitative assume-guarantee contracts support compositional design and verification of multi-agent systems [30]. A recent review organizes trust, risk, security, lifecycle governance, and evaluation concerns for language-model-based multi-agent systems [31]. Message- and agent-level trust management now evaluates unreliable inter-agent communication [32], while trace-to-logic assurance derives interpretable deviation signals from message-action traces under contract-first governance [33]. The proposed agenda must therefore distinguish continuity interpretation not only from classical trust and assurance, but also from contract satisfaction, message trustworthiness, broad risk management, and trace-deviation analysis.

The operational setting is nevertheless changing. Language-model-based agents can now browse, call tools, write and execute code, exchange messages, and pursue tasks through many interactions. Research environments increasingly evaluate multi-turn progress, partially observable tasks, open-ended experimentation, workplace-like activity, and multi-agent collaboration rather than a single answer [10-15]. The shift matters even before agents become consistently successful. A system that acts over hours, days, or organizational handoffs accumulates changes in models, prompts, runtime versions, tools, evidence, delegated scope, environmental state, and human decisions. Each change may be locally reasonable. Their composition may invalidate the assumptions that supported an earlier decision to rely on the system.

Consider a simple case. An organization assigns an agent a bounded goal, verifies its workload identity, grants a limited tool set, observes a successful test run, and permits continued work. Later, the task is delegated to a sub-agent, the model version changes, a key test becomes stale, the environment changes, and the sub-agent refines the plan. No single event necessarily constitutes failure. The relevant question is not merely whether logs exist, credentials remain syntactically valid, or the final task succeeds. It is whether the original grounds for a particular trust claim still apply to the current actor, evidence, delegated scope, and observable task state.

We call the specific combination studied here the **trust continuity problem**. It is a temporal and relational interpretation problem: given a bounded claim at time \(t_0\), the grounds that supported it, and a sequence of observed transitions, determine what, if anything, those grounds support at time \(t_n\). The word *continuity* does not imply an unbroken guarantee. It names the object of inquiry: whether support persists, narrows, expires, conflicts, or becomes unresolved as conditions change. We do not claim to coin the phrase *trust continuity*. Our proposed construct is the narrower, claim-scoped function defined below as *trust continuity interpretation*.

This Viewpoint proposes **multi-agent long-running trust infrastructure** as a candidate research category for studying that problem. Its central analytic function is **trust continuity interpretation**: a claim-scoped assessment of whether prior trust grounds remain applicable to a current claim. The output is not an authorization decision and not a scalar measure of an agent's general trustworthiness. It is a structured explanation of supported scope, missing or conflicting evidence, uncertainty, and conditions for re-confirmation.

The paper makes four contributions.

1. It defines a candidate category around the temporal validity of trust grounds in long-running multi-agent systems.
2. It specifies trust continuity interpretation as a proposed bounded analytic function, explicitly separated from authorization and execution and distinguished from temporal trust maintenance, transfer, and repair.
3. It decomposes the problem into identity, evidence, delegation, and observable-state continuity.
4. It provides a falsifiable research agenda, including simpler baselines and conditions under which the category should be narrowed or abandoned.

The proposal is intentionally conservative. We do not claim that the category is already recognized, that a complete infrastructure exists, or that the problem requires a new universal protocol. We argue instead that the problem is timely enough to state precisely and test against existing alternatives.

## 2 Scope and synthesis method

### 2.1 A scoped conceptual synthesis

This is a Viewpoint, not a systematic review. To avoid presenting an individual intuition as a field-level conclusion, we conducted a scoped conceptual synthesis across two source groups as of 17 July 2026.

The first group contains archival research that directly defines or evaluates an adjacent problem:

- computational trust and reputation in multi-agent systems [1-3];
- trusted autonomy, reliability assurance, and certification [4, 5];
- organizational responsibility, accountability, and commitments [6-8];
- temporal trust maintenance, formal trust reasoning, transfer, and repair [23-26];
- delegation and identity-persistence problems [27-29];
- contract-based multi-agent verification, agentic trust-risk-security management,
  message-level trust assessment, and trace-based runtime assurance [30-33];
- long-horizon, multi-turn, and consequential agent evaluation [9-14]; and
- recent framing of multi-agent artificial intelligence and autonomy [15].

The second group contains active infrastructure specifications whose outputs could serve as inputs to continuity interpretation:

- provenance models [16];
- observability data [17];
- workload identity [18];
- signed-statement transparency [19];
- tool and context interoperability [20]; and
- agent-to-agent task interoperability [21].

We also use the NIST AI Risk Management Framework as a representative risk-management reference [22]. Sources were included when they met at least one of four conditions: they provided a review or research agenda for an adjacent field; defined an assurance or accountability model; reported an archival evaluation involving extended agent interaction; or specified a current interoperable infrastructure boundary. Unaccepted and withdrawn preprints are not used to support the central claim.

The synthesis asks the same three questions of each source family: What fact or relation can it establish? Over what scope and time is that result valid? What additional inference would be required to apply the result to a current bounded trust claim? This method does not establish literature exhaustiveness. It supplies a transparent basis for distinguishing the proposed question from adjacent ones.

### 2.2 Terminological boundaries

We use *agent* broadly for a computational system that selects or sequences actions toward declared objectives, including language-model-based agents. A *multi-agent system* contains two or more agents whose actions, messages, or delegated tasks affect a shared process. *Long-running* is relational rather than a fixed duration: a run is long-running when it crosses enough state, identity, evidence, delegation, or environmental transitions that a one-time trust judgment can no longer be assumed to apply without re-examination.

We use *trust claim* to mean an explicit, bounded proposition used to justify reliance. Examples include “agent A's test evidence is sufficient to continue this coding task,” “agent B is acting under delegation D for tool set T,” or “artifact X was produced by the declared workflow under version V.” This differs from a claim that an agent is trustworthy in general.

*Trust grounds* are observable reasons offered in support of a trust claim: identity records, evidence artifacts, delegation records, traces, policy decisions, evaluation outputs, or other references. Grounds are neither reality itself nor a guarantee that the claim is true. They are inputs to a bounded judgment.

*Interpretation* means evaluating the applicability, coverage, consistency, and temporal relevance of those grounds. It does not mean granting permission, authenticating an identity, executing a policy, controlling an agent, or assigning final legal responsibility.

The phrase *trust continuity* is not asserted to be unique. Related uses occur in identity, session, and operational-trust discussions, while archival multi-agent research already studies trust maintenance, trust over time, transfer, repair, and delegation [23-28]. We use *trust continuity interpretation* only for the proposed claim-ground-transition relation in this paper. The construct is novel only if that relation yields stable and useful decisions beyond those adjacent methods; this is an empirical hypothesis, not a naming claim.

### 2.3 Positionality and use of generative assistance

The agenda emerged from work on SAEE, a research program whose current engineering mainline is limited to agent-evidence integration, evidence evaluation, and readiness-oriented recommendations. No current SAEE capability is treated as proof that trust continuity interpretation is implemented or effective. The paper is deliberately framed so that its hypotheses can be tested independently of SAEE.

A generative large-language-model assistant was used to organize source notes, compare journal requirements, and draft language. The human author remains responsible for source verification, argument selection, authorship, disclosures, and every claim in the submitted version. Any final submission must update this disclosure to reflect actual use and the journal's policy.

## 3 From one-time trust to continuity of grounds

### 3.1 What existing trust models usually ask

Computational trust and reputation research offers rich approaches for deciding whether an agent should rely on another agent, particularly in open systems where direct knowledge is incomplete [1-3]. Models may use past interactions, witness reports, social relations, cognitive beliefs, uncertainty, or domain-specific performance. This literature demonstrates that trust is contextual and decision-related rather than a simple property.

Our proposed question is downstream and temporal. Suppose a model, policy, or human reviewer concluded at \(t_0\) that reliance was justified for claim \(C_0\) on grounds \(G_0\). At \(t_1\), the agent's implementation, evidence, delegated task, or operating state changes. A new trust estimate could be computed, but that alone does not explain whether the earlier grounds remain applicable, which assumptions broke, or what evidence must be renewed. Trust continuity interpretation focuses on the relation among the prior claim, its grounds, the transition, and the current claim.

This distinction also separates the agenda from reputation continuity. Reputation may change as interactions accumulate. Trust continuity asks whether a specific earlier reliance basis can be carried forward. An agent may retain a high reputation while a particular delegation has expired. Conversely, a newly instantiated agent may lack reputation but inherit a narrowly verifiable workload identity and a valid, limited delegation. The relevant object is not a global score but the support relation for a bounded claim.

### 3.2 Closest conceptual collisions

Maintenance-based trust directly addresses changing behavior by retrospectively updating trust assessments [23]. Temporal trust logics represent trust relations over time and support design-time verification of individual, group, distributed, and propagated trust [24]. Trust-transfer research asks when prior experience can inform trust in a new task or context [25], while trust-repair research asks how human trust can be rebuilt after an agent violation [26]. These are not weak baselines; they are close predecessors that any continuity account must respect.

The proposed distinction lies in the object being interpreted. Trust continuity interpretation does not primarily update a trust estimate, verify a temporal trust proposition, transfer a learned trust level, or repair a human attitude. It asks whether identified grounds, such as an identity binding, artifact, delegation record, trace, or evaluation, still support a specified current claim after heterogeneous changes. This distinction may prove too narrow to justify a separate category. If the closest prior methods answer the same operational questions at equal or lower cost, the category should be merged into those fields.

Delegation and identity provide equally important collisions. Early work connected agent trust with delegation [27], and recent work models recursive sub-delegation and delegation-chain formation in dynamic environments [28]. Language-model-agent research now challenges the persistent identity assumptions behind reputation by emphasizing the mutability of models, prompts, tools, memory, and composite-agent structure [29]. Our delegation and identity dimensions therefore organize prior problems around claim applicability; they do not claim to originate those problems.

The collision is sharper in recent agentic-system work. Contract-based verification can establish whether local and shared quantitative requirements are compositionally satisfied [30]. Trust-risk-security management surveys organize a broader lifecycle and governance space [31]. Attention-based trust management estimates whether messages and agents are trustworthy [32]. Trace-to-logic assurance learns recurring operational relations and detects deviations from contract-admissible behavior [33]. Continuity interpretation is defensible only if it answers a different operational question: whether the declared grounds for a prior, bounded claim still cover the current subject, evidence, delegation, and observable state. If the recent methods can answer that question with equal accuracy and lower cost, this agenda should be absorbed into them.

### 3.3 Why assurance and certification are necessary but not sufficient

Trusted-autonomy and certification research asks how reliable behavior can be verified and how evidence can support deployment or regulatory decisions [4, 5]. Fisher et al. emphasize that autonomous-system assurance requires evidence, verification, and an evolving relationship among research, engineering, and regulation [5]. Such work is close to the proposed agenda because assurance arguments depend on assumptions, system boundaries, and artifacts.

Continuity interpretation addresses what happens between or after assurance events. A certified component can be used in an uncertified composition. A valid test result can be applied to a changed environment. A verified policy can remain unchanged while the delegated task exceeds its intended scope. An assurance case may contain the relevant provenance, but the current system still needs to determine whether its supporting assumptions hold for a later claim. The proposed category therefore does not replace certification. It studies the temporal applicability of certification and other assurance grounds.

### 3.4 Why accountability is a consumer, not a synonym

Responsibility and accountability research shows that actions must be understood in organizational and interactional context. Organizational structure shapes responsibility [6]; responsibility reasoning in autonomous systems involves technical, legal, and social questions [7]; commitments can provide semantics for accountable negotiation [8]. Multi-agent and organizational use of language-model-based agents further complicates responsibility gaps [9].

Trust continuity evidence could support accountability, but the concepts are not identical. Accountability asks who must answer for an action, what norm or commitment applied, and what remedy or explanation is due. Continuity interpretation asks whether prior grounds still support a current bounded claim. A continuity result may show that a delegation chain is unresolved; it cannot by itself assign legal responsibility. Keeping the two separate prevents an analytic layer from silently acquiring authority it does not possess.

### 3.5 Why final success and ordinary traces are insufficient

Long-horizon agent benchmarks increasingly expose planning, state tracking, partial observability, and collaboration problems. Generative agents illustrate how memory and reflection can shape behavior across extended interactions [10]. MLAgentBench evaluates iterative machine-learning experimentation and reports large variation across tasks, with long-term planning and hallucination among the challenges [11]. AgentBoard argues that final success rates reveal too little and adds progress-sensitive analysis for multi-turn agents [12]. TheAgentCompany evaluates agents in a simulated workplace and finds that difficult long-horizon tasks remain challenging even when simpler tasks can be completed [13]. More broadly, multi-agent artificial intelligence is becoming a distinct socio-technical object rather than merely a collection of independent model calls [15].

These evaluations motivate process-sensitive measurement. They do not automatically establish the validity of trust grounds. A trace can show that a tool was called, but not that the result covers the claim for which it is cited. A checkpoint can show progress, but not that a delegation remained valid. A successful outcome can coexist with an unauthorized route or stale evidence. A failed outcome can occur even when identity and delegation continuity were preserved. Performance evidence and continuity evidence intersect, but neither subsumes the other.

## 4 Candidate category: multi-agent long-running trust infrastructure

### 4.1 Category definition

We define **multi-agent long-running trust infrastructure** as the set of interoperable evidence sources, representations, and interpretive methods needed to assess whether previously established grounds still support a current bounded trust claim after time, system, agent, delegation, or state transitions.

The definition contains four restrictions.

First, it is **claim-scoped**. The object is not whether an agent is universally trustworthy, but whether specified grounds support a specified claim under stated conditions.

Second, it is **temporal**. The key input is a transition from prior conditions to current conditions. A snapshot may be valid evidence, but continuity cannot be inferred from a snapshot alone.

Third, it is **compositional**. The category should consume identity, provenance, observability, transparency, interoperability, policy, and human-decision signals from existing systems. It should not duplicate their issuance, collection, transport, or enforcement functions.

Fourth, it is **non-authoritative**. An interpretation can recommend re-confirmation, identify insufficient evidence, or support a human or policy decision. It cannot grant permissions or execute the world merely because it reports a favorable result.

### 4.2 Trust continuity interpretation

Let \(C_t\) be a bounded trust claim at time \(t\). Let \(G_t\) denote the declared grounds supporting that claim, including identity (\(I_t\)), evidence (\(E_t\)), delegation (\(D_t\)), observable state (\(S_t\)), and contextual constraints (\(X_t\)):

\[
G_t = \langle I_t, E_t, D_t, S_t, X_t \rangle.
\]

Let \(\Delta_{t_0:t_n}\) denote observed transitions between an earlier and current point. Trust continuity interpretation is not a numerical function that outputs “trust.” It is an assessment relation:

\[
\mathcal{T}(C_{t_n}, G_{t_0}, G_{t_n}, \Delta_{t_0:t_n})
\rightarrow \langle R, Q, U, K \rangle,
\]

where \(R\) is the support result, \(Q\) is the supported claim scope, \(U\) is unresolved uncertainty or conflicting evidence, and \(K\) is the set of conditions required for re-confirmation. A practical result vocabulary might include *supported within scope*, *conditionally supported*, *unsupported*, and *unresolved*. These labels are illustrative research objects, not a proposed standard or current schema.

The central invariant is that a favorable result at \(t_0\) is not inherited automatically at \(t_n\). Inheritance must be justified by evidence about relevant changes. Equally, any change should not automatically invalidate the prior result. The research challenge is to distinguish continuity-preserving transitions from transitions that narrow, break, or render support unresolved.

### 4.3 Why a universal trust score is the wrong target

A scalar score compresses distinct questions: identity validity, evidence coverage, delegation scope, state change, uncertainty, and decision stakes. Compression may be useful for ranking, but it obscures which claim is supported and why. It can also create false transitivity: a high identity-confidence score does not imply sufficient evidence; strong evidence does not imply valid delegation; valid delegation does not imply outcome correctness.

The proposed category therefore treats multidimensional explanation as primary. Aggregation may be studied for specific decisions, but a total score should not become the ontology of trust. The agenda is closer to an evidence-backed argument with explicit defeaters than to an agent credit rating.

## 5 Four continuity dimensions

### 5.1 Identity continuity

Identity continuity asks whether the current acting subject retains a verifiable and semantically relevant relationship to the subject named in the prior claim. The subject may be a workload, agent instance, model configuration, service, organizational role, or composite agent.

This problem is especially acute for language-model agents, whose behaviorally relevant identity may be distributed across mutable models, system prompts, tools, policies, memories, and multi-agent composition [29]. A stable display name or account identifier therefore cannot by itself establish continuity of the subject relevant to a prior claim.

Existing workload-identity systems provide crucial inputs. SPIFFE defines identities and verifiable identity documents for services across heterogeneous environments [18]. Its security considerations are especially instructive: an assertion true at issuance may not remain true at use; scope, interpretation, temporal accuracy, and veracity must all be considered. This illustrates the continuity problem inside an identity standard itself.

Identity continuity is not simply credential validity. A credential may remain cryptographically valid while the role, owner, model, purpose, or operating environment changes. Conversely, a restarted workload may receive a new credential while preserving a valid relation to the same narrowly scoped service identity. Relevant research questions include:

- Which subject attributes are stable enough to carry forward?
- Which changes require a new identity claim rather than a version update?
- How should parent-agent and sub-agent relations be represented?
- When does a valid foreign identity fail to support a local role interpretation?
- How can identity continuity be assessed without claiming a persistent personal essence for a software agent?

A minimal identity-continuity record would likely require a prior subject reference, a current subject reference, the binding authority, relevant versions, the transformation or handoff, validity intervals, and the exact claim that relies on the binding. Whether that information is sufficient is an empirical question.

### 5.2 Evidence continuity

Evidence continuity asks whether current and prior artifacts still cover the same claim, subject, action, scope, and time. W3C PROV provides a vocabulary for entities, activities, agents, derivation, attribution, and provenance exchange [16]. SCITT provides an architecture for transparent, signed supply-chain statements and an irrevocable history of registered statements [19]. These are strong building blocks for traceability.

Traceability is not applicability. A receipt can prove that a signed statement was registered; it does not prove that the statement is complete or correct. A provenance graph can show derivation; it does not decide whether an old test applies to a new binary. A hash can prove byte identity; it does not prove semantic coverage. Evidence continuity therefore requires at least five relations:

1. **Provenance:** where the artifact came from and how it was produced.
2. **Claim binding:** which proposition the artifact is offered to support.
3. **Coverage:** which parts, conditions, and time interval the artifact covers.
4. **Revision:** whether the artifact was superseded, invalidated, or narrowed.
5. **Conflict:** whether new evidence contradicts or undercuts it.

The principle that evidence is not reality is fundamental. Evidence can be authentic and still false; complete for one claim and irrelevant to another; timely at collection and stale at use. A continuity system that equates evidence existence with truth would increase rather than reduce false reliance.

### 5.3 Delegation continuity

Delegation continuity asks whether a task or authority relation remains within its declared source, recipient, scope, purpose, validity period, and re-delegation conditions as work moves among agents. It is related to commitments and organizational responsibility [6-8], but it is not an identity-and-access-management service and does not issue authority.

Prior work already connects trust to agent delegation [27] and models recursive sub-delegation and delegation-chain formation under changing behavior [28]. The added question here is not whether an agent can select a trusted delegate. It is whether the evidence and scope that justified a recorded handoff still support the current claim after later decomposition, re-delegation, or environmental change.

Agent interoperability makes this question operationally urgent. The Agent2Agent protocol supports discovery, collaboration, delegation, asynchronous interactions, and long-running tasks without requiring agents to share internal state [21]. Those capabilities enable valuable composition. They also mean that a task can cross system boundaries while the evidence needed to interpret its continuing scope remains distributed.

Delegation continuity needs to distinguish at least four transitions:

- a valid handoff within the same scope;
- a constrained refinement permitted by the delegator;
- a re-delegation whose authority is unresolved; and
- an expansion or substitution not supported by the recorded delegation.

The research problem is not to forbid change. Long-running work requires clarification, refinement, and re-planning. The problem is to preserve the lineage of why the change was allowed, who proposed and accepted it, what fields could change, what evidence supported it, and when it expires. Missing authority evidence should generally produce an unresolved interpretation, not an automatic accusation of drift or misconduct.

### 5.4 Observable-state continuity

Observable-state continuity asks whether the current declared task state can be related to a known baseline through explainable, evidence-backed transitions. The term *observable* is essential. The agenda does not presume access to a model's hidden thoughts, latent objectives, or complete internal state.

For many agentic tasks, an operational state may include a declared goal, constraints, plan version, evidence references, actions, outputs, environment references, and stop conditions. A transition can be normal evolution, an authorized change, re-planning, or an unexplained divergence. The challenge is to identify the smallest representation that improves decisions without building a universal state engine.

Long-horizon evaluations already show the value of intermediate progress and action-sensitive analysis [10-13]. State continuity shifts the dependent variable. Instead of asking only whether the agent made progress, it asks whether the current state still supports the same bounded claim about what the agent is doing and under which constraints.

This dimension carries the greatest scope risk. It can easily expand into goal engines, memory platforms, workflow orchestration, or automated governance. The research agenda must therefore start with observable state snapshots and narrow decisions. If useful continuity judgments require a complete new runtime, the proposed category has failed its minimum-complexity test.

### 5.5 Interdependence without collapse

The dimensions interact but should not be collapsed.

**Table 1. Continuity dimensions and non-inheritance boundaries.**

| Dimension | Core relation | Example discontinuity | What does not follow automatically |
| --- | --- | --- | --- |
| Identity | Prior subject to current subject | Model or workload changed without an adequate binding | Valid identity does not prove evidence sufficiency. |
| Evidence | Artifact to current claim | Test evidence applies to an earlier version only | Authentic evidence does not prove reality or completeness. |
| Delegation | Task/authority source to current scope | Sub-agent expands the task beyond recorded scope | Valid handoff does not authorize arbitrary re-delegation. |
| Observable state | Baseline to current task state | Constraints disappear through repeated re-planning | State similarity does not prove legitimate authority. |

A continuity failure in one dimension may be decisive for a specific claim but irrelevant to another. For example, a changed model version may break a claim about reproducibility while leaving a claim about artifact provenance intact. Claim-scoped interpretation is therefore more important than dimension-wide status.

## 6 Composition with existing infrastructure

Table 2 states the paper's boundary in operational terms. The listed systems
and methods remain authoritative for the functions they define; continuity
interpretation is only a proposed downstream use of their outputs.

**Table 2. Boundary between adjacent infrastructure and the proposed interpretive task.**

| Adjacent layer or method | What it establishes | What it does not establish by itself | Proposed continuity role |
| --- | --- | --- | --- |
| OpenTelemetry [17] | Recorded traces, metrics, logs, resources, and propagated context | Whether a recorded event still supports a later bounded reliance claim | Supplies observable transition evidence |
| SPIFFE and identity/authorization systems [18] | Workload identity or access decisions within a declared trust domain | Whether an earlier claim remains applicable after subject, issuer, scope, or environment changes | Supplies identity and authority assertions without being replaced |
| MCP [20] | Tool, resource, prompt, session, and capability exchange | Whether returned evidence covers the claim for which it is later used | Supplies tool and context interaction evidence |
| A2A [21] | Agent discovery, messages, task state, artifacts, and long-running interaction semantics | Whether delegated scope and prior evidence remain valid throughout a task | Supplies peer and task-lifecycle evidence |
| Governance and risk management [22, 31] | Policies, risk processes, approvals, and organizational decisions | A universal technical judgment that automatically authorizes action | Consumes qualified interpretations while retaining authority |
| Contracts, trust management, and trace assurance [30, 32, 33] | Requirement satisfaction, message or agent trustworthiness, and trace-deviation signals | The continuing applicability of every heterogeneous ground to a later claim | Serve as strong baselines and possible host fields for the proposed problem |

### 6.1 Provenance and transparency as evidence sources

W3C PROV formalizes provenance interchange and explicitly connects provenance with assessments of quality, reliability, and trustworthiness [16]. SCITT adds transparent, signed-statement registration and receipts for digital supply chains [19]. Together they can supply derivation, attribution, statement history, ordering, and integrity evidence.

Trust continuity interpretation should consume these outputs rather than invent parallel receipts or provenance formats. Its added question is interpretive: does the provenance or transparent statement still support the current claim under current conditions? That question may require version mappings, revocation or supersession evidence, claim scope, and context not contained in the original artifact.

### 6.2 Observability as execution evidence

OpenTelemetry standardizes APIs, software development kits, and data models for traces, metrics, logs, resources, and context [17]. It can reveal what happened in a distributed execution and connect events across services. An agent-specific observability platform can add semantic reconstruction and evaluation.

The proposed category does not compete with collection or storage. It needs observability because continuity cannot be assessed without transitions. It differs by asking whether observed events preserve the grounds for a bounded reliance claim. Sampling, missing spans, clock differences, semantic-convention drift, and cross-provider mappings become evidence-quality questions rather than mere telemetry quality questions.

### 6.3 Identity and authorization as authoritative inputs

SPIFFE and identity-and-access-management systems can authenticate workloads, express roles, and enforce access decisions [18]. Their outputs should remain authoritative within their declared domains. A continuity interpreter must not manufacture identity or infer permission from behavior.

Its role is narrower: preserve the relation between the identity or authorization assertion and the claim that used it, then flag when time, scope, issuer, subject, or interpretation changes. A favorable continuity result cannot elevate a permission. An unfavorable or unresolved result should not revoke credentials by itself. It can inform the identity or policy authority responsible for action.

### 6.4 MCP and A2A as interoperability sources

The Model Context Protocol standardizes interactions through which applications expose tools, resources, and prompts to language-model applications [20]. A2A standardizes agent discovery, messaging, task management, streaming, and asynchronous long-running interactions [21]. These protocols reduce integration friction and can expose valuable evidence about tool calls, resources, messages, task states, and peer capabilities.

Connection is not continuity. A successfully invoked tool can return evidence outside the relevant scope. An advertised agent capability can change. A long-running A2A task can survive a client disconnection while its original evidence or delegation assumptions become stale. The protocols provide events and boundaries; they do not have to answer every trust-interpretation question. A composition layer should respect that division of labor.

### 6.5 Governance and risk management as decision authorities

Governance platforms and risk-management processes decide policies, approvals, controls, exceptions, and organizational responses. The NIST AI Risk Management Framework emphasizes contextual and ongoing management rather than a one-time technical certification [22]. Continuity interpretation can provide decision context to such processes: which grounds remain supported, what changed, and what needs re-confirmation.

It must not become the final authority. Technical evidence does not settle legal responsibility, organizational acceptability, or social legitimacy. Human and institutional authorities retain those decisions. This separation is both a safety property and a scientific boundary: it allows the quality of an interpretation to be measured without conflating it with whether a deployment was approved.

## 7 Research agenda

### 7.1 RQ1: What is the minimum claim-ground-transition representation?

The first question is representational. What information is necessary to assess continuity without requiring a universal agent state model? Candidate elements include:

- a bounded claim and decision context;
- prior and current subject references;
- evidence references and provenance;
- delegation source, scope, recipient, and validity;
- observable state checkpoints;
- transitions, reasons, and accepting authority where applicable;
- defeaters, conflicts, and missing information; and
- time, version, and environment bindings.

Research should compare progressively richer representations. A minimal baseline might contain only a prior claim and current trace. Treatments could add claim-to-evidence bindings, then delegation lineage, then state transitions. Incremental value should be measured before adding fields. If a simpler provenance or observability representation performs equally well, the richer model should be rejected.

### 7.2 RQ2: Can continuity judgments be annotated reliably?

A category is not useful if experts cannot distinguish its labels. Initial studies should avoid a total trust label and annotate narrower questions, such as:

- Does evidence still apply to the current artifact version?
- Is the current actor bound to the subject named in the claim?
- Is the current task within the recorded delegation scope?
- Can the present state be explained by permitted transitions?

Ground truth should allow *unresolved* when the record is insufficient. Forcing ambiguous cases into supported or failed categories would confuse missing evidence with negative evidence. Studies should report inter-annotator agreement, adjudication rates, label prevalence, and failure modes. Domain experts and non-expert reviewers may be compared because practical infrastructure must communicate beyond its designers.

### 7.3 RQ3: Which inference methods are calibrated and explainable?

Possible methods range from deterministic rules and graph queries to probabilistic models and language-model-assisted review. The first objective should not be maximum classification accuracy. It should be calibrated reliance: favorable outputs should be used when correct, uncertain outputs should lead to re-confirmation, and explanations should expose decisive grounds and defeaters.

Evaluation should include precision and recall for discontinuities, coverage of supported scope, abstention quality, calibration, explanation faithfulness, and susceptibility to adversarial or misleading evidence. Language models may help interpret heterogeneous records but introduce their own non-determinism and evidence-grounding risks. Deterministic checks should remain baselines wherever the contract is explicit.

### 7.4 RQ4: Does continuity interpretation improve decisions?

The strongest test is decision utility, not annotation accuracy alone. Controlled studies could compare:

1. raw trace review;
2. conventional observability summaries;
3. claim plus provenance review;
4. claim-scoped continuity interpretation; and
5. human review with or without the interpretation.

Decision tasks should be concrete: continue execution, pause, re-confirm identity, request missing evidence, narrow delegated scope, or escalate to human review. Outcomes should include correct decisions, false continuation, unnecessary interruption, review time, evidence-preparation cost, latency, and reviewer overreliance.

An interpretation that catches more problems but blocks legitimate evolution may be worse than a simpler baseline. False positives are therefore first-class harms. So are verbose reports that do not change a decision. The category earns infrastructure status only if it improves consequential decisions across more than one narrow scenario at acceptable cost.

### 7.5 RQ5: How do continuity failures propagate across agents?

Multi-agent systems create composition questions. If agent A delegates to B, B calls C, and C produces evidence used by A, which trust grounds cross each boundary? A discontinuity can propagate silently when downstream evidence is reused upstream. Alternatively, an upstream identity change may not affect a downstream artifact claim.

Research should model claim dependencies rather than assume global contamination. Useful constructs may include claim-evidence graphs, delegation lineage, scoped invalidation, and re-confirmation propagation. The challenge is to prevent two opposite errors: treating every upstream change as invalidating everything, and treating locally valid downstream artifacts as preserving the whole workflow's trust basis.

### 7.6 RQ6: How robust is the interpretation under adversarial evidence?

Attackers can exploit continuity systems through replayed evidence, selective omission, ambiguous identity attributes, stale but valid credentials, fabricated transition reasons, conflicting clocks, or apparent compliance with an expired delegation. Even non-adversarial systems can produce the same patterns through retries and partial failures.

Security evaluation should test provenance breaks, cross-domain semantic collisions, evidence substitution, order manipulation, and strategic ambiguity. The interpreter should expose uncertainty rather than fill gaps with plausible narratives. Cryptographic integrity helps establish artifact and issuer relations; it does not establish semantic truth. This distinction should remain visible in both metrics and interfaces.

### 7.7 RQ7: When should continuity be re-evaluated?

Continuous re-evaluation after every event may be too costly and may create alert fatigue. Evaluation only at final outcomes is too late for consequential actions. Research should compare event-triggered, checkpoint-based, risk-based, and periodic strategies.

Potential triggers include subject changes, delegation events, evidence supersession, environment changes, policy changes, high-impact tool calls, or divergence from a declared plan. Trigger quality should be measured by detection delay, missed discontinuities, unnecessary evaluations, token and compute cost, and human-review burden. The goal is not maximal monitoring but timely interpretation before the relevant decision.

### 7.8 RQ8: Can standards be composed without semantic overreach?

Each infrastructure source has its own trust domain, version, semantics, and authority. A field named `role` or `status` in two systems may not mean the same thing. Crosswalks can become hidden policy. Research should therefore test explicit semantic mappings, versioned adapters, provenance for transformations, and failure-closed handling of unknown semantics.

The default should be standards composition before protocol substitution. A new representation is justified only for relations that cannot be expressed or referenced through existing standards. Even then, the proposal should define mappings and non-claims rather than declare a universal schema.

## 8 Evaluation program and falsification criteria

### 8.1 A staged empirical program

The agenda should begin smaller than the category description. Stage 1 should evaluate a single continuity dimension in a bounded domain, for example, whether test evidence still applies after a software artifact changes. Stage 2 should compare two dimensions, such as evidence and delegation, only if Stage 1 shows incremental value. Stage 3 may examine multi-agent propagation. Stage 4 may study operational integration. No stage should presume that the next one is warranted.

For each stage, pre-registration should freeze claims, cases, baselines, labels, metrics, and stop conditions. Synthetic cases are useful for control but cannot establish enterprise validity. Real traces improve ecological validity but introduce privacy, authorization, and ground-truth problems. Both negative results and infrastructure failures should be preserved.

A minimum first study should remain smaller than a general benchmark. One
bounded software-change-review domain could contain pre-registered paired cases
for four transition families: subject replacement, stale evidence, delegation
expansion, and observable-state reset. Each family should include at least one
continuity-preserving and one continuity-breaking transition. Two independent,
blinded annotators should label claim support and unresolved evidence before
method outputs are compared. Baselines should include raw trace review, an
observability summary, identity and authorization records, and a deterministic
domain checklist. The study should report per-transition precision and recall,
agreement, abstention quality, decision time, and preparation cost. This design
is a proposed test, not an executed experiment, and a synthetic result would
establish controlled discrimination rather than operational validity.

### 8.2 Baselines

Every study should include simpler alternatives:

- no continuity support;
- raw logs or traces;
- an observability summary;
- provenance-only review;
- identity and authorization records without continuity interpretation;
- a deterministic domain checklist; and
- ordinary expert review.

The proposed category fails if it only outperforms an artificially weak baseline. It should also be compared against the cost of restarting a task, re-running tests, or requesting human confirmation. In many cases, re-confirmation may be safer and cheaper than sophisticated interpretation.

### 8.3 Metrics

Technical metrics should include classification precision, recall, calibration, abstention quality, detection delay, evidence coverage, conflict detection, and explanation faithfulness. Operational metrics should include review time, preparation effort, latency, compute and model cost, and interruption rate. Human-factors metrics should include calibrated reliance, correction of false confidence, and ability to identify the decisive evidence.

No single metric should become a trust score. Results should be reported per claim type, continuity dimension, transition type, and decision. A method that works for artifact-version evidence should not be generalized to identity or delegation without separate evaluation.

### 8.4 Falsification and stop conditions

The candidate category should be narrowed, merged into an existing field, or abandoned if any of the following findings persist:

1. Ordinary observability or provenance review provides equivalent decisions at lower cost.
2. Experts cannot annotate continuity questions with acceptable agreement.
3. Useful judgments require unobservable model internals or unrestricted chain-of-thought access.
4. False positives systematically prevent legitimate adaptation or re-planning.
5. Outputs increase confidence without improving calibration or decision quality.
6. Cross-system mappings introduce more semantic uncertainty than they resolve.
7. The approach requires building a full agent runtime, identity provider, or governance platform before its value can be tested.
8. The agenda cannot demonstrate value outside examples designed by its proponents.

These are not rhetorical caveats. They are criteria for deciding whether trust continuity interpretation is a distinct research problem or merely a new label for existing work.

## 9 Implications for autonomous-agent and multi-agent-systems research

### 9.1 Research implications

The category changes the unit of analysis from an agent or outcome to a time-bounded support relation. This has several implications.

First, agent evaluation should preserve the lineage between claims and evidence, not only trajectories and scores. Second, multi-agent protocols should make task, subject, and delegation boundaries referenceable even if they do not interpret them. Third, assurance arguments should identify conditions that invalidate inheritance over time. Fourth, human-agent interaction should study how unresolved continuity is communicated without causing either blind trust or automatic rejection. Fifth, governance research should distinguish evidence interpretation from authoritative action.

The agenda also suggests a bridge between classical multi-agent trust research and contemporary language-model-agent evaluation. Classical work provides models of reliance, reputation, commitments, and organizational relations. Contemporary benchmarks provide long, partially observable, tool-mediated interactions. Trust continuity interpretation asks how the former's decision grounds survive the latter's transitions.

### 9.2 Ethical and legal considerations

Continuity analysis can increase the collection, retention, correlation, and
inference of identity, communication, delegation, and activity records. Those
records may contain personal data, confidential organizational information,
worker-monitoring data, security-sensitive traces, or information about people
who did not directly interact with the interpreting system. More evidence is
therefore not automatically better evidence. Research designs should state
purpose and authority, minimize collected fields, limit retention, control
access, redact or aggregate where possible, and measure the consequences of
missing data rather than silently expanding surveillance.

The European Union Artificial Intelligence Act illustrates the need for
scope-specific legal claims. For high-risk systems within its scope, the Act
includes requirements concerning automatic event logging, technical
documentation, transparency, human oversight, and retention of provider- or
deployer-controlled logs [34]. Those duties do not apply to every agent merely
because it is autonomous, and they do not endorse the proposed category.
Likewise, a continuity record does not settle data-protection law,
employment-monitoring rules, privilege, liability, or cross-border transfer.
Legal obligations depend on jurisdiction, role, system classification, purpose,
and deployment context. This Viewpoint offers no legal advice and no compliance
claim.

## 10 Limitations and non-claims

This Viewpoint has five major limitations.

First, neither the phrase *trust continuity* nor the broader temporal concern is unique to this paper. Prior work studies trust maintenance, temporal trust logic, transfer, repair, delegation chains, identity instability, multi-agent contracts, agentic trust management, and trace-based assurance [23-33]. The proposed contribution is only the narrower cross-dimensional claim-ground interpretation agenda, and its distinct value remains untested.

Second, the category is proposed, not discovered through a systematic review or validated through experiments. The four dimensions may prove incomplete, overlapping, or unnecessary.

Third, the synthesis spans technical standards, multi-agent theory, assurance, accountability, and emerging agent benchmarks. Their terminology is not uniform. The proposed vocabulary may conceal important disciplinary differences and must be tested with researchers from those communities.

Fourth, bounded interpretation can still be misused as authority. Interfaces, organizational incentives, and automation may turn a recommendation into a de facto gate even when the formal design denies that role. Human-authority separation must therefore be evaluated in practice.

Fifth, current agent systems may not produce enough stable, comparable evidence for continuity interpretation. That would be a substantive negative result, not merely an engineering backlog.

We explicitly do not claim that multi-agent long-running trust infrastructure currently exists as a complete system; that SAEE implements trust continuity interpretation; that hidden agent goals or internal thoughts can be read; that hallucination or drift can be eliminated; that evidence proves reality; that a continuity assessment authorizes action; or that the proposal has customer, production, standards-body, or field-level adoption.

## 11 Conclusion

Long-running multi-agent systems transform trust from a one-time judgment into a problem of temporal applicability. Identity can remain valid while its attributes change meaning. Evidence can remain authentic while its coverage expires. Delegation can remain executable while its scope is exceeded. A task can progress while the grounds for continuing no longer support the current claim.

We have proposed multi-agent long-running trust infrastructure as a candidate category for studying these relations and trust continuity interpretation as its central analytic function. The agenda is claim-scoped, compositional, non-authoritative, and falsifiable. Its four initial dimensions, identity, evidence, delegation, and observable state, are hypotheses to test, not modules to build by default.

The near-term task is therefore not to construct a comprehensive trust platform. It is to determine whether continuity judgments can be represented, annotated, and used better than simpler observability, provenance, identity, and human-review baselines. If they can, the result may provide a missing interpretive layer for autonomous-agent and multi-agent-systems infrastructure. If they cannot, the category should give way to the simpler methods that already work.

## Statements and Declarations

**Funding.** The author received no financial support for the research, authorship, or publication of this article.

**Competing interests.** The author is affiliated with Shanxi Youqibing E-Commerce Co., Ltd. and is involved in the SAEE research program from which this agenda emerged. This relationship is disclosed because future development of the proposed research direction could create a non-financial or commercial interest. The Viewpoint does not present SAEE as empirical proof and makes no claim of customer adoption, revenue, or production validation.

**Author contributions.** Zhang Bin conceived the Viewpoint, defined its scope and claims, developed the framework and research agenda, selected and verified the cited sources, revised the manuscript, and accepts responsibility for the final work. Generative assistance is disclosed separately below and is not attributed authorship.

**Data availability.** No new empirical dataset was created or analyzed for this Viewpoint. The final author must verify whether any supporting synthesis table will be deposited as supplementary material.

**Code availability.** This Viewpoint does not introduce an implementation. No code is presented as evidence for the proposed category.

**Use of generative artificial intelligence.** A generative large-language-model assistant was used to organize source notes, compare journal requirements, and draft language. The human author is responsible for verifying all sources, revising the argument, and approving the final text. This statement must be reviewed and updated before submission.

## References

1. Sabater, J., & Sierra, C. (2005). Review on computational trust and reputation models. *Artificial Intelligence Review, 24*(1), 33-60. <https://doi.org/10.1007/s10462-004-0041-5>

2. Pinyol, I., & Sabater-Mir, J. (2013). Computational trust and reputation models for open multi-agent systems: A review. *Artificial Intelligence Review, 40*(1), 1-25. <https://doi.org/10.1007/s10462-011-9277-z>

3. Braga, D. D. S., Niemann, M., Hellingrath, B., & de Lima Neto, F. B. (2018). Survey on computational trust and reputation models. *ACM Computing Surveys, 51*(5), 1-40. <https://doi.org/10.1145/3236008>

4. Abbass, H. A., Petraki, E., Merrick, K., Harvey, J., & Barlow, M. (2016). Trusted autonomy and cognitive cyber symbiosis: Open challenges. *Cognitive Computation, 8*(3), 385-408. <https://doi.org/10.1007/s12559-015-9365-5>

5. Fisher, M., Mascardi, V., Rozier, K. Y., Schlingloff, B.-H., Winikoff, M., & Yorke-Smith, N. (2021). Towards a framework for certification of reliable autonomous systems. *Autonomous Agents and Multi-Agent Systems, 35*, Article 8. <https://doi.org/10.1007/s10458-020-09487-2>

6. Grossi, D., Royakkers, L., & Dignum, F. (2007). Organizational structure and responsibility. *Artificial Intelligence and Law, 15*(3), 223-249. <https://doi.org/10.1007/s10506-007-9054-0>

7. Yazdanpanah, V., Gerding, E. H., Stein, S., Dastani, M., Jonker, C. M., Norman, T. J., & Ramchurn, S. D. (2023). Reasoning about responsibility in autonomous systems: Challenges and opportunities. *AI & Society, 38*(4), 1453-1464. <https://doi.org/10.1007/s00146-022-01607-8>

8. Sloan, P., & Ajmeri, N. (2024). Commitment-based negotiation semantics for accountability in multi-agent systems. *Annals of Mathematics and Artificial Intelligence, 92*(4), 877-901. <https://doi.org/10.1007/s10472-023-09875-w>

9. Constantinescu, M., & Kaptein, M. (2025). Responsibility gaps, LLMs & organisations: Many agents, many levels, and many interactions. *Science and Engineering Ethics, 31*, Article 36. <https://doi.org/10.1007/s11948-025-00560-1>

10. Park, J. S., O'Brien, J., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). Generative agents: Interactive simulacra of human behavior. In *Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology* (pp. 1-22). <https://doi.org/10.1145/3586183.3606763>

11. Huang, Q., Vora, J., Liang, P., & Leskovec, J. (2024). MLAgentBench: Evaluating language agents on machine learning experimentation. In *Proceedings of the 41st International Conference on Machine Learning* (PMLR 235, pp. 20271-20309). <https://proceedings.mlr.press/v235/huang24y.html>

12. Ma, C., Zhang, J., Zhu, Z., Yang, C., Yang, Y., Jin, Y., Lan, Z., Kong, L., & He, J. (2024). AgentBoard: An analytical evaluation board of multi-turn LLM agents. In *Advances in Neural Information Processing Systems 37*. <https://doi.org/10.52202/079017-2365>

13. Xu, F. F., Song, Y., Li, B., Tang, Y., Jain, K., Bao, M., Wang, Z. Z., Zhou, X., Guo, Z., Cao, M., Yang, M., Lu, H. Y., Martin, A., Su, Z., Maben, L. M., Mehta, R., Chi, W., Jang, L., Xie, Y., ... Neubig, G. (2025). TheAgentCompany: Benchmarking LLM agents on consequential real world tasks. In *Advances in Neural Information Processing Systems 38*. <https://proceedings.neurips.cc/paper_files/paper/2025/hash/0d744742f6fac4d1134c019b7cef3c8a-Abstract-Datasets_and_Benchmarks_Track.html>

14. Allmendinger, S., Bonenberger, L., Endres, K., Fetzer, D., Gimpel, H., & Kühl, N. (2026). Multi-agent AI. *Electronic Markets, 36*, Article 18. <https://doi.org/10.1007/s12525-025-00862-z>

15. Fischli, R., Franklin, M., Manzini, A., & Gabriel, I. (2026). Agents, alignment, and the many faces of autonomy. *Minds and Machines, 36*, Article 34. <https://doi.org/10.1007/s11023-026-09786-9>

16. Groth, P., & Moreau, L. (Eds.). (2013). PROV-Overview: An overview of the PROV family of documents. W3C Working Group Note. <https://www.w3.org/TR/prov-overview/>

17. OpenTelemetry Authors. (2026). *OpenTelemetry specification 1.59.0*. <https://opentelemetry.io/docs/specs/otel/>

18. SPIFFE Project Authors. (2026). *SPIFFE identity and verifiable identity document, version 1.15.1*. <https://spiffe.io/docs/latest/spiffe-specs/spiffe-id/>

19. Birkholz, H., Delignat-Lavaud, A., Fournet, C., Deshpande, Y., & Lasker, S. (2026). An architecture for trustworthy and transparent digital supply chains. RFC 9943. <https://doi.org/10.17487/RFC9943>

20. Model Context Protocol Authors. (2025). *Model Context Protocol specification, 2025-11-25*. <https://modelcontextprotocol.io/specification/2025-11-25>

21. Agent2Agent Protocol Authors. (2026). *Agent2Agent Protocol specification, version 1.0*. <https://a2a-protocol.org/latest/specification/>

22. Tabassi, E. (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. National Institute of Standards and Technology. <https://doi.org/10.6028/NIST.AI.100-1>

23. Khosravifar, B., Gomrokchi, M., Bentahar, J., & Thiran, P. (2009). Maintenance-based trust for multi-agent systems. In *Proceedings of the 8th International Conference on Autonomous Agents and Multiagent Systems* (pp. 1017-1024). International Foundation for Autonomous Agents and Multiagent Systems. <https://www.ifaamas.org/Proceedings/aamas09/pdf/01_Full%20Papers/20_114_FP_0546.pdf>

24. Drawel, N., Bentahar, J., Laarej, A., & Rjoub, G. (2022). Formal verification of group and propagated trust in multi-agent systems. *Autonomous Agents and Multi-Agent Systems, 36*, Article 19. <https://doi.org/10.1007/s10458-021-09542-6>

25. Diab, M., & Demiris, Y. (2024). A framework for trust-related knowledge transfer in human-robot interaction. *Autonomous Agents and Multi-Agent Systems, 38*, Article 24. <https://doi.org/10.1007/s10458-024-09653-w>

26. Kox, E. S., Kerstholt, J. H., Hueting, T. F., & de Vries, P. W. (2021). Trust repair in human-agent teams: The effectiveness of explanations and expressing regret. *Autonomous Agents and Multi-Agent Systems, 35*, Article 30. <https://doi.org/10.1007/s10458-021-09515-9>

27. Hu, Y.-J. (2001). Some thoughts on agent trust and delegation. In *Proceedings of the Fifth International Conference on Autonomous Agents* (pp. 489-496). Association for Computing Machinery. <https://doi.org/10.1145/375735.376424>

28. Baqueta, J. J., & Tacla, C. A. (2026). A task delegation model: An approach based on trustworthiness in sub-delegations and delegation chain formation. *Autonomous Agents and Multi-Agent Systems, 40*, Article 15. <https://doi.org/10.1007/s10458-026-09741-z>

29. Hu, B. A., Rong, H., & Van Kleek, M. (2026). Dissociative identity: Language model agents lack grounding for reputation mechanisms. In *Proceedings of the 2026 ACM Conference on Fairness, Accountability, and Transparency* (pp. 4199-4219). Association for Computing Machinery. <https://doi.org/10.1145/3805689.3806748>

30. Dewes, R., & Dimitrova, R. (2025). Contract-based design and verification of multi-agent systems with quantitative temporal requirements. In *Proceedings of the AAAI Conference on Artificial Intelligence, 39*(22), 23152-23159. <https://doi.org/10.1609/aaai.v39i22.34480>

31. Raza, S., Sapkota, R., Karkee, M., & Emmanouilidis, C. (2026). TRiSM for agentic AI: A review of trust, risk, and security management in LLM-based agentic multi-agent systems. *AI Open, 7*, 71-95. <https://doi.org/10.1016/j.aiopen.2026.02.006>

32. He, P., Dai, Z., Tang, X., Xing, Y., Liu, H., Zeng, J., Peng, Q., Agrawal, S., Varshney, S., Wang, S., Tang, J., & He, Q. (2026). To trust or not to trust: Attention-based trust management for LLM multi-agent systems. In *Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics*. Accepted paper. <https://arxiv.org/abs/2506.02546>

33. Paduraru, C., Macovei, B., & Stefanescu, A. (2026). Trace-to-logic assurance for agentic AI: Mining probabilistic rules from message-action traces. In *Proceedings of the 21st International Conference on Evaluation of Novel Approaches to Software Engineering* (Vol. 1, pp. 579-586). <https://doi.org/10.5220/0014983100004015>

34. European Parliament & Council of the European Union. (2024). Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence. *Official Journal of the European Union*. <https://eur-lex.europa.eu/eli/reg/2024/1689/oj>
