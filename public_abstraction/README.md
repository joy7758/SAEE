# SAEE Public Abstraction Release

Status: local GitHub public-layer package, not released.

## Purpose

This package provides a public-safe abstraction for understanding SAEE without
exposing the private implementation.

It is not the SAEE runtime.

## Contents

- `demo/minimal_public_demo.py`: toy demonstration only.
- `abstraction_layer/phase_space_stub.py`: public phase-space abstraction.
- `documentation_only/BOUNDARY.md`: implementation confidentiality boundary.

## Run

```bash
python3 github_public_release/demo/minimal_public_demo.py
```

## Not Included

- kernel;
- runtime;
- fitness logic;
- selection logic;
- mutation logic;
- lineage implementation;
- reproduction implementation.

## External Status

```text
github_release_created: false
tag_created: false
package_uploaded: false
private_core_exported: false
```

