# JAAMAS Viewpoint Information Sheet - Working Draft

Proposed title: *Multi-Agent Long-Running Trust Infrastructure: A Research
Agenda for Trust Continuity Interpretation*

Article type: Viewpoint

## 1. Novelty and significance

The article proposes a candidate research category, “multi-agent long-running
trust infrastructure,” and specifies a bounded analytic function, “trust
continuity interpretation.” It does not claim to coin the phrase “trust
continuity.” The central question is not whether an agent is trusted once,
but whether the identity, evidence, delegation, and state conditions that
supported a prior trust claim still support a current claim after a sequence of
changes. The contribution matters to autonomous-agent and multi-agent-systems
research because current work often treats trust, observability, identity,
assurance, accountability, interoperability, and task evaluation as separate
problems. Those bodies of work are individually necessary, but long-running
multi-agent operation creates a cross-cutting temporal interpretation problem:
locally valid evidence can remain available while the claim it once supported
has changed in scope, time, subject, or decision context.

The article does not propose a universal trust score, a new authorization
system, or a replacement protocol. It offers a falsifiable decomposition into
identity continuity, evidence continuity, delegation continuity, and state
continuity, together with research questions, baseline comparisons, and stop
conditions.

The novelty claim is deliberately narrow. Prior work already studies adaptive
trust maintenance, temporal trust logic, trust transfer, human-agent trust
repair, agent delegation chains, and the absence of stable identity grounding
for language-model-agent reputation. The manuscript asks whether a distinct
cross-infrastructure decision problem remains: determining whether identified
grounds for a prior bounded claim still apply after heterogeneous changes.
Recent contract-based multi-agent verification, agentic trust-risk-security
management, inter-agent message trust, and trace-to-logic assurance make these
especially strong alternatives rather than evidence that a new category is
needed.

## 2. Why the Viewpoint is timely

Agent research has moved from single-turn responses toward tool use, multi-turn
interaction, digital work, asynchronous tasks, and multi-agent collaboration.
Recent benchmarks show that evaluation now needs intermediate progress,
partially observable environments, long-term planning, and consequential task
outcomes rather than final answers alone. At the same time, infrastructure has
advanced in complementary directions: OpenTelemetry provides observability;
SPIFFE provides workload identity; W3C PROV and SCITT provide provenance and
transparent statements; MCP and A2A provide tool and agent interoperability;
governance systems provide policy and organizational control. The timely
question is how to interpret these signals together over time without
misrepresenting connection, observation, identity, or a signed statement as a
continuing trust guarantee.

## 3. Basis and synthesis method

The Viewpoint is grounded in a scoped conceptual synthesis of adjacent
literature and infrastructure families. The literature includes computational
trust and reputation; reliable-autonomy assurance; responsibility and
accountability; contract-based verification; agentic trust, risk, and security
management; message trust; trace-based assurance; and long-horizon agent
evaluation. The infrastructure families are provenance, observability,
workload identity, transparent statements, tool interoperability, and agent
interoperability.

Sources were selected because they define an adjacent construct, provide a
review or research agenda, report an archival long-horizon-agent evaluation, or
specify an active infrastructure boundary. The synthesis explicitly compares
what each source can establish with what it does not establish. The paper also
states counterexamples and stop conditions: the category should be rejected or
narrowed if ordinary observability review performs equally well, if continuity
labels are unstable, if the method depends on unobservable internal states, or
if costs exceed decision value. This is not claimed to be a systematic review.

## 4. Related research, survey, and viewpoint papers

The closest bodies of work include:

- computational trust and reputation reviews by Sabater and Sierra, Pinyol and
  Sabater-Mir, and Braga et al.;
- the reliable-autonomy certification roadmap by Fisher et al.;
- responsibility and accountability agendas by Yazdanpanah et al., Grossi et
  al., and Sloan and Ajmeri;
- maintenance-based trust and formal temporal trust reasoning by Khosravifar et
  al. and Drawel et al.;
- trust transfer and repair by Diab and Demiris and Kox et al.;
- agent trust, recursive delegation, and delegation chains by Hu and by
  Baqueta and Tacla;
- the critique of persistent identity grounding for language-model-agent
  reputation by Hu, Rong, and Van Kleek;
- quantitative contract-based multi-agent verification by Dewes and Dimitrova;
- the agentic trust-risk-security management review by Raza et al.;
- message- and agent-level trust management by He et al.;
- trace-to-logic assurance by Paduraru et al.;
- long-horizon and multi-turn agent evaluations including MLAgentBench,
  AgentBoard, and TheAgentCompany;
- recent analyses of multi-agent artificial intelligence, autonomy, and
  responsibility gaps.

The manuscript's numbered reference list supplies complete bibliographic data.

## 5. Difference from prior work

Unlike computational trust and reputation work, the article does not estimate a
partner's trustworthiness or aggregate reputation. Unlike temporal trust
maintenance, it does not primarily update a trust estimate. Unlike formal
temporal trust logic, it does not verify a trust proposition over a declared
model. Unlike trust transfer or repair, it does not transfer a learned trust
level or seek to restore a human attitude. Unlike observability, it does not
define telemetry collection. Unlike assurance and certification work, it
does not claim a certification regime. Unlike accountability work, it does not
allocate final responsibility. Unlike agent benchmarks, it does not introduce a
new performance test. Unlike contract verification, message trust management,
or trace-deviation assurance, it does not test requirement satisfaction,
estimate message trustworthiness, or rank contract-admissible actions. Its
distinctive object is the continuing applicability of
the grounds for a bounded claim after changes in agent identity, evidence,
delegation, or observable task state. Its second distinction is architectural:
it requires composition of existing standards rather than protocol
substitution. Its third distinction is authority separation: an interpretation
may support a decision but cannot authorize action.

This claimed distinction is a research hypothesis. If existing maintenance,
temporal-logic, transfer, repair, provenance, or observability methods answer
the same operational questions at equal or lower cost, the proposed category
should be narrowed or abandoned.

## 6. Prior publication and overlap

The manuscript is a new journal-oriented synthesis derived from private
internal SAEE future-research notes. The author confirms that no part of this
Viewpoint has been previously published and that no overlapping public
publication exists. The existing SAEE evidence-evaluation paper draft is a
separate system-oriented manuscript and is not reused as this Viewpoint's
contribution. This package has not been submitted to the journal.
