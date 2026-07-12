# SAEE-v0.1-alpha local Release candidate

This directory is the local, Agent-readable release handoff for `SAEE Agent
Readiness Platform`. It is a candidate manifest, not a Git tag or GitHub
Release.

## Candidate surface

- exactly two public operations: `saee.evaluate_agent_run` and
  `saee.evaluate_evidence`;
- deterministic local service, CLI and stdio MCP adapter;
- Qianfan-style controlled host simulation;
- 30-minute Cloud Entry Package;
- locally rendered 10-page whitepaper and 3-minute demo video.

## Blocking release gates

1. The repository has no owner-selected root `LICENSE`.
2. `main` has no baseline commit; the public first-commit scope needs owner
   review because the workspace contains a much larger historical project.
3. Tag, push and GitHub Release are consequential public actions and require
   explicit authorization.

Read `release-manifest.json` for machine truth and `RELEASE_NOTES.md` for the
draft public narrative.

```text
release_candidate_prepared=true
git_commit_created=false
git_tag_created=false
github_release_created=false
public_release_executed=false
production_ready=false
```
