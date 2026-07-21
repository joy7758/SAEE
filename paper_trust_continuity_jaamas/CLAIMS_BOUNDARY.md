# Claims Boundary

## Paper Identity

This is a category-definition and research-agenda Viewpoint. It is not a system
paper, product paper, standard proposal, empirical validation report, or market
adoption claim.

## Allowed Claims

The manuscript may claim that:

1. Long-running and multi-agent operation creates a temporal interpretation
   problem that is not exhausted by one-time identity, trace collection,
   authorization, final-outcome evaluation, or trust scores.
2. “Multi-Agent Long-Running Trust Infrastructure” is a proposed research
   category, not an established field label.
3. “Trust Continuity Interpretation” is a proposed, specifically scoped
   analytic function that asks
   whether prior trust grounds still support a current, bounded claim.
4. Identity, evidence, delegation, and state continuity form a useful initial
   decomposition for research, subject to empirical revision or rejection.
5. Existing standards and systems should be composed as evidence sources rather
   than replaced by a new universal protocol.
6. The agenda is falsifiable through annotation stability, decision utility,
   comparative baselines, cost, and false-reliance measurements.

## Prohibited Claims

The manuscript must not claim that:

- SAEE has implemented a complete trust infrastructure.
- SAEE has implemented trust-continuity interpretation.
- SAEE detects or repairs goal drift, state drift, or hallucination.
- Evidence proves reality, truth, completeness, or compliance.
- Interpretation authorizes action or replaces human authority.
- A single trust score can represent all relevant uncertainty.
- OpenTelemetry, SPIFFE/SPIRE, SCITT, MCP, A2A, IAM, or governance platforms are
  deficient products or should be replaced.
- The proposed category is recognized by the academic community, standards
  bodies, customers, or the market.
- The phrase “trust continuity” is unique to this work or was coined by this
  paper.
- Temporal trust modeling, trust maintenance, trust transfer, trust repair,
  delegation chains, or language-model-agent identity instability are newly
  discovered by this paper.
- Contract-based multi-agent verification, message and agent trust management,
  trace-based assurance, or agentic trust-risk-security management are absent
  from prior work.
- European Union logging and documentation duties apply to every autonomous
  agent or establish the validity of this research category.
- Customer adoption, production deployment, revenue, or commercial validation
  exists.
- Current Agent Evidence source code or runtime integration is complete unless
  separately verified at submission time.

## Current SAEE Boundary

```text
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
CURRENT_RESEARCH_EXAMPLE=EVIDENCE_EVALUATION_AND_READINESS_BOUNDARY
TRUST_CONTINUITY_INTERPRETATION_IMPLEMENTED=false
STATE_ENGINE_IMPLEMENTED=false
GOAL_ENGINE_IMPLEMENTED=false
AUTONOMOUS_GOVERNANCE_IMPLEMENTED=false
FUTURE_RESEARCH_ONLY=true
```

## Required Language

Prefer:

- “we propose” over “we establish”;
- “candidate category” over “new infrastructure category”;
- “bounded interpretation” over “trust determination”;
- “may support a decision” over “makes a decision”;
- “observable signals” over “internal state”;
- “research hypothesis” over “architecture fact.”

## Stop Rule

If a defensible paper requires claiming an implemented state engine, new
identity authority, universal schema, automated governance, or customer proof,
the paper must be narrowed rather than the product scope expanded.
