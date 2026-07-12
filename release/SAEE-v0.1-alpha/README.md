# SAEE-v0.1-alpha local Release candidate

This directory is the local, Agent-readable release handoff for `SAEE Agent
Readiness Platform`. It is a candidate manifest, not a Git tag or GitHub
Release. The local baseline commit is `c0cf49e`; no tag, push, or GitHub Release
has been created.

## Candidate surface

- exactly two public operations: `saee.evaluate_agent_run` and
  `saee.evaluate_evidence`;
- deterministic local service, CLI and stdio MCP adapter;
- Qianfan-style controlled host simulation plus two sanitized real-provider
  synthetic-scenario receipts;
- 30-minute Cloud Entry Package;
- locally rendered 10-page whitepaper and 3-minute demo video.

## Blocking release gates

1. The owner has chosen to withhold a public root `LICENSE` for now.
2. Tag, push and GitHub Release are not authorized.

Read `release-manifest.json` for machine truth and `RELEASE_NOTES.md` for the
draft public narrative.

```text
release_candidate_prepared=true
git_commit_created=true
git_commit_sha=c0cf49e17ef00038df8e33f7dd3d98956324260f
git_tag_created=false
github_release_created=false
public_release_executed=false
production_ready=false
```
