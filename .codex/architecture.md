# SAEE System Architecture

Core:

- `saee_backend/`

Product:

- `phase_b_product/`

Documentation:

- `docs/`

Public:

- `external-publication/`
- `docs/canonical/`
- `llms.txt`
- `agent-index.json`

Never modify without explicit instruction:

- kernel
- runtime
- private core
- hidden evaluation logic

Commercial execution boundary:

- Documentation, status, and local validation surfaces can be updated when in scope.
- Runtime, backend behavior, API schemas, scoring mechanisms, and private core remain out of scope unless explicitly authorized.
- A local pass, smoke pass, or internal self-play pass must not be described as production readiness, customer validation, or external validation.
