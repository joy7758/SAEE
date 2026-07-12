# SAEE-v0.1-alpha public baseline review

The repository currently has no `HEAD` and contains more than five thousand
non-ignored files from the broader SAEE research and engineering history. The
curated `public-source-allowlist.txt` isolates the Agent Readiness product
slice; PDF/video are separate candidate Release assets.

Run:

```bash
python3 scripts/saee_public_baseline_audit.py
```

Passing this audit means only that all allowlisted files exist, their names do
not include secret/credential paths, and no high-confidence token/private-key
pattern was found. It does not approve disclosure, choose a license, stage
files, create the first commit, tag, push, or publish a GitHub Release.

Human decisions still required:

1. select and add the root `LICENSE`;
2. inspect the exact allowlist and decide whether the website source belongs in
   the first public baseline;
3. approve a commit message and public history scope;
4. separately authorize tag, push and GitHub Release.
