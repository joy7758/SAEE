# Paper author registry

This is the agent-readable entry point for author metadata reused across local
paper packages.

```text
canonical_public_registry=paper_submission/author-registry.public.json
canonical_private_registry=PRIVATE_PAPER_AUTHOR_REGISTRY.json
private_registry_version_controlled=false
paper_specific_author_selection_required=true
paper_specific_author_order_required=true
paper_specific_credit_confirmation_required=true
paper_specific_consent_required=true
```

## Retrieval order

1. Read `paper_submission/author-registry.public.json` for names, emails,
   ORCIDs, public profiles, countries, and affiliations.
2. Read a paper-specific submission manifest to determine which registered
   people are actual authors and their order. Registry presence is not
   authorship evidence.
3. Use `PRIVATE_PAPER_AUTHOR_REGISTRY.json` only for a portal field that
   explicitly requires private information. Never copy private fields into a
   manuscript, public repository, website, citation record, or supplementary
   package.
4. Obtain per-paper consent, CRediT roles, funding, competing-interest details,
   originality confirmation, and final manuscript approval before submission.

## Security boundary

Authentication credentials are forbidden in both registries. Source documents
may contain credentials; agents must ignore them and must not copy, quote,
retain, or synchronize them.
