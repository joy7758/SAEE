# SAEE Agent Review Skill MVP

SAEE Agent Review is a local, Agent-readable Skill package for one narrow
workflow: review the declared evidence for a completed high-impact coding run
before a consequential next step.

It routes an eligible Agent to the existing `saee.evaluate_agent_run`
operation. It does not add a capability, schema, MCP tool, evaluator, wrapper,
CLI, workflow hook, or authorization system.

```text
package_status=created_not_installed
first_carrier=Codex
product_bound_to_codex=false
canonical_operation=saee.evaluate_agent_run
```

## Package contents

```text
saee-agent-review-skill/
├── SKILL.md
├── README.md
└── examples/
    ├── coding-change-review.md
    └── missing-evidence-example.md
```

`SKILL.md` defines discovery, trigger, eligibility, invocation, interpretation,
and stop boundaries. The examples show one qualifying review and one existing
evaluator result without defining a new response format.

## Future installation

Installation is intentionally outside the current creation phase. A future
authorized local Codex carrier may link this source package into the user's
Skill directory:

```bash
export SAEE_REPO=/absolute/path/to/SAEE
test ! -e "$HOME/.codex/skills/saee-agent-review"
mkdir -p "$HOME/.codex/skills"
ln -s "$SAEE_REPO/saee-agent-review-skill" \
  "$HOME/.codex/skills/saee-agent-review"
```

These commands are documentation only and were not run when this package was
created. A future installation must verify the absolute repository path and
must not overwrite an existing file, directory, or symlink.

Codex is the first proposed carrier and observation window, not a permanent
product dependency. Other Agents may consume the same Agent-readable contract
when separately validated.

## Ten-minute future experience

After a separate installation and first-user-test authorization:

1. Confirm the SAEE repository's existing MCP configuration can resolve
   `saee.evaluate_agent_run`.
2. Start a fresh Agent session so the carrier can discover the Skill.
3. Present a completed synthetic or local coding run that is approaching a
   merge- or release-like step.
4. Declare the trace and evidence truthfully, including a missing
   `ROLLBACK_PLAN` when that is the actual condition.
5. Let the Agent decide whether the Skill is eligible; do not force a tool call.
6. If invoked, inspect the existing recommendation, missing evidence, risks,
   limitations, and truth boundary.
7. Observe whether the output makes the next human or Agent action clearer.

The first useful signal is not merely a successful invocation. It is a lower
decision cost: the user can identify what is missing and what must happen next.

## Boundaries

SAEE Agent Review:

- evaluates declared evidence readiness;
- may recommend `CONTINUE`, `HUMAN_REVIEW_REQUIRED`, `REPLAN`, or `STOP`;
- may make an evidence gap easier to act on.

SAEE Agent Review does not:

- authorize, approve, merge, deploy, or execute;
- replace CI, code review, IAM, policy engines, or human responsibility;
- verify trace authenticity or evidence provenance;
- certify safety, security, compliance, trust, or production readiness;
- imply customer validation, commercial validation, or product launch.

The existing evaluator is local Alpha. Its score represents required-evidence
coverage and must not be presented as a probability of reliability or safety.

## Future removal

A future authorized uninstall should remove only the expected symlink after
confirming its target:

```bash
test -L "$HOME/.codex/skills/saee-agent-review"
readlink "$HOME/.codex/skills/saee-agent-review"
unlink "$HOME/.codex/skills/saee-agent-review"
```

These commands were not run during package creation.

## Canonical references

- Skill instructions: [`SKILL.md`](SKILL.md)
- Capability inventory:
  [`../capability-package/manifest.json`](../capability-package/manifest.json)
- Request schema:
  [`../agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json`](../agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json)
- Response schema:
  [`../agent-interface/qianfan/saee-evaluate-agent-run-response.schema.v0.1.json`](../agent-interface/qianfan/saee-evaluate-agent-run-response.schema.v0.1.json)
